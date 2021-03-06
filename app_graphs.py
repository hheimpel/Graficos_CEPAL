import dash
import pandas as pd
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy

csv_files = ['tamano_hogar',
             'mujeres_labor_hogar_AG_quintiles',
             'tasa_de_participacion_economica',
             'tasa_de_participacion_economica_quintil',
             'relacion_ingreso_medio_sexo',
             'ocupados_informal_sexo',
             'gini',
             'poblacion_adulta_escolaridad',
             'hogares_disponibilidad_servicios',
             'tasa_victimizacion',
             'relacion_quintil_5_1',
             'asistencia_escolar_quintil',
             'acceso_electricidad_quintil']

data_frames = {name: pd.read_csv('{}.csv'.format(name)) for name in csv_files}
data_frame = data_frames['tamano_hogar']
pais_iso_df = data_frames['tasa_de_participacion_economica']
pais_iso = {pais : iso for pais,iso in zip(pais_iso_df['País'].unique(),pais_iso_df['iso3'].unique())}
pais_iso['América Latina (promedio ponderado)']='AL (pd)'
pais_iso['América Latina (promedio simple)']='AL (ps)'

# HTML Button styles
white_button = {'background-color': 'white',
                'color': 'black',
                'height': '50px',
                'width': '150px',
                'margin-top': '50px',
                'margin-left': '50px'}

red_button = {'background-color': 'red',
              'color': 'white',
              'height': '50px',
              'width': '150px',
              'margin-top': '50px',
              'margin-left': '50px'}

def time_series_quintil(data, country, area_g, indicador):
    df = data_frames[data]
    df["valor"] = df["valor"].astype(dtype='float64')
    varright = {"Tamaño medio del hogar": [": Tamaño hogar", "Tamaño hogar"],
                "Mujeres con dedicación al hogar": ["Mujeres \ Hogar: ", "Porcentaje"]}

    if area_g == 'Área geográfica':
        q = df[
            (df["País"] == country) &
            (df["Quintil"] == "Total quintiles")
            ]

        q["Años"] = q["Años"].astype(dtype='intc')

        lfig = px.line(q,
                       x="Años",
                       y='valor',
                       color='Área geográfica',
                       labels={'valor': varright[indicador][1]})

    else:
        q = df[
            (df["País"] == country) &
            (df["Área geográfica"] == "Nacional")
            ]

        q["Años"] = q["Años"].astype(dtype='intc')

        lfig = px.line(q,
                       x="Años",
                       y='valor',
                       color='Quintil',
                       labels={'valor': varright[indicador][1]})

    lfig.update_layout(title_text=country + " - " + indicador,
                       legend_title="Desagregación",
                       xaxis=dict(
                           tickmode='linear',
                           tick0=df["Años"].min(),
                           dtick=1
                       ))
    lfig.update_traces(mode='lines+markers')
    return lfig

def side_stacked_bars(data, country, dim):
    # Filter pandas data_frame
    data_frame = data_frames[data]
    filt_cty = data_frame[(data_frame['País'] == country)].copy(deep=True)
    filt_cty['Años'] = filt_cty['Años'].astype(dtype='intc')
    filt_cty['valor'] = filt_cty['valor'].astype(dtype='float64')

    # Get latest year of available data and filter by it
    l_year = filt_cty['Años'].max()
    aggregates = {'Área geográfica': 'Total (15 años y más)',
                  'Grupo edad para participación en la PEA': 'Nacional',
                  'Quintil': 'Nacional'}
    aggregates2 = {'Área geográfica': 'Grupo edad para participación en la PEA',
                   'Grupo edad para participación en la PEA': 'Área geográfica',
                   'Quintil': 'Área geográfica'}
    f_c_y = filt_cty[(filt_cty['Años'] == l_year) &
                     (filt_cty[aggregates2[dim]] == aggregates[dim])]

    xs = list(f_c_y[dim].unique())

    # Figure
    fig = px.bar(f_c_y,
                 x=dim,
                 y='valor',
                 color='Sexo',
                 labels={'valor': 'Porcentaje'})

    fig.update_layout(title_text=country + ' ' + str(l_year) + ' - Tasa de participación económica',
                      barmode='group',
                      yaxis=dict(
                          tickmode='array',
                          tickvals=[i * 10 for i in range(11)])
                      )
    fig.update_yaxes(range=(0, 100))

    return fig

def sort_pais_bar(data, year):
    # Select Data Frame
    data_frame = data_frames[data].copy(deep=True)
    data_frame['valor'] = data_frame['valor'].astype(dtype='float64')
    data_frame['País (ISO)'] = data_frame['País'].apply(lambda x: pais_iso[x])

    # Filter data
    filt_data = data_frame[(data_frame['Años'] == year) &
                           (data_frame['Área geográfica'] == 'Nacional') &
                           (data_frame['Escolaridad (EH)'] == 'Total')]

    filt_data.sort_values(by='valor', inplace=True)

    # Figure
    fig = px.bar(filt_data,
                 x='País (ISO)',
                 y='valor',
                 labels={'valor': 'Relación Ingreso (M/H)'})

    fig.update_layout(title_text=str(year) + ' - Relación del ingreso por sexo',
                      barmode='group',
                      yaxis=dict(
                          tickmode='array',
                          tickvals=[i * 10 for i in range(11)])
                      )

    fig.update_yaxes(range=(0, 100))

    return fig

