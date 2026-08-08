from dash import html, dcc
import dash_bootstrap_components as dbc
from dashboard.components import kpi_card

def layout():
    return html.Div([
        html.H2("Infrastructure & System Health", className="text-light mb-4"),
        dbc.Row([
            dbc.Col(kpi_card("API Status", "infra-api", "fa fa-network-wired"), width=3),
            dbc.Col(kpi_card("PostgreSQL", "infra-db", "fa fa-database"), width=3),
            dbc.Col(kpi_card("Redis Cache", "infra-redis", "fa fa-memory"), width=3),
            dbc.Col(kpi_card("ARQ Workers", "infra-worker", "fa fa-cogs"), width=3),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id="infra-chart-connections"), width=6),
            dbc.Col(dcc.Graph(id="infra-chart-workers"), width=6),
        ])
    ])
