import dash
from dash import dcc  # dash core components
from dash import html # dash html components
from dash.dependencies import Input, Output
import psycopg2
from dotenv import load_dotenv # pip install python-dotenv
import os
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import sqlite3
from io import BytesIO
import base64
import keras

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

model = keras.models.load_model('models/red_iris.keras')

# path to env file
env_path="G:\\Mi unidad\\24_actd\\actd_clase21\\env\\app.env"

# load env
load_dotenv(dotenv_path=env_path)

# extract env variables
USER=os.getenv('USER')
PASSWORD=os.getenv('PASSWORD')
HOST=os.getenv('HOST')
PORT=os.getenv('PORT')
DBNAME=os.getenv('DBNAME')

engine = psycopg2.connect(
    dbname="Base1",  
    user="postgres",
    password="Proyecto2Intento1",
    host="proyecto2prueba.czuvlz3sgcg3.us-east-1.rds.amazonaws.com",
    port="5432"
)
cursor = engine.cursor()

# Cargar los datos desde la base de datos
query = "SELECT * FROM hector_data"
df = pd.read_sql_query(query, engine)

#Interfaz Inicial del Usuario
app = dash.Dash(__name__)
app.layout = html.Div([
    dcc.RadioItems(
        id='interface-selector',
        options=[
            {'label': 'Perfil del Cliente', 'value': 'perfil'},
            {'label': 'Eficiencia de la Campaña', 'value': 'eficiencia'}
        ],
        value='perfil'
    ),
    html.Div(id='interface-content')
])

@app.callback(Output('interface-content', 'children'), Input('interface-selector', 'value'), suppress_callback_exceptions=True)
def display_interface(selected_interface):
    if selected_interface == 'perfil':
        return html.Div([
            dcc.Tabs(id="tabs-profile", value='age', children=[
                dcc.Tab(label='Edad', value='age'),
                dcc.Tab(label='Tipo de Trabajo', value='job'),
                dcc.Tab(label='Estado Civil', value='marital'),
                dcc.Tab(label='Educación', value='education'),
                dcc.Tab(label='Crédito Default', value='default'),
                dcc.Tab(label='Balance Promedio', value='balance'),
                dcc.Tab(label='Préstamo de Vivienda', value='housing'),
                dcc.Tab(label='Préstamo Personal', value='loan')
            ]),
            html.Div(id='tabs-content-profile')
        ])
    elif selected_interface == 'eficiencia':
        return html.Div([
            dcc.Tabs(id="tabs-campaign", value='contact', children=[
                dcc.Tab(label='Tipo de Contacto', value='contact'),
                dcc.Tab(label='Duración de la Llamada', value='duration'),
                dcc.Tab(label='Número de Contactos Previos', value='campaign'),
                dcc.Tab(label='Resultado de Campañas Previas', value='poutcome')
            ]),
            html.Div(id='tabs-content-campaign')
        ])

