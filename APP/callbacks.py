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
import dash_table
import plotly.express as px
import base64
import io
import serial
ser = serial.Serial('COM3', 9600)
ser.close()
import requests
import os
 # Change 'COM3' to your Arduino's COM port




############# HOME PAGE
@app.callback(
    Output('lights_on', 'n_clicks'),
    Input('lights_on', 'n_clicks'),
    prevent_initial_call=True
)
def turn_on_led(n):
    ser.write(b'1')
    return n

# Callback to turn the LED off
@app.callback(
    Output('lights_off', 'n_clicks'),
    Input('lights_off', 'n_clicks'),
    prevent_initial_call=True
)
def turn_off_led(n):
    ser.write(b'0')
    return n
