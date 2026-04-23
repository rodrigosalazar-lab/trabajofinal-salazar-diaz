import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import google.generativeai as genai
from PIL import Image
import io
import json

load_dotenv()

app = Flask(__name__)
CORS(app)

API_KEY = os.getenv("GOOGLE_API_KEY") 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# ==========================================
# RUTAS DEL FRONTEND
# ==========================================
@app.route('/')
def home():
    return send_file('index.html')

@app.route('/style.css')
def style():
    return send_file('style.css')

# ==========================================
# RUTAS DEL BACKEND
# ==========================================
@app.route('/analizar', methods=['POST'])
def analizar_coherencia():
    try:
        ad_file = request.files['ad_image']
        landing_file = request.files['landing_image']
        dispositivo = request.form.get('dispositivo', 'Desktop')

        ad_img = Image.open(io.BytesIO(ad_file.read()))
        landing_img = Image.open(io.BytesIO(landing_file.read()))

        # Añadimos 3 Sub-métricas al esquema JSON
        prompt = f"""
        Eres un Growth Marketer Senior. Analiza este Ad y Landing para {dispositivo}.
        DEVUELVE SOLO UN JSON VÁLIDO CON ESTA ESTRUCTURA EXACTA:
        {{
            "score": 85,
            "sub_metricas": {{
                "continuidad_visual": 90,
                "relevancia_mensaje": 80,
                "friccion_cta": 85
            }},
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
        num_variantes = request.form.get('num_variantes', '3')
        ad_img = Image.open(io.BytesIO(ad_file.read()))

        # Reglas estrictas por plataforma
        if plataforma == "Google Ads":
            reglas = "ESTRICTO: Títulos MÁXIMO 30 caracteres. Descripciones MÁXIMO 90 caracteres. CERO EMOJIS permitidos."
        elif plataforma == "TikTok":
            reglas = "ESTRICTO: Texto principal MÁXIMO 150 caracteres. Usa lenguaje nativo de TikTok, tendencias y 1 o 2 emojis dinámicos."
        else: # Meta (Facebook/IG)
            reglas = "ESTRICTO: Texto Principal MÁXIMO 125 caracteres. Título MÁXIMO 40 caracteres. Usa máximo 2 emojis."

        prompt = f"""
        Analiza esta imagen y crea {num_variantes} variantes de copy para {plataforma} con tono {tono}.
        REGLAS OBLIGATORIAS: {reglas}
        
        DEVUELVE SOLO UN ARRAY EN FORMATO JSON EXACTO COMO ESTE (Sin markdown, solo JSON puro):
        [
            {{"variante": 1, "titulo": "...", "texto": "..."}},
            {{"variante": 2, "titulo": "...", "texto": "..."}}
        ]
        """
        
        response = model.generate_content(
            [prompt, ad_img],
            generation_config=genai.GenerationConfig(response_mime_type="application/json")
        )
        
        return jsonify({"status": "success", "resultado": json.loads(response.text)})
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=False, host='0.0.0.0', port=port)