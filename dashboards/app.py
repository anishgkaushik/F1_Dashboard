# # dashboards/app.py
# # Modern Dash  Bootstrap dashboard for live F1 lap times

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
from datetime import timedelta
from dotenv import load_dotenv
from dash import html, dcc, Input, Output


# Initialize database engine
load_dotenv()
engine = sqlalchemy.create_engine(DB_URL)


 # External stylesheets: Darkly theme  Google Font  FontAwesome
external_stylesheets = [
    dbc.themes.DARKLY,
    "https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap",
    "https://use.fontawesome.com/releases/v5.15.4/css/all.css",
 ]
 # Dash will *automatically* pick up any .css in dashboards/assets/
app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    assets_folder=os.path.join(os.path.dirname(__file__), "assets"),
    title="F1 Live Lap Times",
    suppress_callback_exceptions=True
 )
server = app.server



# --- Data Utilities ---
def get_lap_times(session='FP1'):
    df = pd.read_sql(
        f"SELECT session, driver, lap_num, lap_time, recorded_at FROM lap_times WHERE session='{session}' ORDER BY lap_num",
        engine,
        parse_dates=['recorded_at']
    )
    if not pd.api.types.is_timedelta64_dtype(df['lap_time']):
        df['lap_time'] = pd.to_timedelta(df['lap_time'], unit='s')
    df['lap_time_min'] = df['lap_time'] / timedelta(minutes=1)
    return df


def get_fastest_lap(df):
    idx = df['lap_time'].idxmin()
    row = df.loc[idx]
    return row['driver'], row['lap_time'].total_seconds()


def get_race_results(session='FP1'):
    # Placeholder: integrate FastF1 if desired
    return 'VER', 'BOT'

# --- Layout ---
# Summary cards
cards = dbc.Row([
    dbc.Col(dbc.Card([
        dbc.CardBody([
            html.I(className='fas fa-trophy fa-2x text-warning mb-2'),
            html.H6('Race Winner', className='text-uppercase text-muted mb-1'),
            html.H4(id='winner')
        ], className='text-center')
    ], color='dark', outline=False, className='shadow-sm'), width=4),
    

    dbc.Col(dbc.Card([
        dbc.CardBody([
            html.I(className='fas fa-bolt fa-2x text-info mb-2'),
            html.H6('Pole Position', className='text-uppercase text-muted mb-1'),
            html.H4(id='pole')
        ], className='text-center')
    ], color='dark', outline=False, className='shadow-sm'), width=4),

    dbc.Col(dbc.Card([
        dbc.CardBody([
            html.I(className='fas fa-stopwatch fa-2x text-danger mb-2'),
            html.H6('Fastest Lap', className='text-uppercase text-muted mb-1'),
            html.H4(id='fastest-driver', className='mb-0'),
            html.P(id='fastest-lap', className='mt-1')
        ], className='text-center')
    ], color='dark', outline=False, className='shadow-sm'), width=4)
], className='mb-4')

# Session selector
filter_bar = dbc.Row(
    dbc.Col(
        dcc.Dropdown(
            id='session-filter',
            options=[{'label': s, 'value': s} for s in ['FP1','FP2','FP3','Quali','Race']],
            value='FP1',
            clearable=False,
            style={'maxWidth': '200px'}
        ),
        width='auto'
    ),
    className='mb-4'
)

# Tabs
tabs = dbc.Tabs(
    id='tabs',
    active_tab='evolution',
    className='nav-tabs mb-4',        # ensure your CSS selector .nav-tabs .nav-link matches
    children=[
        dbc.Tab(
            children=[html.Span([html.I(className='fas fa-list me-1'), 'Results'])],
            tab_id='results',
            label_style={'color': 'white'},
            active_label_style={'color': 'white'}
        ),
        dbc.Tab(
            children=[html.Span([html.I(className='fas fa-map-marker-alt me-1'), 'Positions'])],
            tab_id='positions',
            label_style={'color': 'white'},
            active_label_style={'color': 'white'}
        ),
        dbc.Tab(
            children=[html.Span([html.I(className='fas fa-stopwatch me-1'), 'Lap Times'])],
            tab_id='lap_times',
            label_style={'color': 'white'},
            active_label_style={'color': 'white'}
        ),
        dbc.Tab(
            children=[html.Span([html.I(className='fas fa-user-friends me-1'), 'Strategy'])],
            tab_id='strategy',
            label_style={'color': 'white'},
            active_label_style={'color': 'white'}
        ),
        dbc.Tab(
            children=[html.Span([html.I(className='fas fa-chart-line me-1'), 'Evolution'])],
            tab_id='evolution',
            label_style={'color': 'white'},
            active_label_style={'color': 'white'}
        ),
        dbc.Tab(
            children=[html.Span([html.I(className='fas fa-microchip me-1'), 'Telemetry'])],
            tab_id='telemetry',
            label_style={'color': 'white'},
            active_label_style={'color': 'white'}
        ),
    ]
)
# Content container
tab_content = html.Div(id='tab-content')

# App layout
app.layout = dbc.Container([
    html.Header(html.H1('F1 Telemetry Dashboard', className='text-white py-3'), className='bg-dark text-center mb-4'),
    cards,
    tabs,
    filter_bar,
    tab_content,
    dcc.Interval(id='interval', interval=30_000, n_intervals=0)
], fluid=True)

# --- Callbacks ---
@app.callback(
    Output('winner', 'children'),
    Output('pole', 'children'),
    Output('fastest-driver', 'children'),
    Output('fastest-lap', 'children'),
    Input('interval', 'n_intervals'),
    Input('session-filter','value'),  
)
def update_summary(n):
    df = get_lap_times()
    winner, pole = get_race_results()
    fast_drv, fast_sec = get_fastest_lap(df)
    mins, secs = divmod(fast_sec, 60)
    return (
        winner,
        pole,
        fast_drv,
        f"{int(mins)}:{secs:06.3f}"  # mm:ss.sss
    )

@app.callback(
    Output('tab-content', 'children'),
    Input('tabs', 'active_tab'),
    Input('interval', 'n_intervals')
)
def render_tab(active_tab, n):
    df = get_lap_times()
    if active_tab == 'evolution':
        fig = px.line(
            df, x='lap_num', y='lap_time_min', color='driver', markers=True,
            labels={'lap_num':'Lap #','lap_time_min':'Lap Time (min)'},
            template='plotly_dark'
        )
        fig.update_layout(margin={'l':40,'r':20,'t':30,'b':40}, legend={'orientation':'h','y':-0.2})
        return dcc.Graph(figure=fig, config={'displayModeBar':False})

    if active_tab == 'lap_times':
        return dash.dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            page_size=10,
            style_table={'overflowX':'auto'},
            style_header={'backgroundColor':'#2a2a2a','fontWeight':'bold'},
            style_cell={'backgroundColor':'#1f1f1f','color':'#e1e1e1'}
        )

    return html.Div(f"Content for '{active_tab}' coming soon...", className='text-light p-4')

if __name__ == '__main__':
    app.run(debug=True, port=8050)
