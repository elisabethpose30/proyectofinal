from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime
from datetime import timezone, timedelta
from flask_cors import CORS


ARGENTINA_TZ = timezone(timedelta(hours=-3))


app = Flask(__name__)
# CORS(app)
# CORS(app, resources={r"/*": {"origins": "*"}})
CORS(app, resources={r"/*": {"origins": "https://proyectointegradorifts.netlify.app"}})


# Verificamos que las variables de entorno estén bien definidas
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ ERROR: Las variables de entorno de Supabase no están configuradas correctamente.")


@app.route('/')
def home():
    return "✅ Servidor Flask en Heroku funcionando correctamente 🚀", 200




@app.route('/ubicacion', methods=['POST'])
def recibir_ubicacion_ou_transicion():
    data = request.json
    print("📥 Datos recibidos:", data)


    if not data:
        return jsonify({"error": "No se recibieron datos"}), 400


    tipo = data.get("_type")
    if tipo not in ["location", "transition"]:
        print("⚠️ Ignorando mensaje: tipo no válido:", tipo)
        return jsonify({"status": "ignored"}), 200


    lat = data.get("lat")
    lon = data.get("lon")
    timestamp = data.get("tst")
    evento = data.get("event") if tipo == "transition" else None
    zona = data.get("desc") or (data.get("inregions")[0] if data.get("inregions") else None)


    if tipo == "location" and (lat is None or lon is None):
        print("⚠️ Error: Faltan coordenadas en el mensaje de ubicación.")
        return jsonify({"error": "latitud o longitud faltante"}), 400


    fecha = (
        datetime.fromtimestamp(timestamp, tz=timezone.utc)
        .astimezone(ARGENTINA_TZ)
        .isoformat()
    ) if timestamp else None


    print("🧭 Tipo:", tipo)
    print("🌍 Lat:", lat)
    print("🌍 Lon:", lon)
    print("📌 Evento:", evento)
    print("📍 Zona:", zona)
    print("🕒 Fecha:", fecha)


    payload = {
        "latitud": lat,
        "longitud": lon,
        "evento": evento,
        "zona": zona
    }


    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }


    try:
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/ubicaciones",  # tu tabla unificada
            json=payload,
            headers=headers
        )


        print("✅ Supabase:", response.status_code, response.text)


        if response.status_code >= 400:
            return jsonify({"error": "Error al insertar en Supabase", "detalle": response.text}), response.status_code


        return jsonify({
            "status": "ok",
            "supabase_status": response.status_code,
            "supabase_text": response.text
        }), 201


    except Exception as e:
        print("❌ Error al conectar con Supabase:", str(e))
        return jsonify({"error": "Error al conectar con Supabase"}), 500




@app.route('/ultima_ubicacion', methods=['GET'])
def obtener_ultima_ubicacion():
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }


    url = f"{SUPABASE_URL}/rest/v1/ubicaciones?order=timestamp.desc&limit=1"


    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return jsonify({"error": "No se pudo obtener la ubicación", "detalle": response.text}), response.status_code


        datos = response.json()
        if not datos:
            return jsonify({"mensaje": "No hay ubicaciones registradas"}), 404
        print("Última ubicación:", datos[0])


        return jsonify(datos[0]), 200


    except Exception as e:
        print("❌ Error al consultar Supabase:", str(e))
        return jsonify({"error": "Error interno"}), 500




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)


