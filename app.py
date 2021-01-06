# -*- coding: utf-8 -*-
# %% Imports
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import knmi
# import json
# import numpy as np
# import plotly
# from plotly import graph_objs as go
# from datetime import datetime as dt

from textfiles import text_dict # selfmade python file with all the textboxes

# %%

# %% [markdown]
# ### 0. Initialize

# %% Colors
## instigate the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.YETI])
server = app.server

## Make a hex colors database
colors = {
    'blue': '#003E5C',  
    'medium_blue': '#005984',
    'light_blue': '#90ADBF',
    'very_light_blue': '#CAD8E0',
    'dark_orange': '#FF7619',
    'light_orange': '#FFB27D',
    'white': '#ffffff',
    'black': '#000000',
    'stoplight_red': '#D64138',
    'stoplight_yellow': '#FFC000',
    'stoplight_blue': '#133244'
}

## constants
month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 
               'November', 'December']


# %% [markdown]
# ### 1.1 Read data

# %% Data input
## Read data sets
url_GFT_aanbod = 'https://raw.githubusercontent.com/jelledijkema/wormhotel-california/master/Data/GFT_aanbod.csv'
df_GFT_aanbod = pd.read_csv(url_GFT_aanbod,sep=",", encoding='unicode_escape', header=0)
#df_GFT_aanbod = pd.read_csv('./data/GFT_aanbod.csv',sep=',', encoding='unicode_escape', header=0)

url_Environment = 'https://raw.githubusercontent.com/jelledijkema/wormhotel-california/master/Data/Environment_wormhotel.csv'
df_environment = pd.read_csv(url_Environment,sep=",", encoding='unicode_escape', header=0)
#df_environment = pd.read_csv('./data/Environment_wormhotel.csv',sep=',', encoding='unicode_escape', header=0)

## Read textfiles that are on display
welcome_text = text_dict['welcome_text']
test = text_dict['test']
wormbin_measurements_text = text_dict['wormbin_measurements']

# %% [markdown]
# ### 1.2 Set variables

# %%
## Get string of Today
now = datetime.now().strftime('%Y%m%d')


# %%
# ideeen:
# 1. hoeveel gewicht GFT geef je aan je wormen?
    # of:  hoe snel gaat het composteren?
    
# 2. wat zijn de effecten van vocht, temperatuur, zuurgraad op compostering?
    # KNMI weerstation data --> temperatuur meting
    # Raspberry Pi / ander apparaat bodem metingen

# 3.  de "opstartfase", wanneer is die geeindigd? --> ongeveer na eerste oogst pis

# 4. Wat is de conversie van gewicht GFT --> liter wormenpis, gewicht compost

# %% [markdown]
# ### 1.3 Transform data

# %%
def add_date_elements_to_df(df, time_element=False):

    for i,date in df.iterrows():

        # make datetime object from date
        if time_element is True:
            ndate = datetime.strptime(date['Datum'], '%d/%m/%Y %H:%M')
        else:
            ndate = datetime.strptime(date['Datum'], '%d/%m/%Y')

        # assign different time elements to columns
        df.at[i,'Week'] = datetime.strftime(ndate,'%W')
        df.at[i,'Month'] = datetime.strftime(ndate,'%B')
        df.at[i,'Year'] = int(datetime.strftime(ndate,'%Y'))
        
        if time_element is True:
            df.at[i,'Time'] = datetime.strftime(ndate,'%H:%M')
        
        df.at[i,'Date'] = ndate
        
    return (df)


# %%
## Add columns to the date time dataframe
df_GFT_aanbod = add_date_elements_to_df(df_GFT_aanbod)
df_environment = add_date_elements_to_df(df_environment, time_element=True)

# %% [markdown]
# ### 1.4 Make (static) figures of the data

# %%
# parameters
nu = datetime.now().strftime('%Y%m%d')
nu_environment = datetime.now().strftime('%Y-%m-%d')

# %% [markdown]
# #### 1.4.1 Self measurements

