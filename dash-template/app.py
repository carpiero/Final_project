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
import numpy as np
import plotly.express as px
import re
import locale
import plotly.graph_objects as go

# Multi-dropdown options
from controls import COUNTIES, WELL_STATUSES, WELL_TYPES, WELL_COLORS
from controls import  CCAA_dict, PROV,  MUNICIPIOS, PDC, df_final_pob_melt, df_final_pob, df_indicadores, df_final_pob_melt_PC

#################  change data

df_final_pob_melt_PC['Descripción'] = df_final_pob_melt_PC['Descripción'].str.replace(r'^...' , '')


# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

# Create controls

CCAA_options = [ {"label": CCAA_dict[x], "value": x}for x in CCAA_dict]

PROV_type_options = [ {"label": PROV[x], "value":x}for x in PROV ]

mun_type_options = [{"label": MUNICIPIOS[x], "value": x}for x in MUNICIPIOS]

pdc_type_options = [{"label": PDC[x], "value": x} for x in PDC ]

locale.setlocale(locale.LC_ALL, '')

#####################################################3
county_options = [
    {"label": str(COUNTIES[county]), "value": str(county)} for county in COUNTIES
]

well_status_options = [
    {"label": str(WELL_STATUSES[well_status]), "value": str(well_status)}
    for well_status in WELL_STATUSES
]

well_type_options = [
    {"label": str(WELL_TYPES[well_type]), "value": str(well_type)}
    for well_type in WELL_TYPES
]


# Load data
df = pd.read_csv(DATA_PATH.joinpath("wellspublic.csv"), low_memory=False)
df["Date_Well_Completed"] = pd.to_datetime(df["Date_Well_Completed"])
df = df[df["Date_Well_Completed"] > dt.datetime(1960, 1, 1)]

trim = df[["API_WellNo", "Well_Type", "Well_Name"]]
trim.index = trim["API_WellNo"]
dataset = trim.to_dict(orient="index")

