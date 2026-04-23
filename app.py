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

@app.route('/')
def home():
    return send_file('index.html')

@app.route('/style.css')
def style():
    return send_file('style.css')

# ==========================================
# MODO 1: ANALIZADOR UI/UX
# ==========================================
@app.route('/analizar', methods=['POST'])
def analizar_coherencia():
    try:
        ad_file = request.files['ad_image']
        landing_file = request.files['landing_image']
        dispositivo = request.form.get('dispositivo', 'Desktop')

        ad_img = Image.open(io.BytesIO(ad_file.read()))
        landing_img = Image.open(io.BytesIO(landing_file.read()))

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

# ==========================================
# MODO 2: GENERADOR DE COPYS (Añadido Buyer Persona)
# ==========================================
@app.route('/generar', methods=['POST'])
def generar_copys():
    try:
        ad_file = request.files['ad_image']
        plataforma = request.form.get('plataforma', 'Meta')
        tono = request.form.get('tono', 'Urgencia')
        num_variantes = request.form.get('num_variantes', '3')
        persona = request.form.get('persona', '')
        
        ad_img = Image.open(io.BytesIO(ad_file.read()))

        contexto_persona = f"El público objetivo (Buyer Persona) es: '{persona}'. Asegúrate de usar palabras y dolores que conecten con ellos." if persona else ""

        if plataforma == "Google Ads":
            reglas = "ESTRICTO: Títulos MÁXIMO 30 caracteres. Descripciones MÁXIMO 90 caracteres. CERO EMOJIS permitidos."
        elif plataforma == "TikTok":
            reglas = "ESTRICTO: Texto principal MÁXIMO 150 caracteres. Usa lenguaje nativo, tendencias y 1 o 2 emojis dinámicos."
        else: 
            reglas = "ESTRICTO: Texto Principal MÁXIMO 125 caracteres. Título MÁXIMO 40 caracteres. Usa máximo 2 emojis."

        prompt = f"""
        Analiza esta imagen y crea {num_variantes} variantes de copy para {plataforma} con tono {tono}.
        {contexto_persona}
        REGLAS OBLIGATORIAS: {reglas}
        
        DEVUELVE SOLO UN ARRAY EN FORMATO JSON EXACTO COMO ESTE:
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

# ==========================================
# MODO 3: CREADOR MULTI-FORMATO (NUEVO)
# ==========================================
@app.route('/generar_m3', methods=['POST'])
def generar_multiformato():
    try:
        ad_file = request.files['ad_image']
        formato = request.form.get('formato', 'Video Script')
        tono = request.form.get('tono', 'Llamativo')
        
        ad_img = Image.open(io.BytesIO(ad_file.read()))

        if formato == "Video Script":
            instruccion = "Crea un guion de video corto (tipo TikTok/Reels) basado en esta imagen. Divide en 3 a 5 partes."
            formato_json = '[{"seccion": "0-3s (Hook)", "visual": "...", "audio": "..."}, {"seccion": "3-8s (Problema)", "visual": "...", "audio": "..."}]'
        else:
            instruccion = "Crea un texto estructurado para un Carrusel de Instagram/LinkedIn (3 a 5 slides) basado en esta imagen."
            formato_json = '[{"seccion": "Slide 1 (Portada)", "visual": "...", "audio": "Texto/Caption..."}, {"seccion": "Slide 2 (Valor)", "visual": "...", "audio": "Texto/Caption..."}]'

        prompt = f"""
        Eres un Content Creator Senior. {instruccion} Tono: {tono}.
        La columna 'visual' describe qué se debe mostrar en pantalla o diseño.
        La columna 'audio' describe qué se dice en locución o qué texto se lee.
        
        DEVUELVE SOLO UN ARRAY EN FORMATO JSON EXACTO COMO ESTE:
        {formato_json}
        """
        
        response = model.generate_content(
            [prompt, ad_img],
            generation_config=genai.GenerationConfig(response_mime_type="application/json")
        )
        
        return jsonify({"status": "success", "resultado": json.loads(response.text), "formato": formato})
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=False, host='0.0.0.0', port=port)