def sort_gini(area,year):
    # Select Data Frame
    data_frame = data_frames['gini'].copy(deep=True)
    data_frame['valor'] = data_frame['valor'].astype(dtype='float64')
    data_frame['País (ISO)'] = data_frame['País'].apply(lambda x: pais_iso[x])

    # Filter data
    filt_data = data_frame[(data_frame['Años'] == year) &
                           (data_frame['Área geográfica'] == area)]

    filt_data.sort_values(by='valor', inplace=True)

    # Figure
    fig = px.bar(filt_data,
                 x='País (ISO)',
                 y='valor',
                 labels={'valor': 'Gini - '+str(year)})

    fig.update_layout(title_text=str(year) + ' - Gini',
                      barmode='group')

    return fig

def sidebside_bars(data, country, area):
    # Select Data Frame
    data_frame = data_frames[data].copy(deep=True)
    data_frame['valor'] = data_frame['valor'].astype(dtype='float64')
    data_frame['Años'] = data_frame['Años'].astype('str')
    data_frame['Años observados'] = data_frame['Años'].apply(lambda x: x + "-M/H")

    # Filter data
    years = ['2002', '2010', '2018']
    filt_data = data_frame[(data_frame['Años'].isin(years)) &
                           (data_frame['País'] == country) &
                           (data_frame['Área geográfica'] == area)]

    # Figure
    fig = px.bar(filt_data,
                 x='Escolaridad (EH)',
                 y='valor',
                 color='Años observados',
                 labels={'valor': 'Relación Ingreso (M/H)'})

    fig.update_layout(title_text=country + ' - Relación del ingreso por sexo',
                      barmode='group',
                      yaxis=dict(
                          tickmode='array',
                          tickvals=[i * 10 for i in range(11)])
                      )
    fig.update_yaxes(range=(0, 100))

    return fig

def stacked_bars(data, country):
    # Select Data Frame
    data_frame = data_frames[data].copy(deep=True)
    data_frame['valor'] = data_frame['valor'].astype(dtype='float64')
    data_frame['Años'] = data_frame['Años'].astype(dtype='intc')

    # Filter Data
    filt_data = data_frame[(data_frame['Ocupados baja productividad'] == 'Total ocupados baja productividad') &
                           (data_frame['País'] == country) &
                           (data_frame['Sexo'] != 'Ambos sexos')]

    # Figure
    fig = px.line(filt_data,
                  x='Años',
                  y='valor',
                  color='Sexo',
                  labels={'valor': 'Procentaje'})

    fig.update_layout(title_text=country)
    fig.update_layout(title_text=country + ' - Ocupados en baja productividad (informales)',
                      yaxis=dict(
                          tickmode='array',
                          tickvals=[i * 5 for i in range(21)]),
                      xaxis=dict(
                          tickmode='array',
                          tickvals=[i for i in range(filt_data['Años'].min(), filt_data['Años'].max() + 1)])
                      )
    fig.update_xaxes(tickangle=45)
    fig.update_traces(mode='lines+markers')
    return fig

def clean_gini(area):
    gini_df = data_frames['gini']
    gini_df['Años'] = gini_df['Años'].astype(dtype='intc')
    gini_df['valor'] = gini_df['valor'].astype(dtype='float64')
    gini_df['País (ISO)'] = gini_df['País'].apply(lambda x: pais_iso[x])

    gini_df = gini_df[(gini_df['Área geográfica'] == area)].sort_values(['País', 'Años'])

    mn_gini = gini_df[gini_df.groupby('País').cumcount() == 0].rename(columns={'valor': 'Gini - Inicial',
                                                                               'Años': 'Año - Inicial'})

    gini_df = gini_df[(gini_df['Área geográfica'] == area)].sort_values(['País', 'Años'], ascending=[True, False])

    mx_gini = gini_df[gini_df.groupby('País').cumcount() == 0].rename(columns={'valor': 'Gini - Final',
                                                                               'Años': 'Año - Final'})
    mx_gini['Gini - Inicial'] = list(mn_gini['Gini - Inicial'])
    mx_gini['Año - Inicial'] = list(mn_gini['Año - Inicial'])

    mx_gini['Desigualdad'] = numpy.where(mx_gini['Gini - Final'] >= mx_gini['Gini - Inicial'],
                                         'Incremento en Desigualdad',
                                         'Decremento en Desigualdad')
    return mx_gini

def gini(area):
    # FIGURE
    figure = px.scatter(clean_gini(area),
                        x='Gini - Inicial',
                        y='Gini - Final',
                        color='Desigualdad',
                        size='Gini - Inicial',
                        text='País (ISO)',
                        hover_data=['Año - Inicial', 'Año - Final'])
    figure.add_shape(type='line',
                     x0=.3,
                     y0=.3,
                     x1=.7,
                     y1=.7,
                     line=dict(color='Red',
                               width=.5),
                     xref='x',
                     yref='y')

    return figure