# %%
## Organic matter (aanbod)
fig_organic_matter_scatter = px.scatter(df_GFT_aanbod, x="Date", y="Gewicht (g)") 

## Environmental measurements
fig_temperature_in_compost_scatter = px.scatter(df_environment, x="Date", y="Temperature (Celsius)") 

fig_temperature_in_compost_scatter = fig_temperature_in_compost_scatter.update_xaxes(
                                        range=["2020-04-16", nu_environment])
fig_temperature_in_compost_scatter = fig_temperature_in_compost_scatter.update_yaxes(
                                        range=[0, 30])
fig_temperature_in_compost_scatter = fig_temperature_in_compost_scatter.update_layout(
                                        title=dict(text="Compost temperature inside wormhotel",
                                                   font=dict(size=26))
                                        )

# %% [markdown]
# #### 1.4.2 External sources

# %%
## Get string of Today
nu = datetime.now().strftime('%Y%m%d')

## Get temeprature data from KNMI weatherstation Schiphol from start of experiment until now
df_KNMI = df = knmi.get_day_data_dataframe(stations=[240], start='20200416', end=nu, variables=['TG'])

## TG = 'Daily mean temperature in (0.1 degrees Celsius)'
df_KNMI['Temperature']=df_KNMI['TG']/10

## Make graph
fig_KNMI_average_temp = px.line(df_KNMI, x=df_KNMI.index, y="Temperature",title="Average temperature in Amsterdam")

## Update graph
fig_KNMI_average_temp.update_xaxes(title='Date')
fig_KNMI_average_temp.update_yaxes(title='Temperature (Celsius)')
fig_KNMI_average_temp.update_layout(title=dict(font=dict(size=26)))

# %%

# %% [markdown]
# ### 2. Create interface