#INTEFAZ CARÁCTERISTICAS DEL CLIENTE    
@app.callback(Output('tabs-content-profile', 'children'), Input('tabs-profile', 'value'), suppress_callback_exceptions=True)
def render_profile_content(tab):
    if tab == 'job':
        return create_content("job", "Tipo de Trabajo", "Seleccione un tipo de trabajo")
    elif tab == 'housing':
        return display_simple_bar_chart('housing', 'Tiene Préstamo de Vivienda')
    elif tab == 'loan':
        return display_simple_bar_chart('loan', 'Tiene Préstamo Personal')
    elif tab == 'default':
        return display_simple_bar_chart('default', 'Tiene Crédito en Default')
    
    elif tab == 'age':
       # Realiza la consulta SQL para obtener solo las edades con y = 'yes'
        query_yes = "SELECT age FROM hector_data WHERE y = 'yes'"
        df_yes = pd.read_sql_query(query_yes, engine)

        # Realiza la consulta SQL para obtener solo las edades con y = 'no'
        query_no = "SELECT age FROM hector_data WHERE y = 'no'"
        df_no = pd.read_sql_query(query_no, engine)

        # Gráfico de distribución para y = 'yes'
        fig_yes = px.histogram(df_yes, x='age', title='Distribución de Edad de clientes que Aceptan un Depósito a término Fijo')

        # Gráfico de distribución para y = 'no'
        fig_no = px.histogram(df_no, x='age', title='Distribución de Edad de clientes que Rechazan un Depósito a término Fijo')

        return html.Div([
            dcc.Graph(figure=fig_yes),
            dcc.Graph(figure=fig_no)])

    elif tab == 'balance':
        # Consulta SQL para balances con y = 'yes'
        query_yes = "SELECT balance FROM hector_data WHERE y = 'yes'"
        df_yes = pd.read_sql_query(query_yes, engine)

        # Consulta SQL para balances con y = 'no'
        query_no = "SELECT balance FROM hector_data WHERE y = 'no'"
        df_no = pd.read_sql_query(query_no, engine)

        # Gráfico de distribución para y = 'yes'
        fig_yes = px.histogram(df_yes, x='balance', title='Distribución de Balance de clientes que Aceptan un Depósito a término Fijo')

        # Gráfico de distribución para y = 'no'
        fig_no = px.histogram(df_no, x='balance', title='Distribución de Balance de clientes que Rechazan un Depósito a término Fijo')

        return html.Div([
            dcc.Graph(figure=fig_yes),
            dcc.Graph(figure=fig_no)])
    
    elif tab == 'marital':
        return create_content("marital", "Estado Civil", "Seleccione un estado civil")
    elif tab == 'education':
        return create_content("education", "Nivel Educativo", "Seleccione un nivel educativo")
    # Agregar más condiciones aquí para otras pestañas si es necesario

def create_content(column, title, placeholder):
    return html.Div([
        dcc.RadioItems(
            id=f'{column}-option-selector',
            options=[
                {'label': 'Mostrar Gráficas Combinadas', 'value': 'combined'},
                {'label': f'Seleccionar {title}', 'value': 'dropdown'}
            ],
            value='combined'
        ),
        html.Div(id=f'{column}-content')
    ])

@app.callback(Output('job-content', 'children'), Input('job-option-selector', 'value'), suppress_callback_exceptions=True)
def display_job_option(selected_option):
    return display_option(selected_option, 'job', 'Tipo de Trabajo')

@app.callback(Output('marital-content', 'children'), Input('marital-option-selector', 'value'), suppress_callback_exceptions=True)
def display_marital_option(selected_option):
    return display_option(selected_option, 'marital', 'Estado Civil')

@app.callback(Output('education-content', 'children'), Input('education-option-selector', 'value'), suppress_callback_exceptions=True)
def display_education_option(selected_option):
    return display_option(selected_option, 'education', 'Nivel Educativo')

