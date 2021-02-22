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
             'relacion_ingreso_medio_sexo',
             'ocupados_informal_sexo',
             'gini',
             'poblacion_adulta_escolaridad',
             'hogares_disponibilidad_servicios',
             'tasa_victimizacion',
             'relacion_quintil_5_1']

data_frames = {name: pd.read_csv('{}.csv'.format(name)) for name in csv_files}
data_frame = data_frames['tamano_hogar']

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


def time_series_quintil(data, country, area_g):
    df = data_frames[data]
    df["valor"] = df["valor"].astype(dtype='float64')
    quints = {qt : "qt{}".format(qt[-1]) for qt in df["Quintil"].unique()}

    if area_g == 'Área geográfica':
        q = df[
            (df["País"] == country) &
            (df["Quintil"] == "Total quintiles")
            ]

        q["Años"] = q["Años"].astype(dtype='intc')

        lfig = px.line(q,
                       x="Años",
                       y='valor',
                       color='Área geográfica')
        for i, elem in enumerate(lfig.data):
            lfig.data[i].name = "Tam_hog_{}".format(lfig.data[i].name)

    else:
        q = df[
            (df["País"] == country) &
            (df["Área geográfica"] == "Nacional")
            ]

        q["Años"] = q["Años"].astype(dtype='intc')

        lfig = px.line(q,
                       x="Años",
                       y='valor',
                       color='Quintil')

        for i, elem in enumerate(lfig.data):
            lfig.data[i].name = "Tam_hog_{}".format(quints[lfig.data[i].name])

    lfig.update_layout(title_text=country + " - Tamaño Medio del Hogar",
                       legend_title="Desagregación")
    return lfig

def side_stacked_bars(data, country):
    # Filter pandas data_frame
    data_frame = data_frames[data]
    filt_cty = data_frame[(data_frame['País'] == country) &
                          (data_frame['Área geográfica'] != 'Nacional') &
                          (data_frame['Sexo'] != 'Ambos sexos')]
    filt_cty['Años'] = filt_cty['Años'].astype(dtype='intc')
    filt_cty['valor'] = filt_cty['valor'].astype(dtype='float64')

    # Get latest year of available data and filter by it
    l_year = filt_cty['Años'].max()
    f_c_y = filt_cty[(filt_cty['Años'] == l_year)]

    xs = list(f_c_y['Grupo edad para participación en la PEA'].unique())

    ar = ['Rural', 'Urbana']
    sex = ['Hombres', 'Mujeres']
    ys = {a + ' ' + s: list(f_c_y[(f_c_y['Área geográfica'] == a) & (f_c_y['Sexo'] == s)]['valor']) for a in ar for s in
          sex}

    # Figure
    fig = make_subplots(rows=1, cols=2)
    fig.add_trace(go.Bar(name='Rural - Hombres', x=xs, y=ys['Rural Hombres']),
                  row=1, col=1)
    fig.add_trace(go.Bar(name='Rural - Mujeres', x=xs, y=ys['Rural Mujeres']),
                  row=1, col=1)
    fig.add_trace(go.Bar(name='Urbana - Hombres', x=xs, y=ys['Urbana Hombres']),
                  row=1, col=2)
    fig.add_trace(go.Bar(name='Urbana - Mujeres', x=xs, y=ys['Urbana Mujeres']),
                  row=1, col=2)

    try:
        fig.update_layout(title_text=country + ' ' + str(l_year))
    except TypeError:
        pass

    return fig

def sort_pais_bar(data, year):
    # Select Data Frame
    data_frame = data_frames[data]
    data_frame['valor'] = data_frame['valor'].astype(dtype='float64')

    # Filter data
    filt_data = data_frame[(data_frame['Años'] == year) &
                           (data_frame['Área geográfica'] == 'Nacional') &
                           (data_frame['Escolaridad (EH)'] == 'Total')]

    filt_data.sort_values(by='valor', inplace=True)

    # Figure
    fig = go.Figure(data=[go.Bar(name=str(year),
                                 x=list(filt_data['País']),
                                 y=list(filt_data['valor']))]
                    )

    try:
        fig.add_shape(type='line',
                      x0=list(filt_data['País'])[0],
                      y0=100,
                      x1=list(filt_data['País'])[-1],
                      y1=100,
                      line=dict(color='Red', ),
                      xref='x',

                      yref='y')
    except IndexError:
        pass

    return fig

