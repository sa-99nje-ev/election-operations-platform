from dash import html, dcc
import dash_bootstrap_components as dbc
from dashboard.components import kpi_card

def layout():
    return html.Div([
        html.H2("Executive Dashboard", className="text-light mb-4"),
        dbc.Row([
            dbc.Col(kpi_card("Total Votes Cast", "exec-total-votes", "fa fa-vote-yea"), width=4),
            dbc.Col(kpi_card("Registered Voters", "exec-reg-voters", "fa fa-users"), width=4),
            dbc.Col(kpi_card("Voter Turnout %", "exec-turnout", "fa fa-percentage"), width=4),
        ]),
        dbc.Row([
            dbc.Col(kpi_card("Registered Candidates", "exec-candidates", "fa fa-user-tie"), width=4),
            dbc.Col(kpi_card("Active Booths", "exec-booths", "fa fa-building"), width=4),
            dbc.Col(kpi_card("System Health", "exec-health", "fa fa-heartbeat"), width=4),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id="exec-chart-trend"), width=8),
            dbc.Col(dcc.Graph(id="exec-chart-share"), width=4),
        ], className="mb-4"),
        dbc.Row([
            dbc.Col(dcc.Graph(id="exec-chart-constituency"), width=6),
            dbc.Col(dcc.Graph(id="exec-chart-booths"), width=6),
        ])
    ])
