import pandas as pd
import dash
import json
from dash import Dash, dcc, html, Input, Output, State
import plotly.express as px
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
####  Importações de bases de dados  ####

#GeoJson (Fonte IBGE)
geojson = json.load(open('geoJson.json'))


#Base De Dados (Com resumo por municipio)
df = pd.read_csv("Resumo.csv", sep=";")


# Div Dashboard
app = Dash(__name__,external_stylesheets=[dbc.themes.SIMPLEX, dbc.icons.BOOTSTRAP])

server = app.server
app.title = 'Morb-19'

# TO MANIFEST
app.index_string = '''<!DOCTYPE html>
<html>
<head>
<title>MorbCOVID-19</title>
<link rel="manifest" href="./assets/manifest.json" />
{%metas%}
{%favicon%}
{%css%}
</head>
<script type="module">
   import 'https://cdn.jsdelivr.net/npm/@pwabuilder/pwaupdate';
   const el = document.createElement('pwa-update');
   document.body.appendChild(el);
</script>
<body>
<script>
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', ()=> {
      navigator
      .serviceWorker
      .register('./assets/sw01.js')
      .then(()=>console.log("Ready."))
      .catch(()=>console.log("Err..."));
    });
  }
</script>
{%app_entry%}
<footer>
{%config%}
{%scripts%}
{%renderer%}
</footer>
</body>
</html>
'''

logo = dbc.Row(
            [dbc.Col(html.Img(src="assets\logo.png", height="100px")),dbc.Col(dbc.NavbarBrand("MorbCOVID-19", className="ms-2"))],style={"justify-content":"center"})
# Layout
app.layout = html.Div([
    #HeadBar
    dbc.NavbarSimple([
    #Logo    
        
    #Filtros
    
    #Radio
    dbc.RadioItems(
        id='offcanvas-placement-selector',
        options = [
                {"label": "Morbidade", "value": "Morbidade"},
                {"label": "Confirmados", "value": "Confirmados"},
                {"label": "Recuperados", "value":"Recuperados"},
                {"label": "Óbitos", "value":"Obitos"}], value="Morbidade",
            style={"justify-items":"center","margin-left":"2%","font-size":"16px","display":"flex","gap":"1rem"}
        ),
    
    #botoes
    html.Div([
    dbc.Button("Limpar", color="primary", id="location-button", size='sm', style={"margin-left":"2%","height":"50%","align-self":"center"},className="btn btn-dark"),],
    style={"margin-left":"2%","height":"50%","align-self":"center","display":"flex"})
       
    
    ],brand="MorbCOVID-19"),   
   
    # Cards
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Pernambuco",id="loca",className="card-header"),
                    html.H6("Casos Recuperados",className="card-title", style={"padding-top":"2%"}),
                    html.P(df["Recuperados"].sum(),id="casos-recuperados",className="card-text",style={"color":"#4bbf73"})
                ])
            ],outline=True,style={"margin":"10px","text-align":"center"}, className="card text-white bg-dark mb-3")
        ], md=4),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Pernambuco",id="loca2",className="card-header"),
                    html.H6("Casos Confirmados",className="card-title", style={"padding-top":"2%"}),
                    html.P( df["Confirmados"].sum(),id="casos-confirmados",className="card-text",style={"color":"#d9534f"})
                ])
            ],outline=True,style={"margin":"10px","text-align":"center"}, className="card text-white bg-dark mb-3")
        ], md=4),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Pernambuco",id="loca3",className="card-header"),
                    html.H6("Casos de Óbitos",className="card-title", style={"padding-top":"2%"}),
                    html.P( df["Obitos"].sum(),id="obitos",className="card-text",style={"color":"#fcfcfc"})
                ])
            ],outline=True,style={"margin":"10px","text-align":"center"}, className="card text-white bg-dark mb-3")
        ], md=4)
        
    ],style={"display":"flex"}),
   
   #Graficos
    html.Div([ 
        html.Div([html.H5("Mapa por índice de morbidade",id='titulo-1'),
        html.I(className="bi bi-question-circle-fill",id='info'),
        dbc.Tooltip("Índice de Morbidade: Relação entre o número de indivíduos contaminados com a COVID-19 em uma região e o número total da população dessa região.",target="info")
        ],style={"display":"flex"}),
        dcc.Graph(id="graph",style={"margin-top":"2%"},config= dict(displayModeBar = False))
    ]),
    html.Div([
        html.Div([html.H5("7 Maiores cidades por índice de morbidade",id='titulo-2'),
        html.I(className="bi bi-question-circle-fill",id='info2'),
        dbc.Tooltip("Índice de Morbidade: Relação entre o número de indivíduos contaminados com a COVID-19 em uma região e o número total da população dessa região.",target="info2")
        ],style={"display":"flex"}),
        dcc.Graph(id="top", config={ 'responsive': True,'displayModeBar': False,"staticPlot":True})
    ],style={"margin-top":"5%"}),

    
    
], id="geral",style={"padding-right":"3%","padding-left":"3%"})





# MAP function with the choice filter
@app.callback(
    Output("graph", "figure"),
    [Input("offcanvas-placement-selector", "value")])
