# Importa bibliotecas
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import pandas as pd
from datetime import datetime, timezone
import requests
import pytz
import numpy as np
import os

# Fuso horário de Brasília
brasilia_tz = pytz.timezone("America/Sao_Paulo")

# Função para pegar os dados do Weather Underground
def get_weather_data():
    WU_API_KEY = os.getenv('WU_API_KEY')
    if not WU_API_KEY:
        raise ValueError("A chave da API não foi encontrada. Defina 'WU_API_KEY' como uma variável de ambiente.")
    STATION_ID = "ISOPAU314"
    url = f"https://api.weather.com/v2/pws/observations/current?stationId={STATION_ID}&format=json&units=m&numericPrecision=decimal&apiKey={WU_API_KEY}"
    timestamp = datetime.now(tz=brasilia_tz).strftime('%Y-%m-%dT%H:%M:%SZ')
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        observation = data['observations'][0]
        temp = observation["metric"]["temp"]
        humidity = observation["humidity"]
        pressure = observation["metric"]["pressure"]
        dew_point = observation["metric"]["dewpt"]
        obs_time_utc = observation['obsTimeUtc']
        return temp, humidity, pressure, dew_point, timestamp
    except requests.exceptions.RequestException as e:
        print("Erro na requisição:", e)
        return None, None, None, None, timestamp
    except KeyError as e:
        print("Chave não encontrada nos dados da API:", e)
        return None, None, None, None, None

# Caminho do arquivo CSV
csv_file = 'weather_data.csv'

# Verificar se o arquivo existe
if os.path.exists(csv_file):
    df = pd.read_csv(csv_file, parse_dates=['Timestamp'])
else:
    df = pd.DataFrame(columns=['Timestamp', 'Temperature', 'Humidity', 'Pressure', 'Dew Point'])

# Obter os dados atuais
temp, humidity, pressure, dew_point, timestamp = get_weather_data()

# Converter o timestamp atual para datetime e fuso horário correto
timestamp = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
#timestamp = brasilia_tz.localize(timestamp)

# Remover linhas com valores NaT no DataFrame
df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
df = df.dropna(subset=['Timestamp'])

# Verificar se o timestamp já existe no DataFrame
if timestamp not in df['Timestamp'].values:
    new_data = pd.DataFrame({
        'Timestamp': [timestamp],
        'Temperature': [temp],
        'Humidity': [humidity],
        'Pressure': [pressure],
        'Dew Point': [dew_point]
    })

    df = pd.concat([df, new_data], ignore_index=True)

    # Ajustar o fuso horário para o DataFrame
    #df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce').dt.tz_localize('UTC').dt.tz_convert(brasilia_tz)

    # Salvar no arquivo CSV
    df.to_csv(csv_file, index=False)
    estadoEstacao = 'Online'
else:
    print("Dados já existentes para o timestamp:", timestamp)
    estadoEstacao = 'Offline'

# Cálculo de mínimas e máximas
min_temp = df['Temperature'].min()
max_temp = df['Temperature'].max()
min_humidity = df['Humidity'].min()
max_humidity = df['Humidity'].max()
min_pressure = df['Pressure'].min()
max_pressure = df['Pressure'].max()

# Configurar subplots
fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
fig.suptitle("Tempo e Extremos nas últimas 24 horas")

# Gráficos
axs[0].plot(df['Timestamp'], df['Temperature'], label="Temperatura", color='red', marker='o')
axs[0].plot(df['Timestamp'], df['Dew Point'], label="Ponto de orvalho", color="green", linestyle="--", marker='o', markersize=3)
axs[0].set_ylabel("Temperatura (°C)")
axs[0].legend(loc="upper left")
axs[0].grid(True)

axs[1].plot(df['Timestamp'], df['Humidity'], color='blue', marker='o')
axs[1].set_ylabel("Umidade (%)")
axs[1].grid(True)

axs[2].plot(df['Timestamp'], df['Pressure'], color='black', marker='o')
axs[2].set_ylabel("Pressão (hPa)")
axs[2].grid(True)

# Formatação do eixo X
axs[2].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M', tz=brasilia_tz))
axs[2].xaxis.set_major_locator(mdates.HourLocator(interval=2))
plt.xlabel("Hora local")

# Salvar o gráfico
plt.tight_layout()
plt.savefig('graph.png', bbox_inches='tight')
plt.close(fig)
