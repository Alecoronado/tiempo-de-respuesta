import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import io

# Configuración inicial de la página
st.set_page_config(page_title="Análisis de Eficiencia Operativa", page_icon="📊")

# URLs de las hojas de Google Sheets
data_url= "https://docs.google.com/spreadsheets/d/e/2PACX-1vQE1hYnTcdOn72tyNOEQ_6L97XtPx8Hsd1ep-wxi9rLaJJm0KWTGb7JonuPzO-EyQH8g2UZ9rwK0CuF/pub?gid=1428049919&single=true&output=csv"

# Función para cargar los datos desde la URL
def load_data_from_url(url):
    try:
        return pd.read_csv(url, header=0)
    except Exception as e:
        st.error("Error al cargar los datos: " + str(e))
        return None

# Aplicación Streamlit
def main():
    st.title("Análisis de Eficiencia Operativa")

    # Carga los datos
    data = load_data_from_url(data_url)

    if data is not None:
        st.dataframe(data)

        # Configurar el estilo de Seaborn para los gráficos
        sns.set_theme(style="whitegrid")

   # Definir la paleta de colores para los países
        country_colors = {
            "Argentina": "#36A9E1",
            "Bolivia": "#F39200",
            "Brasil": "#009640",
            "Paraguay": "#E30613",
            "Uruguay": "#27348B"
        }
        # Filtros en la parte superior
        # Filtro de línea temporal para el año
        years = data['AÑO'].dropna().astype(int)
        min_year, max_year = int(years.min()), int(years.max())
        selected_years = st.slider('Selecciona el rango de años:', min_year, max_year, (min_year, max_year))

        # Filtro por estación con opción "Todas"
        all_stations = ['Todas'] + list(data['Tipo_KPI'].dropna().unique())
        selected_station = st.selectbox('Selecciona una Estación', all_stations)

        # Filtro por país con opción "Todos"
        all_countries = ['Todos'] + list(data['Pais'].dropna().unique())
        selected_countries = st.multiselect('Selecciona Países', all_countries, default='Todos')

        # Aplicar filtros al DataFrame
        filtered_df = data[
            (data['AÑO'] >= selected_years[0]) &
            (data['AÑO'] <= selected_years[1])
        ]

        # Filtro por estación con opción "Todas"
        if selected_station != 'Todas':
            filtered_df = filtered_df[filtered_df['Tipo_KPI'] == selected_station]

        # Filtro por país con opción "Todos"
        if 'Todos' not in selected_countries:
            filtered_df = filtered_df[filtered_df['Pais'].isin(selected_countries)]

        # Incluir gráficos
        st.header("         Análisis de la Eficiencia Operativa")
        figsize = (7, 5)  # Definir el tamaño de la figura para los gráficos

        # Cálculo de KPI Promedio y conteo de operaciones únicas
        average_kpi = filtered_df['KPI'].mean()
        unique_operation_count = filtered_df['IDEtapa'].nunique()
        total_stations = filtered_df['Tipo_KPI'].count() # Conteo total de estaciones (filas)

        # Mostrar métricas de KPI Promedio, conteo de operaciones únicas y total de estaciones
        col1, col2, col3 = st.columns(3)
        col1.metric("Tiempo Promedio en Meses", f"{average_kpi:.2f}")
        col2.metric("Proyectos", unique_operation_count)
        col3.metric("Total de Estaciones", total_stations)

       
        # Función auxiliar para agregar etiquetas de valor en los gráficos de barra
        def add_value_labels(ax, is_horizontal=False):
            for rect in ax.patches:
                # Obtener las coordenadas X e Y del comienzo de la barra
                x_value = rect.get_x() + rect.get_width() / 2
                y_value = rect.get_y() + rect.get_height() / 2
                # Decidir si la etiqueta es para un gráfico horizontal o vertical
                if is_horizontal:
                    value = rect.get_width()
                    label = f"{int(value)}"  # Convertir a entero y formatear
                    ax.text(value, y_value, label, ha='left', va='center')
                else:
                    value = rect.get_height()
                    label = f"{int(value)}"  # Convertir a entero y formatear
                    ax.text(x_value, value, label, ha='center', va='bottom')

        # Utilizar st.columns para colocar gráficos lado a lado
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Tiempo de Respuesta Promedio en Meses por País")
            fig, ax = plt.subplots(figsize=figsize)
            
            # Calcular el KPI promedio por país
            kpi_avg_by_country = filtered_df.groupby('Pais')['KPI'].mean().sort_values(ascending=True)
            
            # Crear una lista de colores que coincida con el orden de los países en 'kpi_avg_by_country'
            country_order = kpi_avg_by_country.index
            country_palette = [country_colors.get(country, "#333333") for country in country_order]

            # Dibujar el gráfico de barras con la paleta de colores específica
            sns.barplot(x=kpi_avg_by_country.values, y=country_order, ax=ax, palette=country_palette)
            
            # Agregar las etiquetas de valor
            add_value_labels(ax, is_horizontal=True)
            
            plt.tight_layout()
            st.pyplot(fig)

        with col2:
            st.subheader("Eficiencia en Tiempos de Respuesta")
            fig, ax = plt.subplots(figsize=figsize)
            productivity_count = filtered_df['Productividad'].value_counts().sort_values()
            sns.barplot(x=productivity_count.values, y=productivity_count.index, ax=ax, palette='Spectral')
            add_value_labels(ax, is_horizontal=True)
            plt.tight_layout()
            st.pyplot(fig)

        # Reemplazamos el gráfico de "Tiempo de Respuesta a lo largo del tiempo" por el gráfico de barras apiladas
        st.subheader("Tiempo Promedio por Año y Estaciones")

        # Definir la paleta de colores para los países
        station_colors = {
            "Vigencia": "#36A9E1",
            "Aprobación": "#F39200",
            "Elegibilidad": "#009640",
            "PrimerDesembolso": "#E30613"
        }

        # Aplicar filtros al DataFrame
        filtered_df = data[
            (data['AÑO'] >= selected_years[0]) &
            (data['AÑO'] <= selected_years[1])
        ]

        if selected_station != 'Todas':
            filtered_df = filtered_df[filtered_df['Tipo_KPI'] == selected_station]

        # Modificado para manejar múltiples selecciones de países
        if 'Todos' not in selected_countries:
            filtered_df = filtered_df[filtered_df['Pais'].isin(selected_countries)]
    
        # Preparación de datos para el gráfico de barras apiladas por estaciones
        kpi_by_year_station = filtered_df.pivot_table(values='KPI', index='AÑO', columns='Tipo_KPI', aggfunc='mean').fillna(0)
        kpi_by_year_station.index = kpi_by_year_station.index.map(int)

        # Creamos una lista de colores basada en los países presentes en el DataFrame y en el orden correcto
        # Crear una lista de colores basada en las estaciones presentes en el DataFrame
        colors = [station_colors.get(station, "#333333") for station in kpi_by_year_station.columns]

        # Gráfico de barras apiladas con colores específicos
        fig, ax = plt.subplots(figsize=(12, 6))
        kpi_by_year_station.plot(kind='bar', stacked=True, color=colors, ax=ax)

        # Agregar etiquetas de valor a cada segmento de barra
        for i, (year, values) in enumerate(kpi_by_year_station.iterrows()):
            height_accumulator = 0  # Acumulador para la altura de las barras
            for station in values.index:
                value = values[station]
                if value > 0:  # Solo agregamos etiquetas a valores positivos
                    label_y = height_accumulator + (value / 2)
                    ax.text(i, label_y, f'{int(value)}', ha='center', va='center', fontsize=9, color='white')
                    height_accumulator += value
            # Colocar la etiqueta del total acumulado en la parte superior de la barra
            ax.text(i, height_accumulator, f'{int(height_accumulator)}', ha='center', va='bottom', fontsize=9, color='black')

        ax.set_ylabel('KPI Promedio')
        ax.set_xlabel('Año')
        ax.set_xticklabels([str(x) for x in kpi_by_year_station.index], rotation=0)
        ax.legend(title='Estación', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        st.pyplot(fig)

        filtered_df['AÑO'] = filtered_df['AÑO'].astype(int)     

        # Pivotear el DataFrame para obtener el KPI promedio por país y año
        kpi_pivot_df = filtered_df.pivot_table(values='KPI', index='Pais', columns='AÑO', aggfunc='mean')

        # Redondear todos los valores numéricos a dos decimales
        kpi_pivot_df = kpi_pivot_df.round(2)

        # Opción para reemplazar los valores None/NaN con un string vacío
        kpi_pivot_df = kpi_pivot_df.fillna('')

        # Convertir las etiquetas de las columnas a enteros (los años)
        kpi_pivot_df.columns = kpi_pivot_df.columns.astype(int)

        # Resetear el índice para llevar 'ESTACIONES' a una columna
        kpi_pivot_df.reset_index(inplace=True)


        # Convertir el DataFrame pivotado a un archivo de Excel para la descarga
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            kpi_pivot_df.to_excel(writer, index=False)
            # No es necesario llamar a writer.save() aquí, se guarda automáticamente al finalizar el bloque with
        output.seek(0)  # Regresamos al principio del stream para que streamlit pueda leer el contenido

        # Muestra el DataFrame en la aplicación
        st.write("Datos Resumidos:")
        st.dataframe(kpi_pivot_df)

        # Botón de descarga en Streamlit
        st.download_button(
            label="Descargar KPI promedio por país y año como Excel",
            data=output,
            file_name='kpi_promedio_por_pais_y_año.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    # Incluir un nuevo gráfico
    st.header("KPI Promedio por País")

    # Preparar datos para el gráfico por país
    kpi_by_country = filtered_df.pivot_table(values='KPI', index='Pais', columns='AÑO', aggfunc='mean').fillna(0)
    kpi_by_country.index = kpi_by_country.index.map(str)

    # Crear una lista de colores basada en los países presentes en el DataFrame
    colors = [country_colors.get(country, "#333333") for country in kpi_by_country.index]

    # Gráfico de barras apiladas por país
    fig, ax = plt.subplots(figsize=(12, 6))
    kpi_by_country.plot(kind='bar', stacked=True, color=colors, ax=ax)

    # Agregar etiquetas de valor a cada segmento de barra
    for i, (country, values) in enumerate(kpi_by_country.iterrows()):
        height_accumulator = 0  # Acumulador para la altura de las barras
        for year in values.index:
            value = values[year]
            if value > 0:  # Solo agregamos etiquetas a valores positivos
                label_y = height_accumulator + (value / 2)
                ax.text(i, label_y, f'{value:.2f}', ha='center', va='center', fontsize=9, color='white')
                height_accumulator += value

    ax.set_ylabel('KPI Promedio')
    ax.set_xlabel('País')
    ax.set_xticklabels([str(x) for x in kpi_by_country.index], rotation=0)
    ax.legend(title='Año', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    st.pyplot(fig)

    # Crear la tabla pivotada con estaciones como filas y países como columnas
    st.header("KPI Promedio por Estación y País")

    # Pivotear el DataFrame para obtener el KPI promedio por estación (Tipo_KPI) y país
    kpi_pivot_df_by_station_country = filtered_df.pivot_table(values='KPI', index='Tipo_KPI', columns='Pais', aggfunc='mean')

    # Redondear todos los valores numéricos a dos decimales
    kpi_pivot_df_by_station_country = kpi_pivot_df_by_station_country.round(2)

    # Opción para reemplazar los valores None/NaN con un string vacío
    kpi_pivot_df_by_station_country = kpi_pivot_df_by_station_country.fillna('')

    # Muestra el DataFrame en la aplicación
    st.dataframe(kpi_pivot_df_by_station_country)

    # Convertir el DataFrame pivotado a un archivo de Excel para la descarga
    output_by_station_country = io.BytesIO()
    with pd.ExcelWriter(output_by_station_country, engine='openpyxl') as writer:
        kpi_pivot_df_by_station_country.to_excel(writer, index=True)
    output_by_station_country.seek(0)  # Regresamos al principio del stream para que streamlit pueda leer el contenido

    # Botón de descarga en Streamlit
    st.download_button(
        label="Descargar KPI promedio por estación y país como Excel",
        data=output_by_station_country,
        file_name='kpi_promedio_por_estacion_y_pais.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    # Gráfico de barras apiladas o agrupadas con KPI Promedio por País y Estación
    st.header("KPI Promedio por País y Estación")

    # Preparar los datos para el gráfico
    # Primero, creamos un DataFrame con los KPI promedios por país y estación
    kpi_avg_by_country_station = filtered_df.groupby(['Pais', 'Tipo_KPI'])['KPI'].mean().unstack(fill_value=0)

    # Crear el gráfico de barras
    fig, ax = plt.subplots(figsize=(10, 6))

    # Por defecto, pandas hace un gráfico de barras apiladas si no se especifica 'stacked=False'
    # Para un gráfico de barras agrupadas, se debe especificar 'stacked=False'
    kpi_avg_by_country_station.plot(kind='bar', stacked=True, ax=ax)  # Puedes cambiar a stacked=False si prefieres barras agrupadas

    # Agregar etiquetas de valor a cada segmento de barra si es un gráfico apilado
    if kpi_avg_by_country_station.shape[1] > 1:  # Solo si hay más de un Tipo_KPI por país
        for bars in ax.containers:
            ax.bar_label(bars, label_type='center', fmt='%.2f')

    # Personalizar el gráfico
    ax.set_ylabel('KPI Promedio')
    ax.set_xlabel('País')
    ax.set_title('KPI Promedio por País y Estación')
    ax.legend(title='Estación')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

    # Crear la tabla pivotada con estaciones como filas y años como columnas
    st.header("KPI Promedio por Estación y Año")

    # Pivotear el DataFrame para obtener el KPI promedio por estación (Tipo_KPI) y año
    kpi_pivot_df_by_station_year = filtered_df.pivot_table(values='KPI', index='Tipo_KPI', columns='AÑO', aggfunc='mean')

    # Redondear todos los valores numéricos a dos decimales
    kpi_pivot_df_by_station_year = kpi_pivot_df_by_station_year.round(2)

    # Opción para reemplazar los valores None/NaN con un string vacío
    kpi_pivot_df_by_station_year = kpi_pivot_df_by_station_year.fillna('')

    # Muestra el DataFrame en la aplicación
    st.dataframe(kpi_pivot_df_by_station_year)

    # Convertir el DataFrame pivotado a un archivo de Excel para la descarga
    output_by_station_year = io.BytesIO()
    with pd.ExcelWriter(output_by_station_year, engine='openpyxl') as writer:
        kpi_pivot_df_by_station_year.to_excel(writer, index=True)
    output_by_station_year.seek(0)  # Regresamos al principio del stream para que streamlit pueda leer el contenido

    # Botón de descarga en Streamlit
    st.download_button(
        label="Descargar KPI promedio por estación y año como Excel",
        data=output_by_station_year,
        file_name='kpi_promedio_por_estacion_y_año.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

if __name__ == "__main__":
    main()
