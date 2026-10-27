# 1. Importando as bibliotecas

import pandas as pd
import streamlit as st
import plotly.express as px

# Configuração da página

st.set_page_config(layout="wide")


def add_space():
    st.markdown("<br><br><br>", unsafe_allow_html=True)


st.title("Dashboard de Anúncios de Veículos")
st.header("Análise dos preços de veículos usados")
# 2. Carregando os dados da tabela vehicles.csv

vehicles = pd.read_csv(
    r'C:\sprint5dir\sprint_5_project-Dashboard\vehicles.csv')

# 3. Preparando os dados para análise

vehicles = vehicles.drop_duplicates()
vehicles = vehicles[vehicles['price'].between(
    500, 110000)].reset_index(drop=True)

# Criado a coluna brand, que contém a marca do veículo, extraída da coluna model

vehicles['brand'] = vehicles['model'].str.split().str[0]

# Agrupando por marca e calculando a mediana do preço

vehicles_by_brand = vehicles.groupby('brand')
vehicles_by_brand_median = vehicles_by_brand['price'].median().round(
    2).sort_values(ascending=False).head(20)


#  4. Criando um botão para vizualizar uma amostra dos dados
add_space()
st.button('Clique aqui para vizualizar uma amostra dos dados',
          key='sample_button')

if st.session_state.get('sample_button'):
    st.write(vehicles.sample(20))
add_space()

#  5. Construindo histograma da distribução de preço por marca


brand_filter = st.multiselect(
    label='Selecione as marcas para o histograma de preço:',
    options=vehicles_by_brand_median.index.tolist(),
    default=vehicles_by_brand_median.index.tolist(),
    key='brand_histogram'
)

fig_brand_histogram = px.histogram(
    vehicles[vehicles['brand'].isin(brand_filter)],
    x='price',
    title='Distribuição do Preço por Marca',
    color='brand',
    color_discrete_sequence=px.colors.sequential.Blues,
    labels={
        'price': 'Preço ($)',
    },
    opacity=0.5,
    nbins=100
)

fig_brand_histogram.update_layout(
    height=600,
    title_x=0.5,
    legend_title_text='Marca',
    yaxis_title='Quantidade de veículos',
)

st.plotly_chart(fig_brand_histogram)
add_space()

# 6. Construindo gráfico de preço mediano por marca

brands = vehicles_by_brand_median.reset_index()
brands = brands.sort_values(by='price')
palette = px.colors.sample_colorscale(
    'Blues',
    [
        0.25 + i * (0.75 / (len(brands) - 1))
        for i in range(len(brands))
    ]
)

fig = px.bar(
    brands,
    x='brand',
    y='price',
    color='brand',
    color_discrete_sequence=palette,
    title='Preço mediano por marca',
    labels={
        'brand': 'Marca',
        'price': 'Preço mediano ($)'
    }
)

fig.update_layout(
    height=600,
    title_x=0.5,
    legend_title_text='Marca'
)

st.plotly_chart(fig)
add_space()

# 7. Construindo gráfico de dispersão de preço por odômetro

# Construindo um slider para selecionar o valor máximo de milhas

max_odometer = st.slider(
    label='Selecione o valor máximo do odômetro (milhas):',
    min_value=0,
    max_value=1000000,
    value=500000,
    step=10000,
    key='odometer_slider',
)

vehicles_odometer = vehicles.dropna(subset=['odometer'])

odometer = vehicles_odometer.reset_index(drop=True)
odometer = odometer[odometer['odometer'] <= max_odometer]

fig_odo = px.scatter(
    odometer,
    x='odometer',
    y='price',
    title='Relação entre quilometragem e preço',
    labels={
        'odometer': 'Odômetro (milhas)',
        'price': 'Preço ($)'
    },
    opacity=0.25,
    render_mode='webgl',
    log_y=True
)

fig_odo.update_traces(
    marker=dict(size=4)
)

fig_odo.update_layout(
    height=650,
    title_x=0.5,
    xaxis=dict(
        showgrid=True,
        gridcolor='lightgray'
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor='lightgray',
        tickprefix='$'
    )
)

st.plotly_chart(fig_odo)
add_space()

# 8. Construindo gráfico de preço mediano por marca e ano de fabricação

# Criando um novo DataFrame excluindo as linhas com valores nulos na coluna 'model_year' e filtrando as marcas com mais de 1000 veículos

vehicles_filtered_year = vehicles.dropna(subset=['model_year']).copy()
brand_over_1000 = vehicles_filtered_year['brand'].value_counts()
brand_over_1000 = brand_over_1000[brand_over_1000 >= 1000]
vehicles_filtered_year = vehicles_filtered_year[vehicles_filtered_year['brand'].isin(
    brand_over_1000.index)]
vehicles_grouped_year = vehicles_filtered_year.groupby(
    ['brand', 'model_year'])['price'].median().reset_index()

# Criando um slider para selecionar o intervalo de anos de fabricação

year_filter = st.slider(
    label='Selecione os anos de fabricação para filtrar:',
    min_value=1995,
    max_value=2019,
    value=(2015, 2019),
    step=1,
    key='year_slider',
)
fig_year_bars = px.bar(
    vehicles_grouped_year[vehicles_grouped_year['model_year'].between(
        year_filter[0], year_filter[1])],
    x='brand',
    y='price',
    barmode='group',
    title='Preço Mediano por Marca e Ano de Fabricação',
    color='model_year',
    color_discrete_sequence=px.colors.sequential.Blues,
    labels={
        'price': 'Preço ($)',
        'brand': 'Marca',
        'model_year': 'Ano de Fabricação'
    },

)

fig_year_bars.update_layout(
    height=800,
    title_x=0.5,
    legend_title_text='Ano de Fabricação',
    yaxis_title='Preço Mediano ($)',
)

st.plotly_chart(fig_year_bars)
