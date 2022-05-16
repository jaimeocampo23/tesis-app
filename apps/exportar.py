from ast import Div, In
from tkinter.messagebox import NO
import plotly.express as px
import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Output, Input, State, dash_table, callback_context
import plotly.graph_objects as go
import base64
from procesamiento import *
import io

from app import app


layout = html.Div([
    dcc.Upload(
        id='subir-data',
        children=html.Div([
            'Arrasta y suelta o selecciona un archivo']),
        multiple=True,
    ),
    html.Div(id="datatable_upload"),
    html.Br(),
    html.Div(id="crear_plantilla"),

], id="export-page")


def html_component(data: pd.DataFrame) -> html.Div:
    return html.Div([
        html.Hr(),
        dash_table.DataTable(data=data.to_dict('records'),
                             columns=[{"name": i, "id": i}
                                      for i in data.columns],
                             editable=True,
                             page_size=10,
                             id='tbl2',
                             ),
        html.Br(),
        html.Hr(),
        html.Div([
            dbc.Button('descargar', id="btn_csv", n_clicks=0),
            dcc.Download(id="download-dataframe-csv"),
        ], id='descargar'),
    ])


def parse_content(contents: 'list[str]', filename: 'list[str]') -> html.Div:
    content_type, content_string = contents[0].split(',')
    decoded = base64.b64decode(content_string)

    try:
        if 'csv' in filename[0]:
            # Assume that the user uploaded a CSV file
            pandas_frame = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xlsx' in filename[0]:
            # Assume that the user uploaded an excel file
            pandas_frame = pd.read_excel(io.BytesIO(decoded), index_col=False)

    except:
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.Hr(),

        dash_table.DataTable(data=pandas_frame.to_dict('records'),
                             columns=[{"name": i, "id": i}
                                      for i in pandas_frame.columns],
                             editable=True,
                             page_size=15,
                             id='tbl'
                             ),

        html.Br(),

        dbc.Row([
            dbc.Col(dbc.Button("Procesar", color="primary",
                    id="procesar-button", n_clicks=0)),
            dbc.Col(dbc.Input(placeholder="peso molecular",
                    type='number', id="input_pesomol"), lg=3, md=3, sm=3, xs=5),
            dbc.Col(dcc.Dropdown(['plantilla 1', 'plantilla 2'],
                                 placeholder="plantilla", id="type-plantilla"), lg=3, md=3, sm=3, xs=5),
            dbc.Col(dcc.Dropdown(['ppm', 'mg/dL', '%', 'mmol/L'],
                                 placeholder="unidades", id="units"), lg=3, md=3, sm=3, xs=5),
            dbc.Col(dbc.Input(placeholder="longitud_nanometros",
                              type='text', id="nanometros-input"), lg=3, md=3, sm=3, xs=5),

        ]),

    ])


@app.callback(Output('datatable_upload', 'children'),
              Input('subir-data', 'contents'),
              State('subir-data', 'filename'))
def importar_tabla(list_of_content, list_of_name):
    if list_of_content is not None:
        return parse_content(list_of_content, list_of_name)


@app.callback(Output(component_id='crear_plantilla', component_property='children'),
              Input("procesar-button", "n_clicks"),
              Input('tbl', 'data'),
              State('input_pesomol', 'value'),
              State('type-plantilla', 'value'),
              State('units', 'value'),
              State('nanometros-input', 'value')
              )
def procesar_plantilla(n, data, peso, plantilla, unidades, nanometros):
    global data_frame2
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'procesar-button' in changed_id and plantilla == 'plantilla 1' and peso and unidades != None:
        data_frame = pd.DataFrame(data)
        L_o, data_frame = preprocesamiento(data_frame)
        data_frame = procesamiento(data_frame)
        data_frame, concentracion = longitud_onda_ordenar_plantilla(
            data_frame, L_o)
        new_dataframe = crear_dataframe_de_dato_plantilla(
            data_frame, peso, concentracion, unidades)
        data_frame2 = agrupar_datos_plantilla(data_frame, new_dataframe)
        return html_component(data_frame2)

    if 'procesar-button' in changed_id and plantilla == 'plantilla 2' and unidades != None and nanometros != None:
        nms, booleano = checar_info(nanometros)
        if booleano:
            data_frame = pd.DataFrame(data)
            L_o, data_frame = preprocesamiento(data_frame)
            data_frame = procesamiento(data_frame)
            data_frame = segmentar(data_frame, L_o, unidades, peso, nms)
            new_dataframe = crear_dataframe_de_datos(data_frame, nms, unidades)
            data_frame2 = agrupar_datos_plantilla(data_frame, new_dataframe)
            return html_component(data_frame2)

        else:
            return html.Div([
                dbc.Alert(
                    "Los valores deben ser numericos separados por una coma y en un rango de [190 - 1000]!", color="danger"),
            ])


@app.callback(Output(component_id="nanometros-input", component_property='style'),
              Input('type-plantilla', 'value'),
              )
def crear_input(plantilla):
    if plantilla == 'plantilla 2':
        return {'visibility': 'visible'}
    return {'visibility': 'hidden'}


@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
)
def func(n_clicks):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'btn_csv' in changed_id:
        return dcc.send_data_frame(data_frame2.to_csv, 'plantilla.csv', index=False)
