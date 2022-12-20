import requests
import pandas as pd
from urllib.request import urlopen
import json
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc

# Div Dashboard
app = Dash(external_stylesheets=[dbc.themes.CYBORG])

app.layout = html.Div([
    html.H3('Estatisticas de Covid', style={"font-famiy":"'Source Sans Pro', 'sans-serif'",
                                            "text-align": "center",
                                            "background-color":"#2780e3",
                                            "color":"white",
                                            "margin-top":"0px"}),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Span("Casos Recuperados",className="card-text"),
                    html.H3(style={"color":"#e7e9eb"}, id="casos-recuperados")
                ])
            ],color='#555555',outline=True,style={"margin":"10px"})
        ], md=4),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Span("Casos Confirmados",className="card-text"),
                    html.H3(style={"color":"#e7e9eb"}, id="casos-confirmados")
                ])
            ],color='#555555',outline=True,style={"margin":"10px"})
        ], md=4),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Span("Casos de Óbito",className="card-text"),
                    html.H3(style={"color":"#e7e9eb"}, id="obito")
                ])
            ],color='#555555',outline=True,style={"margin":"10px"})
        ], md=4)
        
    ]),
    html.P("Selecione uma Categoria:"),
    html.Div(
    [dcc.RadioItems(
        id='offcanvas-placement-selector', 
        options=["Morbidade","Confirmados", "Recuperados", "Obitos"],
        value="Morbidade",
        inline=True,
        
    )],style={"margin-rigth":"5%"}
    ,className="mb-2"),
    dcc.Graph(id="graph"),
    dcc.Graph(id="top"),
    
    
])

# Interactivity
@app.callback(
    [
        Output("casos-recuperados", "children"),
        Output("obito", "children"),
        Output("casos-confirmados", "children"),
    ], [Input("offcanvas-placement-selector", "value")])
def display_status(categoria):
    recuperados = f'{int(categoria["Recuperados"].sum):,}'.replace(",", ".") 
    confirmados = f'{int(categoria["Confirmados"].sum):,}'.replace(",", ".") 
    obitos = f'{int(categoria["Obitos"].sum):,}'.replace(",", ".")
    
    return(recuperados,confirmados,obitos)

# MAP function with the choice filter
@app.callback(
    Output("graph", "figure"),
    Input("offcanvas-placement-selector", "value"))
def display_choropleth(categoria):
    ####  Importações de bases de dados  ####

    #GeoJson (Fonte IBGE)
    response = requests.get(url='https://servicodados.ibge.gov.br/api/v3/malhas/estados/26?formato=application/vnd.geo+json&qualidade=maxima&intrarregiao=municipio')    
    if response.status_code == 200:
        geojson = response.json()

    #Base De Dados (Com resumo por municipio)
    df = pd.read_csv('RESUMO.CSV',sep=';')
    
    #Grafico Do Mapa
    
    # condição para definir o tema
    if categoria == 'Morbidade':
        tema = 'sunsetdark'
    elif categoria == 'Obitos':
        tema = 'dense'
    elif categoria == 'Recuperados':
        tema = 'darkmint'
    else: tema = 'greys'
    
    fig = px.choropleth_mapbox(df, geojson=geojson, color=categoria,
                            locations="codarea", featureidkey="properties.codarea",color_continuous_scale=tema,
                            center={"lat":  -8.27519, "lon": -38.0376},mapbox_style="carto-positron", zoom=7,
                            hover_data={"Municipio":True,"codarea":False, "Morbidade":True, "Confirmados":True,"Recuperados":True,"Obitos":True})


    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        autosize=True,showlegend=False
        )
    return fig

# graph Bar top 10
@app.callback(
Output("top","figure"),
Input("offcanvas-placement-selector", "value"))
def top_gra(categoria):
    ####  Importações de bases de dados  ####

    #GeoJson (Fonte IBGE)
    response = requests.get(url='https://servicodados.ibge.gov.br/api/v3/malhas/estados/26?formato=application/vnd.geo+json&qualidade=maxima&intrarregiao=municipio')    
    if response.status_code == 200:
        geojson = response.json()

    #Base De Dados (Com resumo por municipio)
    df = pd.read_csv('RESUMO.CSV',sep=';')
    
    #top 10
    top10 = df.nlargest(n=10, columns=['{}'.format(categoria)])
    fig = px.bar(df, x=top10['Municipio'],
                     y=top10['{}'.format(categoria)],
                     color=top10['Municipio'], title='10 Cidades com maior {}'.format(categoria))
    fig.update_layout(
    margin=dict(l=10, r=10, t=30, b=10)
)
    return fig
    
# Run Aplication
app.run_server(debug=True)