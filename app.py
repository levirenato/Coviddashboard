import pandas as pd
import dash
import json
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc

####  Importações de bases de dados  ####

#GeoJson (Fonte IBGE)
geojson = json.load(open('geoJson.json'))
#Base De Dados (Com resumo por municipio)
df = pd.read_csv('RESUMO.csv',sep=';',index_col=False)

# Div Dashboard
app = Dash(__name__,external_stylesheets=[dbc.themes.SIMPLEX])

server = app.server
app.title = 'Morb-19'

# TO MANIFEST
app.index_string = '''<!DOCTYPE html>
<html>
<head>
<title>.</title>
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


# Layout
app.layout = html.Div([
    #Head
    dbc.NavbarSimple([
    dbc.RadioItems(
        id='offcanvas-placement-selector',
        options = [
                {"label": "Morbidade", "value": "Morbidade"},
                {"label": "Confirmados", "value": "Confirmados"},
                {"label": "Recuperados", "value":"Recuperados"},
                {"label": "Obitos", "value":"Obitos"}], value="Morbidade",
        style={"align-self":"center"}
        ),
    dbc.Button("Limpar", color="primary", id="location-button", size='sm', style={"margin-left":"2%"},className="btn btn-dark")
    ],brand='Estatisticas de Covid'),   
   
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
                    html.H6("Casos de Óbito",className="card-title", style={"padding-top":"2%"}),
                    html.P( df["Obitos"].sum(),id="obitos",className="card-text",style={"color":"#fcfcfc"})
                ])
            ],outline=True,style={"margin":"10px","text-align":"center"}, className="card text-white bg-dark mb-3")
        ], md=4)
        
    ],style={"display":"flex"}),
   
   #Graficos
    html.Div([ 
        dcc.Graph(id="graph",style={"margin-top":"2%"},config= dict(displayModeBar = False))
    ]),
    html.Div([
        dcc.Graph(id="top", config={ 'responsive': True,'displayModeBar': False})
    ],style={"margin-top":"5%"})
    
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
        tema = "#d6d6d5",'#484848','#020202'
    elif categoria == 'Recuperados':
        tema = 'darkmint'
    else: tema = "#fcc2aa","#f14230","#67000d"
    
    fig = px.choropleth_mapbox(df, geojson=geojson, color=categoria,locations="codarea", featureidkey="properties.codarea",color_continuous_scale=tema,
                               center={"lat":  -8.27519, "lon": -38.0376},mapbox_style="carto-positron", zoom=5,title="Mapa Taxa de {}".format(categoria),
                                 hover_data={"Municipio":True,"codarea":False, "Morbidade":True, "Confirmados":True,"Recuperados":True,"Obitos":True})


    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        autosize=True,
        coloraxis_colorbar_x=-0.15
        )
    return fig

# graph Bar top 10
@app.callback(
Output("top","figure"),
Input("offcanvas-placement-selector", "value"))
def top_gra(categoria):  
     # condição para definir o tema
    if categoria == 'Morbidade':
        tema = "#e24c70"
    elif categoria == 'Obitos':
        tema = "#020202"
    elif categoria == 'Recuperados':
        tema = "#123f5a"
    else: tema = "#67000d"
    
    #top 10
    top10 = df.nlargest(n=6, columns=['{}'.format(categoria)])
    fig = px.bar(df, x=top10['Municipio'],text_auto=True,
                     y=top10['{}'.format(categoria)],
                     title='6 Cidades com maior {}'.format(categoria))
    
    fig.update_layout(margin=dict(l=10, r=10, t=30, b=10),autosize=True, plot_bgcolor="rgba(0, 0, 0, 0)",paper_bgcolor="rgba(0, 0, 0, 0)",
                      )
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



# Run Aplication
if __name__ == '__main__':
    app.run_server(debug=True)
