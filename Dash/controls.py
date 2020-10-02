import pandas as pd

df_indicadores = pd.read_parquet(f'../data/processed/df_indicadores.parquet')
df_final_pob = pd.read_parquet('../data/processed/df_final_pob.parquet')
df_final_pob_melt = pd.read_parquet('../data/processed/df_final_pob_melt.parquet')
df_final_pob_melt_PC = pd.read_parquet('../data/processed/df_final_pob_melt_PC.parquet')

CCAA=sorted(df_final_pob['CCAA'].unique().to_list())
CCAA.insert(0, 'TODAS')
CCAA_dict = dict(zip(CCAA, CCAA))

prov=sorted(df_final_pob['Provincia'].unique().to_list())
prov.insert(0, 'TODAS')
PROV = dict(zip(prov, prov))

mun=sorted(df_final_pob['Nombre Ente Principal'].unique().to_list())
mun.insert(0, 'TODOS')
MUNICIPIOS = dict(zip(mun, mun))

pdc=sorted(list(df_final_pob_melt['Descripción'].unique()))
pdc.insert(0, 'TODOS')
PDC = dict(zip(pdc, pdc))





WELL_COLORS = dict(
    GD="#FFEDA0",
    GE="#FA9FB5",
    GW="#A1D99B",
    IG="#67BD65",
    OD="#BFD3E6",
    OE="#B3DE69",
    OW="#FDBF6F",
    ST="#FC9272",
    BR="#D0D1E6",
    MB="#ABD9E9",
    IW="#3690C0",
    LP="#F87A72",
    MS="#CA6BCC",
    Confidential="#DD3497",
    DH="#4EB3D3",
    DS="#FFFF33",
    DW="#FB9A99",
    MM="#A6D853",
    NL="#D4B9DA",
    OB="#AEB0B8",
    SG="#CCCCCC",
    TH="#EAE5D9",
    UN="#C29A84",
)