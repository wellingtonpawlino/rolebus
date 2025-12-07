
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
    try:
        df = pd.read_csv(url)
        onibus = [
            {
                "codigo": str(row["codigo_linha"]),
                "descricao": row["DescricaoCompleto"],
                "lat": float(row["latitude"]),
                "lon": float(row["longitude"])
            }
            for _, row in df.iterrows()
        ]
        print(f"✅ Dados atualizados em: {pd.Timestamp.now()}")
    except Exception as e:
        print(f"❌ Erro ao atualizar dados: {e}")

# Atualiza imediatamente ao iniciar
atualizar_dados()

# Agendador para atualizar a cada 1 minuto
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(atualizar_dados, 'interval', minutes=1)
scheduler.start()

# Função para calcular distância (Haversine)
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

# ✅ Mais próximo de qualquer linha
@app.route("/onibus-proximo")
def onibus_proximo():
    lat_user = float(request.args.get("lat"))
    lon_user = float(request.args.get("lon"))
    if not onibus:
        return jsonify({"erro": "Dados não disponíveis no momento"}), 503
    mais_proximo = min(onibus, key=lambda o: haversine(lat_user, lon_user, o["lat"], o["lon"]))
    distancia = haversine(lat_user, lon_user, mais_proximo["lat"], mais_proximo["lon"])
    return jsonify({
        "linha": mais_proximo["codigo"],
        "descricao": mais_proximo["descricao"],
        "latitude": mais_proximo["lat"],
        "longitude": mais_proximo["lon"],
        "distancia_km": round(distancia, 2)
    })

# ✅ Filtro por código da linha
@app.route("/onibus-linha")
def onibus_linha():
    codigo = request.args.get("codigo")
    lat_user = float(request.args.get("lat"))
    lon_user = float(request.args.get("lon"))

    if not onibus:
        return jsonify({"erro": "Dados não disponíveis"}), 503

    filtrados = [o for o in onibus if o["codigo"] == codigo]

    if not filtrados:
        return jsonify({"erro": f"Nenhum ônibus encontrado para a linha {codigo}"}), 404

