import requests
import time

from config import TELEGRAM_BOT_TOKEN


# ==========================================
# ENVIAR MENSAJE
# ==========================================

def enviar_mensaje(
    chat_id,
    mensaje
):

    if not TELEGRAM_BOT_TOKEN:

        print(
            "❌ Falta TELEGRAM_BOT_TOKEN."
        )

        return False

    if not chat_id:

        print(
            "❌ Falta chat_id."
        )

        return False

    url = (
        "https://api.telegram.org/bot"
        + TELEGRAM_BOT_TOKEN
        + "/sendMessage"
    )

    datos = {
        "chat_id": chat_id,
        "text": mensaje
    }

    try:

        respuesta = requests.post(
            url,
            data=datos,
            timeout=15
        )

        if respuesta.ok:

            print(
                f"Mensaje enviado a {chat_id}."
            )

            return True

        print(
            "Error de Telegram:",
            respuesta.text
        )

        return False

    except requests.RequestException as e:

        print(
            "No se pudo conectar con Telegram:",
            e
        )

        return False


# ==========================================
# OBTENER ACTUALIZACIONES
# ==========================================

def obtener_actualizaciones(
    offset=None
):

    if not TELEGRAM_BOT_TOKEN:

        return []

    url = (
        "https://api.telegram.org/bot"
        + TELEGRAM_BOT_TOKEN
        + "/getUpdates"
    )

    parametros = {}

    if offset is not None:

        parametros["offset"] = offset

    try:

        respuesta = requests.get(
            url,
            params=parametros,
            timeout=35
        )

        if not respuesta.ok:

            return []

        datos = respuesta.json()

        if not datos.get("ok"):

            return []

        return datos.get(
            "result",
            []
        )

    except requests.RequestException:

        return []


# ==========================================
# ESPERAR MENSAJE DE UN USUARIO
# ==========================================

def esperar_mensaje(
    chat_id,
    offset=None
):

    while True:

        actualizaciones = obtener_actualizaciones(
            offset
        )

        for actualizacion in actualizaciones:

            offset = (
                actualizacion["update_id"]
                + 1
            )

            mensaje = actualizacion.get(
                "message"
            )

            if not mensaje:
                continue

            chat = mensaje.get(
                "chat",
                {}
            )

            mensaje_chat_id = str(
                chat.get(
                    "id",
                    ""
                )
            )

            if mensaje_chat_id != str(
                chat_id
            ):
                continue

            texto = mensaje.get(
                "text",
                ""
            ).strip()

            if texto:

                return (
                    texto,
                    offset
                )

        time.sleep(1)