def sidebside_bars(data, country, area):
    # Select Data Frame
    data_frame = data_frames[data].copy(deep=True)
    data_frame['valor'] = data_frame['valor'].astype(dtype='float64')
    data_frame['Años'] = data_frame['Años'].astype(dtype='intc')

    # Filter data
    years = [2002, 2010, 2018]
    filt_data = data_frame[(data_frame['Años'].isin(years)) &
                           (data_frame['País'] == country) &
                           (data_frame['Área geográfica'] == area)]

    # Figure
    fig = go.Figure(data=[
        go.Bar(name=str(year),
               x=list(filt_data['Escolaridad (EH)'].unique()),
               y=filt_data[filt_data["Años"] == year]['valor']) for year in years]
    )

    fig.update_layout(title_text=country,
                      barmode='group')

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
    fig = go.Figure(data=[
        go.Bar(name=str(sex),
               x=list(filt_data['Años'].unique()),
               y=filt_data[filt_data['Sexo'] == sex]['valor']) for sex in ['Hombres', 'Mujeres']]
    )

    fig.update_layout(title_text=country,
                      barmode='stack')

    return fig

def gini(area, decade):
    gini_df = data_frames['gini']
    gini_df['Años'] = gini_df['Años'].astype(dtype='intc')
    gini_df['valor'] = gini_df['valor'].astype(dtype='float64')

    graph_gini_df = {'País': [], 'Primer Año': [], 'Ultimo Año': [], 'Gini {}'.format(decade): [],
                     'Gini (2014-2019)': []}

    if decade != '2000s':
        gini_df = gini_df[gini_df['Años'] > 2009]

    for pais in gini_df['País'].unique():
        aux = gini_df[(gini_df["País"] == pais)]
        try:
            graph_gini_df['Gini {}'.format(decade)].append(gini_df[(gini_df["País"] == pais) &
                                                                   (gini_df['Años'] == aux['Años'].min()) &
                                                                   (gini_df["Área geográfica"] == area)]['valor'].iloc[
                                                               0])
            graph_gini_df['Gini (2014-2019)'].append(gini_df[(gini_df["País"] == pais) &
                                                             (gini_df['Años'] == aux['Años'].max()) &
                                                             (gini_df["Área geográfica"] == area)]['valor'].iloc[0])
            graph_gini_df['Primer Año'].append(aux['Años'].min())
            graph_gini_df['Ultimo Año'].append(aux['Años'].max())
            graph_gini_df['País'].append(pais)
        except IndexError:
            pass

    gini_filt = pd.DataFrame(graph_gini_df)
    gini_filt['color'] = numpy.where(gini_filt['Gini (2014-2019)'] >= gini_filt['Gini {}'.format(decade)],
                                     'Increased Inequality',
                                     'Decreased Inequality')

    try:
        figure = px.scatter(gini_filt, x='Gini {}'.format(decade),
                            y='Gini (2014-2019)',
                            color='color',
                            size='Gini {}'.format(decade),
                            text='País')
        figure.add_shape(type='line',
                         x0=.3,
                         y0=.3,
                         x1=.7,
                         y1=.7,
                         line=dict(color='Red', ),
                         xref='x',
                         yref='y')
        return figure
    except KeyError:
        return {}

