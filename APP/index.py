from dash import dcc,html
import dash

from app import app
from app import server
from layouts import home, page2, page3,page4,page5
import callbacks
import serial
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

ser = serial.Serial('COM3', 9600)

@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/home':
         return home
    elif pathname == '/page2':
         return page2
    elif pathname == '/page3':
         return page3
    elif pathname == '/page4':
         return page4
    elif pathname == '/page5':
         return page5
    else:
        return home # This is the "home page"

if __name__ == '__main__':
    app.run_server(debug=True)
