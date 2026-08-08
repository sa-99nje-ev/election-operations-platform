from dash import html, dcc
import dash_bootstrap_components as dbc
from dashboard.components import kpi_card

def layout():
    return html.Div([
        html.H2("Audit & Security Operations", className="text-light mb-4"),
        dbc.Row([
            dbc.Col(kpi_card("Total Audit Events", "audit-total", "fa fa-list-alt"), width=3),
            dbc.Col(kpi_card("Successful Logins", "audit-logins", "fa fa-sign-in-alt"), width=3),
            dbc.Col(kpi_card("Failed Logins", "audit-failed", "fa fa-exclamation-triangle"), width=3),
            dbc.Col(kpi_card("Blocked Requests", "audit-blocked", "fa fa-shield-alt"), width=3),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id="audit-chart-timeline"), width=8),
            dbc.Col(dcc.Graph(id="audit-chart-distribution"), width=4),
        ])
    ])
