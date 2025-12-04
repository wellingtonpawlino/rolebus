
from flask import Flask, request, jsonify, render_template
import math
import pandas as pd

app = Flask(__name__)

# Buscar dados diretamente do GitHub (arquivo CSV)
url = "https://raw.githubusercontent.com/wellingtonpawlino/sptrans_pipeline/main/data/ultima_posicao/view_ultima_posicao.csv"
df = pd.read_csv(url)

# Converter para lista de dicionários no formato esperado
onibus = [
    {
        "codigo": row["codigo_linha"],
        "descricao": row["DescricaoCompleto"],
        "lat": float(row["latitude"]),
        "lon": float(row["longitude"])
    }
    for _, row in df.iterrows()
]

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
