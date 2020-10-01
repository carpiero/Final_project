# Import required libraries
import pickle
import copy
import pathlib
import dash
import math
import datetime as dt
import pandas as pd
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html

# Multi-dropdown options
from controls import  WELL_STATUSES, WELL_TYPES, WELL_COLORS, MUNICIPIOS, PDC,df_final_pob_melt

df=df_final_pob_melt

# get relative data folder
# PATH = pathlib.Path(__file__).parent
# DATA_PATH = PATH.joinpath("data").resolve()

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

# Create controls

well_status_options = [
    {"label": WELL_STATUSES[well_status], "value": well_status}
    for well_status in WELL_STATUSES
]

well_type_options = [
    {"label": str(WELL_TYPES[well_type]), "value": str(well_type)}
    for well_type in WELL_TYPES
]

mun_type_options = [
    {"label": str(MUNICIPIOS[x]), "value": str(x)}
    for x in MUNICIPIOS
]

pdc_type_options = [
    {"label": str(PDC[x]), "value": str(x)}
    for x in PDC
]


# Load data
# df = pd.read_csv(DATA_PATH.joinpath("wellspublic.csv"), low_memory=False)
# df["Date_Well_Completed"] = pd.to_datetime(df["Date_Well_Completed"])
# df = df[df["Date_Well_Completed"] > dt.datetime(1960, 1, 1)]
#
# trim = df[["API_WellNo", "Well_Type", "Well_Name"]]
# trim.index = trim["API_WellNo"]
# dataset = trim.to_dict(orient="index")
#
# points = pickle.load(open(DATA_PATH.joinpath("points.pkl"), "rb"))


# Create global chart template
mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Satellite Overview",
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="light",
        center=dict(lon=-78.05, lat=42.54),
        zoom=7,
    ),
)

# Create app layout
app.layout = html.Div(
    [
        # dcc.Store(id="aggregate_data"),
        # empty Div to trigger javascript file for graph resizing
        html.Div(id="output-clientside"),
        html.Div(
            [
                # html.Div(
                #     [
                #         html.Img(
                #             src=app.get_asset_url("dash-logo.png"),
                #             id="plotly-image",
                #             style={
                #                 "height": "60px",
                #                 "width": "auto",
                #                 "margin-bottom": "25px",
                #             },
                #         )
                #     ],
                #     className="one-third column",
                # ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "Municipios",
                                    style={"margin-bottom": "10px"},
                                ),
                                html.H5(
                                    "Coste efectivo", style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="one-half column",
                    id="title",
                ),
                # html.Div(
                #     [
                #         html.A(
                #             html.Button("Learn More", id="learn-more-button"),
                #             href="https://plot.ly/dash/pricing/",
                #         )
                #     ],
                #     className="one-third column",
                #     id="button",
                # ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
        html.Div(
            [
                html.Div(
                    [

                        html.P("Comunidad Autónoma", className="control_label"),
                           dcc.Dropdown(
                            id="well_statuses",
                            options=well_status_options,
                            value=list(WELL_STATUSES.keys())[0],
                            className="dcc_control",
                        ),

                        html.P("Provincia", className="control_label"),
                        dcc.Dropdown(
                            id="well_types",
                            # options=well_type_options,
                            # value=list(WELL_TYPES.keys()),
                            className="dcc_control",
                        ),
                        html.P("Municipio", className="control_label"),
                        dcc.Dropdown(
                            id="municipio_types",
                            options=mun_type_options,
                            value=list(MUNICIPIOS.keys()),
                            className="dcc_control",
                        ),
                        html.P("Partida de Coste", className="control_label"),
                        dcc.Dropdown(
                            id="partida_de_coste_types",
                            options=pdc_type_options,
                            value=list(PDC.keys()),
                            className="dcc_control",
                        ),
                    ],
                    className="pretty_container four columns",
                    id="cross-filter-options",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [html.H6(id="Población_text"), html.P('Población')],
                                    id="Población",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="Coste efectivo Total_text"), html.P("Coste efectivo Total")],
                                    id="Coste efectivo Total",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id='Coste efectivo por Habitante_text'), html.P("Coste efectivo por Habitante")],
                                    id="Coste efectivo por Habitante",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="Coste efectivo Medio por Habitante_text"), html.P("Coste efectivo Medio por Habitante")],
                                    id="Coste efectivo Medio por Habitante",
                                    className="mini_container",
                                ),
                            ],
                            id="info-container",
                            className="row container-display",
                        ),
                        html.Div(
                            [dcc.Graph(id="count_graph")],
                            id="countGraphContainer",
                            className="pretty_container",
                        ),
                    ],
                    id="right-column",
                    className="eight columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="main_graph")],
                    className="pretty_container seven columns",
                ),
                html.Div(
                    [dcc.Graph(id="individual_graph")],
                    className="pretty_container five columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="pie_graph")],
                    className="pretty_container seven columns",
                ),
                html.Div(
                    [dcc.Graph(id="aggregate_graph")],
                    className="pretty_container five columns",
                ),
            ],
            className="row flex-display",
        ),
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)

# def filter_dataframe(df, well_statuses, well_types, municipio_types, partida_de_coste_types):
#     dff = df[df["CCAA"].isin(well_statuses)
#         & df['Provincia'].isin(well_types)
#         & df['Nombre Ente Principal'].isin(municipio_types)
#         & df['Descripción'].isin(partida_de_coste_types)
#     ]
#     return dff



# Create callbacks
# app.clientside_callback(
#     ClientsideFunction(namespace="clientside", function_name="resize"),
#     Output("output-clientside", "children"),
#     [Input("count_graph", "figure")],
# )


@app.callback(
    [Output("well_types", "value"),Output("well_types", "options")], [Input("well_statuses", "value")]
)
def display_status(well_statuses):

    value=well_statuses
    options=[{"label": str(well_statuses), "value": str(well_statuses)}]


    return (value,options)




# Main
if __name__ == "__main__":
    app.run_server(debug=True)