points = pickle.load(open(DATA_PATH.joinpath("points.pkl"), "rb"))


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
        dcc.Store(id="aggregate_data"),
        # empty Div to trigger javascript file for graph resizing
        html.Div(id="output-clientside"),
        html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("dash-logo.png"),
                            id="plotly-image",
                            style={
                                "height": "60px",
                                "width": "auto",
                                "margin-bottom": "25px",
                            },
                        )
                    ],
                    className="one-third column",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "Municipios",
                                    style={"margin-bottom": "2px"},
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
        #         html.Div(
        #             [
        #                 html.A(
        #                     html.Button("Learn More", id="learn-more-button"),
        #                     href="https://plot.ly/dash/pricing/",
        #                 )
        #             ],
        #             className="one-third column",
        #             id="button",
        #         ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "2px"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            "Comunidad Autónoma",
                            className="control_label",
                        ),
                        dcc.Dropdown(
                            id="CCAA_types" ,
                            options=CCAA_options ,
                            value=list(CCAA_dict.keys())[0] ,
                            className="dcc_control" ,
                        ) ,
                        html.P("Provincia", className="control_label"),
                        dcc.Dropdown(
                            id="PROV_types" ,
                            # options=well_type_options,
                            # value=list(WELL_TYPES.keys()),
                            className="dcc_control" ,
                        ) ,
                         html.P("Municipio", className="control_label"),
                        dcc.Dropdown(
                            id="municipio_types" ,
                            # options=mun_type_options,
                            # value=list(MUNICIPIOS.keys()),
                            className="dcc_control" ,
                        ) ,
                        html.P("Partida de Coste" , className="control_label") ,
                        dcc.Dropdown(
                            id="partida_de_coste_types" ,
                            # options=pdc_type_options,
                            # value=list(PDC.keys()),
                            className="dcc_control" ,
                        ) ,
                    ],
                    className="pretty_container four columns",
                    id="cross-filter-options",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [html.H6(id="Población_text") , html.P('Población')] ,
                                    id="Población" ,
                                    className="mini_container" ,
                                ) ,
                                html.Div(
                                    [html.H6(id="Coste_efectivo_Total_text") , html.P("Coste efectivo Total")] ,
                                    id="Coste_efectivo_Total" ,
                                    className="mini_container" ,
                                ) ,
                                html.Div(
                                    [html.H6(id='Coste_efectivo_por_Habitante_text') ,
                                     html.P("Coste efectivo por Habitante")] ,
                                    id="Coste_efectivo_por_Habitante" ,
                                    className="mini_container" ,
                                ) ,
                                html.Div(
                                    [html.H6(id="Coste_efectivo_Medio_por_Habitante_text") ,
                                     html.P("Coste efectivo Medio por Habitante")] ,
                                    id="Coste_efectivo_Medio_por_Habitante" ,
                                    className="mini_container" ,
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
                    className="pretty_container seven columns",style={'width': '40%'}
                ),
                html.Div(
                    [dcc.Graph(id="individual_graph")],
                    className="pretty_container five columns",style={'width': '60%'}
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

####################################################

@app.callback(
    [Output("PROV_types", "value"),Output("PROV_types", "options")], [Input("CCAA_types", "value")]
)
def display_status(CCAA_types):
    if CCAA_types == 'TODAS':
        value = list(PROV.keys())[0]
        options = PROV_type_options
    else:
        prov_def=sorted(df_final_pob_melt.loc[df_final_pob_melt['CCAA']==CCAA_types,'Provincia'].unique().to_list())
        prov_def.insert(0, 'TODAS')
        PROV_def = dict(zip(prov_def, prov_def))
        options = [ {"label": PROV_def[x], "value":x}for x in PROV_def ]
        value=list(PROV_def.keys())[0]

    return (value,options)



@app.callback(
    [Output("municipio_types", "value"),Output("municipio_types", "options")], [Input("CCAA_types", "value"),Input("PROV_types", "value")]
)
def display_status(CCAA_types, PROV_types):
    if CCAA_types == 'TODAS' and PROV_types == 'TODAS':
        value = list(MUNICIPIOS.keys())[0]
        options = mun_type_options

    elif CCAA_types != 'TODAS' and PROV_types == 'TODAS':
        mun_def = sorted(df_final_pob_melt.loc[df_final_pob_melt['CCAA'] == CCAA_types ,'Nombre Ente Principal'].unique().to_list())
        mun_def.insert(0 , 'TODOS')
        MUN_def = dict(zip(mun_def , mun_def))
        options = [{"label": MUN_def[x] , "value": x} for x in MUN_def]
        value = list(MUN_def.keys())[0]

    else:
        mun_def =sorted(df_final_pob_melt.loc[df_final_pob_melt['Provincia']==PROV_types,'Nombre Ente Principal'].unique().to_list())
        mun_def.insert(0, 'TODOS')
        MUN_def = dict(zip(mun_def, mun_def))
        options = [ {"label": MUN_def[x], "value":x}for x in MUN_def ]
        value=list(MUN_def.keys())[0]

    return (value,options)


@app.callback(
    [Output("partida_de_coste_types", "value"),Output("partida_de_coste_types", "options")],
    [Input("CCAA_types", "value"), Input("PROV_types", "value"), Input("municipio_types", "value") ]
)
def display_status(CCAA_types, PROV_types,municipio_types):
    if  municipio_types != 'TODOS':
        pdc_def = sorted(list(df_final_pob_melt\
        .loc[(df_final_pob_melt['Nombre Ente Principal'] == municipio_types) & (df_final_pob_melt['coste_efectivo']>100)
        ,'Descripción'].unique()))

        pdc_def.insert(0 , 'TODOS')
        PDC_def = dict(zip(pdc_def , pdc_def))
        options = [{"label": PDC_def[x] , "value": x} for x in PDC_def]
        value = list(PDC_def.keys())[0]

    else:
        value = list(PDC.keys())[0]
        options = pdc_type_options

    return (value,options)

@app.callback(Output("Población_text", "children"),
    [
        Input("CCAA_types" , "value") , Input("PROV_types" , "value") , Input("municipio_types" , "value")

    ],
)
def update_text(CCAA_types, PROV_types,municipio_types ):
    if CCAA_types == 'TODAS' and PROV_types == 'TODAS' and municipio_types == 'TODOS':
        value=df_final_pob['Población 2018'].sum()

    elif CCAA_types != 'TODAS' and PROV_types == 'TODAS' and municipio_types == 'TODOS':
        value = df_final_pob.loc[df_final_pob['CCAA'] == CCAA_types,'Población 2018'].sum()

    elif PROV_types != 'TODAS' and municipio_types == 'TODOS':
        value = df_final_pob.loc[df_final_pob['Provincia']==PROV_types,'Población 2018'].sum()

    else:
        value=df_final_pob.loc[df_final_pob['Nombre Ente Principal'] == municipio_types,'Población 2018'].sum()

    value=locale.format_string('%.0f', value, True)

    return f'{value} hab.'


@app.callback (Output("Coste_efectivo_Total_text", "children"),
    [
        Input("CCAA_types" , "value") , Input("PROV_types" , "value") , Input("municipio_types" , "value"),
        Input("partida_de_coste_types" , "value")

    ],
)

def update_text(CCAA_types, PROV_types,municipio_types,partida_de_coste_types ):
    if partida_de_coste_types== 'TODOS':

        if CCAA_types == 'TODAS' and PROV_types == 'TODAS' and municipio_types == 'TODOS':
            value=df_final_pob_melt['coste_efectivo'].sum()

        elif CCAA_types != 'TODAS' and PROV_types == 'TODAS' and municipio_types == 'TODOS':
            value = df_final_pob_melt.loc[df_final_pob_melt['CCAA'] == CCAA_types,'coste_efectivo'].sum()

        elif PROV_types != 'TODAS' and municipio_types == 'TODOS':
            value = df_final_pob_melt.loc[df_final_pob_melt['Provincia']==PROV_types,'coste_efectivo'].sum()

        else:
            value=df_final_pob_melt.loc[df_final_pob_melt['Nombre Ente Principal'] == municipio_types,'coste_efectivo'].sum()

    else:
        if CCAA_types == 'TODAS' and PROV_types == 'TODAS' and municipio_types == 'TODOS':
            value=df_final_pob_melt.loc[df_final_pob_melt['Descripción'] == partida_de_coste_types,'coste_efectivo'].sum()

        elif CCAA_types != 'TODAS' and PROV_types == 'TODAS' and municipio_types == 'TODOS':
            value = df_final_pob_melt.loc[(df_final_pob_melt['Descripción'] == partida_de_coste_types) &(df_final_pob_melt['CCAA'] == CCAA_types),'coste_efectivo'].sum()

        elif PROV_types != 'TODAS' and municipio_types == 'TODOS':
            value = df_final_pob_melt.loc[(df_final_pob_melt['Descripción'] == partida_de_coste_types) &(df_final_pob_melt['Provincia']==PROV_types),'coste_efectivo'].sum()

        else:
            value=df_final_pob_melt.loc[(df_final_pob_melt['Descripción'] == partida_de_coste_types) &(df_final_pob_melt['Nombre Ente Principal'] == municipio_types),'coste_efectivo'].sum()



    value=locale.format_string('%.0f', round(value,0), True)

    return f'{value} Euros'

@app.callback (Output("Coste_efectivo_por_Habitante_text", "children"),
    [
        Input("Población_text", "children") , Input("Coste_efectivo_Total_text", "children")

    ],
)
def update_text(Población_text, Coste_efectivo_Total_text):
    pob=int(''.join(re.findall(r'\d' , Población_text)))
    cost=int(''.join(re.findall(r'\d' , Coste_efectivo_Total_text)))

    value= cost/pob
    value = locale.format_string('%.0f' , round(value,0) , True)

    return f'{value} Euros/Hab.'


@app.callback (Output("Coste_efectivo_Medio_por_Habitante_text", "children"),
    [
        Input("CCAA_types" , "value") , Input("PROV_types" , "value") , Input("municipio_types" , "value") ,
        Input("partida_de_coste_types" , "value")

    ],
)
def update_text(CCAA_types, PROV_types,municipio_types,partida_de_coste_types ):
    if partida_de_coste_types== 'TODOS':

        if CCAA_types == 'TODAS' and PROV_types == 'TODAS' and municipio_types == 'TODOS':
            value=df_final_pob_melt['coste_efectivo'].sum()/df_final_pob['Población 2018'].sum()

        elif CCAA_types != 'TODAS' and PROV_types == 'TODAS' and municipio_types == 'TODOS':
            value = df_final_pob_melt['coste_efectivo'].sum()/df_final_pob['Población 2018'].sum()

        elif CCAA_types != 'TODAS' and PROV_types != 'TODAS' and municipio_types == 'TODOS':
            value = df_final_pob_melt.loc[df_final_pob_melt['CCAA'] == CCAA_types,'coste_efectivo'].sum()\
            / df_final_pob.loc[df_final_pob['CCAA'] == CCAA_types,'Población 2018'].sum()

        elif CCAA_types == 'TODAS' and PROV_types != 'TODAS' and municipio_types == 'TODOS':
            value = df_final_pob_melt['coste_efectivo'].sum()/df_final_pob['Población 2018'].sum()

        else:
            cohorte=df_final_pob_melt.loc[df_final_pob_melt['Nombre Ente Principal'] == municipio_types , 'cohorte_pob']\
                          .unique().to_list()[0]

            value=df_final_pob_melt.loc[df_final_pob_melt['cohorte_pob'] == cohorte,'coste_efectivo'].sum() \
                    /df_final_pob.loc[df_final_pob['cohorte_pob'] == cohorte , 'Población 2018'].sum()

    else:
        if CCAA_types == 'TODAS' and PROV_types == 'TODAS' and municipio_types == 'TODOS':
            value=df_final_pob_melt.loc[df_final_pob_melt['Descripción'] == partida_de_coste_types,'coste_efectivo'].sum()\
                   /df_final_pob['Población 2018'].sum()

        elif CCAA_types != 'TODAS' and PROV_types == 'TODAS' and municipio_types == 'TODOS':
            value = df_final_pob_melt.loc[df_final_pob_melt['Descripción'] == partida_de_coste_types,'coste_efectivo'].sum()\
                   /df_final_pob['Población 2018'].sum()

        elif CCAA_types != 'TODAS' and PROV_types != 'TODAS' and municipio_types == 'TODOS':
             value = df_final_pob_melt.loc[(df_final_pob_melt['CCAA'] == CCAA_types)&(df_final_pob_melt['Descripción'] == partida_de_coste_types), 'coste_efectivo'].sum() \
                    / df_final_pob.loc[df_final_pob['CCAA'] == CCAA_types , 'Población 2018'].sum()

        elif CCAA_types == 'TODAS' and PROV_types != 'TODAS' and municipio_types == 'TODOS':
            value= df_final_pob_melt.loc[df_final_pob_melt['Descripción'] == partida_de_coste_types , 'coste_efectivo'].sum() \
            / df_final_pob['Población 2018'].sum()

        else:
            cohorte =df_final_pob_melt.loc[df_final_pob_melt['Nombre Ente Principal'] == municipio_types , 'cohorte_pob'] \
                .unique().to_list()[0]
            value = np.median(df_final_pob_melt_PC.loc[(df_final_pob_melt_PC['cohorte_pob'] == cohorte) & \
                    (df_final_pob_melt_PC['Descripción'] == f'{partida_de_coste_types}') & (df_final_pob_melt_PC['coste_efectivo_PC'] > 0) , 'coste_efectivo_PC'])

            # value=df_final_pob_melt.loc[(df_final_pob_melt['cohorte_pob'] == cohorte) & (df_final_pob_melt['Descripción'] == partida_de_coste_types), 'coste_efectivo'].sum() \
            #                     / df_final_pob.loc[df_final_pob['cohorte_pob'] == cohorte , 'Población 2018'].sum()

    value=locale.format_string('%.0f', round(value,0), True)

    return f'{value} Euros/Hab.'

# Helper functions
# def human_format(num):
#     if num == 0:
#         return "0"
#
#     magnitude = int(math.log(num, 1000))
#     mantissa = str(int(num / (1000 ** magnitude)))
#     return mantissa + ["", "K", "M", "G", "T", "P"][magnitude]
#
#
# def filter_dataframe(df, well_statuses, well_types, year_slider):
#     dff = df[
#         df["Well_Status"].isin(well_statuses)
#         & df["Well_Type"].isin(well_types)
#         & (df["Date_Well_Completed"] > dt.datetime(year_slider[0], 1, 1))
#         & (df["Date_Well_Completed"] < dt.datetime(year_slider[1], 1, 1))
#     ]
#     return dff
#
#
# def produce_individual(api_well_num):
#     try:
#         points[api_well_num]
#     except:
#         return None, None, None, None
#
#     index = list(
#         range(min(points[api_well_num].keys()), max(points[api_well_num].keys()) + 1)
#     )
#     gas = []
#     oil = []
#     water = []
#
#     for year in index:
#         try:
#             gas.append(points[api_well_num][year]["Gas Produced, MCF"])
#         except:
#             gas.append(0)
#         try:
#             oil.append(points[api_well_num][year]["Oil Produced, bbl"])
#         except:
#             oil.append(0)
#         try:
#             water.append(points[api_well_num][year]["Water Produced, bbl"])
#         except:
#             water.append(0)
#
#     return index, gas, oil, water
#
#
# def produce_aggregate(selected, year_slider):
#
#     index = list(range(max(year_slider[0], 1985), 2016))
#     gas = []
#     oil = []
#     water = []
#
#     for year in index:
#         count_gas = 0
#         count_oil = 0
#         count_water = 0
#         for api_well_num in selected:
#             try:
#                 count_gas += points[api_well_num][year]["Gas Produced, MCF"]
#             except:
#                 pass
#             try:
#                 count_oil += points[api_well_num][year]["Oil Produced, bbl"]
#             except:
#                 pass
#             try:
#                 count_water += points[api_well_num][year]["Water Produced, bbl"]
#             except:
#                 pass
#         gas.append(count_gas)
#         oil.append(count_oil)
#         water.append(count_water)
#
#     return index, gas, oil, water


# Create callbacks
# app.clientside_callback(
#     ClientsideFunction(namespace="clientside", function_name="resize"),
#     Output("output-clientside", "children"),
#     [Input("count_graph", "figure")],
# )


# @app.callback(
#     Output("aggregate_data", "data"),
#     [
#         Input("well_statuses", "value"),
#         Input("well_types", "value"),
#         Input("year_slider", "value"),
#     ],
# )
# def update_production_text(well_statuses, well_types, year_slider):
#
#     dff = filter_dataframe(df, well_statuses, well_types, year_slider)
#     selected = dff["API_WellNo"].values
#     index, gas, oil, water = produce_aggregate(selected, year_slider)
#     return [human_format(sum(gas)), human_format(sum(oil)), human_format(sum(water))]


# # Radio -> multi
# @app.callback(
#     Output("well_statuses", "value"), [Input("well_status_selector", "value")]
# )
# def display_status(selector):
#     if selector == "all":
#         return list(WELL_STATUSES.keys())
#     elif selector == "active":
#         return ["AC"]
#     return []
#
#
# # Radio -> multi
# @app.callback(Output("well_types", "value"), [Input("well_type_selector", "value")])
# def display_type(selector):
#     if selector == "all":
#         return list(WELL_TYPES.keys())
#     elif selector == "productive":
#         return ["GD", "GE", "GW", "IG", "IW", "OD", "OE", "OW"]
#     return []
#
#
# # Slider -> count graph
# @app.callback(Output("year_slider", "value"), [Input("count_graph", "selectedData")])
# def update_year_slider(count_graph_selected):
#
#     if count_graph_selected is None:
#         return [1990, 2010]
#
#     nums = [int(point["pointNumber"]) for point in count_graph_selected["points"]]
#     return [min(nums) + 1960, max(nums) + 1961]
#
#
# # Selectors -> well text
# @app.callback(
#     Output("well_text", "children"),
#     [
#         Input("well_statuses", "value"),
#         Input("well_types", "value"),
#         Input("year_slider", "value"),
#     ],
# )
# def update_well_text(well_statuses, well_types, year_slider):
#
#     dff = filter_dataframe(df, well_statuses, well_types, year_slider)
#     return dff.shape[0]
#
#
# @app.callback(
#     [
#         Output("gasText", "children"),
#         Output("oilText", "children"),
#         Output("waterText", "children"),
#     ],
#     [Input("aggregate_data", "data")],
# )
# def update_text(data):
#     return data[0] + " mcf", data[1] + " bbl", data[2] + " bbl"


# Selectors -> main graph

@app.callback(
    Output("main_graph", "figure"),
    [
        Input("CCAA_types" , "value") , Input("PROV_types" , "value") , Input("municipio_types" , "value") ,
        Input("partida_de_coste_types" , "value")
    ],[State("main_graph", "relayoutData")]
    # [State("lock_selector", "value"), State("main_graph", "relayoutData")],
)
def make_main_figure(CCAA_types, PROV_types,municipio_types,partida_de_coste_types,main_graph_layout):
    graph = df_final_pob_melt.loc[(df_final_pob_melt['Nombre Ente Principal'] == municipio_types)]
    fig = px.bar(graph,x='Descripción', y='coste_efectivo',template='seaborn',title='sdsds',barmode='stack', orientation='v')

    # relayoutData is None by default, and {'autosize': True} without relayout action
    # if main_graph_layout is not None :
    #     if "mapbox.center" in main_graph_layout.keys():
    #         lon = float(main_graph_layout["mapbox.center"]["lon"])
    #         lat = float(main_graph_layout["mapbox.center"]["lat"])
    #         zoom = float(main_graph_layout["mapbox.zoom"])
    #         layout["mapbox"]["center"]["lon"] = lon
    #         layout["mapbox"]["center"]["lat"] = lat
    #         layout["mapbox"]["zoom"] = zoom

    # figure = dict(data=traces, layout=layout)

    return fig

@app.callback(Output("individual_graph", "figure"),
    [
        Input("CCAA_types" , "value") , Input("PROV_types" , "value") , Input("municipio_types" , "value")
    ],[State("main_graph", "relayoutData")]
    # [State("lock_selector", "value"), State("main_graph", "relayoutData")],
)
def make_individual_figure(CCAA_types, PROV_types,municipio_types, main_graph):

    if CCAA_types == 'TODAS' and PROV_types == 'TODAS' and municipio_types == 'TODOS':

        df = df_final_pob_melt.pivot_table(index=['Descripción'] , values=['coste_efectivo'] , aggfunc=sum).sort_values(
            by='coste_efectivo' , ascending=False).reset_index()
        div = df_final_pob['Población 2018'].sum()
        df['coste_efectivo_new'] = df.apply(lambda new: round(new['coste_efectivo'] / div , 0) , axis=1)

        fig = go.Figure()
        fig.add_trace(go.Bar(x=df['Descripción'] ,y=df['coste_efectivo_new'] ,name='Total Nacional' ,marker_color='rgb(55, 83, 109)'))
        fig.add_trace(go.Bar(x=df['Descripción'] ,y=df['coste_efectivo_new'] ,name='Total Nacional' ,marker_color='rgb(26, 118, 255)'))

    elif CCAA_types != 'TODAS' and PROV_types == 'TODAS' and municipio_types == 'TODOS':

        df = df_final_pob_melt.pivot_table(index=['Descripción'] , values=['coste_efectivo'] , aggfunc=sum).sort_values(
            by='coste_efectivo' , ascending=False).reset_index()
        div = df_final_pob['Población 2018'].sum()
        df['coste_efectivo_new'] = df.apply(lambda new: round(new['coste_efectivo'] / div , 0) , axis=1)

        df2 = df_final_pob_melt.pivot_table(index=['CCAA' , 'Descripción'] , values=['coste_efectivo'] ,
                                           aggfunc=sum).sort_values(by='coste_efectivo' , ascending=False).reset_index()
        div = df_final_pob.loc[df_final_pob['CCAA'] == CCAA_types , 'Población 2018'].sum()
        df2 = df2.loc[df2['CCAA'] == CCAA_types]
        df2['coste_efectivo_new'] = df2.apply(lambda new: round(new['coste_efectivo'] / div,0) , axis=1)


        fig = go.Figure()
        fig.add_trace(go.Bar(x=df2['Descripción'] , y=df2['coste_efectivo_new'] , name=f'{CCAA_types}' ,
                             marker_color='rgb(55, 83, 109)'))
        fig.add_trace(go.Bar(x=df['Descripción'] , y=df['coste_efectivo_new'] , name='Total Nacional' ,
                             marker_color='rgb(26, 118, 255)'))


    elif CCAA_types != 'TODAS' and PROV_types != 'TODAS' and municipio_types == 'TODOS':

        df = df_final_pob_melt.pivot_table(index=['Provincia' , 'Descripción'] , values=['coste_efectivo'] ,
                                           aggfunc=sum).sort_values(by='coste_efectivo' , ascending=False).reset_index()
        div = df_final_pob.loc[df_final_pob['Provincia'] == PROV_types , 'Población 2018'].sum()
        df = df.loc[df['Provincia'] == PROV_types]
        df['coste_efectivo_new'] = df.apply(lambda new: round(new['coste_efectivo'] / div,0) , axis=1)


        df2 = df_final_pob_melt.pivot_table(index=['CCAA' , 'Descripción'] , values=['coste_efectivo'] ,
                                            aggfunc=sum).sort_values(by='coste_efectivo' ,ascending=False).reset_index()
        div = df_final_pob.loc[df_final_pob['CCAA'] == CCAA_types , 'Población 2018'].sum()
        df2 = df2.loc[df2['CCAA'] == CCAA_types]
        df2['coste_efectivo_new'] = df2.apply(lambda new: round(new['coste_efectivo'] / div,0) , axis=1)


        fig = go.Figure()
        fig.add_trace(go.Bar(x=df['Descripción'] , y=df['coste_efectivo_new'] , name=f'{PROV_types}' ,
                             marker_color='rgb(55, 83, 109)'))
        fig.add_trace(go.Bar(x=df2['Descripción'] , y=df2['coste_efectivo_new'] , name=f'{CCAA_types}' ,
                             marker_color='rgb(26, 118, 255)'))

    elif CCAA_types == 'TODAS' and PROV_types != 'TODAS' and municipio_types == 'TODOS':

        df = df_final_pob_melt.pivot_table(index=['Provincia' , 'Descripción'] , values=['coste_efectivo'] ,
                                           aggfunc=sum).sort_values(by='coste_efectivo' , ascending=False).reset_index()
        div = df_final_pob.loc[df_final_pob['Provincia'] == PROV_types , 'Población 2018'].sum()
        df = df.loc[df['Provincia'] == PROV_types]
        df['coste_efectivo_new'] = df.apply(lambda new: round(new['coste_efectivo'] / div,0) , axis=1)


        df2 = df_final_pob_melt.pivot_table(index=['Descripción'] , values=['coste_efectivo'] , aggfunc=sum).sort_values(
            by='coste_efectivo' , ascending=False).reset_index()
        div = df_final_pob['Población 2018'].sum()
        df2['coste_efectivo_new'] = df2.apply(lambda new: round(new['coste_efectivo'] / div , 0) , axis=1)


        fig = go.Figure()
        fig.add_trace(go.Bar(x=df['Descripción'] , y=df['coste_efectivo_new'] , name=f'{PROV_types}' ,
                             marker_color='rgb(55, 83, 109)'))
        fig.add_trace(go.Bar(x=df2['Descripción'] , y=df2['coste_efectivo_new'] , name=f'Total Nacional' ,
                             marker_color='rgb(26, 118, 255)'))

    else:
        df =df_final_pob_melt_PC.loc[df_final_pob_melt_PC['Nombre Ente Principal'] == municipio_types].sort_values(by='coste_efectivo_PC',ascending=False)
        df['coste_efectivo_PC'] = df.apply(lambda new: round(new['coste_efectivo_PC'] , 0) , axis=1)



        cohorte = df_final_pob_melt.loc[df_final_pob_melt['Nombre Ente Principal'] == municipio_types , 'cohorte_pob'] \
            .unique().to_list()[0]

        df2 = df_final_pob_melt_PC.loc[ df_final_pob_melt_PC['coste_efectivo_PC'] > 0]
        df2 = df2.pivot_table(index=['cohorte_pob','Descripción'],values=['coste_efectivo_PC'],aggfunc=np.median).reset_index()
        df2= df2.loc[df2['cohorte_pob'] == cohorte]
        df2['coste_efectivo_PC'] = df2.apply(lambda new: round(new['coste_efectivo_PC'] , 0) , axis=1)


        fig = go.Figure()
        fig.add_trace(go.Bar(x=df['Descripción'] , y=df['coste_efectivo_PC'] , name=f'{municipio_types}' ,
                             marker_color='rgb(55, 83, 109)'))
        fig.add_trace(go.Bar(x=df2['Descripción'] , y=df2['coste_efectivo_PC'] , name=f'Municipios con {cohorte} Hab.' ,
                             marker_color='rgb(26, 118, 255)'))






    fig.update_layout(margin=dict(l=20 , r=50 , t=50 , b=50) ,
                          title='Costes efectivo por tipo de coste' ,
                          xaxis_tickfont_size=12 ,
                          xaxis_tickangle=-45 ,
                          yaxis=dict(
                              title='Coste efectivo Euros' ,
                              titlefont_size=16 ,
                              tickfont_size=14 ,
                          ) ,
                          xaxis=dict(
                              title='Tipos de Coste efectivo' ,
                              titlefont_size=16 ,
                              tickfont_size=14 , showticklabels=False ,
                          ) ,

                          legend=dict(
                              x=0.6 ,
                              y=0.8 ,
                              bgcolor='rgba(255, 255, 255, 0)' ,
                              bordercolor='rgba(255, 255, 255, 0)'
                          ) ,
                          barmode='group' ,
                          bargap=0.20 ,  # gap between bars of adjacent location coordinates.
                          bargroupgap=0.1  # gap between bars of the same location coordinate.
                          )

    return fig





# @app.callback(
#     Output("main_graph", "figure"),
#     [
#         Input("well_statuses", "value"),
#         Input("well_types", "value"),
#         Input("year_slider", "value"),
#     ],
#     [State("lock_selector", "value"), State("main_graph", "relayoutData")],
# )
# def make_main_figure(
#     well_statuses, well_types, year_slider, selector, main_graph_layout
# ):
#
#     dff = filter_dataframe(df, well_statuses, well_types, year_slider)
#
#     traces = []
#     for well_type, dfff in dff.groupby("Well_Type"):
#         trace = dict(
#             type="scattermapbox",
#             lon=dfff["Surface_Longitude"],
#             lat=dfff["Surface_latitude"],
#             text=dfff["Well_Name"],
#             customdata=dfff["API_WellNo"],
#             name=WELL_TYPES[well_type],
#             marker=dict(size=4, opacity=0.6),
#         )
#         traces.append(trace)
#
#     # relayoutData is None by default, and {'autosize': True} without relayout action
#     if main_graph_layout is not None and selector is not None and "locked" in selector:
#         if "mapbox.center" in main_graph_layout.keys():
#             lon = float(main_graph_layout["mapbox.center"]["lon"])
#             lat = float(main_graph_layout["mapbox.center"]["lat"])
#             zoom = float(main_graph_layout["mapbox.zoom"])
#             layout["mapbox"]["center"]["lon"] = lon
#             layout["mapbox"]["center"]["lat"] = lat
#             layout["mapbox"]["zoom"] = zoom
#
#     figure = dict(data=traces, layout=layout)
#     return figure


# # Main graph -> individual graph
# @app.callback(Output("individual_graph", "figure"), [Input("main_graph", "hoverData")])
# def make_individual_figure(main_graph_hover):
#
#     layout_individual = copy.deepcopy(layout)
#
#     if main_graph_hover is None:
#         main_graph_hover = {
#             "points": [
#                 {"curveNumber": 4, "pointNumber": 569, "customdata": 31101173130000}
#             ]
#         }
#
#     chosen = [point["customdata"] for point in main_graph_hover["points"]]
#     index, gas, oil, water = produce_individual(chosen[0])
#
#     if index is None:
#         annotation = dict(
#             text="No data available",
#             x=0.5,
#             y=0.5,
#             align="center",
#             showarrow=False,
#             xref="paper",
#             yref="paper",
#         )
#         layout_individual["annotations"] = [annotation]
#         data = []
#     else:
#         data = [
#             dict(
#                 type="scatter",
#                 mode="lines+markers",
#                 name="Gas Produced (mcf)",
#                 x=index,
#                 y=gas,
#                 line=dict(shape="spline", smoothing=2, width=1, color="#fac1b7"),
#                 marker=dict(symbol="diamond-open"),
#             ),
#             dict(
#                 type="scatter",
#                 mode="lines+markers",
#                 name="Oil Produced (bbl)",
#                 x=index,
#                 y=oil,
#                 line=dict(shape="spline", smoothing=2, width=1, color="#a9bb95"),
#                 marker=dict(symbol="diamond-open"),
#             ),
#             dict(
#                 type="scatter",
#                 mode="lines+markers",
#                 name="Water Produced (bbl)",
#                 x=index,
#                 y=water,
#                 line=dict(shape="spline", smoothing=2, width=1, color="#92d8d8"),
#                 marker=dict(symbol="diamond-open"),
#             ),
#         ]
#         layout_individual["title"] = dataset[chosen[0]]["Well_Name"]
#
#     figure = dict(data=data, layout=layout_individual)
#     return figure


# Selectors, main graph -> aggregate graph
@app.callback(
    Output("aggregate_graph", "figure"),
    [
        Input("well_statuses", "value"),
        Input("well_types", "value"),
        Input("year_slider", "value"),
        Input("main_graph", "hoverData"),
    ],
)
def make_aggregate_figure(well_statuses, well_types, year_slider, main_graph_hover):

    layout_aggregate = copy.deepcopy(layout)

    if main_graph_hover is None:
        main_graph_hover = {
            "points": [
                {"curveNumber": 4, "pointNumber": 569, "customdata": 31101173130000}
            ]
        }

    chosen = [point["customdata"] for point in main_graph_hover["points"]]
    well_type = dataset[chosen[0]]["Well_Type"]
    dff = filter_dataframe(df, well_statuses, well_types, year_slider)

    selected = dff[dff["Well_Type"] == well_type]["API_WellNo"].values
    index, gas, oil, water = produce_aggregate(selected, year_slider)

    data = [
        dict(
            type="scatter",
            mode="lines",
            name="Gas Produced (mcf)",
            x=index,
            y=gas,
            line=dict(shape="spline", smoothing="2", color="#F9ADA0"),
        ),
        dict(
            type="scatter",
            mode="lines",
            name="Oil Produced (bbl)",
            x=index,
            y=oil,
            line=dict(shape="spline", smoothing="2", color="#849E68"),
        ),
        dict(
            type="scatter",
            mode="lines",
            name="Water Produced (bbl)",
            x=index,
            y=water,
            line=dict(shape="spline", smoothing="2", color="#59C3C3"),
        ),
    ]
    layout_aggregate["title"] = "Aggregate: " + WELL_TYPES[well_type]

    figure = dict(data=data, layout=layout_aggregate)
    return figure


# Selectors, main graph -> pie graph
@app.callback(
    Output("pie_graph", "figure"),
    [
        Input("well_statuses", "value"),
        Input("well_types", "value"),
        Input("year_slider", "value"),
    ],
)
def make_pie_figure(well_statuses, well_types, year_slider):

    layout_pie = copy.deepcopy(layout)

    dff = filter_dataframe(df, well_statuses, well_types, year_slider)

    selected = dff["API_WellNo"].values
    index, gas, oil, water = produce_aggregate(selected, year_slider)

    aggregate = dff.groupby(["Well_Type"]).count()

    data = [
        dict(
            type="pie",
            labels=["Gas", "Oil", "Water"],
            values=[sum(gas), sum(oil), sum(water)],
            name="Production Breakdown",
            text=[
                "Total Gas Produced (mcf)",
                "Total Oil Produced (bbl)",
                "Total Water Produced (bbl)",
            ],
            hoverinfo="text+value+percent",
            textinfo="label+percent+name",
            hole=0.5,
            marker=dict(colors=["#fac1b7", "#a9bb95", "#92d8d8"]),
            domain={"x": [0, 0.45], "y": [0.2, 0.8]},
        ),
        dict(
            type="pie",
            labels=[WELL_TYPES[i] for i in aggregate.index],
            values=aggregate["API_WellNo"],
            name="Well Type Breakdown",
            hoverinfo="label+text+value+percent",
            textinfo="label+percent+name",
            hole=0.5,
            marker=dict(colors=[WELL_COLORS[i] for i in aggregate.index]),
            domain={"x": [0.55, 1], "y": [0.2, 0.8]},
        ),
    ]
    layout_pie["title"] = "Production Summary: {} to {}".format(
        year_slider[0], year_slider[1]
    )
    layout_pie["font"] = dict(color="#777777")
    layout_pie["legend"] = dict(
        font=dict(color="#CCCCCC", size="10"), orientation="h", bgcolor="rgba(0,0,0,0)"
    )

    figure = dict(data=data, layout=layout_pie)
    return figure


# Selectors -> count graph
@app.callback(
    Output("count_graph", "figure"),
    [
        Input("well_statuses", "value"),
        Input("well_types", "value"),
        Input("year_slider", "value"),
    ],
)
def make_count_figure(well_statuses, well_types, year_slider):

    layout_count = copy.deepcopy(layout)

    dff = filter_dataframe(df, well_statuses, well_types, [1960, 2017])
    g = dff[["API_WellNo", "Date_Well_Completed"]]
    g.index = g["Date_Well_Completed"]
    g = g.resample("A").count()

    colors = []
    for i in range(1960, 2018):
        if i >= int(year_slider[0]) and i < int(year_slider[1]):
            colors.append("rgb(123, 199, 255)")
        else:
            colors.append("rgba(123, 199, 255, 0.2)")

    data = [
        dict(
            type="scatter",
            mode="markers",
            x=g.index,
            y=g["API_WellNo"] / 2,
            name="All Wells",
            opacity=0,
            hoverinfo="skip",
        ),
        dict(
            type="bar",
            x=g.index,
            y=g["API_WellNo"],
            name="All Wells",
            marker=dict(color=colors),
        ),
    ]

    layout_count["title"] = "Completed Wells/Year"
    layout_count["dragmode"] = "select"
    layout_count["showlegend"] = False
    layout_count["autosize"] = True

    figure = dict(data=data, layout=layout_count)
    return figure


# Main
if __name__ == "__main__":
    app.run_server(debug=True)
