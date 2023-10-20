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
from bleak import BleakScanner, BleakClient



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

@app.callback(
    Output("output_data_bluetooth", "children"),
    [Input("btn_retrieve_bluetooth", "n_clicks")]
)
def retrieve_data_bluetooth(n_clicks):
    if n_clicks is None:
        return "Press the button to retrieve Bluetooth data."

    # Here we move the event loop creation and closing inside the function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(fetch_data_from_arduino())
    loop.close()

    value = bytearray(result)
    drunk_amount = value[0] | (value[1] << 8)

    print("Drunk amount from Arduino:", drunk_amount)
    return f"Drunk amount from Arduino: {drunk_amount}"




async def fetch_data_from_arduino(retries=3):
    for _ in range(retries):
        devices = await BleakScanner.discover()

        hydroMate_address = None
        for device in devices:
            if device.name == "HydroMate":
                hydroMate_address = device.address
                break

        if not hydroMate_address:
            await asyncio.sleep(2)  # Sleep for a bit before retrying
            continue

        client = BleakClient(hydroMate_address, timeout=120)
        try:
            connected = await client.connect()
            if not connected:
                continue

            await client.write_gatt_char("00002a37-0000-1000-8000-00805f9b34fb", bytearray([1]))
            await asyncio.sleep(1)  # Wait a bit to give the Arduino time to respond
            value = await client.read_gatt_char("00002a37-0000-1000-8000-00805f9b34fb")

            print("Value before return:", value)
            return value.splitlines()


        finally:
            if client.is_connected:
                await client.disconnect()
            await asyncio.sleep(2)  # This sleep ensures some time gap between subsequent BLE operations
    return ["Could not fetch data after multiple attempts"]






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
     Output('consecutive-days-output', 'children')],
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
    goal = data['total']
    days_above_goal = compute_consecutive_days_above_goal(df_water, goal)
    message = f"You've been above your hydration goal for {days_above_goal} consecutive days!" if days_above_goal > 0 else "You're below your hydration goal."

    return {'data': [trace], 'layout': layout}, message


