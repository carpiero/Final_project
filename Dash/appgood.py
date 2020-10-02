# Import required libraries
import pickle
import re
import locale
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
from controls import  CCAA_dict, PROV,  MUNICIPIOS, PDC, df_final_pob_melt, df_final_pob, df_indicadores, WELL_COLORS

# df=df_final_pob_melt

# get relative data folder
# PATH = pathlib.Path(__file__).parent
# DATA_PATH = PATH.joinpath("data").resolve()

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
                            id="CCAA_types",
                            options=CCAA_options,
                            value=list(CCAA_dict.keys())[0],
                            className="dcc_control",
                        ),

                        html.P("Provincia", className="control_label"),
                        dcc.Dropdown(
                            id="PROV_types",
                            # options=well_type_options,
                            # value=list(WELL_TYPES.keys()),
                            className="dcc_control",
                        ),
                        html.P("Municipio", className="control_label"),
                        dcc.Dropdown(
                            id="municipio_types",
                            # options=mun_type_options,
                            # value=list(MUNICIPIOS.keys()),
                            className="dcc_control",
                        ),
                        html.P("Partida de Coste", className="control_label"),
                        dcc.Dropdown(
                            id="partida_de_coste_types",
                            # options=pdc_type_options,
                            # value=list(PDC.keys()),
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
                                    [html.H6(id="Coste_efectivo_Total_text"), html.P("Coste efectivo Total")],
                                    id="Coste_efectivo_Total",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id='Coste_efectivo_por_Habitante_text'), html.P("Coste efectivo por Habitante")],
                                    id="Coste_efectivo_por_Habitante",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="Coste_efectivo_Medio_por_Habitante_text"), html.P("Coste efectivo Medio por Habitante")],
                                    id="Coste_efectivo_Medio_por_Habitante",
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



    value=locale.format_string('%.0f', value, True)

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
    value = locale.format_string('%.0f' , value , True)

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
            value = df_final_pob_melt.loc[(df_final_pob_melt['cohorte_pob'] == cohorte) & (df_final_pob_melt['Descripción'] == partida_de_coste_types), 'coste_efectivo'].sum() \
                    / df_final_pob.loc[df_final_pob['cohorte_pob'] == cohorte , 'Población 2018'].sum()

    value=locale.format_string('%.0f', value, True)

    return f'{value} Euros/Hab.'








  # Output("Coste efectivo Total_text", "children"),
                # Output("Coste efectivo por Habitante_text", "children"),
                # Output("Coste efectivo Medio por Habitante_text", "children")






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





# Main
if __name__ == "__main__":
    app.run_server(debug=True)