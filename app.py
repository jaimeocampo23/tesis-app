import dash
bs = "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[bs],
                meta_tags=[
                    {'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}]
                )


server = app.server
