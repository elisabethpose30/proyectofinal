from flask import Flask, request, jsonify
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Servidor Flask en modo local funcionando correctamente 🚀", 200

@app.route('/ubicacion', methods=['POST'])
def recibir_ubicacion():
    data = request.json
    print("📍 Datos recibidos:", data)  # Log para ver la data en la consola

    if not data:
        return jsonify({"error": "No se recibieron datos"}), 400

    evento = data.get("evento")
    zona = data.get("zona")
    lat = data.get("lat")
    lon = data.get("lon")
    timestamp = data.get("tst")

    print("Evento:", evento)
    print("Zona:", zona)
    print("Lat:", lat)
    print("Lon:", lon)
    print("Timestamp:", timestamp)

    if lat is None or lon is None:
        print("⚠️ Error: Falta latitud o longitud en la data.")
        return jsonify({"error": "latitud o longitud faltante"}), 400

    fecha = datetime.fromtimestamp(timestamp).isoformat() if timestamp else None

    payload = {
        "latitud": lat,
        "longitud": lon,
        "timestamp": fecha,
        "evento": evento,
        "zona": zona
    }

    print("✅ Datos que se hubieran enviado a Supabase:", payload)

    # 🔒 Parte de Supabase comentada
    # headers = {
    #     "apikey": SUPABASE_KEY,
    #     "Authorization": f"Bearer {SUPABASE_KEY}",
    #     "Content-Type": "application/json",
    #     "Prefer": "return=representation"
    # }
    #
    # try:
    #     response = requests.post(
    #         f"{SUPABASE_URL}/rest/v1/ubicaciones",
    #         json=payload,
    #         headers=headers
    #     )
    #
    #     print("🔄 Respuesta de Supabase:", response.status_code, response.text)
    #
    #     if response.status_code >= 400:
    #         return jsonify({"error": "Error al insertar en Supabase", "detalle": response.text}), response.status_code
    #
    #     return jsonify({
    #       "status": "ok",
    #       "supabase_status": response.status_code,
    #       "supabase_text": response.text
    #     }), 201
