import requests
import pandas as pd
from io import BytesIO
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
colors = ['red', 'yellow', 'lightgreen','mediumseagreen' ,'green','seagreen', 
    'forestgreen', 'darkgreen']
cmap_semaforo = LinearSegmentedColormap.from_list('semaforo', colors)

# Definir los nombres de los meses
months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo']



# URL del archivo Excel
url_archivo = "https://www.indec.gob.ar/ftp/cuadros/economia/sh_emae_actividad_base2004.xls"


# Leer el archivo Excel directamente desde su URL
try:
    # Descarga el archivo desde la URL
    response = requests.get(url_archivo)
    response.raise_for_status()  # Esto lanzará una excepción si la descarga falla

    # Leer el contenido del archivo Excel en un DataFrame
    df = pd.read_excel(BytesIO(response.content),sheet_name=1, header=None, skiprows=2)

    # Configurar la tercera fila como encabezado de las columnas
    df.columns = df.iloc[0]

    # Eliminar las primeras tres filas para limpiar el DataFrame
    df = df[3:]

    # Filtrar todas las filas desde la primera que contiene '2024' en la primera columna
    idx_start = df[df.iloc[:, 0].astype(str).str.startswith('2024')].index[0]
    df_2024_onwards = df.loc[idx_start:]

    # Resetear el índice del DataFrame
    df_2024_onwards.reset_index(drop=True, inplace=True)

    # Mostrar el DataFrame resultante
    print(df_2024_onwards.head())

        # Extraer la tercera columna (asumiendo que la tercera columna es la de interés)
    data = df_2024_onwards.iloc[:, 2:].dropna().astype(float)  # Convertir a float si es necesario
    # Transponer el DataFrame para que las columnas estén en el eje vertical
    data_to_plot = data.transpose()
    
    # Recortar la lista de meses para que coincida con el número de columnas en el DataFrame
    num_columns = data_to_plot.shape[0]  # Número de columnas en el DataFrame transpuesto
    months_truncated = months[:num_columns]

    # Ajustar los límites de la escala de color para mejorar la dispersión
    vmin = data_to_plot.min().min()
    vmax = data_to_plot.max().max()

    # Crear el heatmap
    plt.figure(figsize=(14, 10))  # Ajustar el tamaño de la figura según sea necesario
    ax = sns.heatmap(data_to_plot, cmap=cmap_semaforo, cbar=True, annot=True, fmt=".1f")


    # Ajustar las etiquetas del eje x para que se muestren completas
    ax.set_xticks(range(len(months)))
    ax.set_xticks(range(len(months_truncated)))
    ax.set_xticklabels(months_truncated, rotation=0, ha='left', fontsize=8)  # Ajustar el tamaño de la fuente y la rotación
    plt.yticks(rotation=0, fontsize=8)  # Ajustar el tamaño de la fuente para las etiquetas del eje y

    # Ajustar el título y etiquetas de los ejes
    plt.title('Variación interanual sectorial', fontsize=14)
    plt.xlabel('2024', fontsize=12)
    plt.ylabel('Sectores', fontsize=12)

    # Ajustar los límites y el espaciado de los ejes
    plt.tight_layout(pad=1.0)  # Ajustar el diseño para evitar que se corten las etiquetas
    plt.show()

except requests.exceptions.RequestException as e:
    print(f"Error al descargar el archivo desde la URL: {e}")
except Exception as e:
    print(f"Error al leer el archivo desde la URL: {e}")