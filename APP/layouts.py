
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify
import dash_mantine_components as dmc
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import dash
import dash_enterprise_auth as auth
import dash_auth
from datetime import datetime as dt
from app import app
import plotly.express as px 
import requests
import os

auth=dash_auth.BasicAuth(
    app,
    {'iwo':'123'}
)


df_water = pd.read_csv('water_consumption.csv')

df_day = pd.read_csv('water_consumption_day.csv')



####################################################################################################
# 000 - IMPORT DATA
####################################################################################################


###########################
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "20rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# padding for the page content
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}


#####################
# HEADER
def get_header():

    header = html.Div([

        html.Div([], className = 'col-2'), #Same as img width, allowing to have the title centrally aligned

        html.Div([
            html.H1(children='Welcome to HydroMate',
                    style = {'textAlign' : 'center',
                             'color': 'black'}
            )],
            className='col-8',
            style = {'padding-top' : '1%'}
        ),
        html.Div(className='col-2')
        ],className = 'row',
        style = {'height' : '15%'}
        )

    return header

def get_sidebar(p='home'):
    sidebar = html.Div(
    [
        html.H2("HydroMate", className="display-4"),
        html.Hr(),
        html.P(
            "Great to see you here!", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/home", active="exact"),
                dbc.NavLink("Profile", href="/page2", active="exact"),
                dbc.NavLink("Hydration Data", href="/page3", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
    )
    return sidebar
    


def get_sidebar_button():
    Btn1 = dmc.Button(
        children=[DashIconify(icon="ci:hamburger-lg", width=24, height=24, color="#c2c7d0")],
        variant="subtle", 
        p=1,
        id='sidebar-button'
    )
    return Btn1

#####################
# Empty row

def get_emptyrow(h='45px'):
    """This returns an empty row of a defined height"""

    emptyrow = html.Div([
        html.Div([
            html.Br()
        ], className = 'col-12')
    ],
    className = 'row',
    style = {'height' : h})

    return emptyrow



####################################################################################################
# 001 - HOME
####################################################################################################

home = html.Div(
    children=[
        # Row 1: Nav bar & Button combined
        get_header(),
        html.Div(
            children=[
                get_sidebar_button(),
                get_sidebar(),
            ]),
        # Row 2:
        get_emptyrow(),

        #Row 3 Fill your data:
        html.Div([
            html.Div(className='col-3'),
            html.Div([
                html.H1('Your Progress',style={'textAlign':'center'}),
                dbc.Progress(id="progress",value=50, style={"height": "30px"},striped=True),
                dbc.Button("Show Remaining Water", id="show-remaining-button", className="mt-3"),
                html.Div(id="water-message"),
            ],className='col-6'),
        ],className='row'),
        #Row 4 Empty Row:
        get_emptyrow(),

        #Row 5 Check Arduino:

        html.Div([
            html.Div(className='col-3'),
            html.Div([
                dbc.Button("Retrieve Bluetooth Data", id="btn_retrieve_bluetooth", className="mt-3"),
                html.Span(id="output_data_bluetooth", style={"marginLeft": "10px"})
            ],className='col-6'),
        ], className='row'),
    ])




####################################################################################################
# 002 - Page 2
####################################################################################################

page2 = html.Div(
    children=[
        # Row 1: Nav bar & Button combined
        html.Div(
            children=[
                get_sidebar(),
                html.H1('Welcome to your profile',
                        style={'textAlign':'center'}),]),
        # Row 2 empty
        get_emptyrow(),

        #Row 3 Data:
        html.Div([
            html.Div(className='col-4'),
            html.Div([
                html.Div([
                    dbc.InputGroup(
                        [dbc.InputGroupText("@"), dbc.Input(id='Name',placeholder="Name")],
                        className="mb-3",
                    ),
                    dbc.InputGroup(
                        [
                            dbc.Input(id='age',placeholder="Age",type="number"),
                            dbc.InputGroupText("years")
                        ],
                        className="mb-3",
                    ),
                    dbc.InputGroup(
                        [
                            dbc.Input(id='weight',placeholder="Weight", type="number"),
                            dbc.InputGroupText("kg"),
                        ],
                        className="mb-3",
                    ),
                    dbc.InputGroup(
                        [
                            dbc.Input(id='height',placeholder="Height", type="number"),
                            dbc.InputGroupText("cm"),
                        ],
                        className="mb-3",
                    ),
                    dbc.InputGroup(
                        [
                            dbc.Select(id='gender',
                                options=[
                                    {"label": "Male", "value": 1.15},
                                    {"label": "Female", "value": 1},
                                    {"label": "Other", "value": 1.01},
                                ]
                            ),
                            dbc.InputGroupText("Gender"),
                        ],className="mb-3"),
                    dbc.InputGroup(
                        [
                            dbc.Select(id='activity',
                                options=[
                                    {"label": "Light Activity", "value": 0.75},
                                    {"label": "Moderate Activity", "value": 1},
                                    {"label": "High Activity", "value": 1.25},
                                ]
                            ),
                            dbc.InputGroupText("Activity Level"),
                        ],className="mb-3"),
                    html.Br(),
                    dbc.Button("Submit",id="submit", color="light", className="me-1"),
                    html.Div(id='water_recommendation_ouput', style={'whiteSpace': 'pre-line'})
                ]
            )],className='col-4')
        ],className='row')
])

####################################################################################################
# 003 - Page 3
####################################################################################################
trace = go.Scatter(x=df_water['Date'], 
                   y=df_water['Water Consumption (L)'], 
                   mode='lines+markers', 
                   name='Water Consumption')


trace_day = go.Scatter(
    x=df_day['Hour'], 
    y=df_day['Cumulative Consumption (L)'], 
    mode='lines+markers',
    name='Hourly Consumption'
)


page3 = html.Div([


    #####################
    #Row 1 : Nav bar
    get_sidebar(),
    html.H1('Your Hydration Data',style={'textAlign':'center'}),
    #####################
    #Row 2 : Empty row
    get_emptyrow(),
    html.Div([
        html.Div(className='col-3'),
        html.Div([
            dbc.Button("Show Goal", id="show-chart-button", className="mt-3"),
        ],className='col-2'),
    ],className='row'),
    #####################
    html.Div([
        html.Div(className='col-3'),
        html.Div([dcc.Graph(id='empty-graph',
            figure={
            'data': [trace],
            'layout': go.Layout(
                title='Daily Water Consumption',
                xaxis=dict(title='Date'),
                yaxis=dict(title='Water Consumption (L)'))},
            style={'width': '100%', 'height': '600px', 'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto'}  # Adjust the size and center the graph
            ),],className='col-8'),
        #html.Div(className='col-2'),

    ],className='row'),

    #Row 4 : Streak
    html.Div([
        html.Div(className='col-3'),
        html.Div([
            html.Div(id='consecutive-days-output', children='', style={'textAlign': 'center', 'fontSize': 24, 'padding': '20px'}),
        ],className='col-8'),

    ],className='row'),

    #Row 5 empty
    html.Br(),
    html.Br(),

    #Row 6 : Daily Graph
        html.Div([
        html.Div(className='col-3'),
        html.Div([dcc.Graph(id='day-graph',
            figure={
            'data': [],
            'layout': go.Layout(
                title='Todays Water Consumption',
                xaxis=dict(title='Hour'),
                yaxis=dict(title='Water Consumption (L)'))},
            style={'width': '100%', 'height': '600px', 'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto'}  # Adjust the size and center the graph
            ),],className='col-8'),

    ],className='row'),

    #Row 4 : Streak
    html.Div([
        html.Div(className='col-3'),
        html.Div([
            html.Div(id='today-output', children='', style={'textAlign': 'center', 'fontSize': 24, 'padding': '20px'}),
        ],className='col-8'),

    ],className='row'),



])
    
    






