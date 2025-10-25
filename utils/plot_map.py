import plotly.graph_objects as go

def plot_grid(buses, lines):
    fig = go.Figure()

    for _, line in lines.iterrows():
        from_bus = buses[buses.id == line["from"]].iloc[0]
        to_bus = buses[buses.id == line["to"]].iloc[0]
        stress = line["stress"]

        color = "green" if stress < 80 else "orange" if stress < 100 else "red"

        fig.add_trace(go.Scattermapbox(
            lon=[from_bus.lon, to_bus.lon],
            lat=[from_bus.lat, to_bus.lat],
            mode="lines",
            line=dict(color=color, width=3),
            hoverinfo="text",
            text=f"{from_bus.name}–{to_bus.name}<br>Stress: {stress:.1f}%",
        ))

    fig.add_trace(go.Scattermapbox(
        lon=buses.lon,
        lat=buses.lat,
        text=buses.name,
        mode="markers+text",
        textposition="top center",
        marker=dict(size=6, color="blue")
    ))

    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=9,
        mapbox_center={"lat": buses.lat.mean(), "lon": buses.lon.mean()},
        margin=dict(l=0, r=0, t=0, b=0)
    )

    return fig