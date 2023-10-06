
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
                dbc.NavLink("Page 2", href="/page3", active="exact"),
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
            html.Div(className='col-4'),
        ],className='row'),

        html.Div([
            dbc.Button("ON",id="lights_on", color="light", className="me-1"),
            dbc.Button("OFF",id="lights_off", color="light", className="me-1"),
        ],className='row')
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
                                    {"label": "Male", "value": 1},
                                    {"label": "Female", "value": 2},
                                    {"label": "Other", "value": 3},
                                ]
                            ),
                            dbc.InputGroupText("Gender"),
                        ],className="mb-3"),
                    dbc.InputGroup(
                        [
                            dbc.Select(id='Mode',
                                options=[
                                    {"label": "Silent", "value": 1},
                                    {"label": "Normal", "value": 2},
                                    {"label": "Off", "value": 3}
                                ]
                            ),
                            dbc.InputGroupText("Mode"),
                        ],className="mb-3",
                    ),

                    html.Br(),
                    dbc.Button("Submit",id="submit", color="light", className="me-1"),
                ]
            )],className='col-4')
        ],className='row')
])

####################################################################################################
# 003 - Page 3
####################################################################################################

page3 = html.Div([


    #####################
    #Row 1 : Nav bar
    get_sidebar(),
    html.H1('Something else 2',style={'textAlign':'center'}),

    
    #####################


])
    
    


####################################################################################################
# 003 - Page 4
####################################################################################################

page4 = html.Div([

    #####################
    #Row 1 : Header
    get_header(),
    #####################
    #Row 2 : Nav bar
    get_sidebar(), 
    


])



####################################################################################################
# 003 - Page 5
####################################################################################################

page5 = html.Div([

    

])


