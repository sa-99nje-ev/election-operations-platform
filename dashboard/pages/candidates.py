from dash import html, dcc
import dash_bootstrap_components as dbc
from dashboard.components import kpi_card

def layout():
    return html.Div([
        html.H2("Candidate & Constituency Analytics", className="text-light mb-4"),
        dbc.Row([
            dbc.Col(kpi_card("Total Candidates", "cand-total", "fa fa-users"), width=3),
            dbc.Col(kpi_card("Political Parties", "cand-parties", "fa fa-flag"), width=3),
            dbc.Col(kpi_card("Constituencies", "cand-const", "fa fa-map"), width=3),
            dbc.Col(kpi_card("Polling Booths", "cand-booths", "fa fa-store"), width=3),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id="cand-chart-bar"), width=6),
            dbc.Col(dcc.Graph(id="cand-chart-pie"), width=6),
        ])
    ])
