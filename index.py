import base64
import io
import plotly.express as px
import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Output, Input, State
import plotly.graph_objects as go

# coonect to main.py file
from app import app
from app import server
from procesamiento import *

# connect to your app pages
from apps import analizar, calcular, exportar
# import templates
app.title = "UV - vis app "


app.layout = html.Div([
    dbc.Navbar(
        dbc.Container([
            dbc.Row([
                dbc.Col(html.Img(src='/assets/upiita-logo.png', height='35px')),
                dbc.Col(dbc.NavbarBrand('UV-vis analizar app', className='ms-2'))
            ], align='center', className='g-0',),
            dbc.NavbarToggler(id='navbar-toggler', n_clicks=0),
            dbc.Collapse(
                dbc.Nav([
                    dbc.Col(dbc.NavLink('Analizar', href='/apps/analizar')),
                    dbc.Col(dbc.NavLink('Calcular', href='/apps/calcular')),
                    dbc.Col(dbc.NavLink('Exportar', href='/apps/exportar')),
                ], className=' ms-auto', navbar=True),
                id='navbar-collapse',
                is_open=False,
                navbar=True
            )
        ])
    ),
    dcc.Location(id="url", refresh=False),
    html.Div(id='page-content', children=[])
], className='nav-bar')


@app.callback(Output(component_id='page-content', component_property='children'),
              [Input(component_id='url', component_property='pathname')]
              )
def page_content(pathname):
    if pathname == '/apps/analizar':
        return analizar.layout
    elif pathname == '/apps/calcular':
        return calcular.layout
    elif pathname == '/apps/exportar':
        return exportar.layout
    else:
        return analizar.layout


if __name__ == "__main__":
    app.run_server(debug=True)
