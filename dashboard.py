import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
df_0 = df_0[["attack", "timestamps", "neuron_ids"]]
df_FLO_0  = pd.read_csv("./csv/spikes_FLO_0.csv", delimiter=";")
df_FLO_0 = df_FLO_0[["attack", "timestamps", "neuron_ids"]]

df_1 = pd.read_csv("./csv/spikes_1.csv", delimiter=";")
df_1 = df_1[["attack","timestamps", "neuron_ids"]]
df_FLO_1  = pd.read_csv("./csv/spikes_FLO_1.csv", delimiter=";")
df_FLO_1 = df_FLO_1[["attack", "timestamps", "neuron_ids"]]

df_2 = pd.read_csv("./csv/spikes_2.csv", delimiter=";")
df_2 = df_2[["attack","timestamps", "neuron_ids"]]
df_FLO_2  = pd.read_csv("./csv/spikes_FLO_2.csv", delimiter=";")
df_FLO_2 = df_FLO_2[["attack", "timestamps", "neuron_ids"]]

#######################
# Sidebar
with st.sidebar:
    st.title('Dashboard para la visualización de datos cerebrales 🐭')
    
    # Selectbox for dataset selection
    dataset_choice = st.selectbox(
        "Selecciona el conjunto de datos:",
        ("df0", "df1", "df2", "todos") 
    )
    
    # Selectbox for time interval selection
    time_interval = st.selectbox(
        "Selecciona el intervalo de tiempo (ms):",
        [50, 75, 100, 150, 200, 300],
        index=2  # Valor por defecto (100 ms)
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
        title=f'Diagrama de dispersión de la simulación {dataset_choice}',
    )

    # Ajustar el tamaño del título
    fig.update_layout(title_font_size=24)

    # Centrar el título
    fig.update_layout(title_x=0.3)

    # Ajustes adicionales del gráfico
    fig.update_layout(
        width=600 * relacion_aspecto,   # Ajustar el ancho del gráfico según la relación de aspecto
        height=400,                     # Altura fija
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
    bins = range(0, 3000 + length_interval, length_interval)  # 0 a 3000 ms en intervalos de 100 ms

    # Agregamos una nueva columna al DataFrame con las etiquetas de los intervalos
    data.loc[:, 'interval'] = pd.cut(data['timestamps'], bins=bins, labels=False) + 1

    df_agrupacion_intervalos = data.groupby('interval').size().reset_index(name='spikes')

    fig = px.line(
        df_agrupacion_intervalos,
        x="interval",
        y="spikes",
        title=f"Serie temporal con {length_interval} ms",
        markers=True,
    )

    # Ajustar el tamaño del título
    fig.update_layout(title_font_size=24)

    # Centrar el título
    fig.update_layout(title_x=0.3)

    return fig

def time_series_spontaneous_vs_attack(data, dataFLO, length_interval):
    bins = range(0, 3000 + length_interval, length_interval)  # 0 a 3000 ms en intervalos de length_interval ms

    # Agregar una nueva columna al DataFrame con las etiquetas de los intervalos
    data.loc[:, 'interval'] = pd.cut(data['timestamps'], bins=bins, labels=False) + 1
    dataFLO.loc[:, 'interval'] = pd.cut(dataFLO['timestamps'], bins=bins, labels=False) + 1

    # Agrupación de los datos por intervalos
    df_agrupacion_intervalos = data.groupby('interval').size().reset_index(name='spikes')
    df_agrupacion_intervalos_FLO = dataFLO.groupby('interval').size().reset_index(name='spikes')

    # Crear el gráfico usando go.Scatter para que ambos tengan nombre
    fig = go.Figure()

    # Añadir la serie de datos 'spontaneous'
    fig.add_trace(
        go.Scatter(
            x=df_agrupacion_intervalos["interval"],
            y=df_agrupacion_intervalos["spikes"],
            mode='lines+markers',
            name='Spontaneous',  # Etiqueta para la leyenda
            line=dict(color='blue')  # Color de la línea
        )
    )

    # Añadir la serie de datos 'FLO attack'
    fig.add_trace(
        go.Scatter(
            x=df_agrupacion_intervalos_FLO["interval"],
            y=df_agrupacion_intervalos_FLO["spikes"],
            mode='lines+markers',
            name='FLO attack',  # Etiqueta para la leyenda
            line=dict(color='orange')  # Color de la línea
        )
    )

        # Añadir el título a la gráfica
    fig.update_layout(
        title=f'Serie temporal con ataque vs espontáneo {length_interval} ms',  # Título del gráfico
        title_font_size = 22,
        title_x = 0.1
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
        title=f'Serie temporal del caso espontáneo usando {long_interval} ms (lineplot)',
        labels={
            'interval': 'Intervals',
            'spikes': 'Number of spikes',
        },
        color_discrete_sequence=custom_colors  # Aplicar los colores personalizados
    )
    # Ajustar el tamaño del título
    fig.update_layout(title_font_size=22)

    # Centrar el título
    fig.update_layout(title_x=0.1)


    return fig

def compare_datasets_boxplot(grouped_data, long_interval):
    custom_colors= ['red', 'green', 'blue']
    fig = px.box(
        grouped_data,
        x='dataset_ID',
        y='spikes',
        title=f'Variabilidad del nº spikes (espontáneo, {long_interval} ms, boxplot)',
        labels={
            'dataset_ID': 'dataset ID',
            'spikes': 'Number of spikes'
        },
        color='dataset_ID',  # Use dataset_ID for color mapping
        color_discrete_sequence=custom_colors  # Apply the specified colors
    )
    # Ajustar el tamaño del título
    fig.update_layout(title_font_size=20)

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
    df_agrupacion_intervalos = df_agrupacion_intervalos.groupby(['attack', 'interval', 'dataset_ID']).size().reset_index(name='spikes')
    return df_agrupacion_intervalos

def compare_datasets_boxplot_attack(grouped_data, long_interval):
    # Crear el boxplot usando plotly express
    fig = px.box(grouped_data, x='interval', y='spikes', color='attack',
                 title=f"Comparación espontáneo vs ataque usando {long_interval} ms (boxplot)",
                 labels={'interval': 'Interval', 'spikes': 'Number of spikes'},
                 color_discrete_map={  # Mapa de colores personalizado
                     'Spontaneous': 'blue',  # Azul para spontaneous
                     'FLO': 'orange'         # Naranja para FLO
                 })

    # Ajustar el tamaño del título
    fig.update_layout(title_font_size=24)

    # Centrar el título
    fig.update_layout(title_x=0.2)

    # Actualizar el tamaño de la fuente de los ejes
    fig.update_layout(
        xaxis_title='Interval',  # Etiqueta del eje X
        yaxis_title='Number of spikes',  # Etiqueta del eje Y
        height = 600,
        font=dict(size=14)  # Tamaño general de la fuente
    )
    
    return fig

def compare_datasets_lineplot_attack(grouped_data, long_interval):
    # Crear gráfico con Plotly Express
    fig = px.line(
        grouped_data,
        x="interval",        # Eje X
        y="spikes",          # Eje Y
        color="attack",      # Diferenciar líneas por "attack"
        facet_col="dataset_ID",  # Crear subgráficos por "dataset_ID"
        facet_col_wrap=3,    # Agrupar las facetas en filas, 5 gráficos por fila
        title=f"Comparación espontáneo vs ataque usando {long_interval} ms (lineplot)",  # Título del gráfico principal
        labels={"interval": "Interval", "spikes": "Number of Spikes"},  # Etiquetas de los ejes
        height=500,          # Altura del gráfico
        width=1200,          # Anchura del gráfico
        color_discrete_map={  # Mapa de colores personalizado
            'Spontaneous': 'blue',  # Azul para spontaneous
            'FLO': 'orange'         # Naranja para FLO
        }
    )

    # Ajustar el tamaño del título
    fig.update_layout(title_font_size=24)

    # Centrar el título
    fig.update_layout(title_x=0.2)

    # Ajustar los títulos de las facetas
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1], font_size=14))  # Personalizar los títulos de faceta
    
    # Devolver la figura
    return fig



