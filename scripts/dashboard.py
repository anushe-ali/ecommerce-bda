from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from pymongo import MongoClient

# -----------------------------
# MongoDB connection
# -----------------------------
MONGO_URI = "mongodb://mongo:27017"
DB_NAME = "ecommerce"
COLLECTION_NAME = "orders"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# -----------------------------
# Dash app
# -----------------------------
app = Dash(__name__)
app.title = "Real-Time E-Commerce Dashboard"

# -----------------------------
# Layout
# -----------------------------
app.layout = html.Div(
    style={
        "fontFamily": "Arial",
        "backgroundColor": "#f5f6fa",
        "padding": "20px"
    },
    children=[
        html.H1(
            "📊 Real-Time E-Commerce KPIs",
            style={"textAlign": "center"}
        ),

        html.P(
            "Live metrics updated every minute from streaming data",
            style={"textAlign": "center", "color": "#555"}
        ),

        dcc.Interval(
            id="refresh-interval",
            interval=60 * 1000,  # 1 minute
            n_intervals=0
        ),

        html.Div(
            style={
                "display": "flex",
                "gap": "20px",
                "marginTop": "30px"
            },
            children=[
                html.Div(
                    style={
                        "backgroundColor": "white",
                        "padding": "15px",
                        "borderRadius": "10px",
                        "boxShadow": "0px 0px 10px rgba(0,0,0,0.1)",
                        "flex": 1
                    },
                    children=[
                        dcc.Graph(id="revenue-by-city")
                    ]
                ),

                html.Div(
                    style={
                        "backgroundColor": "white",
                        "padding": "15px",
                        "borderRadius": "10px",
                        "boxShadow": "0px 0px 10px rgba(0,0,0,0.1)",
                        "flex": 1
                    },
                    children=[
                        dcc.Graph(id="aov-by-city")
                    ]
                )
            ]
        )
    ]
)

# -----------------------------
# Callbacks
# -----------------------------
@app.callback(
    Output("revenue-by-city", "figure"),
    Output("aov-by-city", "figure"),
    Input("refresh-interval", "n_intervals")
)
def update_charts(_):
    data = list(collection.find({}, {"_id": 0, "city": 1, "order_value": 1}))

    if not data:
        empty_fig = px.bar(title="No data available yet")
        return empty_fig, empty_fig

    df = pd.DataFrame(data)

    # Revenue by city
    revenue_df = (
        df.groupby("city", as_index=False)["order_value"]
        .sum()
        .rename(columns={"order_value": "revenue"})
    )

    revenue_fig = px.bar(
        revenue_df,
        x="city",
        y="revenue",
        title="Total Revenue by City",
        text_auto=".2s",
        color="revenue",
        color_continuous_scale="Blues"
    )

    revenue_fig.update_layout(
        xaxis_title="City",
        yaxis_title="Revenue",
        title_x=0.5
    )

    # Average Order Value by city
    aov_df = (
        df.groupby("city", as_index=False)["order_value"]
        .mean()
        .rename(columns={"order_value": "avg_order_value"})
    )

    aov_fig = px.bar(
        aov_df,
        x="city",
        y="avg_order_value",
        title="Average Order Value (AOV) by City",
        text_auto=".2f",
        color="avg_order_value",
        color_continuous_scale="Greens"
    )

    aov_fig.update_layout(
        xaxis_title="City",
        yaxis_title="Average Order Value",
        title_x=0.5
    )

    return revenue_fig, aov_fig


# -----------------------------
# Run server
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True)
