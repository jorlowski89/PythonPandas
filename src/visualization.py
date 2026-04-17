from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.config import COLOR_SEQUENCE, INDICATOR_LABELS, PLOTLY_TEMPLATE


def build_yearly_average_line_figure(
    yearly_frame: pd.DataFrame,
    metric: str,
    title: str,
) -> go.Figure:
    figure = px.line(
        yearly_frame,
        x="rok",
        y=metric,
        markers=True,
        title=title,
        labels={"rok": "Rok", metric: INDICATOR_LABELS.get(metric, metric)},
        template=PLOTLY_TEMPLATE,
    )
    figure.update_traces(line_color=COLOR_SEQUENCE[0], marker_color=COLOR_SEQUENCE[1])
    figure.update_layout(margin=dict(l=20, r=20, t=60, b=20), height=420)
    return figure


def build_scatter_figure(
    frame: pd.DataFrame,
    crime_column: str,
    title: str,
) -> go.Figure:
    data = frame[["powiat", "rok", "unemployment_rate", crime_column]].dropna().copy()
    figure = px.scatter(
        data,
        x="unemployment_rate",
        y=crime_column,
        color="rok",
        hover_name="powiat",
        title=title,
        labels={
            "unemployment_rate": INDICATOR_LABELS["unemployment_rate"],
            crime_column: INDICATOR_LABELS.get(crime_column, crime_column),
            "rok": "Rok",
        },
        color_continuous_scale="Teal",
        template=PLOTLY_TEMPLATE,
    )

    if len(data) >= 2:
        slope, intercept = np.polyfit(
            data["unemployment_rate"].to_numpy(),
            data[crime_column].to_numpy(),
            1,
        )
        x_range = np.linspace(
            data["unemployment_rate"].min(),
            data["unemployment_rate"].max(),
            100,
        )
        figure.add_trace(
            go.Scatter(
                x=x_range,
                y=intercept + slope * x_range,
                mode="lines",
                name="Linia trendu",
                line=dict(color="#b91c1c", width=2),
            )
        )

    figure.update_layout(margin=dict(l=20, r=20, t=60, b=20), height=460)
    return figure


def build_yearly_correlation_figure(
    correlation_frame: pd.DataFrame,
    title: str,
) -> go.Figure:
    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=correlation_frame["rok"],
            y=correlation_frame["pearson_r"],
            mode="lines+markers",
            name="Pearson r",
            line=dict(color=COLOR_SEQUENCE[1], width=2),
        )
    )
    figure.add_trace(
        go.Scatter(
            x=correlation_frame["rok"],
            y=correlation_frame["spearman_rho"],
            mode="lines+markers",
            name="Spearman rho",
            line=dict(color=COLOR_SEQUENCE[0], width=2),
        )
    )
    figure.update_layout(
        title=title,
        template=PLOTLY_TEMPLATE,
        xaxis_title="Rok",
        yaxis_title="Wartosc korelacji",
        margin=dict(l=20, r=20, t=60, b=20),
        height=420,
    )
    figure.add_hline(y=0, line_dash="dash", line_color="#94a3b8")
    return figure


def build_lag_scatter_figure(
    lagged_frame: pd.DataFrame,
    crime_column: str,
    title: str,
) -> go.Figure:
    next_year_column = f"{crime_column}_next_year"
    figure = px.scatter(
        lagged_frame,
        x="unemployment_rate",
        y=next_year_column,
        color="rok",
        hover_name="powiat",
        title=title,
        labels={
            "unemployment_rate": "Bezrobocie w roku t (%)",
            next_year_column: f"{INDICATOR_LABELS.get(crime_column, crime_column)} w roku t+1",
            "rok": "Rok t",
        },
        color_continuous_scale="Teal",
        template=PLOTLY_TEMPLATE,
    )
    figure.update_layout(margin=dict(l=20, r=20, t=60, b=20), height=460)
    return figure


def build_outlier_bar_figure(outliers_frame: pd.DataFrame, title: str) -> go.Figure:
    plot_data = outliers_frame.sort_values("srednia_reszta")
    figure = px.bar(
        plot_data,
        x="srednia_reszta",
        y="powiat",
        color="kierunek",
        orientation="h",
        title=title,
        labels={
            "srednia_reszta": "Srednia odchyłka od trendu",
            "powiat": "Powiat",
            "kierunek": "Typ odchylenia",
        },
        template=PLOTLY_TEMPLATE,
        color_discrete_map={
            "Powyzej trendu": "#dc2626",
            "Ponizej trendu": "#0f766e",
        },
    )
    figure.update_layout(margin=dict(l=20, r=20, t=60, b=20), height=500)
    return figure


def build_yoy_change_figure(
    yearly_frame: pd.DataFrame,
    metric: str,
    title: str,
) -> go.Figure:
    figure = px.bar(
        yearly_frame.dropna(subset=[f"{metric}_yoy_pct"]),
        x="rok",
        y=f"{metric}_yoy_pct",
        title=title,
        labels={"rok": "Rok", f"{metric}_yoy_pct": "Zmiana r/r (%)"},
        template=PLOTLY_TEMPLATE,
        color_discrete_sequence=[COLOR_SEQUENCE[3]],
    )
    figure.add_hline(y=0, line_dash="dash", line_color="#94a3b8")
    figure.update_layout(margin=dict(l=20, r=20, t=60, b=20), height=380)
    return figure
