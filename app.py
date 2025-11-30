
from flask import Flask, request, jsonify, render_template
import math

app = Flask(__name__)

# Base de dados (exemplo)
onibus = [
    {"codigo": "1012-21", "descricao": "JD. ROSINHA", "lat": -23.432145, "lon": -46.787099999999995},
    {"codigo": "1016-10", "descricao": "SHOP. CENTER NORTE", "lat": -23.446737, "lon": -46.611729},
    {"codigo": "1018-10", "descricao": "METRÔ SANTANA", "lat": -23.4602115, "lon": -46.626517},
    {"codigo": "1019-10", "descricao": "TERM. PIRITUBA", "lat": -23.4618575, "lon": -46.753502999999995}
]

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
