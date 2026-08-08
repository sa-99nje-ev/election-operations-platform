import plotly.express as px

def create_latency_chart(df):
    fig = px.bar(df, x='Metric', y='Latency_ms', title="Pytest API Latency Benchmarks", template="plotly_dark")
    fig.update_layout(paper_bgcolor="#1e293b", plot_bgcolor="#1e293b")
    return fig

def create_scaling_chart(df):
    fig = px.line(df, x='Workers', y='Throughput_RPS', title="Worker Scaling vs Throughput", template="plotly_dark", markers=True)
    fig.update_layout(paper_bgcolor="#1e293b", plot_bgcolor="#1e293b")
    return fig
