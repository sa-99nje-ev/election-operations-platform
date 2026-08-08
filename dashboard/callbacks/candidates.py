from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from sqlalchemy import text
from dashboard.database import engine
from dashboard.charts.vote_trend import create_share_chart

def register_candidate_callbacks(app):
    @app.callback(
        [
            Output("cand-total", "children"), Output("cand-parties", "children"),
            Output("cand-const", "children"), Output("cand-booths", "children"),
            Output("cand-chart-bar", "figure"), Output("cand-chart-pie", "figure")
        ],
        [Input("global-interval", "n_intervals")]
    )
    def update_candidates(n):
        with engine.connect() as conn:
            cand_result = conn.execute(text("SELECT COUNT(*) as total FROM candidates"))
            tot_cands = cand_result.scalar()

            party_result = conn.execute(text("SELECT COUNT(DISTINCT party) as total FROM candidates"))
            tot_parties = party_result.scalar()

            const_result = conn.execute(text("SELECT COUNT(*) as total FROM constituencies"))
            tot_const = const_result.scalar()

            booth_result = conn.execute(text("SELECT COUNT(*) as total FROM polling_booths"))
            tot_booths = booth_result.scalar()

            df_cand_rank = pd.read_sql(text("""
                SELECT c.full_name, c.party, COUNT(v.id) as votes
                FROM candidates c
                LEFT JOIN voting_records v ON v.candidate_id = c.id
                GROUP BY c.full_name, c.party
                ORDER BY votes DESC
            """), conn)

            df_share = pd.read_sql(text("""
                SELECT c.party, COUNT(v.id) as cnt
                FROM candidates c
                LEFT JOIN voting_records v ON v.candidate_id = c.id
                GROUP BY c.party
                ORDER BY cnt DESC
            """), conn)

        if df_cand_rank.empty:
            df_cand_rank = pd.DataFrame({
                'full_name': ['Candidate A', 'Candidate B', 'Candidate C'],
                'party': ['Party A', 'Party B', 'Party C'],
                'votes': [0, 0, 0]
            })

        if df_share.empty:
            df_share = pd.DataFrame({'party': ['Party A', 'Party B', 'Party C'], 'cnt': [0, 0, 0]})

        # Top candidates with party as color
        fig_cand_bar = px.bar(df_cand_rank.head(5),
                              x='votes', y='full_name',
                              color='party',
                              orientation='h',
                              title="Top Candidates by Votes",
                              template="plotly_dark")
        fig_cand_bar.update_layout(
            paper_bgcolor="#1e293b",
            plot_bgcolor="#1e293b",
            margin=dict(t=30, b=20, l=20, r=20)
        )

        return (
            f"{tot_cands}",
            f"{tot_parties}",
            f"{tot_const}",
            f"{tot_booths}",
            fig_cand_bar,
            create_share_chart(df_share)
        )
