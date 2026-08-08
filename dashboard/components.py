from dash import html
import dash_bootstrap_components as dbc

def kpi_card(title, value_id, icon_class):
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.Div([
                    html.H6(title, className="text-muted mb-1 text-uppercase", style={"fontSize": "12px"}),
                    html.H3(id=value_id, children="...", className="text-light fw-bold mb-0")
                ]),
                html.Div([html.I(className=f"{icon_class} fa-2x text-info opacity-75")])
            ], className="d-flex justify-content-between align-items-center")
        ])
    ], className="bg-dark border-secondary shadow-sm mb-4")
