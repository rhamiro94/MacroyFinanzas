# -*- coding: utf-8 -*-


!pip install --upgrade pandas

#Instalo librerias
!pip install requests
!pip install alphacast

from alphacast import Alphacast
import pandas as pd
import io

API_key = 'ak_Sm9t04ouWlOc4VHzsmgm'

alphacast = Alphacast(API_key)

alphacast.datasets.dataset(5288).metadata()

df = pd.read_csv( io.StringIO(alphacast.datasets.dataset(5288).download_data("csv").decode("UTF-8")))

#Traigo la data del dataset fx premiums daily
df = alphacast.datasets.dataset(5288).download_data("pandas")

#Embi codigo 5293
#Traigo la data del dataset fx premiums daily
df_em = alphacast.datasets.dataset(5293).download_data("pandas")

#Ahora utilizamos la funcion para mergear y generar un df
# Definir el rango temporal
fecha_inicio = '2012-01-18'
fecha_fin = '2024-05-05'

# Filtrar filas dentro del rango temporal para df1
df_10y = df[(df['Date'] >= fecha_inicio) & (df['Date'] <= fecha_fin)]
df_emar10y = df_em[(df_em['Date'] >= fecha_inicio) & (df_em['Date'] <= fecha_fin)]

#Ahora transformo el otro df
#Necesito una columna que me muestre el cclgalicia
# Definir una función que realizará la ope de ccl
def funcion_ccl(x, y):
    return (x/y)*10  # Puedes cambiar esta función según tu necesidad

# Aplicar la función a las columnas correspondientes y crear una nueva columna
df_10y['CCL_GGAL'] = df_10y.apply(lambda row: funcion_ccl(row['GGAL'], row['ADR GGAL']), axis=1)

# Mostrar el DataFrame con la nueva columna
print(df_10y)

#Ahora uso una funcion identica para calcular el merval a ccl de galicia
# Definir una función que realizará la ope de ccl
def merv_ccl(x, y):
    return (x/y) # Puedes cambiar esta función según tu necesidad

# Aplicar la función a las columnas correspondientes y crear una nueva columna
df_10y['merval_ccl'] = df_10y.apply(lambda row: merv_ccl(row['Merval'], row['CCL_GGAL']), axis=1)

# Mostrar el DataFrame con la nueva columna
print(df_10y)

print(df_10y['Date'].value_counts())
print(df_emar10y['Date'].value_counts())

df_emar10y=df_emar10y[df_emar10y['country'] == 'Argentina']
df_emar10y

df_comb = pd.merge(df_10y, df_emar10y, left_on='Date', right_on='Date', how='inner')

#Defino columnas a mantener
colum=['Date','ADR GGAL','Dolar CCL','BLUE','Dolar Mayorista','Dolar Oficial','Dolar MEP','Brecha CCL','merval_ccl','CCL_GGAL','EMBI Global Diversified Subindices']
df_comb = df_comb[colum]

# Mostrar el DataFrame filtrado
print(df_comb)

df['Date'].info()

# Definir los rangos temporales y las categorías
df_comb['Date'] = pd.to_datetime(df_comb['Date'])

# Definir los rangos temporales y las categorías
rangos_temporales = [
    pd.to_datetime('2015-10-12'), pd.to_datetime('2019-10-11'),
    pd.to_datetime('2023-10-12'), pd.to_datetime('2024-10-11')
]
categorias = ['MM', 'AF', 'JM']

# Categorizar las fechas como MM, AF o JM
df_comb['Presidente'] = pd.cut(df_comb['Date'], bins=rangos_temporales, labels=categorias, right=False)

# Verificar el resultado

df_comb

# Crear la columna 'Presidente' con la categoría por defecto 'Sin presidente'
# Convertir la columna 'Presidente' a un tipo de datos de objeto (object)
df_comb['Presidente'] = df_comb['Presidente'].astype('object')

# Reemplazar los valores NaN por cero en la columna 'Presidente'
df_comb['Presidente'].fillna("CFK", inplace=True)

# Contar el número de categorías únicas en la columna 'Presidente'
num_categorias = df_comb['Presidente'].nunique()

# Mostrar el resultado
print("Número de categorías únicas en la columna 'Presidente':", num_categorias)

df_comb

df_filtrado = df_comb[df_comb['Presidente'] == "AF"]
df_filtrado

df_comb['Date'] = pd.to_datetime(df_comb['Date'])

import seaborn as sns
import matplotlib.pyplot as plt

sns.set_style("darkgrid")


