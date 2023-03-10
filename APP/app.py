"""
Main file for Sales Forecasting.
"""

import io
import os

import flask
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

app = flask.Flask(__name__, static_folder="static")

SESSION = dict()

path = os.path.join("..", "DATA", "datos_venta.csv")
result_path = os.path.join("..", "DATA", "results.csv")
col_types = {
"Producto": object, 
"Unidades": float, 
"Almacen": object
}
sales_df = pd.read_csv(path, sep=";", decimal=",",
                    parse_dates=["Fecha Prevista de Entrega"],
                    dtype=col_types)

result_df = pd.read_csv(result_path, parse_dates=["last_weekday"])

sales_df.columns = [col.lower().replace(" ", "_") for col in sales_df.columns]


@app.route("/", methods=("GET", "POST"))
def main():
    """
    Main route for Sales Forecasting app.
    ---
    responses:
      500:
        description: Error in Sales Forecasting.
      200:
        description: OK.

    """

    if flask.request.method == "POST":
        SESSION["store"] = flask.request.form.getlist("store")[0]
        SESSION["product"] = flask.request.form.getlist("product")[0]
        return flask.redirect("forecasting.png")
    else:
        SESSION.clear()

    return flask.render_template("items/main.html", stores=sales_df["almacen"].unique(), 
                                 products=sales_df["producto"].unique())

@app.route("/forecasting.png", methods=("GET", "POST"))
def forecasting():
    """
    Main route for Sales Forecasting app.
    ---
    responses:
      500:
        description: Error in Sales Forecasting.
      200:
        description: OK.

    """
    choose_df = result_df[(result_df["almacen"] == SESSION["store"]) & (result_df["producto"] == SESSION["product"])]
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    xs = choose_df["last_weekday"]
    ys = choose_df["forecasting"]
    axis.title.set_text(f"{SESSION['store']} - {SESSION['product']}")
    axis.plot(xs, ys)
    axis.tick_params(labelrotation=15)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)

    return flask.Response(output.getvalue(), mimetype='image/png')