def bars_lines(country, year, b1, b2, b3, b4):
    # Filters
    if b1 == red_button and b3 == red_button:
        filt = [('Hombres', 'Urbana'), ('Hombres', 'Rural')]
    elif b1 == red_button and b4 == red_button:
        filt = [('Hombres', 'Urbana'), ('Mujeres', 'Rural')]
    elif b2 == red_button and b3 == red_button:
        filt = [('Mujeres', 'Urbana'), ('Hombres', 'Rural')]
    elif b1 == red_button and b2 == red_button:
        filt = [('Hombres', 'Urbana'), ('Mujeres', 'Urbana')]
    elif b3 == red_button and b4 == red_button:
        filt = [('Hombres', 'Rural'), ('Mujeres', 'Rural')]
    else:
        filt = [('Mujeres', 'Urbana'), ('Mujeres', 'Rural')]

    df = data_frames['poblacion_adulta_escolaridad']

    filt_df = df.query(
        "(Sexo=='{}' & `Área geográfica`=='{}') | (Sexo=='{}' & `Área geográfica`=='{}')".format(filt[0][0],
                                                                                                 filt[0][1],
                                                                                                 filt[1][0],
                                                                                                 filt[1][1]))

    filt_df = filt_df.query("País=='{}' & Años=='{}'".format(country, year))

    filt_df = filt_df.groupby(['Sexo', 'Área geográfica'],
                              as_index=False).apply(lambda x: x.sort_values(by=['Escolaridad (EH)'],
                                                                            axis=0, key=lambda x: pd.Series(
            [0, 2, 3, 1]))).reset_index()

    filt_df['valor'] = filt_df['valor'].astype(dtype='float64')

    # FIGURE
    xs = filt_df['Escolaridad (EH)'].unique()
    ybars = filt_df.query("Sexo == '{}' & `Área geográfica`=='{}'".format(filt[0][0], filt[0][1]))['valor']
    yline = filt_df.query("Sexo == '{}' & `Área geográfica`=='{}'".format(filt[1][0], filt[1][1]))['valor']

    fig = go.Figure()
    fig.add_trace(go.Bar(name='{} - {}'.format(filt[0][0], filt[0][1]),
                         x=xs,
                         y=ybars))
    fig.add_trace(go.Scatter(name='{} - {}'.format(filt[1][0], filt[1][1]),
                             x=xs, y=yline, mode='lines+markers'))

    fig.update_layout(title_text="{} - {}".format(country, year))
    return fig

def side_side_bars(data, country, year):
    # Select Data Frame
    data_frame = data_frames[data].copy(deep=True)
    data_frame['valor'] = data_frame['valor'].astype(dtype='float64')
    data_frame['Años'] = data_frame['Años'].astype(dtype='intc')

    # Filter data
    filt_data = data_frame[(data_frame['Años'] == year) &
                           (data_frame['País'] == country)]

    # Figure
    fig = go.Figure(data=[
        go.Bar(name=area,
               x=filt_data['Servicios básicos_(EH)'].unique(),
               y=filt_data[filt_data["Área geográfica"] == area]['valor']) for area in
        filt_data['Área geográfica'].unique()]
    )

    fig.update_layout(title_text='{} {}'.format(country, str(year)),
                      barmode='group')

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

# User input
desagregacion = ["Área geográfica", "Quintil"]
paises = list(data_frame['País'].unique())

# Desagregaciones
anios = sorted(list(map(int, data_frame['Años'].unique())))
years = [2002, 2010, 2019]
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

# Single column layout
def single_column_layout(**kwargs):
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
                        id=id_dropdown1,
                        options=dropdown_options1,
                        placeholder=dropdown_placeholder1
                    ),
                    dcc.Dropdown(
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
                        id=id_dropdown1,
                        options=dropdown_options1,
                        placeholder=dropdown_placeholder1
                    ),
                    dcc.Graph(id=id_graph)
                ], width={'offset': 2, 'size': 8})
            ]),
        ])

# App Layout
app = dash.Dash(external_stylesheets=external_stylesheets)

server = app.server

