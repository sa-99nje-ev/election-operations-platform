import plotly.express as px
import pandas as pd

def create_trend_chart(df):
    """Create cumulative vote trend chart."""
    # Calculate cumulative sum
    if not df.empty and 'cnt' in df.columns:
        df = df.copy()
        df['cumulative'] = df['cnt'].cumsum()
        fig = px.line(df, x='hr', y='cumulative',
                      title="Cumulative Vote Count Over Time",
                      template="plotly_dark", markers=True,
                      labels={'cumulative': 'Cumulative Votes', 'hr': 'Time'})
    else:
        fig = px.line(df, x='hr', y='cnt',
                      title="Cumulative Vote Count Over Time",
                      template="plotly_dark", markers=True)

    fig.update_layout(
        paper_bgcolor="#1e293b",
        plot_bgcolor="#1e293b",
        margin=dict(t=30, b=20, l=20, r=20),
        yaxis_tickformat=',d'  # Format as thousands
    )
    return fig

def create_share_chart(df):
    fig = px.pie(df, names='party', values='cnt',
                 title="Vote Share by Party",
                 template="plotly_dark", hole=0.4)
    fig.update_layout(
        paper_bgcolor="#1e293b",
        plot_bgcolor="#1e293b",
        margin=dict(t=30, b=20, l=20, r=20)
    )
    return fig

def create_constituency_chart(df):
    """Show top 10 constituencies by turnout."""
    if not df.empty and len(df) > 10:
        df = df.head(10)
    fig = px.bar(df, x='const_name', y='cnt',
                 title="Top 10 Constituencies by Turnout",
                 template="plotly_dark")
    fig.update_layout(
        paper_bgcolor="#1e293b",
        plot_bgcolor="#1e293b",
        margin=dict(t=30, b=20, l=20, r=20),
        xaxis_tickangle=-45
    )
    return fig

def create_booth_chart(df):
    """Show booth activity with professional booth codes."""
    if not df.empty:
        # Format booth codes to look professional
        df = df.copy()
        df['booth_name'] = df['booth_name'].apply(
            lambda x: f"PB-{x:03d}" if isinstance(x, (int, float)) else x
        )
        fig = px.bar(df, x='cnt', y='booth_name', orientation='h',
                     title="Top Polling Booth Activity",
                     template="plotly_dark")
    else:
        fig = px.bar(df, x='cnt', y='booth_name', orientation='h',
                     title="Top Polling Booth Activity",
                     template="plotly_dark")

    fig.update_layout(
        paper_bgcolor="#1e293b",
        plot_bgcolor="#1e293b",
        margin=dict(t=30, b=20, l=20, r=20)
    )
    return fig