def display_option(selected_option, column, title):
    if selected_option == 'combined':
        query_yes = f"SELECT {column}, COUNT(*) as yes_count FROM hector_data WHERE y = 'yes' GROUP BY {column}"
        df_yes = pd.read_sql_query(query_yes, engine)

        query_no = f"SELECT {column}, COUNT(*) as no_count FROM hector_data WHERE y = 'no' GROUP BY {column}"
        df_no = pd.read_sql_query(query_no, engine)

        df = pd.merge(df_yes, df_no, on=column, how='outer').fillna(0)
        df['total'] = df['yes_count'] + df['no_count']
        df['percentage_yes'] = (df['yes_count'] / df['total']) * 100
        df['cumulative_percentage'] = df['percentage_yes'].cumsum()

        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            x=df[column],
            y=df['yes_count'],
            name='Yes Count',
            marker_color='green'
        ))
        fig1.add_trace(go.Scatter(
            x=df[column],
            y=df['cumulative_percentage'],
            name='Cumulative Percentage',
            yaxis='y2',
            mode='lines+markers',
            marker_color='black'
        ))
        fig1.update_layout(
            title=f'{title} con Clientes que Aceptan el Depósito a término fijo',
            yaxis=dict(title='Cantidad de Satisfechos'),
            yaxis2=dict(title='Porcentaje Acumulativo', overlaying='y', side='right', showgrid=False),
            xaxis=dict(title=title)
        )

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=df[column],
            y=df['no_count'],
            name='No Count',
            marker_color='red'
        ))
        fig2.add_trace(go.Scatter(
            x=df[column],
            y=df['cumulative_percentage'],
            name='Cumulative Percentage',
            yaxis='y2',
            mode='lines+markers',
            marker_color='black'
        ))
        fig2.update_layout(
            title=f'{title} con Clientes que Rechazan el Depósito a término fijo',
            yaxis=dict(title='Cantidad de No Satisfechos'),
            yaxis2=dict(title='Porcentaje Acumulativo', overlaying='y', side='right', showgrid=False),
            xaxis=dict(title=title)
        )

        return html.Div([
            dcc.Graph(figure=fig1),
            dcc.Graph(figure=fig2)
        ])

    elif selected_option == 'dropdown':
        query_unique = f"SELECT DISTINCT {column} FROM hector_data"
        df_unique = pd.read_sql_query(query_unique, engine)
        options = [{'label': value, 'value': value} for value in df_unique[column].unique()]

        return html.Div([
            dcc.Dropdown(id=f'{column}-dropdown', options=options, placeholder=f"Seleccione {title.lower()}"),
            html.Div(id=f'{column}-bar-chart')
        ])

@app.callback(Output('job-bar-chart', 'children'), Input('job-dropdown', 'value'), suppress_callback_exceptions=True)
def display_job_bar_chart(selected_value):
    return display_bar_chart(selected_value, 'job')

@app.callback(Output('marital-bar-chart', 'children'), Input('marital-dropdown', 'value'), suppress_callback_exceptions=True)
def display_marital_bar_chart(selected_value):
    return display_bar_chart(selected_value, 'marital')

@app.callback(Output('education-bar-chart', 'children'), Input('education-dropdown', 'value'), suppress_callback_exceptions=True)
def display_education_bar_chart(selected_value):
    return display_bar_chart(selected_value, 'education')

def display_bar_chart(selected_value, column):
    if selected_value:
        query = f"SELECT y, COUNT(*) as count FROM hector_data WHERE {column} = '{selected_value}' GROUP BY y"
        df_counts = pd.read_sql_query(query, engine)

        fig = px.bar(df_counts, x='y', y='count', title=f'Distribución de y para {selected_value}', labels={'y': 'Resultado', 'count': 'Cantidad'})

        return dcc.Graph(figure=fig)
    return html.Div(f"Seleccione un {column} para ver el gráfico")

def display_simple_bar_chart(column, title):
    # Realizar consultas SQL para obtener los conteos de 'yes' y 'no' en la variable de interés 'y'
    query = f"SELECT {column}, y, COUNT(*) as count FROM hector_data GROUP BY {column}, y"
    df_counts = pd.read_sql_query(query, engine)

    # Crear gráfico de barras
    fig = px.bar(
        df_counts,
        x=column,
        y='count',
        color='y',
        barmode='group',
        title=f'Distribución de {title} por Variable de Interés',
        labels={column: title, 'count': 'Cantidad', 'y': 'Variable de Interés'}
    )
    return html.Div([dcc.Graph(figure=fig)])


#INTERFAZ EFICIENCIA DE CAMPAÑA
@app.callback(Output('tabs-content-campaign', 'children'),
              Input('tabs-campaign', 'value'),
              suppress_callback_exceptions=True)


