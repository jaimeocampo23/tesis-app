from app import app
import plotly.express as px
import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Output, Input, State, callback_context
import plotly.graph_objects as go
import base64
from procesamiento import *
import io


layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.Div(
                id="sidebar",
                children=[
                    dbc.Card([
                        dcc.Upload(
                            id="upload-data",
                            children=[
                                "Arrastra y suelta o ",
                                html.A(children="Selecciona una imagen")
                            ])
                    ])
                ]
            )
        ], sm=4, lg=3),

        dbc.Col([
            html.Div(id='output-data-upload')], sm=4, lg=9, md=8),

    ]),

    html.Hr(),


    html.Div([
        dcc.Input(id="input_nms",
                  placeholder="Longitud de onda", type='number'),
        dbc.Button('Calcular', id="submit_boton", n_clicks=0),
    ], id='calcular'),

    html.Hr(),

    html.Div([
        html.Div(id='regresion_lineal',
                 children='Enter a value and press submit')
    ])
], className='nav-bar')


def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xlsx' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    longitud_onda, data = preprocesamiento(df)
    data = procesamiento2(data)
    data, concentraciones = longitud_onda_ordenar(data, longitud_onda)
    y = [data.columns[i] for i in range(1, data.shape[1])]
    return data, y, concentraciones


@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'))
def update_output(list_of_contents, list_of_names):
    if list_of_contents is not None:
        global df
        global concentraciones
        df, y, concentraciones = parse_contents(
            list_of_contents, list_of_names)
        fig = px.line(df, x="Longitud de onda", y=y)
        fig.update_yaxes(title_text='Absorbancia')

        return html.Div([
            dcc.Graph(figure=fig)
        ])


@app.callback(Output('regresion_lineal', 'children'),
              Input('submit_boton', 'n_clicks'),
              State('upload-data', 'contents'),
              State('input_nms', 'value'),
              )
def create_graph(n_clicks, list_of_contents, value):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if list_of_contents is not None and df.shape[1] > 2:
        if 'submit_boton' in changed_id and value >= df["Longitud de onda"].min() and value <= df["Longitud de onda"].max():
            datos = df[df["Longitud de onda"] == value]
            absorbancia = [datos.values[0][i]
                           for i in range(1, datos.shape[1])]
            concentra = [concentraciones.values[0][i]
                         for i in range(1, concentraciones.shape[1])]

            data = pd.DataFrame()
            data.insert(0, column="y_fit", value=absorbancia)
            data.insert(1, column="x_fit", value=concentra)

            ajuste = coeficientes_estimados(x=concentra, y=absorbancia)
            a1 = ajuste[0]
            a0 = ajuste[1]

            st = sumatoria_total_cuadrados(absorbancia)
            sr = sumatoria_residuos(concentra, absorbancia, a1, a0)
            fc = factor_correlacion(sr, st)

            x_fit = np.linspace(min(concentra), max(concentra), 1000)
            y_fit = a0 + a1*x_fit
            regresion = pd.DataFrame()
            regresion.insert(0, column="y_fit", value=y_fit)
            regresion.insert(1, column="x_fit", value=x_fit)

            fig = px.scatter(data_frame=data, x="x_fit", y="y_fit",
                             title=f"Absorbancia vs concentracion fc = {round(fc, 4)}")
            fig.update_yaxes(title_text='Concentracion')
            fig.update_xaxes(title_text='Absorbancia')
            fig.add_traces(go.Scatter(
                x=x_fit, y=y_fit, name="regresion lineal"))

            return html.Div([
                dcc.Graph(figure=fig)
            ])

        elif 'submit_boton' in changed_id and value < df["Longitud de onda"].min() or value > df["Longitud de onda"].max():
            return html.Div([
                dbc.Alert(
                    "Introduce un valor de Longitud de onda valido!", color="danger"),
            ])

    elif 'submit_boton' in changed_id and list_of_contents is None:
        return html.Div([
            dbc.Alert(
                "Importa un archivo antes de calcular!", color="danger"),
        ])

    elif list_of_contents is not None and df.shape[1] < 3:
        return html.Div([
            dbc.Alert(
                "Se necesitan mas de una medicion para crear una regresion lineal", color="danger"),
        ])


@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open
