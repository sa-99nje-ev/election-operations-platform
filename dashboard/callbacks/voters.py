from dash.dependencies import Input, Output
from dash import dash_table
import pandas as pd
from sqlalchemy import text
from dashboard.database import engine

def register_voter_callbacks(app):
    @app.callback(
        [
            Output("voter-eligible", "children"),
            Output("voter-voted", "children"),     # Changed from voter-inactive
            Output("voter-inactive", "children"),
            Output("voter-table-container", "children")
        ],
        [Input("global-interval", "n_intervals"), Input("voter-search", "value")]
    )
    def update_voters(n, search_val):
        with engine.connect() as conn:
            # Count by status
            status_result = conn.execute(text("""
                SELECT status, COUNT(*) as cnt
                FROM voters
                GROUP BY status
            """))
            status_counts = {row[0]: row[1] for row in status_result}

            total = sum(status_counts.values())

            # Get counts for each status
            eligible = status_counts.get('eligible', 0)
            voted = status_counts.get('voted', 0)
            inactive = status_counts.get('inactive', 0)

        # Build voter table
        if search_val:
            search_pattern = f"%{search_val}%"
            query = text("""
                SELECT id, national_id, full_name, status, constituency_id
                FROM voters
                WHERE full_name ILIKE :search
                OR national_id ILIKE :search
                LIMIT 50
            """)
            with engine.connect() as conn:
                df_voter_list = pd.read_sql(query, conn, params={"search": search_pattern})
        else:
            query = text("""
                SELECT id, national_id, full_name, status, constituency_id
                FROM voters
                LIMIT 50
            """)
            with engine.connect() as conn:
                df_voter_list = pd.read_sql(query, conn)

        # Convert UUIDs to strings
        records = []
        if not df_voter_list.empty:
            for _, row in df_voter_list.iterrows():
                records.append({
                    'id': str(row['id']),
                    'national_id': row['national_id'],
                    'full_name': row['full_name'],
                    'status': row['status'],
                    'constituency_id': str(row['constituency_id'])
                })
        else:
            records = [{
                'id': 'N/A',
                'national_id': 'N/A',
                'full_name': 'No voters found',
                'status': 'N/A',
                'constituency_id': 'N/A'
            }]

        voter_table = dash_table.DataTable(
            data=records,
            columns=[
                {"name": "Id", "id": "id", "hideable": True},
                {"name": "National ID", "id": "national_id"},
                {"name": "Full Name", "id": "full_name"},
                {"name": "Status", "id": "status"},
                {"name": "Constituency", "id": "constituency_id", "hideable": True}
            ],
            page_size=10,
            style_header={'backgroundColor': '#111827', 'color': 'white', 'border': '1px solid #374151'},
            style_cell={'backgroundColor': '#1e293b', 'color': 'white', 'border': '1px solid #374151'},
            style_table={'overflowX': 'auto'}
        )

        return (
            f"{eligible:,}",
            f"{voted:,}",
            f"{inactive:,}",
            voter_table
        )
