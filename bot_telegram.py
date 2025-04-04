from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from bot_cervezas import responder

# Diccionario para mantener sesiones individuales por usuario
usuarios = {}

# Reemplaza esto por tu token real
TOKEN = "7801532929:AAG2mRQS3gIb8rGYb8_2P8JXIvsuT0NxRPQ"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    mensaje = update.message.text.strip()

    if user_id not in usuarios:
        usuarios[user_id] = {"estado": "inicio"}

    respuesta = responder(mensaje, usuarios[user_id])
    await update.message.reply_text(respuesta)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    app.add_handler(handler)

    print("🤖 Bot cervecero corriendo en Telegram...")
    app.run_polling()
