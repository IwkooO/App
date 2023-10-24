from dash import dcc,html
import dash

from app import app
from app import server
from layouts import home, page2, page3
import callbacks
import serial
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='water-value', data={'total': 2.0}),
    dcc.Store(id='daily-water-store', data=0.3),
    html.Div(id='page-content')
])



@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/home':
         return home
    elif pathname == '/page2':
         return page2
    elif pathname == '/page3':
         return page3
    else:
         dash.callback_context.response.set_cookie('home_visited', 'true')
         return home # This is the "home page"

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=False, use_reloader=False, threaded=True)