# %% Dashboard app layout
app.layout = html.Div(style={}, children=[

#     # Header box
#     html.Div(style={'display': 'flex',
#                     'backgroundColor': colors['blue'],
#                     'width': '100%'}, children=[
#         html.Div(children=[
#              # textbox on left side of header
#              html.H1(
#                  children='i2i - Production Dashboard',
#                  style={
#                      'textAlign': 'left',
#                      'color': colors['white'],
#                      # 'backgroundColor': colors['light_blue'],
#                      'display': 'flex',
#                      'width' : '200%',
#                      'margin-left':'3%',
#                      'margin-top':'0%',
#                      'font-size':'400%'
#                  }
#              )
#              ])
#     ]),

    # Titel textbox
    html.H1(
        children='Welcome',
        style={'color': colors['blue'],
               'backgroundColor':colors['white'],
               'width':'100%',
               'margin-left':'5%',
               'margin-top':'3%'
               }
    ),
    
    ## Textbox
    html.Div(
    dcc.Textarea(
        id='textarea-example',
        value=welcome_text,
        style={'fontSize':24,
               'textAlign': 'left',
               'margin-left':'5%',
               'width': '90%',
               'height': 420,
               'overflow':'hidden', ## no scroll
               'resize':'none', ## no resizeing option
               'border':'none' ## no border
              }
        )
    ),
        

    # Tabs
    html.Div([
        dcc.Tabs(id='tabs-main',
                 value='tab-1',
                 style={'margin-left': '5%', 'margin-right': '5%'},
                 children=[
                     dcc.Tab(
                         label='Set-up',
                         children=[
#                                     stuff
                         ])
                     
                     ,
                     dcc.Tab(
                         label='Organic matter',
                         children=[
#                              html.Div(children=[
#                                  html.H3(children='Select year and month number:',
#                                          style={'margin-left': '5%'}
#                                          )
# #                                  ,
# #                                  html.Div(dcc.Dropdown(
# #                                      id='alg_jaar_dropdown',
# #                                      options=[{'label': i, 'value': i}
# #                                               for i in jaar_opties],
# #                                      value='Choose a year first.',
# #                                      style={'margin-left': '5%',
# #                                             'margin-right': '70%'}
# #                                  )),
# #                                  html.Div(dcc.Dropdown(
# #                                      id='alg_maand_dropdown',
# #                                      options=[{'label': i, 'value': i}
# #                                               for i in maand_opties],
# #                                      value='Choose month first.',
# #                                      style={'margin-left': '5%',
# #                                             'margin-right': '70%'}
# #                                  ))
#                                  ])
#                              ,
                             dcc.Graph(id='GFT_aanbod_scatter'
#                                      ,style={'display': 'inline-block',
#                                                  'width': '49%',
#                                                  'height': '420%'}
                                       ,figure = fig_organic_matter_scatter
                                         )
                             ,
                             dcc.Graph(id='GFT_aanbod_custom'
#                                           ,style={'display': 'inline-block',
#                                                  'width': '49%',
#                                                  'height': '420%'}
                                      )
                             ,
                             dcc.RadioItems(id='GFT_aanbod_radio'
                                    ,options=[
                                        {'label': 'Week', 'value': 'Week'}
                                        ,{'label': 'Month', 'value': 'Month'}
#                                         ,{'label': 'Year', 'value': 'Year'}
                                            ]
                                    ,value='Month'
                                    ,style={'display': 'inline-block',
                                            'margin-left': '5%',
                                            'fontSize':20}
                             )
#                              ,
#                              dcc.Graph(id='waterfall_factor_graph_alg',
#                                       style={'display': 'inline-block',
#                                                  'width': '49%',
#                                                  'height': '420%'}
#                                       ),
#                              html.H3(children='Stuwmeer (verwacht-gerealiseerd):',
#                                      style={'margin-left': '5%'}
#                                      ),
#                              dcc.Graph(id='omzet_graph_alg',
#                                           style={'margin-left': '5%', 'margin-right': '10%'}),
#                              html.Div(children=[
#                                  html.H3(children='Input values:',
#                                          ),
#                                  dcc.Input(id="input1",
#                                               type="text",
#                                               placeholder="factor 1"
#                                            ),
#                                  dcc.Input(id="input2",
#                                               type="text",
#                                               placeholder="factor 2",
#                                               debounce=True
#                                            )],
#                                       style={'margin-left': '5%'}
#                                       )
                         ])
                     ,
                     dcc.Tab(
                         label='Climate',
                         children=[
                             dcc.Textarea(id='wormbin_measurement_intro',
                                          value=wormbin_measurements_text,
                                          style={'fontSize':24,
                                               'textAlign': 'left',
                                               'margin-left':'5%',
                                               'width': '90%',
                                               'height': 250,
                                               'overflow':'hidden', ## no scroll
                                               'resize':'none', ## no resizeing option
                                               'border':'none' ## no border
                                              }
                                    )
                             ,dcc.Graph(id='KNMI_temperature_line'
                                     ,style={'display': 'inline-block',
                                                 'width': '49%',
                                                 'height': '420%'}
                                         
                                     ,figure = fig_KNMI_average_temp
                                    )
                             ,dcc.Graph(id='Compost_temperature_line'
                                       ,style={'display': 'inline-block',
                                                 'width': '49%',
                                                 'height': '420%'}
                                       ,figure = fig_temperature_in_compost_scatter
                                       )
                         ])
                     ,
                     dcc.Tab(
                         label='Benefits',
                         children=[
#                              html.H3(children='Choose Specialism:',
#                                      style={'margin-left': '5%', 'margin-right': '70%'})
#                              ,
#                              html.Div(dcc.Dropdown(
#                                  id='specialisatie_dropdown',
#                                  options=[{'label': i, 'value': i}
#                                           for i in specialisatie_opties],
#                                  value='Choose a specialisation first.',
#                                  style={'margin-left': '5%',
#                                         'margin-right': '70%'}
#                              )),
#                              dcc.Graph(id='waterfall_graph_spec',
#                                           style={'display': 'inline-block',
#                                                  'width': '49%',
#                                                  'height': '420%'},
#                                           figure=fig),
#                              dcc.Graph(id='waterfall_factor_graph_spec',
#                                       style={'display': 'inline-block',
#                                                  'width': '49%',
#                                                  'height': '420%'}
#                                       ),
#                              html.H3(children='Trendlines',
#                                      style={'margin-left': '5%', 'margin-right': '70%'}),
#                              dcc.Graph(id='omzet_graph_spec',
#                                           style={'margin-left': '5%', 'margin-right': '10%'}),
#                              html.H3(children='Reservoir',
#                                      style={'margin-left': '5%', 'margin-right': '70%'}),
                         ])
                     
                 ]),
    ])

])

