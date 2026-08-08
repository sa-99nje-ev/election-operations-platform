from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from sqlalchemy import text
from dashboard.database import engine

def register_audit_callbacks(app):
    @app.callback(
        [
            Output("audit-total", "children"), Output("audit-logins", "children"),
            Output("audit-failed", "children"), Output("audit-blocked", "children"),
            Output("audit-chart-timeline", "figure"), Output("audit-chart-distribution", "figure")
        ],
        [Input("global-interval", "n_intervals")]
    )
    def update_audit(n):
        with engine.connect() as conn:
            # Total audit events
            total_result = conn.execute(text("SELECT COUNT(*) as total FROM audit_logs"))
            total_audit = total_result.scalar()

            # Successful logins
            login_result = conn.execute(text("SELECT COUNT(*) as total FROM audit_logs WHERE event_type = 'login_success'"))
            login_success = login_result.scalar()

            # Failed logins
            failed_result = conn.execute(text("SELECT COUNT(*) as total FROM audit_logs WHERE event_type = 'login_failed'"))
            login_failed = failed_result.scalar()

            # Blocked requests
            blocked_result = conn.execute(text("SELECT COUNT(*) as total FROM audit_logs WHERE event_type = 'duplicate_vote_blocked'"))
            blocked = blocked_result.scalar() or 0

            # Audit timeline
            df_trend = pd.read_sql(text("""
                SELECT DATE_TRUNC('hour', created_at) as hr, COUNT(*) as cnt
                FROM audit_logs
                GROUP BY hr
                ORDER BY hr
            """), conn)

            # Audit distribution
            df_audit = pd.read_sql(text("""
                SELECT event_type, COUNT(*) as cnt
                FROM audit_logs
                GROUP BY event_type
                ORDER BY cnt DESC
            """), conn)

        if df_trend.empty:
            df_trend = pd.DataFrame({
                'hr': ['08:00', '10:00', '12:00', '14:00', '16:00'],
                'cnt': [0, 0, 0, 0, 0]
            })

        if df_audit.empty:
            df_audit = pd.DataFrame({'event_type': ['LOGIN', 'VOTE', 'LOGOUT'], 'cnt': [0, 0, 0]})

        # Create audit timeline chart with correct title
        fig_audit_time = px.line(df_trend, x='hr', y='cnt',
                                 title="Audit Events Over Time",
                                 template="plotly_dark", markers=True)
        fig_audit_time.update_layout(
            paper_bgcolor="#1e293b",
            plot_bgcolor="#1e293b",
            margin=dict(t=30, b=20, l=20, r=20)
        )

        fig_audit_dist = px.pie(df_audit, names='event_type', values='cnt',
                                title="Audit Action Distribution", template="plotly_dark")
        fig_audit_dist.update_layout(
            paper_bgcolor="#1e293b",
            plot_bgcolor="#1e293b"
        )

        return (
            f"{total_audit:,}",
            f"{login_success:,}",
            f"{login_failed:,}",
            f"{blocked:,}",
            fig_audit_time,
            fig_audit_dist
        )
