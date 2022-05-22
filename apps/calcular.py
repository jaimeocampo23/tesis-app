from dash import dcc, html
import dash_bootstrap_components as dbc
from dash import html, Output, Input, State, dash_table
from procesamiento import calcularConcentraciones


from app import app
clicks = 0

Peso_mg = html.Div([
    dbc.Label("Peso en miligramos"),
    dbc.Input(type="number", id="peso-mg",
              placeholder="Peso en miligramos"
              )],
    className="mb-3")

NoDisoluciones = html.Div([
    dbc.Label("Numero de disoluciones"),
    dbc.Input(type="number", id="No-disoluciones",
              placeholder="Numero de disoluciones"
              )],
    className="mb-3")

Peso_molecular = html.Div([
    dbc.Label("Peso molecular del reactivo"),
    dbc.Input(type="number", id="Peso-molecular",
              placeholder="Peso molecular"
              )],
    className="mb-3")

Volumen_disolucion = html.Div([
    dbc.Label("Volumen de disolucion"),
    dbc.Input(type="number", id="Volumen-disolucion",
              placeholder="Volumen"
              )],
    className="mb-3")

Volumen_mililitros = html.Div([
    dbc.Label("Volumen de agua en mililitros"),
    dbc.Input(type="number", id="Volumen-mililitros",
              placeholder="Volumen"
              )],
    className="mb-3")

Proporcion = html.Div([
    dbc.Label("Proporción"),
    dbc.Input(type="number", id="Proporcion",
              placeholder="Proporción"
              )],
    className="mb-3")

layout = html.Div([
    dbc.Form([Peso_mg, NoDisoluciones, Peso_molecular,
             Volumen_disolucion, Volumen_mililitros, Proporcion]),
    html.Br(),
    dbc.Button('Calcular', id='calcular', n_clicks=clicks),
    html.Div(id='crea-tabla')
], id="calcular-compo")


@app.callback(
    Output("crea-tabla", "children"),
    Input("calcular", "n_clicks"),
    State("peso-mg", "value"),
    State("No-disoluciones", "value"),
    State("Peso-molecular", "value"),
    State("Volumen-disolucion", "value"),
    State("Volumen-mililitros", "value"),
    State("Proporcion", "value"),
)
def crea_tabla(n, pesomg, no_disol, peso_mol, vol_disol, vol_mil, propor):
    if n > 0:
        clicks = 0
        tabla = calcularConcentraciones(pesomg, no_disol, peso_mol,
                                        vol_disol, vol_mil, propor)

        return html.Div([
            dash_table.DataTable(
                data=tabla.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in tabla.columns],
                editable=True),
        ], id="tabla")
