import pandas as pd
from dashboard.database import fetch_safe

def get_executive_metrics():
    df_votes = fetch_safe("SELECT COUNT(*) as total FROM voting_records", pd.DataFrame({'total': [0]}))
    df_voters = fetch_safe("SELECT COUNT(*) as total FROM voters", pd.DataFrame({'total': [0]}))
    df_cands = fetch_safe("SELECT COUNT(*) as total FROM candidates", pd.DataFrame({'total': [0]}))
    df_booths = fetch_safe("SELECT COUNT(*) as total FROM polling_booths", pd.DataFrame({'total': [0]}))

    tot_votes = int(df_votes['total'].iloc[0])
    tot_voters = int(df_voters['total'].iloc[0])
    tot_cands = int(df_cands['total'].iloc[0])
    tot_booths = int(df_booths['total'].iloc[0])
    turnout_pct = (tot_votes / tot_voters * 100) if tot_voters > 0 else 0.0

    return tot_votes, tot_voters, tot_cands, tot_booths, turnout_pct
