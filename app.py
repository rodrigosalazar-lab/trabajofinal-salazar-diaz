import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import google.generativeai as genai
from PIL import Image
import io
import json

load_dotenv() # Carga las variables del archivo .env

app = Flask(__name__)
CORS(app)

# 1. CONFIGURACIÓN SEGURA DE LA LLAVE
API_KEY = os.getenv("GOOGLE_API_KEY") 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# ==========================================
# RUTAS DEL FRONTEND (LA CARA)
# ==========================================
@app.route('/')
def home():
    # Cuando alguien entre al link, le mostramos el HTML
    return send_file('index.html')

@app.route('/style.css')
def style():
    # Entregamos los colores y diseño
    return send_file('style.css')

# ==========================================
# RUTAS DEL BACKEND (EL CEREBRO)
# ==========================================
@app.route('/analizar', methods=['POST'])
def analizar_coherencia():
    try:
        ad_file = request.files['ad_image']
        landing_file = request.files['landing_image']
        dispositivo = request.form.get('dispositivo', 'Desktop')

        ad_img = Image.open(io.BytesIO(ad_file.read()))
        landing_img = Image.open(io.BytesIO(landing_file.read()))

        # Pedimos JSON estricto para estructurar el Front-end
        prompt = f"""
        Eres un Growth Marketer. Analiza este Ad y Landing para {dispositivo}.
        DEVUELVE SOLO UN JSON VÁLIDO CON ESTA ESTRUCTURA EXACTA, SIN MARKDOWN NI TEXTO EXTRA:
        {{
            "score": 85,
            "emocion": "El Ad transmite urgencia, la landing calma.",
            "ocr_mismatch": ["Palabra Faltante 1", "Palabra Faltante 2"],
            "hipotesis_ab": "Si cambiamos X por Y, entonces Z.",
            "matriz": [
                {{"accion": "Cambiar color CTA", "cuadrante": "q1"}},
                {{"accion": "Rediseñar header", "cuadrante": "q2"}}
            ]
        }}
        Nota: Cuadrantes permitidos: q1 (Quick Wins), q2 (Proyectos), q3 (Tareas Menores), q4 (Ignorar).
        """
        
        # Forzamos a que Gemini responda en formato JSON puro
        response = model.generate_content(
            [prompt, ad_img, landing_img],
            generation_config=genai.GenerationConfig(response_mime_type="application/json")
        )
        
        return jsonify({"status": "success", "resultado": json.loads(response.text)})
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)})

@app.route('/generar', methods=['POST'])
def generar_copys():
    try:
        ad_file = request.files['ad_image']
        plataforma = request.form.get('plataforma', 'Meta')
        tono = request.form.get('tono', 'Urgencia')
        ad_img = Image.open(io.BytesIO(ad_file.read()))

        if plataforma == "Google Ads":
            reglas = "Límite: Headlines max 30 carac, Descripciones max 90 carac. PROHIBIDO usar emojis. Usa Title Case."
        else:
            reglas = "Límite: Texto Principal max 125 carac, Título max 40 carac. Usa emojis moderados. Estructura: Gancho + Valor + CTA."

        prompt = f"Analiza esta imagen y crea 3 variantes de copy para {plataforma} con tono {tono}. Sigue estas reglas: {reglas}"
        response = model.generate_content([prompt, ad_img])
        
        return jsonify({"status": "success", "resultado": response.text})
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)})

if __name__ == '__main__':
    # Cloud Run requiere el puerto 8080
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=False, host='0.0.0.0', port=port)