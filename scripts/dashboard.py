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
COLLECTION_NAME = "orders_live"

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
    style={"fontFamily": "Arial", "backgroundColor": "#f5f6fa", "padding": "20px"},
    children=[

        # Title
        html.H1("📊 Real-Time E-Commerce KPIs", style={"textAlign": "center"}),
        html.P("Live metrics updated every minute from streaming data",
               style={"textAlign": "center", "color": "#555"}),

        # Refresh interval
        dcc.Interval(id="refresh-interval", interval=60*1000, n_intervals=0),

        # ---------------- KPIs ----------------
        html.Div(
            style={"display": "flex", "gap": "20px", "marginTop": "20px", "justifyContent": "center"},
            children=[
                html.Div(style={"backgroundColor": "#fffae6", "padding": "20px", "borderRadius": "10px",
                                "boxShadow": "0px 0px 10px rgba(0,0,0,0.1)", "textAlign": "center", "flex": 1},
                         children=[html.H3("💰 Total Revenue"), html.H2(id="total-revenue-value")]),

                html.Div(style={"backgroundColor": "#e6f7ff", "padding": "20px", "borderRadius": "10px",
                                "boxShadow": "0px 0px 10px rgba(0,0,0,0.1)", "textAlign": "center", "flex": 1},
                         children=[html.H3("🛒 Total Orders"), html.H2(id="total-orders-value")]),

                html.Div(style={"backgroundColor": "#e6ffe6", "padding": "20px", "borderRadius": "10px",
                                "boxShadow": "0px 0px 10px rgba(0,0,0,0.1)", "textAlign": "center", "flex": 1},
                         children=[html.H3("📊 Average Order Value"), html.H2(id="average-order-value-value")])
            ]
        ),

        # ---------------- Main charts ----------------
        html.Div(
            style={"display": "flex", "gap": "20px", "marginTop": "30px"},
            children=[
                html.Div(style={"backgroundColor": "white", "padding": "15px", "borderRadius": "10px",
                                "boxShadow": "0px 0px 10px rgba(0,0,0,0.1)", "flex": 1},
                         children=[dcc.Graph(id="revenue-by-city")]),

                html.Div(style={"backgroundColor": "white", "padding": "15px", "borderRadius": "10px",
                                "boxShadow": "0px 0px 10px rgba(0,0,0,0.1)", "flex": 1},
                         children=[dcc.Graph(id="aov-by-city")]),

                html.Div(style={"backgroundColor": "#fff5e6", "padding": "15px", "borderRadius": "10px",
                                "boxShadow": "0px 0px 10px rgba(0,0,0,0.1)", "flex": 1},
                         children=[dcc.Graph(id="cancelled-orders-by-city")]),

                html.Div(style={"backgroundColor": "#fff0f0", "padding": "20px", "borderRadius": "10px",
                                "boxShadow": "0px 0px 10px rgba(0,0,0,0.1)", "textAlign": "center", "flex": 1},
                         children=[dcc.Graph(id="failed-payments-by-city")])

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
    Output("failed-payments-by-city", "figure"),
    Output("cancelled-orders-by-city", "figure"),
    Output("total-revenue-value", "children"),
    Output("total-orders-value", "children"),
    Output("average-order-value-value", "children"),
    Input("refresh-interval", "n_intervals")
)
def update_charts(_):
    data = list(collection.find({}, {"_id": 0, "city": 1, "total_amount": 1, "payment_status": 1, "order_status": 1}))

    if not data:
        empty_fig = px.bar(title="No data available yet")
        return empty_fig, empty_fig, empty_fig, empty_fig, "N/A", "N/A", "N/A"

    df = pd.DataFrame(data)
    df.rename(columns={"total_amount": "order_value"}, inplace=True)

    # KPIs
    total_revenue = f"${df['order_value'].sum():,.2f}"
    total_orders = f"{len(df)}"
    average_order_value = f"${df['order_value'].mean():,.2f}"

    # Revenue by city
    revenue_df = df.groupby("city", as_index=False)["order_value"].sum().rename(columns={"order_value": "revenue"})
    revenue_fig = px.bar(revenue_df, x="city", y="revenue", text_auto=".2f", color="revenue", color_continuous_scale="Blues")
    revenue_fig.update_layout(xaxis_title="City", yaxis_title="Revenue", title_x=0.5)

    # Average Order Value by city
    aov_df = df.groupby("city", as_index=False)["order_value"].mean().rename(columns={"order_value": "avg_order_value"})
    aov_fig = px.bar(aov_df, x="city", y="avg_order_value", text_auto=".2f", color="avg_order_value", color_continuous_scale="Greens")
    aov_fig.update_layout(xaxis_title="City", yaxis_title="Average Order Value", title_x=0.5)

    # Failed Payments by city
    failed_df = df[df["payment_status"] == "failed"].groupby("city", as_index=False)["payment_status"].count().rename(columns={"payment_status": "failed_payments"})
    failed_fig = px.bar(failed_df, x="city", y="failed_payments", text_auto=True, color="failed_payments", color_continuous_scale="Reds")
    failed_fig.update_layout(xaxis_title="City", yaxis_title="Failed Payments", title_x=0.5)

    # Cancelled Orders by city
    cancelled_df = df[df["order_status"] == "cancelled"].groupby("city", as_index=False)["order_status"].count().rename(columns={"order_status": "cancelled_orders"})
    cancelled_fig = px.bar(cancelled_df, x="city", y="cancelled_orders", text_auto=True, color="cancelled_orders", color_continuous_scale="Oranges")
    cancelled_fig.update_layout(xaxis_title="City", yaxis_title="Cancelled Orders", title_x=0.5)

    return revenue_fig, aov_fig, failed_fig, cancelled_fig, total_revenue, total_orders, average_order_value


# -----------------------------
# Run server
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True)
