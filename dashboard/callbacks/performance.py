from dash.dependencies import Input, Output
import pandas as pd
from dashboard.charts.performance import create_latency_chart, create_scaling_chart

def register_performance_callbacks(app):
    @app.callback(
        [
            Output("perf-latency", "children"), Output("perf-commit", "children"), Output("perf-rps", "children"),
            Output("perf-chart-latency", "figure"), Output("perf-chart-scaling", "figure")
        ],
        [Input("global-interval", "n_intervals")]
    )
    def update_performance(n):
        df_lat = pd.DataFrame({'Metric': ['Average', 'p95', 'p99'], 'Latency_ms': [12.5, 45.2, 89.1]})
        df_scaling = pd.DataFrame({'Workers': [10, 25, 50], 'Throughput_RPS': [120, 280, 510]})

        return (
            "18.4 ms", "42.1 ms", "450 RPS",
            create_latency_chart(df_lat), create_scaling_chart(df_scaling)
        )