def bars_lines(country, year, xdim_b, group_b):
    # Filter Data
    def filters_data(country, year, filt):
        df = data_frames['asistencia_escolar_quintil']
        df = df[(df['País'] == country) &
                (df['Años'] == year) &
                (df[filt[0]] == filt[1]) &
                (df['Grandes grupos de edad'] == 'Total (7 a 24 años)')]
        return df
    if xdim_b == [white_button]*3 or group_b == [white_button]*3 or group_b==xdim_b:
        return {}
    if xdim_b == [red_button, white_button, white_button] and group_b == [white_button, red_button, white_button]:
        df = filters_data(country, year, ('Área geográfica', 'Nacional'))
        x = 'Sexo'
    elif xdim_b == [red_button, white_button, white_button] and group_b == [white_button, white_button, red_button]:
        df = filters_data(country, year, ('Quintil', 'Total quintiles'))
        x = 'Sexo'
    elif xdim_b == [white_button, red_button, white_button] and group_b == [red_button, white_button, white_button]:
        df = filters_data(country, year, ('Área geográfica', 'Nacional'))
        x = 'Quintil'
    elif xdim_b == [white_button, red_button, white_button] and group_b == [white_button, white_button, red_button]:
        df = filters_data(country, year, ('Sexo', 'Ambos sexos'))
        x = 'Quintil'
    elif xdim_b == [white_button, white_button, red_button] and group_b == [red_button, white_button, white_button]:
        df = filters_data(country, year, ('Quintil', 'Total quintiles'))
        x = 'Área geográfica'
    else:
        df = filters_data(country, year, ('Sexo', 'Ambos sexos'))
        x = 'Área geográfica'

    df['valor'] = df['valor'].astype(dtype='float64')

    # Group bars
    if group_b == [red_button, white_button, white_button]:
        group = 'Sexo'
    elif group_b == [white_button, red_button, white_button]:
        group = 'Quintil'
    else:
        group = 'Área geográfica'

    # FIGURE
    fig = px.bar(df,
                 x=x,
                 y='valor',
                 color=group,
                 labels={'valor': 'Procentaje'})
    fig.update_layout(title_text='{} {} - Asistencia Escolar'.format(country, year),
                      barmode='group',
                      yaxis=dict(
                          tickmode='array',
                          tickvals=[i * 10 for i in range(11)])
                      )
    fig.update_yaxes(range=(0, 100))
    return fig

def side_side_bars(data, country, year, title, x, color):
    # Select Data Frame
    data_frame = data_frames[data].copy(deep=True)
    data_frame['valor'] = data_frame['valor'].astype(dtype='float64')
    data_frame['Años'] = data_frame['Años'].astype(dtype='intc')

    # Filter data
    filt_data = data_frame[(data_frame['Años'] == year) &
                           (data_frame['País'] == country)]

    filt_data.sort_values('Quintil', inplace=True)

    # Figure
    fig = px.bar(filt_data,
                 x=x,
                 y='valor',
                 color=color,
                 labels={'valor': 'Porcentaje'})

    fig.update_layout(title_text="{} {} - {}".format(country, year, title),
                      barmode='group',
                      yaxis=dict(
                          tickmode='array',
                          tickvals=[i * 10 for i in range(11)])
                      )
    fig.update_yaxes(range=(0, 100))

    return fig

def points(data, year, initsort, sex_area, sa_dims):
    # Data frame
    df = data_frames[data].copy(deep=True)
    df['Años'] = df['Años'].astype(dtype='intc')
    df['valor'] = df['valor'].astype(dtype='float64')

    # Filter
    df_year = df[df['Años'] == year]

    # Sorting
    minyear = df['Años'].min()
    ys = list(df[(df['Años'] == minyear) &
                 (df[sex_area] == initsort)].sort_values(by=['valor'])['País'])
    ysort = {y: i for i, y in enumerate(ys)}
    counter = 0
    initlen = int(len(ysort))
    for elem in df_year['País'].unique():
        if elem not in ysort:
            ysort[elem] = initlen + counter
            ys.append(elem)
            counter += 1

    # Figure
    layout = go.Layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(
            showline=True,
            gridcolor='lightgrey',
            gridwidth=1,
            linecolor='black',
            linewidth=2
        ),
        xaxis=dict(
            showline=True,
            linecolor='black',
            linewidth=2
        )
    )

    fig = go.Figure(data=[
        go.Scatter(name='{} {}'.format(sa, year),
                   x=df[(df['Años'] == year) &
                        (df[sex_area] == sa)].sort_values(by=['País'],
                                                          axis=0,
                                                          key=lambda x: pd.Series([ysort[y] for y in x]))['valor'],
                   y=ys,
                   mode='markers',
                   marker=dict(size=8)
                   ) for sa in sa_dims],
        layout=layout
    )
    fig.update_xaxes(color='black')
    return fig

def time_series_mult_facet(data, countries, title, yleg):
    # Data frame
    df = data_frames[data].copy(deep=True)
    df['Años'] = df['Años'].astype(dtype='intc')
    df['valor'] = df['valor'].astype(dtype='float64')

    # Filter
    df_country = df[(df['País'].isin(countries)) &
                   (df['Sexo'].isin(['Hombres', 'Mujeres']))]


    # Figure
    fig = px.line(df_country,
                  x='Años',
                  y='valor',
                  color='País',
                  facet_col = 'Sexo',
                  labels={'valor': yleg})

    fig.update_layout(title_text=title)
    fig.update_xaxes(tickangle=45)
    fig.update_traces(mode='lines+markers')
    for i, elem in enumerate(fig.data):
        fig.data[i].name = pais_iso[fig.data[i].name]
    return fig

def time_series_mult(data, countries, area, title, yleg):
    # Data frame
    df = data_frames[data].copy(deep=True)
    df['Años'] = df['Años'].astype(dtype='intc')
    df['valor'] = df['valor'].astype(dtype='float64')

    # Filter
    try:
        df_country = df[(df['País'].isin(countries)) &
                        (df['Área geográfica'] == area)]
    except KeyError:
        df_country = df[(df['País'].isin(countries)) &
                        (df['Sexo'] == area)]

    # Figure
    fig = px.line(df_country,
                  x='Años',
                  y='valor',
                  color='País',
                  labels={'valor': yleg})

    fig.update_layout(title_text=title,
                      xaxis=dict(
                          tickmode='array',
                          tickvals=[i for i in range(df_country['Años'].min(), df_country['Años'].max() + 1)])
                      )
    fig.update_xaxes(tickangle=45)
    fig.update_traces(mode='lines+markers')
    for i, elem in enumerate(fig.data):
        fig.data[i].name = pais_iso[fig.data[i].name]
    return fig

