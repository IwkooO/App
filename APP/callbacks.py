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
from datetime import datetime
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

# Create a queue to pass data between threads


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
    Output("output_data_bluetooth", "children"),Output('daily-water-store', 'data'),Output('historical-water-store', 'data'),
    Input("btn_retrieve_bluetooth", "n_clicks"),
    State('historical-water-store', 'data')
)

def update_output(n_clicks,historical):
    if n_clicks and n_clicks > 0:
        historical_df = pd.DataFrame(columns=["Date", "Consumed"])
        water_consumed = get_ble_data()  # Assuming this function retrieves daily water data
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if water_consumed=="Device not found.":
            water_consumed=0
        water_consumed=water_consumed/1000
        historical.append({"Date": current_date, "Consumed": water_consumed})
        print(historical)
        return f"Water consumed today: {water_consumed} L", water_consumed,historical
    return "Press button to get data.", 0,historical



### PROGREES BAR

@app.callback(
    Output("progress", "value"),
    Output("water-message", "children"),  # Output for displaying water consumed today
    Input("show-remaining-button", "n_clicks"),
    State('daily-water-store', 'data'),
    State('water-value', 'data')
)
def update_progress_bar_and_water_message(n_clicks, daily_water_consumption,water_value):
    # Initialize progress_value and water_message with default values
    progress_value = 0.0
    water_message = "Press button to get data."
    
    if n_clicks and n_clicks > 0:
        
        water_goal = water_value['total']*1000  # Set your daily water goal
        print(water_goal)
        daily_water_consumption=daily_water_consumption*1000
        daily_water_consumption = int(daily_water_consumption) if daily_water_consumption else 0  # Convert to integer with a default value of 0
        remaining_water = max(water_goal - daily_water_consumption, 0)
        progress_value = min((daily_water_consumption / water_goal) * 100, 100)
        water_message = f"Water consumed today: {daily_water_consumption} mL"
    
    return progress_value, water_message


############ PAGE 1 SETTINGS
Netherlands_activity_level = 0  # Mean physical activity level
Netherlands_humidity = 70  # Mean humidity in percentage
Netherlands_athlete_status = 0  # Non-athlete status
Netherlands_human_development_index = 1  # Middle human development index
Netherlands_altitude = 0  # Altitude in meters
Netherlands_temperature = 17  # Mean temperature in °C

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

def suggest_drink(Name, age, weight, height, gender, activity, n_clicks):
    if ctx.triggered_id == 'submit':
        # Constants for the formula
        water_turnover_constants = {
            'activity_level': 1076,
            'bodyweight': 14.34,
            'sex': 374.9,
            'humidity': 5.823,
            'athlete_status': 1070,
            'human_development_index': 104.6,
            'altitude': 0.4726,
            'age_squared': -0.3529,
            'age': 24.78,
            'temperature_squared': 1.865,
            'temperature': -19.66,
        }

        base_intake = 1.8  # Base intake in liters
        weight = float(weight)
        age = int(age)

        # Define criteria
        activity = float(activity)  # Convert activity to a float
        athlete_status = 2 if activity == 3.0 else 0  # Set athlete status based on activity
        #gender = 0 if gender == 2 or gender == 3 else 1  # Set gender as 0 for women, 1 for men
        gender = float(gender)
        # Calculate water turnover using the formula
        water_turnover = (
            water_turnover_constants['activity_level'] * activity +
            water_turnover_constants['bodyweight'] * weight +
            water_turnover_constants['sex'] * gender +
            water_turnover_constants['humidity'] * Netherlands_humidity +
            #water_turnover_constants['athlete_status'] * athlete_status +
            water_turnover_constants['human_development_index'] * Netherlands_human_development_index +
            water_turnover_constants['altitude'] * Netherlands_altitude +
            water_turnover_constants['age_squared'] * age**2 +
            water_turnover_constants['age'] * age +
            water_turnover_constants['temperature_squared'] * Netherlands_temperature**2 +
            water_turnover_constants['temperature'] * Netherlands_temperature -
            713.1
        )

        # Calculate recommended water intake
        drink = base_intake + water_turnover
        drink=drink/1000
        message = 'Hello {}! You should drink {:.2f} liters of water per day'.format(Name, drink)
        return message, {'total': drink}
    return "Hello! Please fill in the form above to get your water recommendation", {'total': 2.0}



############ PAGE 3 WATER CONSUMPTION
@app.callback(
    [Output('empty-graph', 'figure'),
     Output('consecutive-days-output', 'children'),
     Output('day-graph', 'figure'),
     Output('today-output', 'children')],
    [Input('show-chart-button', 'n_clicks')],
    [State('water-value', 'data'),
     State('historical-water-store', 'data')]
)
def update_graph(n_clicks, data, historical_data):
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

    # Extract data from the historical-water-store for the Hourly Water Consumption Graph
    dates = [entry['Date'] for entry in historical_data]
    consumed_values = [entry['Consumed'] for entry in historical_data]

    trace_hourly = go.Scatter(
        x=dates,
        y=consumed_values,
        mode='lines+markers',
        name='Hourly Water Consumption'
    )
    
    layout_hourly = go.Layout(
        title='Hourly Water Consumption',
        xaxis=dict(title='Hour'),
        yaxis=dict(title='Water Consumption (L)'),
        shapes=[
            dict(
                type='line',
                y0=constant_value,
                y1=constant_value,
                x0=min(dates),
                x1=max(dates),
                line=dict(color='Red')
            )
        ]
    )
    
    hourly_figure = {'data': [trace_hourly], 'layout': layout_hourly}

    # Calculate days above goal (keep this logic if you still want it)
    goal = data['total']
    days_above_goal = compute_consecutive_days_above_goal(df_water, goal)
    message = f"You've been above your hydration goal for {days_above_goal} consecutive days!" if days_above_goal > 0 else "You're below your hydration goal."

    # Calculate the difference between daily goal and current consumption
    # NOTE: This will need to be adjusted if you are not using df_day anymore
    missing_amount = data['total'] - float(consumed_values[-1])

    missing_message = f"You're missing {missing_amount:.2f}L to reach your goal today." if missing_amount > 0 else "You've reached your goal today!"

    return {'data': [trace], 'layout': layout}, message, hourly_figure, missing_message


