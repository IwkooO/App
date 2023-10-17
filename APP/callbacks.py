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

    return f"Data: {result[0]}, Random Number: {result[1]}"


async def fetch_data_from_arduino(retries=3):
    for _ in range(retries):
        devices = await BleakScanner.discover()
        
        rp2040_address = None
        for device in devices:
            if device.name == "RP2040":
                rp2040_address = device.address
                break

        if not rp2040_address:
            await asyncio.sleep(2)  # Sleep for a bit before retrying
            continue

        client = BleakClient(rp2040_address, timeout=120)
        try:
            connected = await client.connect()
            if not connected:
                continue

            services = client.services
            data = ("Data not found", "")

            for service in services:
                if service.uuid == "0000180d-0000-1000-8000-00805f9b34fb":
                    for char in service.characteristics:
                        if char.uuid == "00002a37-0000-1000-8000-00805f9b34fb":
                            value = await client.read_gatt_char(char.uuid)
                            date, number = value.decode("utf-8").split(',')
                            data = (date, number)
                            break
            return data
        finally:
            if client.is_connected:
                await client.disconnect()
            await asyncio.sleep(2)  # This sleep ensures some time gap between subsequent BLE operations
    return "Could not fetch data after multiple attempts", ""












@app.callback(
    Output('water-message', 'children'),
    [Input('show-remaining-button', 'n_clicks'),
     Input('progress', 'value')],
    State('water-value', 'data')
)
def update_water_message(n, percentage_drunk, water_data):
    if not n:  # This checks if the button hasn't been pressed.
        return "Press the button to see remaining water."
    
    if water_data and isinstance(water_data, dict) and 'total' in water_data:
        total_water = water_data['total']
        amount_drunk = (percentage_drunk / 100) * total_water
        remaining_water = total_water - amount_drunk
        return f"You still need to drink {remaining_water}L today :)"
    else:
        return "No water recommendation data available yet."





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