# User input
desagregacion = ["Quintil", "Área geográfica"]
paises = list(data_frame['País'].unique())

# Desagregaciones
anios = sorted(list(map(int, data_frame['Años'].unique())))
anios_rim = sorted(list(map(int, data_frames['relacion_ingreso_medio_sexo']['Años'].unique())))
anios_gini = sorted(list(map(int, data_frames['gini']['Años'].unique())))
years = [2002, 2005, 2010, 2014, 2019]
quintiles = list(data_frame["Quintil"].unique())
area = list(data_frame["Área geográfica"].unique())

external_stylesheets = [dbc.themes.BOOTSTRAP]

# 2 Column layout
def two_column_layout(**kwargs):
    title = kwargs['title']
    title_graph1 = kwargs['title_graph1']
    title_graph2 = kwargs['title_graph2']
    id_dropdown1 = kwargs['id_dropdown1']
    dropdown_options1 = kwargs['dropdown_options1']
    dropdown_placeholder1 = kwargs['dropdown_placeholder1']
    id_dropdown2 = kwargs['id_dropdown2']
    dropdown_options2 = kwargs['dropdown_options2']
    dropdown_placeholder2 = kwargs['dropdown_placeholder2']
    id_dropdown3 = kwargs['id_dropdown3']
    dropdown_options3 = kwargs['dropdown_options3']
    dropdown_placeholder3 = kwargs['dropdown_placeholder3']
    id_graph1 = kwargs['id_graph1']
    id_graph2 = kwargs['id_graph2']

    return html.Div(children=[

        dbc.Row([
            html.H2(title)
        ],
            justify='center'
        ),

        dbc.Row([
            dbc.Col(html.H3(title_graph1), align='center'),
            dbc.Col(html.H3(title_graph2))
        ],
            justify='center', align='center'
        ),

        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id=id_dropdown1,
                    options=dropdown_options1,
                    placeholder=dropdown_placeholder1
                ),
                dcc.Dropdown(
                    id=id_dropdown2,
                    options=dropdown_options2,
                    placeholder=dropdown_placeholder2
                )
            ]),
            dbc.Col(
                dcc.Dropdown(
                    id=id_dropdown3,
                    options=dropdown_options3,
                    placeholder=dropdown_placeholder3
                )
            )
        ],
            justify='center'
        ),

        dbc.Row([
            dbc.Col(dcc.Graph(id=id_graph1)),
            dbc.Col(dcc.Graph(id=id_graph2))
        ],
            justify='center'
        )
    ])

# 2 Column layout 4 placeholders
def two_column_layout_4place(**kwargs):
    title = kwargs['title']
    title_graph1 = kwargs['title_graph1']
    title_graph2 = kwargs['title_graph2']
    id_dropdown1 = kwargs['id_dropdown1']
    dropdown_options1 = kwargs['dropdown_options1']
    dropdown_placeholder1 = kwargs['dropdown_placeholder1']
    id_dropdown2 = kwargs['id_dropdown2']
    dropdown_options2 = kwargs['dropdown_options2']
    dropdown_placeholder2 = kwargs['dropdown_placeholder2']
    id_dropdown3 = kwargs['id_dropdown3']
    dropdown_options3 = kwargs['dropdown_options3']
    dropdown_placeholder3 = kwargs['dropdown_placeholder3']
    id_dropdown4 = kwargs['id_dropdown4']
    dropdown_options4 = kwargs['dropdown_options4']
    dropdown_placeholder4 = kwargs['dropdown_placeholder4']
    id_graph1 = kwargs['id_graph1']
    id_graph2 = kwargs['id_graph2']

    return html.Div(children=[

        dbc.Row([
            html.H2(title)
        ],
            justify='center'
        ),

        dbc.Row([
            dbc.Col(html.H3(title_graph1), align='center'),
            dbc.Col(html.H3(title_graph2))
        ],
            justify='center', align='center'
        ),

        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id=id_dropdown1,
                    options=dropdown_options1,
                    placeholder=dropdown_placeholder1
                ),
                dcc.Dropdown(
                    id=id_dropdown2,
                    options=dropdown_options2,
                    placeholder=dropdown_placeholder2
                )
            ]),
            dbc.Col([
                dcc.Dropdown(
                    id=id_dropdown3,
                    options=dropdown_options3,
                    placeholder=dropdown_placeholder3
                ),
                dcc.Dropdown(
                    id=id_dropdown4,
                    options=dropdown_options4,
                    placeholder=dropdown_placeholder4
                )
            ])
        ],
            justify='center'
        ),

        dbc.Row([
            dbc.Col(dcc.Graph(id=id_graph1)),
            dbc.Col(dcc.Graph(id=id_graph2))
        ],
            justify='center'
        )
    ])

