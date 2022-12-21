import requests
import pandas as pd
from urllib.request import urlopen
import json
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc

####  Importações de bases de dados  ####

#GeoJson (Fonte IBGE)
response = requests.get(url='https://servicodados.ibge.gov.br/api/v3/malhas/estados/26?formato=application/vnd.geo+json&qualidade=maxima&intrarregiao=municipio')    
if response.status_code == 200:
    geojson = response.json()

#Base De Dados (Com resumo por municipio)
df = pd.read_csv('RESUMO.CSV',sep=';')

# Div Dashboard
app = Dash(__name__,external_stylesheets=[dbc.themes.LUX])

app.layout = html.Div([
    #Head
    dbc.NavbarSimple([
    
    dbc.RadioItems(
        className="btn-group",
        inputClassName="btn-check",
        labelClassName="btn btn-outline-primary",
        labelCheckedClassName="active",
        id='offcanvas-placement-selector',
        options = [
                {"label": "Morbidade", "value": "Morbidade"},
                {"label": "Confirmados", "value": "Confirmados"},
                {"label": "Recuperados", "value":"Recuperados"},
                {"label": "Obitos", "value":"Obitos"}], value="Morbidade",
        )
    ],brand='Estatisticas de Covid'),
    
    # Cards
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Casos Recuperados",className="card-title"),
                    html.P(df["Recuperados"].sum(),id="casos-recuperados",className="card-text")
                ])
            ],outline=True,style={"margin":"10px","text-align":"center"})
        ], md=4),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Casos Confirmados",className="card-title"),
                    html.P( df["Confirmados"].sum(),id="casos-confirmados",className="card-text")
                ])
            ],outline=True,style={"margin":"10px","text-align":"center"})
        ], md=4),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Casos de Óbito",className="card-title"),
                    html.P( df["Obitos"].sum(),id="obitos",className="card-text")
                ])
            ],outline=True,style={"margin":"10px","text-align":"center"})
        ], md=4)
        
    ]),
   
   #Graficos
    html.Div([ 
        dcc.Graph(id="graph",style={"margin-top":"2%"}),
        dcc.Graph(id="top",style={"margin-top":"2%"})
    ])
    
], style={"padding-right":"3%","padding-left":"3%"})



# MAP function with the choice filter
@app.callback(
    Output("graph", "figure"),
    Input("offcanvas-placement-selector", "value"))
def display_choropleth(categoria):    
    #Grafico Do Mapa
    
    # condição para definir o tema
    if categoria == 'Morbidade':
        tema = 'sunsetdark'
    elif categoria == 'Obitos':
        tema = 'dense'
    elif categoria == 'Recuperados':
        tema = 'darkmint'
    else: tema = 'greys'
    
    fig = px.choropleth_mapbox(df, geojson=geojson, color=categoria,locations="codarea", featureidkey="properties.codarea",color_continuous_scale=tema,
                            center={"lat":  -8.27519, "lon": -38.0376},mapbox_style="carto-positron", zoom=6.6,title="Mapa Taxa de {}".format(categoria),
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
    #top 10
    top10 = df.nlargest(n=6, columns=['{}'.format(categoria)])
    fig = px.bar(df, x=top10['Municipio'],
                     y=top10['{}'.format(categoria)],
                     color=top10['Municipio'], title='6 Cidades com maior {}'.format(categoria))
    fig.update_layout(
    margin=dict(l=10, r=10, t=30, b=10)
)
    return fig

#Click




      
      
# Run Aplication
app.run_server(debug=True)