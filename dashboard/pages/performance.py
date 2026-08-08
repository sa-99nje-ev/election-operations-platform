from dash import html, dcc
import dash_bootstrap_components as dbc
from dashboard.components import kpi_card

def layout():
    return html.Div([
        html.H2("Performance Monitoring (Pytest Benchmarks)", className="text-light mb-4"),
        dbc.Row([
            dbc.Col(kpi_card("Avg API Latency", "perf-latency", "fa fa-bolt"), width=4),
            dbc.Col(kpi_card("DB Commit p95", "perf-commit", "fa fa-tachometer-alt"), width=4),
            dbc.Col(kpi_card("Throughput (RPS)", "perf-rps", "fa fa-exchange-alt"), width=4),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id="perf-chart-latency"), width=6),
            dbc.Col(dcc.Graph(id="perf-chart-scaling"), width=6),
        ])
    ])