# Single column layout
def single_column_layout(multi1=False,multi2=False,offset=2,size=8,**kwargs):
    title = kwargs['title']
    title2 = kwargs['title2']
    id_dropdown1 = kwargs['id_dropdown1']
    dropdown_options1 = kwargs['dropdown_options1']
    dropdown_placeholder1 = kwargs['dropdown_placeholder1']

    try:
        id_dropdown2 = kwargs['id_dropdown2']
        dropdown_options2 = kwargs['dropdown_options2']
        dropdown_placeholder2 = kwargs['dropdown_placeholder2']
    except KeyError:
        id_dropdown2 = None

    id_graph = kwargs['id_graph']

    if id_dropdown2 is not None:

        return html.Div(children=[

            dbc.Row([
                html.H2(title)
            ],
                justify='center'
            ),

            dbc.Row([
                html.H3(title2)
            ],
                justify='center'
            ),

            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(
                        multi=multi1,
                        id=id_dropdown1,
                        options=dropdown_options1,
                        placeholder=dropdown_placeholder1
                    ),
                    dcc.Dropdown(
                        multi=multi2,
                        id=id_dropdown2,
                        options=dropdown_options2,
                        placeholder=dropdown_placeholder2
                    ),
                    dcc.Graph(id=id_graph)
                ], width={'offset': 2, 'size': 8})
            ]),
        ])

    else:

        return html.Div(children=[

            dbc.Row([
                html.H2(title)
            ],
                justify='center'
            ),

            dbc.Row([
                html.H3(title2)
            ],
                justify='center'
            ),

            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(
                        multi=multi1,
                        id=id_dropdown1,
                        options=dropdown_options1,
                        placeholder=dropdown_placeholder1
                    ),
                    dcc.Graph(id=id_graph)
                ], width={'offset': offset, 'size': size})
            ]),
        ])

# App Layout
app = dash.Dash(external_stylesheets=external_stylesheets)

server = app.server