# %% Callback algemeen
## Callback
@app.callback(
    Output('GFT_aanbod_custom', 'figure')
    ,[
    Input('GFT_aanbod_radio', 'value')
    ]
)


def update_figure(GFT_aanbod_radio):
    '''explanation graph'''
    
    if GFT_aanbod_radio == 'Month':
        df_GFT_aanbod_custom = df_GFT_aanbod.groupby(['Month']).sum().reindex(month_order, axis=0)
    else:
        df_GFT_aanbod_custom = df_GFT_aanbod.groupby([GFT_aanbod_radio]).sum()
    
    fig = px.bar(df_GFT_aanbod_custom, x=df_GFT_aanbod_custom.index, y="Gewicht (g)") 
    fig.update_layout(xaxis_type='category')
    fig.update_xaxes(title=GFT_aanbod_radio)
    
    return fig



# ## Graph hover factoren
# @app.callback(
#     Output('waterfall_factor_graph_alg', 'figure'),
#     [Input('waterfall_graph_alg', 'hoverData'),
#      Input('alg_jaar_dropdown', 'value'),
#      Input('alg_maand_dropdown', 'value')])


# def update_factoren_graph(hoverData, jaar, maand):
#     '''
#     When hovering over the waterfall graph the factoren graph shows a more detailed breakdown of the urgency categories
#     into several factors. The graph automatically updates
#     '''
#     # In the beginning there is no year and month selected, so default values are set
#     try:
#         urgency_code = hoverData['points'][0]['x'] #The x in the waterfall is the urgency category used for filtering
#         jaar = int(jaar)
#         maand = int(maand)
#     except:
#         urgency_code = 'A'
#         jaar = 2019
#         maand = 1

#     # update graph based on input
#     dff = df_factoren[df_factoren['jaar_analyse'] == jaar]
#     dff = dff[dff['maand_nr_analyse'] == maand]
#     dff = dff[dff['urgentie_code'] == urgency_code]
    
#     return create_time_series_factoren(dff, urgency_code)
    


# ## Graph of the trendlines for entire hospital
# @app.callback(
#     Output('omzet_graph_alg', 'figure'),
#     [Input('specialisatie_dropdown', 'value')])

# def update_figure_expected_realized_revenue(selected_spec):
#     ''' Trendlines
#     '''
#     dff = df_omzet_agb
#     x_value = 'maand_nr'
#     y_value = 'verschil_omzet_agb'
#     y2_value = 'verschil_omzet_peergroup'
#     return {
#         'data': [
#             dict(
#                 x=dff[x_value].unique(),
#                 y=dff.groupby([x_value]).sum()[y_value].cumsum(),
#                 name=y_value,
#                 text=selected_spec,
#                 mode='lines',
#                 marker={
#                     'size': 15,
#                     'opacity': 0.5,
#                     'line': {'width': 0.5, 'color': 'white'}
#                 }
#             ),
#             dict(
#                 x=dff[x_value].unique(),
#                 y=dff.groupby([x_value]).sum()[y2_value].cumsum(),
#                 name=y2_value,
#                 text=selected_spec,
#                 mode='lines',
#                 marker={
#                     'size': 15,
#                     'opacity': 0.5,
#                     'line': {'width': 0.5, 'color': 'white'}
#                 }
#             )
#         ],
#         'layout': dict(
#             xaxis={
#                 'title': x_value,
#             },
#             yaxis={
#                 'title': 'euro',
#             }
#         )
#     }


# This part is here so you can run the Python script from the Prompt
if __name__ == '__main__':
    app.run_server(debug=True)