def display_choropleth(categoria): 
    df = pd.read_csv("Resumo.csv", sep=";")

    # condição para definir o tema
    if categoria == 'Morbidade':
        tema = 'sunsetdark'
    elif categoria == 'Obitos':
        tema = "#d6d6d5",'#484848','#020202'
    elif categoria == 'Recuperados':
        tema = 'darkmint'
    else: tema = "#fcc2aa","#f14230","#67000d"
    
    fig = px.choropleth_mapbox(df, geojson=geojson, color=categoria,locations="codarea", featureidkey="properties.codarea",color_continuous_scale=tema,
                               center={"lat":  -8.27519, "lon": -38.0376},mapbox_style="carto-positron", zoom=5,
                                 hover_data={"Municipio":True,"codarea":False, "Morbidade":True, "Confirmados":True,"Recuperados":True,"Obitos":True})


    fig.update_layout(plot_bgcolor="rgba(0, 0, 0, 0)",paper_bgcolor="rgba(0, 0, 0, 0)",
        margin={"r":0,"t":0,"l":0,"b":0},
        autosize=True,
        coloraxis_colorbar_x=-0.15
        )
    return fig

# graph Bar top 7
@app.callback(
Output("top","figure"),
[Input("offcanvas-placement-selector", "value")])
def top_gra(categoria):

    base_ano = pd.read_csv("Resumo.csv", sep=";")

     # condição para definir o tema
    if categoria == 'Morbidade':
        tema = "#e24c70"
    elif categoria == 'Obitos':
        tema = "#020202"
    elif categoria == 'Recuperados':
        tema = "#123f5a"
    else: tema = "#67000d"
    
    #top 7
    top7 = df.nlargest(n=7, columns=['{}'.format(categoria)])
    
    fig = go.Figure([go.Bar(x=top7['Municipio'], y=top7['{}'.format(categoria)], text=top7['{}'.format(categoria)],textposition='auto')])
    
    fig.update_layout(margin=dict(l=10, r=10, t=30, b=10),autosize=True, plot_bgcolor="rgba(0, 0, 0, 0)",paper_bgcolor="rgba(0, 0, 0, 0)")
    fig.update_traces(marker_color=tema)
    return fig

#Click
@app.callback(
    Output("loca", "children"),
    Output("loca2", "children"),
    Output("loca3", "children"),
    Output("casos-recuperados", "children"),
    Output("casos-confirmados", "children"),
    Output("obitos", "children"),
    [Input("graph", "clickData"), Input("location-button", "n_clicks")]
)
def update_location(click_data, n_clicks):
    #Muda a base de dados de acordo com o filtro
    df = pd.read_csv("Resumo.csv", sep=";")

    df.reset_index
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if click_data is not None and changed_id != "location-button.n_clicks":
        state = click_data["points"][0]["location"]
        casos_recuperados = "{}".format(df.query("codarea == {}".format(state))['Recuperados'].sum())   
        casos_confirmados = "{}".format(df.query("codarea == {}".format(state))['Confirmados'].sum())   
        obitos = "{}".format(df.query("codarea == {}".format(state))['Obitos'].sum())
        loca = "{}".format((df.query("codarea == {}".format(state))['Municipio'].to_string(index=False)))
        loca2 = "{}".format((df.query("codarea == {}".format(state))['Municipio'].to_string(index=False)))
        loca3 = "{}".format((df.query("codarea == {}".format(state))['Municipio'].to_string(index=False)))
    else:
        casos_recuperados = "{}".format(df["Recuperados"].sum())
        casos_confirmados = "{}".format(df["Confirmados"].sum())
        obitos = "{}".format(df["Obitos"].sum())
        loca = "Pernambuco"
        loca2 = "Pernambuco"
        loca3 = "Pernambuco"

    return (loca,loca2,loca3,casos_recuperados,casos_confirmados,obitos)

# Mudar titulos
@app.callback(
Output("titulo-1","children"),
Output("titulo-2","children"),
Output("info",component_property='hidden'),
Output("info2",component_property='hidden'),
[Input("offcanvas-placement-selector", "value")])
def muda_titulos(categoria):
    if categoria == 'Morbidade':
        titulo_1 = '{}'.format('Mapa por índice de morbidade/COVID-19')
        titulo_2 = '{}'.format('7 cidades com maior índice de morbidade/COVID-19')
        show = False
        show2 = False
    elif categoria == 'Confirmados':
        titulo_1 = '{}'.format('Mapa por número de casos confirmados')
        titulo_2 = '{}'.format('7 cidades com mais casos confirmados')
        show = True
        show2 = True
    elif categoria == 'Obitos':
        titulo_1 = '{}'.format('Mapa por número de óbitos')
        titulo_2 = '{}'.format('7 cidades com maior número de óbitos')
        show = True
        show2 = True
    else:
        titulo_1 = '{}'.format('Mapa por número de pessoas Recuperadas')
        titulo_2 = '{}'.format('7 cidades com maior número de Recuperados')
        show = True
        show2 = True
    
    return (
        titulo_1,
        titulo_2,
        show,
        show2
    )



# Run Aplication
if __name__ == '__main__':
    app.run_server(debug=True)