app.layout = html.Div(children=[
    html.H1('Indicadores Muestra'),

    # COEFICIENTE DE GINI
    single_column_layout(title='Coeficiente de Gini',
                         title2='Línea 45 grados',
                         id_dropdown1='gini_input_area',
                         dropdown_options1=[{'label': c, 'value': c} for c in
                                            data_frames['gini']['Área geográfica'].unique()],
                         dropdown_placeholder1='Seleccionar área geográfica',
                         id_graph='gini_graph'),

    single_column_layout(title='',
                         title2='Barras Ordenadas',
                         id_dropdown1='gini_input_a',
                         dropdown_options1=[{'label': c, 'value': c} for c in
                                            data_frames['gini']['Área geográfica'].unique()],
                         dropdown_placeholder1='Seleccionar área geográfica',
                         id_dropdown2='gini_input_y',
                         dropdown_options2=[{'label': c, 'value': c} for c in anios_gini],
                         dropdown_placeholder2='Seleccionar Año',
                         id_graph='gini_bars'),

    # TAMANO MEDIO HOGARES
    two_column_layout_4place(title='Tamaño medio de los hogares',
                      title_graph1='Barras Agrupadas',
                      title_graph2='Serie de Tiempo',
                      id_dropdown1='input_country',
                      dropdown_options1=[{'label': c, 'value': c} for c in paises],
                      dropdown_placeholder1='Seleccionar País o Región',
                      id_dropdown2='input_dim',
                      dropdown_options2=[{'label': c, 'value': c} for c in desagregacion],
                      dropdown_placeholder2='Seleccionar desagregación',
                      id_dropdown3='input_country_line',
                      dropdown_options3=[{'label': c, 'value': c} for c in paises],
                      dropdown_placeholder3='Seleccionar País o Región',
                      id_dropdown4='input_geog_area',
                      dropdown_placeholder4='Seleccionar desagregación',
                      dropdown_options4=[{'label': c, 'value': c} for c in ['Área geográfica','Quintil']],
                      id_graph1='Graph',
                      id_graph2='Graph_line'),

    # MUJERES LABOR HOGAR
    single_column_layout(title='Mujeres con dedicación exclusivas a las labores del hogar, por quintil y área',
                         title2='Serie de Tiempo',
                         id_dropdown1='mh_input_country',
                         dropdown_options1=[{'label': c, 'value': c} for c in
                                            data_frames['mujeres_labor_hogar_AG_quintiles']['País'].unique()],
                         dropdown_placeholder1='Seleccionar País o Región',
                         id_dropdown2='mh_input_dim',
                         dropdown_options2=[{'label': c, 'value': c} for c in desagregacion],
                         dropdown_placeholder2='Seleccionar desagregación',
                         id_graph='mujeres_lh_ts'),

    # PARTICIPACION ECONOMICA
    single_column_layout(
        title='Tasa de participación económica de la población, por grupos de edad, sexo y área geográfica',
        title2='Barras lado a lado',
        id_dropdown1='tpe_input_dim',
        dropdown_options1=[{'label': c, 'value': c} for c in
                           data_frames['tasa_de_participacion_economica']['País'].unique()],
        dropdown_placeholder1='Seleccionar País o Región',
        id_dropdown2='tpe_input_aqe',
        dropdown_options2=[{'label': c, 'value': c} for c in ['Área geográfica',
                                                              'Grupo edad para participación en la PEA',
                                                              'Quintil']],
        dropdown_placeholder2='Seleccionar dimensión de desagregación',
        id_graph='tpe_graph'),

    # RELACION INGRESO MEDIO
    two_column_layout(title='Relacion del ingreso medio entre los sexos por años de educación y área geográfica',
                      title_graph1='Serie de Tiempo',
                      title_graph2='Barras lado a lado',
                      id_dropdown1='rims2_input_cty',
                      dropdown_options1=[{'label': c, 'value': c} for c in
                                         data_frames['relacion_ingreso_medio_sexo']['País'].unique()],
                      dropdown_placeholder1='Seleccionar País o Región',
                      id_dropdown2='rims2_input_ag',
                      dropdown_options2=[{'label': c, 'value': c} for c in
                                         data_frames['relacion_ingreso_medio_sexo']['Área geográfica'].unique()],
                      dropdown_placeholder2='Seleccionar área geográfica',
                      id_dropdown3='rims_input_dim',
                      dropdown_options3=[{'label': c, 'value': c} for c in anios_rim],
                      dropdown_placeholder3='Seleccionar Año',
                      id_graph1='rims2_graph',
                      id_graph2='rims_graph'),

    # OCUPADOS URBANOS INFORMALES
    single_column_layout(title='Ocupados urbanos en sectores de baja productividad (informales), por sexo',
                         title2='Barras ordenadas',
                         id_dropdown1='oui_input_cty',
                         dropdown_options1=[{'label': c, 'value': c} for c in
                                            data_frames['ocupados_informal_sexo']['País'].unique()],
                         dropdown_placeholder1='Seleccionar País o Región',
                         id_graph='oui_graph'),

    # ASISTENCIA ESCOLAR
    html.Div(children=[

        dbc.Row([
            html.H2('Asistencia Escolar (7 a 24 años), por sexo, quintil y área geográfica')
        ],
            justify='center'
        ),

        dbc.Row([
            dbc.Col(html.Label('Seleccionar dimensión del eje horizontal'),
            width={'offset': 2, 'size': 8})
        ],
            justify='start',
            align='end'
        ),

        dbc.Row([
            dbc.Col([
                html.Button('Sexo', id='button_sexo', n_clicks=0, style=white_button),
                html.Button('Quintil', id='button_quintil', n_clicks=0, style=white_button),
                html.Button('Área geográfica', id='button_area', n_clicks=0, style=white_button)
            ], width={'offset': 2, 'size': 8})],
            justify='center',
            align='start'
        ),

        dbc.Row([
            dbc.Col(html.Label('Seleccionar agrupación de barras'),
            width={'offset': 2, 'size': 8})
        ],
            justify='start',
            align='end'
        ),

        dbc.Row([
            dbc.Col([
                html.Button('Sexo', id='button_sexo2', n_clicks=0, style=white_button),
                html.Button('Quintil', id='button_quintil2', n_clicks=0, style=white_button),
                html.Button('Área geográfica', id='button_area2', n_clicks=0, style=white_button)
            ], width={'offset': 2, 'size': 8})],
            justify='center',
            align='start'
        ),
    ]),

    # POBLACION ADULTA ESCOLARIDAD
    single_column_layout(title='',
                         title2='Barras y línea',
                         id_dropdown1='edu_input_cty',
                         dropdown_options1=[{'label': c, 'value': c} for c in
                                            data_frames['poblacion_adulta_escolaridad']['País'].unique()],
                         dropdown_placeholder1='Seleccionar País',
                         id_dropdown2='edu_input_year',
                         dropdown_options2=[{'label': c, 'value': c} for c in anios_gini],
                         dropdown_placeholder2='Seleccionar año',
                         id_graph='edu_graph'),

    # SERVICIOS BASICOS HOGAR
    single_column_layout(title='Hogares según disponibilidad de servicios básicos en la vivienda, por área geográfica',
                         title2='Barras lado a lado',
                         id_dropdown1='hog_input_cty',
                         dropdown_options1=[{'label': c, 'value': c} for c in
                                            data_frames['hogares_disponibilidad_servicios']['País'].unique()],
                         dropdown_placeholder1='Seleccionar País',
                         id_graph='hog_graph'),
    dbc.Row([
        dbc.Col([
            html.Label('Seleccionar un año'),
            dcc.Slider(
                id='slider_hog',
                min=data_frames['hogares_disponibilidad_servicios']['Años'].astype(dtype='intc').min(),
                max=data_frames['hogares_disponibilidad_servicios']['Años'].astype(dtype='intc').max(),
                step=1,
                marks={int(year) : str(year) for year in anios_rim+[2019]},
                value=data_frames['hogares_disponibilidad_servicios']['Años'].astype(dtype='intc').min(),
            )
        ], width={'offset': 2, 'size': 8})
    ]),

    # ACCESO A ELECTRICIDAD
    single_column_layout(title='Proporción de la población con acceso a electricidad, por área geográfica y quintil',
                         title2='Barras lado a lado',
                         id_dropdown1='elec_input_cty',
                         dropdown_options1=[{'label': c, 'value': c} for c in
                                            sorted(list(data_frames['acceso_electricidad_quintil']['País'].unique()))],
                         dropdown_placeholder1='Seleccionar País',
                         id_graph='elec_graph'),
    dbc.Row([
        dbc.Col([
            html.Label('Seleccionar un año'),
            dcc.Slider(
                id='slider_elec',
                min=data_frames['acceso_electricidad_quintil']['Años'].astype(dtype='intc').min(),
                max=data_frames['acceso_electricidad_quintil']['Años'].astype(dtype='intc').max(),
                step=1,
                marks={int(year): str(year) for year in anios_rim + [2019]},
                value=data_frames['acceso_electricidad_quintil']['Años'].astype(dtype='intc').min(),
            )
        ], width={'offset': 2, 'size': 8})
    ]),
    # TASA DE VICTIMIZACION
    single_column_layout(multi1=True,
                         offset=1,
                         size=10,
                         title='Tasa de victimización, por sexo',
                         title2='Serie de Tiempo',
                         id_dropdown1='vic_input_cty',
                         dropdown_options1=[{'label': c, 'value': c} for c in
                                            data_frames['tasa_victimizacion']['País'].unique()],
                         dropdown_placeholder1='Seleccionar Países',
                         id_graph='vic_graph'),

    # RELACION DEL INGRESO MEDIO: QUINTIL 5/ QUINTIL 1
    single_column_layout(multi1=True,
                         title='Relación del ingreso medio per cápita del hogar: quintil 5 / quintil 1',
                         title2='Serie de Tiempo',
                         id_dropdown1='51_input_cty',
                         dropdown_options1=[{'label': c, 'value': c} for c in
                                            data_frames['relacion_quintil_5_1']['País'].unique()],
                         dropdown_placeholder1='Seleccionar Países',
                         id_dropdown2='51_input_area',
                         dropdown_options2=[{'label': c, 'value': c} for c in
                                            data_frames['relacion_quintil_5_1']['Área geográfica'].unique()],
                         dropdown_placeholder2='Seleccionar área geográfica',
                         id_graph='51_graph'),
])