# Crear un gráfico de dispersión con niveles
fig, ax = plt.subplots(figsize=(15, 6))
sns.scatterplot(x='EMBI Global Diversified Subindices', y='merval_ccl', hue='Presidente', data=df_comb, palette='Set2', marker='o', s=50)

# Puedes personalizar el gráfico según tus necesidades
plt.xlabel('Riesgo país')
plt.ylabel('Merval CCL')
plt.title('Merval vs Riesgo país')

# Mostrar la leyenda
plt.legend(title='Presidente')

# Obtener las coordenadas y la fecha del último dato
ultimo_dato = df_comb.tail(1)
coord_x = ultimo_dato['EMBI Global Diversified Subindices'].iloc[0]
coord_y = ultimo_dato['merval_ccl'].iloc[0]
fecha_ultimo_dato = ultimo_dato['Date'].iloc[0].strftime('%Y-%m-%d')  # Convertir la fecha a una cadena con el formato deseado

# Anotar el último dato con la etiqueta de la fecha correspondiente
plt.annotate(f'Último dato: {fecha_ultimo_dato}', xy=(coord_x, coord_y),
             xytext=(coord_x - 5, coord_y + 50),
             arrowprops=dict(facecolor='black', shrink=0.05))

plt.show()

columna_especifica = 'Brecha CCL'  # Reemplaza 'nombre_de_la_columna' con el nombre real de tu columna
df_filtrado = df_comb[df_comb[columna_especifica] > 0]




fig, ax = plt.subplots(figsize=(10, 4))


# Definir los límites del eje y
limite_inferior_y = 0
media = df_filtrado['Brecha CCL'].mean()


# Crear el gráfico de líneas
plt.plot(df_filtrado['Date'], df_filtrado['Brecha CCL'], linestyle='-', color='b')

# Puedes personalizar el gráfico según tus necesidades
plt.xlabel('Fecha')
plt.ylabel('Valor')
plt.title('Brecha fx oficial vs CCL')
plt.axhline(y=media, color='r', linestyle='--', label=f'Media = {media:.2f}')
# Encontrar los tres máximos
top_tres_maximos_indices = df_filtrado['Brecha CCL'].nlargest(3).index
top_tres_maximos_valores = df_filtrado[top_tres_maximos_indices, 'Brecha CCL']

# Resaltar los tres máximos con marcadores
plt.scatter(df.loc[top_tres_maximos_indices, 'Fecha'], top_tres_maximos_valores, color='red', label='Top 3 Máximos')

# Mostrar la cuadrícula
plt.grid(True)

# Mostrar el gráfico
plt.show()

# Ajustar el tamaño de la figura y dividirla en dos cuadrantes
fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(15, 5))

# Boxplot para Variable1 en el primer cuadrante
sns.boxplot(x='Presidente', y='Brecha CCL', data=df_comb, hue='Presidente', palette='Set2', ax=axes[0])
axes[0].set_xlabel('Presidente')
axes[0].set_ylabel('Brecha CCL')
axes[0].set_title('Brecha CCL por mandato')

# Boxplot para Variable2 en el segundo cuadrante
sns.boxplot(x='Presidente', y='merval_ccl', data=df_comb, hue='Presidente', palette='Set2', ax=axes[1])
axes[1].set_xlabel('Presidente')
axes[1].set_ylabel('merval_ccl')
axes[1].set_title('merval_ccl por mandato')
# Boxplot para Variable2 en el segundo cuadrante
sns.boxplot(x='Presidente', y='EMBI Global Diversified Subindices', data=df_comb, hue='Presidente', palette='Set2', ax=axes[2])
axes[2].set_xlabel('Presidente')
axes[2].set_ylabel('Riesgo pais')
axes[2].set_title('Riesgo pais por mandato')

# Supongamos que quieres la media y la desviación estándar para 'Columna_Numérica' agrupadas por 'Variable_Categorica'
Resumen = df_comb.groupby('Presidente')['Brecha CCL'].agg(['mean', 'std'])
print(Resumen)

from google.colab import drive

# Montar Google Drive en Colab (solo si aún no lo has hecho)
drive.mount('/content/drive')

# Supongamos que tu DataFrame se llama df
# Puedes cargar tus datos o seguir trabajando con el DataFrame que ya tienes

# Guardar el DataFrame en un archivo CSV en Google Drive
df_comb1

columnas = dfcomb.columns.tolist()
columnas

# Verificar si el objeto es un DataFrame
if isinstance(df_em, pd.DataFrame):
    print("Es un DataFrame")
else:
    print("No es un DataFrame")