grouped_data = agrupar_datos(time_interval, df_0, df_1, df_2)
grouped_data_FLO = agrupar_datos(time_interval, df_FLO_0, df_FLO_1, df_FLO_2)
combined_data = pd.concat([grouped_data, grouped_data_FLO], ignore_index=True)

#######################
# Dashboard Main Panel (Single Column)
if dataset_choice == "todos":
    # Crear columnas para los gráficos
    col1, col2 = st.columns([3, 2])  # Primera columna es más grande que la segunda
    
    # Graficar el lineplot en col1
    with col1:
        lineplot = compare_datasets_lineplot(grouped_data, time_interval)  # Llamada correcta a la función
        st.plotly_chart(lineplot, use_container_width=True)

    # Graficar el boxplot en col2
    with col2:
        boxplot = compare_datasets_boxplot(grouped_data, time_interval)  # Llamada correcta a la función
        st.plotly_chart(boxplot, use_container_width=True)

    # Ahora mostrar el gráfico de compare_boxplot que debe ocupar ambas columnas
    compare_lineplot = compare_datasets_lineplot_attack(combined_data, time_interval)  # Llamada correcta a la función
    st.plotly_chart(compare_lineplot, use_container_width=True)  # Este gráfico ocupará las dos columnas anteriores

    # Ahora mostrar el gráfico de compare_boxplot que debe ocupar ambas columnas
    compare_boxplot = compare_datasets_boxplot_attack(combined_data, time_interval)  # Llamada correcta a la función
    st.plotly_chart(compare_boxplot, use_container_width=True)  # Este gráfico ocupará las dos columnas anteriores



else:
    if dataset_choice == "df0":
        df = df_0
        dfFLO = df_FLO_0
    elif dataset_choice == "df1":
        df = df_1
        dfFLO = df_FLO_1
    else:
        df = df_2
        dfFLO = df_FLO_2

    # Mostrar los gráficos individuales
    scatterplot = make_scatterplot(df)
    st.plotly_chart(scatterplot, use_container_width=True)

    # Crear dos columnas para las dos gráficas time_series y time_series_FLO
    col1, col2 = st.columns(2)  # Dividimos en dos columnas de igual tamaño

    with col1:
        time_series = make_line_time_series(df, time_interval)
        st.plotly_chart(time_series, use_container_width=True)

    with col2:
        time_series_FLO = time_series_spontaneous_vs_attack(df, dfFLO, time_interval)
        st.plotly_chart(time_series_FLO, use_container_width=True)
    