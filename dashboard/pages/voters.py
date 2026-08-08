from dash import html, dcc
import dash_bootstrap_components as dbc
from dashboard.components import kpi_card

def layout():
    return html.Div([
        html.H2("Voter Management & Search", className="text-light mb-4"),
        dbc.Row([
            dbc.Col(kpi_card("Eligible Voters", "voter-eligible", "fa fa-user-check"), width=4),
            dbc.Col(kpi_card("Voted", "voter-voted", "fa fa-check-circle"), width=4),
            dbc.Col(kpi_card("Inactive", "voter-inactive", "fa fa-user-slash"), width=4),
        ]),
        dbc.Row([
            dbc.Col(
                dbc.Input(
                    id="voter-search",
                    placeholder="?? Search by Name or National ID...",
                    type="text",
                    className="mb-4 bg-dark text-light border-secondary"
                ),
                width=12
            )
        ]),
        html.Div(id="voter-table-container")
    ])
