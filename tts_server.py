from flask import Flask, request, Response
from flask_cors import CORS
import edge_tts
import asyncio

app = Flask(__name__)
# Permitir que la página web (app.js) se comunique con este servidor
CORS(app)

# 🇪🇨 Voz premium de Microsoft con acento Ecuatoriano!
VOICE = "es-EC-AndreaNeural" 

@app.route('/generar_audio', methods=['POST'])
def generar_audio():
    data = request.json
    texto = data.get("text", "")
    
    if not texto:
        return {"error": "No se envió texto"}, 400

    # Función asíncrona para descargar el audio directamente a la memoria
    async def procesar_voz():
        communicate = edge_tts.Communicate(texto, VOICE)
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return audio_data

    # Ejecutar la descarga y guardar los bytes
    audio_bytes = asyncio.run(procesar_voz())

    # Devolver el archivo de audio directamente al navegador
    return Response(audio_bytes, mimetype="audio/mpeg")

if __name__ == '__main__':
    print("🎙️ Servidor de Voz de Consultina iniciado en el puerto 5002...")
    app.run(port=5002)