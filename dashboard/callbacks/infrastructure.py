from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

def register_infrastructure_callbacks(app):
    @app.callback(
        [
            Output("infra-api", "children"), Output("infra-db", "children"),
            Output("infra-redis", "children"), Output("infra-worker", "children"),
            Output("infra-chart-connections", "figure"), Output("infra-chart-workers", "figure")
        ],
        [Input("global-interval", "n_intervals")]
    )
    def update_infrastructure(n):
        df_conn = pd.DataFrame({'Metric': ['Current', 'Peak', 'Available'], 'Connections': [12, 45, 100]})
        fig_conn = px.bar(df_conn, x='Metric', y='Connections', title="PostgreSQL Connections", template="plotly_dark")
        fig_conn.update_layout(paper_bgcolor="#1e293b", plot_bgcolor="#1e293b")

        df_workers = pd.DataFrame({'Status': ['Completed', 'Running', 'Failed', 'Retried'], 'Count': [1420, 4, 1, 2]})
        fig_workers = px.pie(df_workers, names='Status', values='Count', title="ARQ Worker Activity", template="plotly_dark")
        fig_workers.update_layout(paper_bgcolor="#1e293b", plot_bgcolor="#1e293b")

        return "ONLINE", "CONNECTED", "ACTIVE", "RUNNING", fig_conn, fig_workers