#Graph  : Ordered Bars - Gini
@app.callback(
    Output('gini_bars', 'figure'),
    Input('gini_input_a', 'value'),
    Input('gini_input_y', 'value'))
def update_ginibars(area, year):
    return sort_gini(area,year)

#Graph 1 : Stacked Bars - Tamano medio hogar
@app.callback(
    Output('Graph', 'figure'),
    Input('input_country', 'value'),
    Input('input_dim', 'value'))
def update_graph(country, dim):
    # Convert datatypes
    data_frame["Años"] = data_frame["Años"].astype(dtype='intc')
    data_frame["valor"] = data_frame["valor"].astype(dtype='float64')

    # If user chooses 'Quintil'
    # Filter the dataframe by quintil and country
    if dim == 'Quintil':

        filt = data_frame[
            (data_frame["País"] == country) &
            (data_frame["Área geográfica"] == "Nacional") &
            (data_frame["Años"].isin(years))
            ]

        x_d = quintiles

    else:

        filt = data_frame[
            (data_frame["País"] == country) &
            (data_frame["Quintil"] == "Total quintiles") &
            (data_frame["Años"].isin(years))
            ]

        x_d = area

    # The Figure
    fig = go.Figure(data=[
        go.Bar(name=str(year),
               x=x_d,
               y=filt[data_frame["Años"] == year]['valor']) for year in years
    ])

    fig.update_layout(title_text="{} - Tamaño Medio del Hogar".format(country),
                      barmode='group')

    return fig

#Graph 2 : Time Series - Tamano medio hogar
@app.callback(
    Output('Graph_line', 'figure'),
    Input('input_country_line', 'value'),
    Input('input_geog_area', 'value'))
def update_graph_line(country, dim):
    try:
        return time_series_quintil('tamano_hogar', country, dim, "Tamaño medio del hogar")
    except (ValueError, KeyError, IndexError):
        return {}

# Graph 3 : Time Series - Mujeres con dedicacion hogar
@app.callback(
    Output('mujeres_lh_ts', 'figure'),
    Input('mh_input_country', 'value'),
    Input('mh_input_dim', 'value'))
def update_graph_line_mh(country, dim):
    try:
        return time_series_quintil('mujeres_labor_hogar_AG_quintiles', country, dim, "Mujeres con dedicación al hogar")
    except (ValueError, KeyError):
        return {}

#Graph 4 : Side stacked bars - Tasa de participacion economica
@app.callback(
        Output('tpe_graph','figure'),
        Input('tpe_input_dim','value'),
        Input('tpe_input_aqe', 'value'))
def ug_bars(country, dim):
    if dim == 'Quintil':
        try: return side_stacked_bars('tasa_de_participacion_economica_quintil',
                                      country,
                                     'Quintil')
        except (TypeError, ValueError, KeyError): return side_stacked_bars('tasa_de_participacion_economica',
                                                                 'América Latina (promedio simple)',
                                                                 'Quintil')
    else:
        try: return side_stacked_bars('tasa_de_participacion_economica',
                                      country,
                                      dim)
        except (TypeError, ValueError, KeyError): return side_stacked_bars('tasa_de_participacion_economica',
                                                                 'América Latina (promedio simple)',
                                                                 'Área geográfica')

# Graph 5 : Ordered bars - relacion ingreso sexo
@app.callback(
    Output('rims_graph', 'figure'),
    Input('rims_input_dim', 'value'))
def order_bars(year):
    try:
        return sort_pais_bar('relacion_ingreso_medio_sexo', year)
    except ValueError:
        {}

# Graph 6 : Side by side bars - relacion ingreso sexo
@app.callback(
    Output('rims2_graph', 'figure'),
    Input('rims2_input_cty', 'value'),
    Input('rims2_input_ag', 'value'))
def ss_bars(country, area):
    try:
        return sidebside_bars('relacion_ingreso_medio_sexo', country, area)
    except (ValueError, KeyError):
        return {}

#Graph 7 : Time series - Ocupados urbanos informales
@app.callback(
        Output('oui_graph','figure'),
        Input('oui_input_cty','value'))
def stack_bars(country):
    try: return stacked_bars('ocupados_informal_sexo', country)
    except (KeyError,ValueError): return {}

#Graph 8 : Gini : 45 degree line
@app.callback(
        Output('gini_graph','figure'),
        Input('gini_input_area','value'))