app.layout = html.Div(children=[
    html.H1('Indicadores Muestra'),

    # TAMANO MEDIO HOGARES
    two_column_layout(title='Tamaño medio de los hogares',
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
    html.Div(children=[

        dbc.Row([
            html.H2('Tasa de participación económica de la población, por grupos de edad, sexo y área geográfica')
        ],
            justify='center'
        ),

        dbc.Row([
            html.H3('Barras lado a lado'),
        ],
            justify='center'
        ),

        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id='tpe_input_dim',
                    options=[{'label': c, 'value': c} for c in
                             data_frames['tasa_de_participacion_economica']['País'].unique()],
                    placeholder='Seleccionar País o Región'
                )
            ], width={'size': 8})
        ],
            justify='center'
        ),

        dbc.Row([
            dbc.Col([
                dcc.Graph(id='tpe_graph')
            ], width={'size': 12})
        ])
    ]),

    # RELACION INGRESO MEDIO
    two_column_layout(title='Relacion del ingreso medio entre los sexos por años de instrucción y área geográfica',
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
                      dropdown_options3=[{'label': c, 'value': c} for c in
                                         data_frames['relacion_ingreso_medio_sexo']['Años'].unique()],
                      dropdown_placeholder3='Seleccionar País o Región',
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

    # COEFICIENTE DE GINI
    single_column_layout(title='Coeficiente de Gini',
                         title2='Línea 45 grados',
                         id_dropdown1='gini_input_area',
                         dropdown_options1=[{'label': c, 'value': c} for c in
                                            data_frames['gini']['Área geográfica'].unique()],
                         dropdown_placeholder1='Seleccionar área geográfica',
                         id_dropdown2='gini_input_time',
                         dropdown_options2=[{'label': c, 'value': c} for c in ['2000s', '2010s']],
                         dropdown_placeholder2='Seleccionar periodo de comparación',
                         id_graph='gini_graph'),

    # EDUCACION ADULTOS
    html.Div(children=[

        dbc.Row([
            html.H2('Población adulta según nivel educativo, por área geográfica y sexo')
        ],
            justify='center'
        ),

        dbc.Row([
            html.Label('Seleccionar dos opciones (botones)')
        ],
            justify='center'
        ),

        dbc.Row([
            dbc.Col([
                html.Button('Hombres Urbanos', id='button_hombres', n_clicks=0, style=white_button),
                html.Button('Mujeres Urbanas', id='button_mujeres', n_clicks=0, style=white_button)
            ], width={'offset': 4, 'size': 8})],
            justify='center'
        ),

        dbc.Row([
            dbc.Col([
                html.Button('Hombres Rurales', id='button_hombres_r', n_clicks=0, style=white_button),
                html.Button('Mujeres Rurales', id='button_mujeres_r', n_clicks=0, style=white_button)
            ], width={'offset': 4, 'size': 8})],
            justify='center'
        ),
    ]),
    single_column_layout(title='',
                         title2='Barras y línea',
                         id_dropdown1='edu_input_cty',
                         dropdown_options1=[{'label': c, 'value': c} for c in
                                            data_frames['poblacion_adulta_escolaridad']['País'].unique()],
                         dropdown_placeholder1='Seleccionar País',
                         id_dropdown2='edu_input_year',
                         dropdown_options2=[{'label': c, 'value': c} for c in
                                            data_frames['poblacion_adulta_escolaridad']['Años'].unique()],
                         dropdown_placeholder2='Seleccionar año',
                         id_graph='edu_graph'),
    single_column_layout(title='Hogares según disponibilidad de servicios básicos en la vivienda, por área geográfica',
                     title2='Barras lado a lado',
                     id_dropdown1='hog_input_cty',
                     dropdown_options1=[{'label' : c, 'value' : c} for c in data_frames['hogares_disponibilidad_servicios']['País'].unique()],
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
                    marks={2000:'2000',
                          2010:'2010',
                          2019:'2019'},
                    value=data_frames['hogares_disponibilidad_servicios']['Años'].astype(dtype='intc').min(),
                    )
                ], width={'offset' : 2, 'size' : 8})
    ]),
    single_column_layout(title='Tasa de victimización, por sexo',
                     title2='Scatter dinámico',
                     id_dropdown1='vic_input_cty',
                     dropdown_options1=[],
                     dropdown_placeholder1='',
                     id_graph='vic_graph'),
    dbc.Row([
                dbc.Col([
                    html.Label('Seleccionar un año'),
                    dcc.Slider(
                    id='slider_vic',
                    min=data_frames['tasa_victimizacion']['Años'].astype(dtype='intc').min(),
                    max=data_frames['tasa_victimizacion']['Años'].astype(dtype='intc').max(),
                    step=None,
                    marks={int(year) : str(year) for year in data_frames['tasa_victimizacion']['Años'].unique()},
                    value=data_frames['tasa_victimizacion']['Años'].astype(dtype='intc').min(),
                    )
                ], width={'offset' : 2, 'size' : 8})
    ]),
    html.Div(children=[

        dbc.Row([
            html.H2('Relación del ingreso medio per cápita del hogar: quintil 5/ quintil 1')
        ],
            justify='center'
        ),

        dbc.Row([
            html.H3('Scatter dinámico')
        ],
            justify='center'
        ),

        dbc.Row([
            dbc.Col([
                dcc.Graph(id='quintil51_graph')
            ], width={'offset': 2, 'size': 8})
        ]),
    ]),
    dbc.Row([
        dbc.Col([
            html.Label('Seleccionar un año'),
            dcc.Slider(
                id='slider_quintil51',
                min=data_frames['relacion_quintil_5_1']['Años'].astype(dtype='intc').min(),
                max=data_frames['relacion_quintil_5_1']['Años'].astype(dtype='intc').max(),
                step=None,
                marks={int(year): str(year) for year in data_frames['relacion_quintil_5_1']['Años'].unique()},
                value=data_frames['relacion_quintil_5_1']['Años'].astype(dtype='intc').min(),
            )
        ], width={'offset': 2, 'size': 8})
    ])
])

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

    fig.update_layout(title_text=country,
                      barmode='group')

    return fig

