import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from dash_table.Format import Format, Group, Scheme
import dash_table.FormatTemplate as FormatTemplate
from datetime import datetime as dt
from app import app
import dash
from dash.dependencies import Input, Output, State
from dash import ctx
import dash_table
import plotly.express as px
import base64
import io
import serial
import requests
import os
import layouts
import asyncio
import threading
import queue
import orjson
from bleak import BleakScanner, BleakClient
import bleak



#####################
## HELPER FUNCTIONS ##
def compute_consecutive_days_above_goal(df, goal):
    consecutive_days = 0
    for consumption in df['Water Consumption (L)'].iloc[::-1]:  # Start from the end
        if consumption > goal:
            consecutive_days += 1
        else:
            break  # Stop counting if a day below the goal is found
    return consecutive_days

def get_daily_figure(df_day, goal=3):
    trace_day = go.Scatter(x=df_day['Time'], 
                           y=df_day['Cumulative Consumption (L)'], 
                           mode='lines+markers', 
                           name='Hourly Consumption')
    layout_day = go.Layout(title='Today\'s Water Consumption',
                           xaxis=dict(title='Hour of the Day'),
                           yaxis=dict(title='Water Consumption (L)'),
                           shapes=[
                               dict(
                                   type='line',
                                   y0=goal,
                                   y1=goal,
                                   x0=df_day['Time'].min(),
                                   x1=df_day['Time'].max(),
                                   line=dict(color='Red')
                               )
                           ]
                          )
    return {'data': [trace_day], 'layout': layout_day}



df_water=pd.read_csv('water_consumption.csv')
df_day = pd.read_csv('water_consumption_day.csv')
############ HOME PAGE


####
#ARDUINO DATA

# Create a queue to pass data between threads
import asyncio
from bleak import BleakScanner, BleakClient

async def retrieve_ble_data():
    devices = await BleakScanner.discover()
    hydromate_device = None
    
    for device in devices:
        if device.name == "HydromateBLE":
            hydromate_device = device
            break

    if not hydromate_device:
        return "Device not found."

    async with BleakClient(hydromate_device.address) as client:
        value = await client.read_gatt_char("0000ABCD-0000-1000-8000-00805f9b34fb")
        return int.from_bytes(value, byteorder='little', signed=True)

def get_ble_data():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(retrieve_ble_data())



@app.callback(
    Output("output_data_bluetooth", "children"),
    Input("btn_retrieve_bluetooth", "n_clicks")
)
def update_output(n_clicks):
    if n_clicks and n_clicks > 0:
        return get_ble_data()
    return "Press button to get data."



############ PAGE 1 SETTINGS

@app.callback(
    Output('water_recommendation_ouput', 'children'),
    Output('water-value', 'data'),
    Input('Name', 'value'),
    Input('age', 'value'),
    Input('weight', 'value'),
    Input('height', 'value'),
    Input('gender', 'value'),
    Input('activity', 'value'),
    Input('submit', 'n_clicks')
)
def suggest_drink(Name, age,weight,height,gender,activity,n_clicks):
    if ctx.triggered_id == 'submit':
        base_intake = 1.8  # Base intake in liters
        activity=int(activity)
        # Weight adjustment
        weight_adjustment = 0.05 * max((weight - 50) / 10, 0)

        # Age adjustment
        age_adjustment = -0.01 * max((age - 20) / 10, 0)

        # Height adjustment
        height_adjustment = 0.05 if height > 175 else 0

        # Gender adjustment
        gender_adjustment = 0.1 if gender == 1 else -0.1 if gender == 2 else 0

        # Activity adjustment
        activity_adjustments = [0.1, 0.2, 0.3]
        activity_adjustment = activity_adjustments[activity - 1]

        # Calculate total adjustment
        total_adjustment = (1 + weight_adjustment + age_adjustment + height_adjustment + gender_adjustment + activity_adjustment)

        # Calculate recommended water intake
        drink = base_intake * total_adjustment
        message = 'Hello {}! You should drink {:.2f} liters of water per day'.format(Name, drink)
        return message,{'total': drink}
    return "Hello! Please fill in the form above to get your water recommendation", {'total': 2.0}


############ PAGE 3 WATER CONSUMPTION
@app.callback(
    [Output('empty-graph', 'figure'),
     Output('consecutive-days-output', 'children'),
     Output('day-graph', 'figure'),
     Output('today-output', 'children')],
    [Input('show-chart-button', 'n_clicks')],
    [State('water-value', 'data')]
)
def update_graph(n_clicks, data):
    if not n_clicks:
        raise dash.exceptions.PreventUpdate  # Do not update if button hasn't been clicked

    # Extract the constant value from the dcc.Store
    constant_value = data['total']
    
    # Define the trace for the water consumption data
    trace = go.Scatter(x=df_water['Date'], 
                       y=df_water['Water Consumption (L)'], 
                       mode='lines+markers', 
                       name='Water Consumption')
    
    # Define the layout with the constant line using 'shapes'
    layout = go.Layout(title='Daily Water Consumption',
                       xaxis=dict(title='Date'),
                       yaxis=dict(title='Water Consumption (L)'),
                       shapes=[
                           dict(
                               type='line',
                               y0=constant_value,
                               y1=constant_value,
                               x0=df_water['Date'].min(),
                               x1=df_water['Date'].max(),
                               line=dict(color='Red')
                           )
                       ]
                      )
    trace_hourly = go.Scatter(x=df_day['Hour'], 
                              y=df_day['Cumulative Consumption (L)'], 
                              mode='lines+markers', 
                              name='Hourly Water Consumption')
    
    layout_hourly = go.Layout(title='Hourly Water Consumption',
                              xaxis=dict(title='Hour'),
                              yaxis=dict(title='Water Consumption (L)'),
                              shapes=[
                                  dict(
                                      type='line',
                                      y0=constant_value,
                                      y1=constant_value,
                                      x0=df_day['Hour'].min(),
                                      x1=df_day['Hour'].max(),
                                      line=dict(color='Red')
                                  )
                              ]
                             )
    
    hourly_figure = {'data': [trace_hourly], 'layout': layout_hourly}

    # Calculate days above goal
    goal = data['total']
    days_above_goal = compute_consecutive_days_above_goal(df_water, goal)
    message = f"You've been above your hydration goal for {days_above_goal} consecutive days!" if days_above_goal > 0 else "You're below your hydration goal."

    # Calculate the difference between daily goal and current consumption
    missing_amount = data['total'] - df_day['Cumulative Consumption (L)'].iloc[-1]
    missing_message = f"You're missing {missing_amount:.2f}L to reach your goal today." if missing_amount > 0 else "You've reached your goal today!"

    return {'data': [trace], 'layout': layout}, message, hourly_figure, missing_message