def c_gini(area):
    try: return gini(area)
    except (ValueError,KeyError): return {}

# BOTONES EJE HORIZONTAL
@app.callback(
    Output('button_sexo', 'style'),
    Input('button_sexo', 'n_clicks'),
    State('button_sexo', 'style'),
    State('button_quintil', 'style'),
    State('button_area', 'style'))
def updatem(click, s1, s2, s3):
    count = [1 for s in [s1, s2, s3] if s == red_button]
    if click > 0:
        if len(count) == 0:
            return red_button
        else:
            return white_button
    else:
        return white_button

@app.callback(
    Output('button_quintil', 'style'),
    Input('button_quintil', 'n_clicks'),
    State('button_sexo', 'style'),
    State('button_quintil', 'style'),
    State('button_area', 'style'))
def updatew(click, s1, s2, s3):
    count = [1 for s in [s1, s2, s3] if s == red_button]
    if click > 0:
        if len(count) == 0:
            return red_button
        else:
            return white_button
    else:
        return white_button

@app.callback(
    Output('button_area', 'style'),
    Input('button_area', 'n_clicks'),
    State('button_sexo', 'style'),
    State('button_quintil', 'style'),
    State('button_area', 'style'))
def updatemr(click, s1, s2, s3):
    count = [1 for s in [s1, s2, s3] if s == red_button]
    if click > 0:
        if len(count) == 0:
            return red_button
        else:
            return white_button
    else:
        return white_button

# BOTONES AGRUPACION BARRAS
@app.callback(
    Output('button_sexo2', 'style'),
    Input('button_sexo2', 'n_clicks'),
    State('button_sexo', 'style'),
    State('button_sexo2', 'style'),
    State('button_quintil2', 'style'),
    State('button_area2', 'style'))
def updates2(click, s1, s4, s5, s6):
    count = [1 for s in [s4, s5, s6] if s == red_button]
    if click > 0 and s1 == white_button:
        if len(count) == 0:
            return red_button
        else:
            return white_button
    else:
        return white_button

@app.callback(
    Output('button_quintil2', 'style'),
    Input('button_quintil2', 'n_clicks'),
    State('button_quintil', 'style'),
    State('button_sexo2', 'style'),
    State('button_quintil2', 'style'),
    State('button_area2', 'style'))
def updateq2(click, s2, s4, s5, s6):
    count = [1 for s in [s4, s5, s6] if s == red_button]
    if click > 0 and s2 == white_button:
        if len(count) == 0:
            return red_button
        else:
            return white_button
    else:
        return white_button

@app.callback(
    Output('button_area2', 'style'),
    Input('button_area2', 'n_clicks'),
    State('button_area', 'style'),
    State('button_sexo2', 'style'),
    State('button_quintil2', 'style'),
    State('button_area2', 'style'))
def updatea2(click, s3, s4, s5, s6):
    count = [1 for s in [s4, s5, s6] if s == red_button]
    if click > 0 and s3 == white_button:
        if len(count) == 0:
            return red_button
        else:
            return white_button
    else:
        return white_button

# Graph 9 : Asistencia Escolar
@app.callback(
    Output('edu_graph', 'figure'),
    Input('edu_input_cty', 'value'),
    Input('edu_input_year', 'value'),
    Input('button_sexo', 'style'),
    Input('button_quintil', 'style'),
    Input('button_area', 'style'),
    Input('button_sexo2', 'style'),
    Input('button_quintil2', 'style'),
    Input('button_area2', 'style'))
def edu_graph(c, y, b1, b2, b3, b4, b5, b6):
    try:
        xdim = [b1,b2,b3]
        group = [b4,b5,b6]
        return bars_lines(c, y, xdim, group)
    except KeyError:
        return {}

#Graph 10 : Hogares Servicios Vivienda
@app.callback(
    Output('hog_graph','figure'),
    Input('hog_input_cty','value'),
    Input('slider_hog','value'))
def hog_graph(country,year):
    try: return side_side_bars('hogares_disponibilidad_servicios',
                               country,
                               year,
                               "Disponibilidad de Servicios",
                               'Servicios básicos_(EH)',
                               'Área geográfica')
    except (KeyError,ValueError): return {}

#Graph # : Hogares Electricidad
@app.callback(
    Output('elec_graph','figure'),
    Input('elec_input_cty','value'),
    Input('slider_elec','value'))
def elec_graph(country,year):
    try: return side_side_bars('acceso_electricidad_quintil',
                               country,
                               year,
                               "Acceso a Electricidad",
                               'Quintil',
                               'Área geográfica')
    except (KeyError,ValueError): return {}

#Graph 11 : Tasa de victimizacion
@app.callback(
    Output('vic_graph','figure'),
    [Input('vic_input_cty','value')])
def victim(countries):
    try: return time_series_mult_facet('tasa_victimizacion',
                                        countries,
                                        "Tasa de victimización",
                                        "Porcentaje")
    except (TypeError,ValueError,KeyError): return {}

#Graph 12 : Relacion quintil 5 y quintil 1.
@app.callback(
    Output('51_graph','figure'),
    [Input('51_input_cty','value')],
    Input('51_input_area', 'value'))
def quintil51(countries, area):
    try: return time_series_mult('relacion_quintil_5_1', countries, area,
                                 'Relación Quintil de Ingreso: 5 y 1',
                                 "Quintil 5 / Quintil 1")
    except (TypeError,ValueError,KeyError): return {}

if __name__ == '__main__':
    app.run_server(debug=True)