#Graph 2 : Time Series - Tamano medio hogar
@app.callback(
    Output('Graph_line', 'figure'),
    Input('input_country_line', 'value'))
def update_graph_line(country):
    try:
        return time_series_quintil('tamano_hogar', country, 'Quintil')
    except (ValueError, KeyError):
        return {}

# Graph 3 : Time Series - Mujeres con dedicacion hogar
@app.callback(
    Output('mujeres_lh_ts', 'figure'),
    Input('mh_input_country', 'value'),
    Input('mh_input_dim', 'value'))
def update_graph_line_mh(country, dim):
    try:
        return time_series_quintil('mujeres_labor_hogar_AG_quintiles', country, dim)
    except (ValueError, KeyError):
        return {}

#Graph 4 : Side stacked bars - Tasa de participacion economica
@app.callback(
        Output('tpe_graph','figure'),
        Input('tpe_input_dim','value'))
def ug_bars(country):
    try: return side_stacked_bars('tasa_de_participacion_economica', country)
    except ValueError: return {}

# Graph 5 : Ordered bars - relacion ingreso sexo
@app.callback(
    Output('rims_graph', 'figure'),
    Input('rims_input_dim', 'value'))
def order_bars(year):
    try:
        return sort_pais_bar('relacion_ingreso_medio_sexo', year)
    except ValueError:
        return {}

# Graph 6 : Side by side bars - relacion ingreso sexo
@app.callback(
    Output('rims2_graph', 'figure'),
    Input('rims2_input_cty', 'value'),
    Input('rims2_input_ag', 'value'))
def ss_bars(country, area):
    try:
        return sidebside_bars('relacion_ingreso_medio_sexo', country, area)
    except ValueError:
        return {}

#Graph 7 : Stacked Bars - Ocupados urbanos informales
@app.callback(
        Output('oui_graph','figure'),
        Input('oui_input_cty','value'))
def stack_bars(country):
    try: return stacked_bars('ocupados_informal_sexo', country)
    except ValueError: return {}

