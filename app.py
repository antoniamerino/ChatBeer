from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from bot_cervezas import responder
import os  # 👈 Necesario para leer la variable de entorno PORT

app = Flask(__name__)
usuarios = {}  # Diccionario para mantener sesiones simples por número

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    from_number = request.form.get("From")
    mensaje = request.form.get("Body")

    if from_number not in usuarios:
        usuarios[from_number] = {"estado": "inicio", "historial": []}

    respuesta_bot = responder(mensaje, usuarios[from_number])
    usuarios[from_number]["historial"].append((mensaje, respuesta_bot))

    resp = MessagingResponse()
    resp.message(respuesta_bot)
    return str(resp)

# 👇 Esta es la parte que debes cambiar
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render usa esta variable
    app.run(host="0.0.0.0", port=port)        # Escuchar en todas las interfaces
