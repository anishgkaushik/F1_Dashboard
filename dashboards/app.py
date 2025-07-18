# dashboards/app.py
# Modern Dash + Bootstrap dashboard for live F1 lap times

import sys
import os
# add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import sqlalchemy
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
from config import DB_URL

# Initialize database engine
engine = sqlalchemy.create_engine(DB_URL)

# Choose a Bootstrap theme
BOOTSTRAP_THEME = dbc.themes.FLATLY

# Initialize Dash app with Bootstrap
app = dash.Dash(
    __name__,
    external_stylesheets=[BOOTSTRAP_THEME],
    title="F1 Live Lap Times",
    suppress_callback_exceptions=True
)
server = app.server

# Helper to fetch driver options
def get_driver_options():
    df = pd.read_sql("SELECT DISTINCT driver FROM lap_times ORDER BY driver", engine)
    return [{'label': d, 'value': d} for d in df['driver']]

# Page layout
app.layout = dbc.Container([
    dbc.Navbar(
        dbc.Container([
            html.A(
                dbc.Row([
                    dbc.Col(html.Img(src="/assets/f1_logo.png", height="30px")),
                    dbc.Col(html.Span("F1 Telemetry Dashboard", className="navbar-brand ms-2")),
                ], align="center", className="g-0"),
                href="/",
                style={"textDecoration": "none"},
            ),
        ]),
        color="dark", dark=True, className="mb-4"
    ),

    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Driver Selection"),
                dbc.CardBody([
                    dcc.Dropdown(
                        id='driver-dropdown',
                        options=get_driver_options(),
                        multi=True,
                        placeholder="Select driver(s)",
                    ),
                ])
            ]), width=4
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Lap Time Trends"),
                dbc.CardBody([
                    dcc.Graph(id='lap-times-graph', config={'displayModeBar': False}),
                ]),
                dbc.CardFooter(html.Div(id='last-update', className='text-end fst-italic'))
            ]), width=8
        )
    ], className="gy-4"),

    dcc.Interval(id='interval-component', interval=30_000, n_intervals=0)
], fluid=True)

# Callback to update graph
@app.callback(
    [Output('lap-times-graph', 'figure'),
     Output('last-update', 'children')],
    [Input('interval-component', 'n_intervals'),
     Input('driver-dropdown', 'value')]
)
def update_graph(n_intervals, selected_drivers):
    # Build query
    base = "SELECT driver, lap_num, lap_time, recorded_at FROM lap_times"
    if selected_drivers:
        placeholders = ','.join(['%s'] * len(selected_drivers))
        base += f" WHERE driver IN ({placeholders})"
        params = selected_drivers
    else:
        params = []
    base += " ORDER BY recorded_at ASC LIMIT 1000"

    df = pd.read_sql(base, engine, params=params)

    if df.empty:
        fig = px.line(title="No lap data available")
    else:
        fig = px.scatter(
            df,
            x='recorded_at', y='lap_time', color='driver',
            size='lap_time', hover_name='driver',
            title="Lap Time (s) over Time",
            labels={'recorded_at':'Time','lap_time':'Lap Time (s)','driver':'Driver'},
            template='plotly_dark'
        )
        fig.update_traces(mode='markers+lines', marker={'opacity':0.7})
        fig.update_layout(
            legend={'title':'Driver','orientation':'h','y':-0.2},
            margin={'l':40,'r':20,'t':60,'b':40}
        )

    timestamp = df['recorded_at'].max() if not df.empty else None
    footer = f"Last update: {timestamp:%Y-%m-%d %H:%M:%S}" if timestamp else "Last update: N/A"
    return fig, footer

if __name__ == '__main__':
    app.run(debug=True, port=8050)
