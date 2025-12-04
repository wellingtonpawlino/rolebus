
from flask import Flask, request, jsonify, render_template
import math
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# URL do CSV no GitHub
url = "https://raw.githubusercontent.com/wellingtonpawlino/sptrans_pipeline/main/data/ultima_posicao/view_ultima_posicao.csv"

# Variável global para armazenar os dados
onibus = []

def atualizar_dados():
    global onibus
    df = pd.read_csv(url)
    onibus = [
        {
            "codigo": row["codigo_linha"],
            "descricao": row["DescricaoCompleto"],
            "lat": float(row["latitude"]),
            "lon": float(row["longitude"])
        }
        for _, row in df.iterrows()
    ]
    print("✅ Dados atualizados do GitHub")

# Atualiza imediatamente ao iniciar
atualizar_dados()

# Agendador para atualizar a cada 5 minutos
scheduler = BackgroundScheduler()
scheduler.add_job(atualizar_dados, 'interval', minutes=1)
scheduler.start()

# Função para calcular distância (mantida)
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/onibus-proximo")
def onibus_proximo():
    lat_user = float(request.args.get("lat"))
    lon_user = float(request.args.get("lon"))
    mais_proximo = min(onibus, key=lambda o: haversine(lat_user, lon_user, o["lat"], o["lon"]))
    distancia = haversine(lat_user, lon_user, mais_proximo["lat"], mais_proximo["lon"])
    return jsonify({
        "linha": mais_proximo["codigo"],
        "descricao": mais_proximo["descricao"],
        "latitude": mais_proximo["lat"],
        "longitude": mais_proximo["lon"],
        "distancia_km": round(distancia, 2)
    })

if __name__ == "__main__":
    app.run(debug=True)
