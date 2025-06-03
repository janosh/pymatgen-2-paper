"""
Plot a X-monthly number of active contributors bar plot,
with the color of bars showing total number of commits.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

BINNED_PERIOD_MONTH = 6
CSV_PATH = "contributor_commits_by_month.csv"

df = pd.read_csv(CSV_PATH)
df_grouped = df.groupby("contributor_id").sum(numeric_only=True)

# Convert columns to datetime
df_grouped.columns = pd.to_datetime(df_grouped.columns, format="%Y-%m")

# Count active contributors
active_contributors = (df_grouped > 0).sum(axis=0)

# Total number of commits per month
total_commits = df_grouped.sum(axis=0)

# Resample into X-month bins
active_binned = active_contributors.resample(f"{BINNED_PERIOD_MONTH}ME").sum()
commits_binned = total_commits.resample(f"{BINNED_PERIOD_MONTH}ME").sum()

# Normalize for colormap
normed = (commits_binned - commits_binned.min()) / (
    commits_binned.max() - commits_binned.min()
)
colors = [px.colors.sample_colorscale("RdYlGn_r", val)[0] for val in normed]

# Build bar plot
fig = go.Figure(
    [
        go.Bar(
            x=active_binned.index.strftime("%Y-%m"),
            y=active_binned.values,
            marker=dict(color=colors),
            customdata=commits_binned.values.reshape(-1, 1),
            hovertemplate="Period: %{x}<br>Contributors: %{y}<br>Total Commits: %{customdata[0]}",
            showlegend=False,
        )
    ]
)

# Add colorbar using a dummy scatter trace
# Colorbar using a dummy scatter trace
fig.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        mode="markers",
        marker=dict(
            colorscale="RdYlGn_r",
            cmin=commits_binned.min(),
            cmax=commits_binned.max(),
            color=[commits_binned.max()],
            showscale=True,
            colorbar=dict(
                title="Total Commits",
                title_side="right",  # ← this line fixes it
            ),
        ),
        hoverinfo="skip",
        showlegend=False,
    )
)

fig.update_layout(
    title=f"Active Contributors per {BINNED_PERIOD_MONTH}-Month Period",
    title_x=0.5,
    xaxis_title="Date",
    yaxis_title="Number of Contributors",
    template="plotly_white",
    # xaxis_tickangle=45,
    width=900,
    height=600,
)

fig.write_image("active_contributors_colored.svg")
fig.show()
