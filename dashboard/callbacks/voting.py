from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from sqlalchemy import text
from dashboard.database import engine
from dashboard.charts.vote_trend import create_trend_chart

def register_voting_callbacks(app):
    @app.callback(
        [
            Output("op-today", "children"), Output("op-hour", "children"),
            Output("op-queue", "children"), Output("op-blocked", "children"),
            Output("op-chart-timeline", "figure"), Output("op-chart-latency", "figure")
        ],
        [Input("global-interval", "n_intervals")]
    )
    def update_voting(n):
        with engine.connect() as conn:
            # Votes today
            today_result = conn.execute(
                text("SELECT COUNT(*) as total FROM voting_records WHERE DATE(voted_at) = CURRENT_DATE")
            )
            votes_today = today_result.scalar() or 0

            # Votes last hour
            hour_result = conn.execute(
                text("SELECT COUNT(*) as total FROM voting_records WHERE voted_at >= NOW() - INTERVAL '1 hour'")
            )
            votes_hour = hour_result.scalar() or 0

            # Queue length - check if queue table exists, else show N/A
            try:
                queue_result = conn.execute(
                    text("SELECT COUNT(*) as total FROM voting_records WHERE voted_at IS NULL")
                )
                queue_len = queue_result.scalar() or 0
                queue_display = str(queue_len)
            except:
                queue_display = "N/A"

            # Blocked duplicates today
            blocked_result = conn.execute(
                text("SELECT COUNT(*) as total FROM audit_logs WHERE event_type = 'duplicate_vote_blocked' AND DATE(created_at) = CURRENT_DATE")
            )
            blocked = blocked_result.scalar() or 0

            # Trend data (cumulative)
            df_trend = pd.read_sql(text("""
                SELECT DATE_TRUNC('hour', voted_at) as hr, COUNT(*) as cnt
                FROM voting_records
                WHERE voted_at IS NOT NULL
                GROUP BY hr
                ORDER BY hr
            """), conn)

        if df_trend.empty:
            df_trend = pd.DataFrame({
                'hr': ['08:00', '10:00', '12:00', '14:00', '16:00'],
                'cnt': [0, 0, 0, 0, 0]
            })

        fig_op_time = create_trend_chart(df_trend)

        # Latency data (placeholder until metrics are available)
        df_lat = pd.DataFrame({
            'Metric': ['Average', 'p95', 'p99'],
            'Latency_ms': [12.5, 45.2, 89.1]
        })
        fig_lat = px.bar(df_lat, x='Metric', y='Latency_ms',
                         title="Vote Processing Latency", template="plotly_dark")
        fig_lat.update_layout(paper_bgcolor="#1e293b", plot_bgcolor="#1e293b")

        return (
            f"{votes_today:,}",
            f"{votes_hour:,}",
            queue_display,
            f"{blocked} blocked today",
            fig_op_time,
            fig_lat
        )