#Graph 8 : Gini : 45 degree line
@app.callback(
        Output('gini_graph','figure'),
        Input('gini_input_area','value'),
        Input('gini_input_time', 'value'))
def c_gini(area, time):
    return gini(area,time)

# BOTONES URBANOS
@app.callback(
    Output('button_hombres', 'style'),
    Input('button_hombres', 'n_clicks'),
    State('button_mujeres', 'style'),
    State('button_hombres', 'style'),
    State('button_mujeres_r', 'style'),
    State('button_hombres_r', 'style'))
def updatem(click, s1, s2, s3, s4):
    count = [1 for s in [s1, s2, s3, s4] if s == red_button]
    if click > 0:
        if len(count) < 2 and s2 == white_button:
            return red_button
        else:
            return white_button
    else:
        return white_button

@app.callback(
    Output('button_mujeres', 'style'),
    Input('button_mujeres', 'n_clicks'),
    State('button_mujeres', 'style'),
    State('button_hombres', 'style'),
    State('button_mujeres_r', 'style'),
    State('button_hombres_r', 'style'))
def updatew(click, s1, s2, s3, s4):
    count = [1 for s in [s1, s2, s3, s4] if s == red_button]
    if click > 0:
        if len(count) < 2 and s1 == white_button:
            return red_button
        else:
            return white_button
    else:
        return white_button

# BOTONES RURALES
@app.callback(
    Output('button_hombres_r', 'style'),
    Input('button_hombres_r', 'n_clicks'),
    State('button_mujeres', 'style'),
    State('button_hombres', 'style'),
    State('button_mujeres_r', 'style'),
    State('button_hombres_r', 'style'))
def updatemr(click, s1, s2, s3, s4):
    count = [1 for s in [s1, s2, s3, s4] if s == red_button]
    if click > 0:
        if len(count) < 2 and s4 == white_button:
            return red_button
        else:
            return white_button
    else:
        return white_button

@app.callback(
    Output('button_mujeres_r', 'style'),
    Input('button_mujeres_r', 'n_clicks'),
    State('button_mujeres', 'style'),
    State('button_hombres', 'style'),
    State('button_mujeres_r', 'style'),
    State('button_hombres_r', 'style'))
def updatewr(click, s1, s2, s3, s4):
    count = [1 for s in [s1, s2, s3, s4] if s == red_button]
    if click > 0:
        if len(count) < 2 and s3 == white_button:
            return red_button
        else:
            return white_button
    else:
        return white_button

# Graph 9 : Educacion Adultos
@app.callback(
    Output('edu_graph', 'figure'),
    Input('edu_input_cty', 'value'),
    Input('edu_input_year', 'value'),
    Input('button_hombres', 'style'),
    Input('button_mujeres', 'style'),
    Input('button_hombres_r', 'style'),
    Input('button_mujeres_r', 'style'))
def edu_graph(c, y, b1, b2, b3, b4):
    try: return bars_lines(c, y, b1, b2, b3, b4)
    except KeyError: return {}

#Graph 10 : Hogares Servicios Vivienda
@app.callback(
    Output('hog_graph','figure'),
    Input('hog_input_cty','value'),
    Input('slider_hog','value'))
def hog_graph(country,year):
    try: return side_side_bars('hogares_disponibilidad_servicios',country,year)
    except ValueError: return {}

#Graph 11 : Tasa de victimizacion
@app.callback(
    Output('vic_graph','figure'),
    Input('slider_vic','value'))
def victim(year):
    try: return points('tasa_victimizacion', year, 'Mujeres', 'Sexo', ['Hombres', 'Mujeres'])
    except ValueError: return {}

#Graph 12 : Relacion quintil 5 y quintil 1.
@app.callback(
    Output('quintil51_graph','figure'),
    Input('slider_quintil51','value'))
def quintil51(year):
    try: return points('relacion_quintil_5_1', year, 'Urbana', 'Área geográfica', ['Urbana', 'Rural'])
    except ValueError: return {}

if __name__ == '__main__':
    app.run_server(debug=True)