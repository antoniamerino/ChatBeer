
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from bot_cervezas import responder

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

if __name__ == "__main__":
    app.run(debug=True)
