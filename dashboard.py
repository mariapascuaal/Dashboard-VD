import streamlit as st
import pandas as pd
import plotly.express as px

#######################
# Page configuration
st.set_page_config(
    page_title="Dashboard VD",
    page_icon="🐭",
    layout="wide",
    initial_sidebar_state="expanded"
)

#######################
# CSS styling
st.markdown("""
<style>
/* Sidebar width adjustment */
[data-testid="stSidebar"] {
    width: 10%; /* Sidebar occupies 10% of the width */
}

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    background-color: #393939;
    text-align: center;
    padding: 15px 0;
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}

[data-testid="stMetricDeltaIcon-Up"],
[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    transform: translateX(-50%);
}

</style>
""", unsafe_allow_html=True)

#######################
# Data loading

df_0 = pd.read_csv("./csv/spikes_0.csv", delimiter=";")
df_0 = df_0[["timestamps", "neuron_ids"]]

df_1 = pd.read_csv("./csv/spikes_1.csv", delimiter=";")
df_1 = df_1[["timestamps", "neuron_ids"]]

df_2 = pd.read_csv("./csv/spikes_2.csv", delimiter=";")
df_2 = df_2[["timestamps", "neuron_ids"]]

#######################
# Sidebar
with st.sidebar:
    st.title('Dashboard para la visualización de datos cerebrales 🐭')
    
    # Selectbox for dataset selection
    dataset_choice = st.selectbox(
        "Selecciona el conjunto de datos:",
        ("df0", "df1", "df2", "todos") 
    )

#####################
# Visualization

def make_scatterplot(data):
    tamaño_puntos = 0.9
    relacion_aspecto = 1.5  # Relación de aspecto para hacer el gráfico más ancho

    # Crear gráfico de dispersión en Plotly Express
    fig = px.scatter(
        data,
        x="timestamps",         # Eje X
        y="neuron_ids",         # Eje Y
    )

    # Ajustes adicionales del gráfico
    fig.update_layout(
        width=720 * relacion_aspecto,   # Ajustar el ancho del gráfico según la relación de aspecto
        height=550,                     # Altura fija
        xaxis_title="Timestamps",       # Etiqueta del eje X
        yaxis_title="Neuron IDs",       # Etiqueta del eje Y
        font=dict(size=20),             # Tamaño de la fuente
    )

    fig.update_traces(marker=dict(size=tamaño_puntos))
    # Configurar límites de los ejes
    fig.update_xaxes(range=[0, data['timestamps'].max()])  # Límites del eje X
    fig.update_yaxes(range=[1, data['neuron_ids'].max()])  # Límites del eje Y

    return fig

def make_line_time_series(data, length_interval):
    bins = range(0, 3000 + length_interval, 100)  # 0 a 3000 ms en intervalos de 100 ms

    # Agregamos una nueva columna al DataFrame con las etiquetas de los intervalos
    data.loc[:, 'interval'] = pd.cut(data['timestamps'], bins=bins, labels=False) + 1

    df_agrupacion_intervalos = data.groupby('interval').size().reset_index(name='spikes')

    fig = px.line(
        df_agrupacion_intervalos,
        x="interval",
        y="spikes",
        markers=True,
    )

    # Ajustes adicionales del gráfico
    fig.update_layout(
        width=1000,
        height=600,
        xaxis_title="Interval",
        yaxis_title="Spikes",
        font=dict(size=20),
    )

    return fig

def compare_datasets_lineplot(grouped_data, long_interval):
    # Definir una secuencia personalizada de colores
    custom_colors= ['red', 'green', 'blue']

    fig = px.line(
        grouped_data,
        x='interval',
        y='spikes',
        color='dataset_ID',
        title=f'Number of spikes per {long_interval} ms interval with lineplot',
        labels={
            'interval': 'Intervals',
            'spikes': 'Number of spikes',
        },
        color_discrete_sequence=custom_colors  # Aplicar los colores personalizados
    )

    return fig

def compare_datasets_boxplot(grouped_data, long_interval):
    custom_colors= ['red', 'green', 'blue']
    fig = px.box(
        grouped_data,
        x='dataset_ID',
        y='spikes',
        title=f'Number of spikes per {long_interval} ms interval with boxplot',
        labels={
            'dataset_ID': 'Dataset ID',
            'spikes': 'Number of spikes'
        },
        color='dataset_ID',  # Use dataset_ID for color mapping
        color_discrete_sequence=custom_colors  # Apply the specified colors
    )

    return fig

def add_dataset_column(df, i):
    df['dataset_ID'] = i
    return df
  
def add_interval_column(df, long_interval):
    # Definimos los límites de los intervalos
    bins = range(0, 3000 + long_interval, long_interval)  # 0 a 3000 ms en intervalos de long_interval ms

    # Agregamos una nueva columna al DataFrame con las etiquetas de los intervalos
    df.loc[:, 'interval'] = pd.cut(df['timestamps'], bins=bins, labels=False) + 1
    
    return df

def agrupar_datos(length_interval, df0, df1, df2):
    dataframes = [df0, df1, df2]

    for i, df in enumerate(dataframes):
        df = add_dataset_column(df, i)
        df = add_interval_column(df, length_interval)
      
    df_agrupacion_intervalos = pd.concat(dataframes, ignore_index=True)
    df_agrupacion_intervalos = df_agrupacion_intervalos.groupby(['interval', 'dataset_ID']).size().reset_index(name='spikes')
    return df_agrupacion_intervalos


#######################
# Dashboard Main Panel (Single Column)
if dataset_choice == "todos":
    grouped_data = agrupar_datos(100, df_0, df_1, df_2)
    lineplot = compare_datasets_lineplot(grouped_data, 100)
    st.plotly_chart(lineplot, use_container_width=True)
    boxplot = compare_datasets_boxplot(grouped_data, 100)
    st.plotly_chart(boxplot, use_container_width=True)

else:
    if dataset_choice == "df0":
        df = df_0
    elif dataset_choice == "df1":
        df = df_1
    else:
        df = df_2

    # Mostrar los gráficos individuales
    st.markdown(f'#### Datos de la simulación: ({dataset_choice})')
    scatterplot = make_scatterplot(df)
    st.plotly_chart(scatterplot, use_container_width=True)
    time_series = make_line_time_series(df, 100)
    st.plotly_chart(time_series, use_container_width=True)
