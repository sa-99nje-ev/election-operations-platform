from dash import html, dcc
import dash_bootstrap_components as dbc
from dashboard.components import kpi_card

def layout():
    return html.Div([
        html.H2("Voting Operations & Live Pipeline", className="text-light mb-4"),
        dbc.Row([
            dbc.Col(kpi_card("Votes Today", "op-today", "fa fa-calendar-day"), width=3),
            dbc.Col(kpi_card("Votes Last Hour", "op-hour", "fa fa-clock"), width=3),
            dbc.Col(kpi_card("Queue Length", "op-queue", "fa fa-layer-group"), width=3),
            dbc.Col(kpi_card("Blocked Today", "op-blocked", "fa fa-ban"), width=3),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id="op-chart-timeline"), width=8),
            dbc.Col(dcc.Graph(id="op-chart-latency"), width=4),
        ])
    ])