def render_campaign_content(tab):
    if tab == 'contact':
        # Consulta SQL para obtener los datos
        query = "SELECT contact, y FROM hector_data"
        df_contact = pd.read_sql_query(query, engine)

        # Agrupar los datos para crear la tabla de frecuencia
        heatmap_data = df_contact.groupby(['contact', 'y']).size().unstack(fill_value=0)

        # Crear el heatmap usando Plotly
        fig = px.imshow(heatmap_data,
                        color_continuous_scale='Viridis',
                        labels=dict(x='Respuesta (y)', y='Tipo de Contacto', color='Número de Contactos'))

        # Configurar el título
        fig.update_layout(title='Mapa de Calor del Tipo de Contacto')

        return html.Div([
            dcc.Graph(figure=fig)
        ])
    elif tab == 'duration':
        query = """
        SELECT duration, balance, y
        FROM hector_data
        """
        # Ejecutar la consulta
        df = pd.read_sql_query(query, engine)

        # Separar los datos por suscripción
        suscrito = df[df['y'] == 'yes']
        no_suscrito = df[df['y'] == 'no']

        # Crear la gráfica de dispersión
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(suscrito['duration'], suscrito['balance'], color='green', label='Suscrito', alpha=0.6)
        ax.scatter(no_suscrito['duration'], no_suscrito['balance'], color='red', label='No Suscrito', alpha=0.6)

        # Añadir etiquetas y título
        ax.set_xlabel("Duración del Último Contacto (segundos)")
        ax.set_ylabel("Balance")
        ax.set_title("Duración del Último Contacto vs Balance según Suscripción")

        # Añadir leyenda
        ax.legend()

        # Guardar la gráfica como imagen en un buffer de memoria
        buffer = BytesIO()
        fig.savefig(buffer, format='png')
        buffer.seek(0)
        plt.close(fig)

        # Convertir la imagen a formato base64
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        image_src = f"data:image/png;base64,{image_base64}"

        # Mostrar la imagen en Dash
        return html.Div([
            html.H3("Duración del Último Contacto vs Balance según Suscripción"),
            html.Img(src=image_src)
        ])
    elif tab == 'poutcome':
        # Consulta SQL para obtener los datos para el resultado de campañas previas
        query = """
        SELECT poutcome, y
        FROM hector_data
        """
        df_poutcome = pd.read_sql_query(query, engine)

        # Crear la tabla de frecuencia sin agrupar en 'y'
        heatmap_data = df_poutcome['poutcome'].value_counts().to_frame().sort_index().T

        # Crear el heatmap usando Plotly
        fig = px.imshow(heatmap_data,
                        color_continuous_scale='Viridis',
                        labels=dict(x='Resultado de la Campaña', y='Frecuencia', color='Número de Contactos'))

        # Configurar el título
        fig.update_layout(title='Mapa de Calor del Resultado de Campañas Previas')

        return html.Div([
            dcc.Graph(figure=fig)
        ])
    elif tab == 'campaign':
        # Consulta SQL para obtener los datos para la variable 'campaign' y 'y'
        query = "SELECT campaign, y FROM hector_data"
        df_campaign = pd.read_sql_query(query, engine)

        # Filtrar los datos por suscripción
        suscrito = df_campaign[df_campaign['y'] == 'yes']
        no_suscrito = df_campaign[df_campaign['y'] == 'no']

        # Crear los histogramas para ambas distribuciones
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), sharey=True)

        # Histograma para los clientes suscritos
        ax1.hist(suscrito['campaign'], bins=10, color='green', alpha=0.7)
        ax1.set_title("Distribución de Número de Contactos Previos (Suscrito)")
        ax1.set_xlabel("Número de Contactos Previos")
        ax1.set_ylabel("Frecuencia")

        # Histograma para los clientes no suscritos
        ax2.hist(no_suscrito['campaign'], bins=10, color='red', alpha=0.7)
        ax2.set_title("Distribución de Número de Contactos Previos (No Suscrito)")
        ax2.set_xlabel("Número de Contactos Previos")

        # Guardar la gráfica como imagen en un buffer de memoria
        buffer = BytesIO()
        fig.savefig(buffer, format='png')
        buffer.seek(0)
        plt.close(fig)

        # Convertir la imagen a formato base64
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        image_src = f"data:image/png;base64,{image_base64}"

        # Mostrar la imagen en Dash
        return html.Div([
            html.H3("Distribución de Número de Contactos Previos por Suscripción"),
            html.Img(src=image_src)
        ])

if __name__ == '__main__':
    app.run_server(debug=True)