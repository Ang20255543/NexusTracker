import requests
import time

from datetime import datetime
from zoneinfo import ZoneInfo

from config import (
    NEXUS_API,
    TIMEZONE
)

from telegram_bot import (
    enviar_mensaje,
    obtener_actualizaciones
)

from database import (
    usuario_configurado,
    guardar_usuario,
    obtener_usuario,
    obtener_password,
    obtener_intervalo,
    obtener_avisar_nuevas,
    obtener_avisos_diarios,
    obtener_hora_1,
    obtener_hora_2,
    tarea_conocida,
    registrar_tarea,
    notificacion_enviada,
    registrar_notificacion
)


# ==========================================
# DATOS EN MEMORIA
# ==========================================

tareas_usuarios = {}

ultima_revision = {}

offset_telegram = None


# ==========================================
# HORA
# ==========================================

def ahora():

    return datetime.now(
        ZoneInfo(TIMEZONE)
    )


# ==========================================
# LIMPIAR MENSAJES VIEJOS
# ==========================================

def limpiar_mensajes_pendientes():

    global offset_telegram

    actualizaciones = obtener_actualizaciones()

    if not actualizaciones:

        return

    for actualizacion in actualizaciones:

        offset_telegram = (
            actualizacion["update_id"]
            + 1
        )

    print(
        "Mensajes antiguos de Telegram ignorados."
    )


# ==========================================
# ESPERAR RESPUESTA
# ==========================================

def esperar_respuesta(
    chat_id
):

    global offset_telegram

    while True:

        actualizaciones = obtener_actualizaciones(
            offset_telegram
        )

        for actualizacion in actualizaciones:

            offset_telegram = (
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

                return texto

        time.sleep(1)


# ==========================================
# PREGUNTAR
# ==========================================

def preguntar(
    chat_id,
    mensaje
):

    if not enviar_mensaje(
        chat_id,
        mensaje
    ):

        return None

    return esperar_respuesta(
        chat_id
    )


# ==========================================
# CONFIGURAR USUARIO
# ==========================================

def configurar_usuario(
    chat_id
):

    # ======================================
    # USUARIO
    # ======================================

    enviar_mensaje(
        chat_id,
        "⚙️ CONFIGURACIÓN DE NEXUS TRACKER\n\n"
        "Vamos a configurarlo paso por paso."
    )

    usuario = preguntar(
        chat_id,
        "👤 Escribe tu usuario de SIASE."
    )

    if not usuario:

        enviar_mensaje(
            chat_id,
            "❌ No recibí tu usuario.\n\n"
            "Configuración cancelada."
        )

        return False

    # ======================================
    # CONTRASEÑA
    # ======================================

    password = preguntar(
        chat_id,
        "🔐 Ahora escribe tu contraseña de SIASE."
    )

    if not password:

        enviar_mensaje(
            chat_id,
            "❌ No recibí tu contraseña.\n\n"
            "Configuración cancelada."
        )

        return False

    # ======================================
    # VERIFICAR LOGIN
    # ======================================

    enviar_mensaje(
        chat_id,
        "🔄 Verificando tus datos de SIASE...\n\n"
        "Esto puede tardar unos segundos."
    )

    datos = {
        "user": usuario,
        "password": password
    }

    try:

        respuesta = requests.post(
            f"{NEXUS_API}/login",
            json=datos,
            timeout=120
        )

        print(
            "Login:",
            respuesta.status_code
        )

        if not respuesta.ok:

            enviar_mensaje(
                chat_id,
                "❌ El usuario o la contraseña "
                "son incorrectos.\n\n"
                "No se guardaron tus datos."
            )

            return False

        data = respuesta.json()

        token = data.get(
            "token"
        )

        if not token:

            enviar_mensaje(
                chat_id,
                "❌ Nexus no aceptó tus datos.\n\n"
                "No se guardaron tus datos."
            )

            return False

    except Exception as e:

        print(
            "Error de login:",
            e
        )

        enviar_mensaje(
            chat_id,
            "❌ No pude conectarme con NexusAPI.\n\n"
            "Asegúrate de que NexusAPI esté funcionando."
        )

        return False

    # ======================================
    # INTERVALO
    # ======================================

    intervalo = preguntar(
        chat_id,
        "⏱️ ¿Cada cuántas horas quieres "
        "que revise Nexus?\n\n"
        "Ejemplos:\n"
        "1\n"
        "2\n"
        "3\n"
        "6"
    )

    try:

        horas = float(
            intervalo
        )

        if horas <= 0:

            raise ValueError

    except:

        horas = 2

        enviar_mensaje(
            chat_id,
            "⚠️ Valor no válido.\n\n"
            "Se utilizarán 2 horas."
        )

    # ======================================
    # AVISOS DE TAREAS NUEVAS
    # ======================================

    respuesta = preguntar(
        chat_id,
        "🆕 ¿Quieres que te avise cuando aparezca "
        "una tarea nueva que VENZA ESE MISMO DÍA?\n\n"
        "Las tareas de días futuros NO generan aviso.\n\n"
        "Responde:\n"
        "SI\n"
        "NO"
    )

    avisar_nuevas = (
        str(respuesta).lower()
        in ["si", "sí", "s", "yes"]
    )

    # ======================================
    # AVISOS DIARIOS
    # ======================================

    respuesta = preguntar(
        chat_id,
        "📅 ¿Quieres recibir avisos diarios "
        "cuando tengas tareas para ese día?\n\n"
        "Si no tienes tareas ese día, "
        "no recibirás ningún mensaje.\n\n"
        "Responde:\n"
        "SI\n"
        "NO"
    )

    avisos_diarios = (
        str(respuesta).lower()
        in ["si", "sí", "s", "yes"]
    )

    hora_1 = ""
    hora_2 = ""

    # ======================================
    # HORARIOS
    # ======================================

    if avisos_diarios:

        hora_1 = preguntar(
            chat_id,
            "🕒 ¿A qué hora quieres el primer "
            "aviso diario?\n\n"
            "Formato HH:MM\n\n"
            "Ejemplo:\n"
            "07:00"
        )

        if not hora_1:

            hora_1 = "07:00"

        hora_2 = preguntar(
            chat_id,
            "🕒 ¿A qué hora quieres el segundo "
            "aviso diario?\n\n"
            "Ejemplo:\n"
            "20:00\n\n"
            "Si no quieres un segundo aviso, "
            "responde NO."
        )

        if not hora_2:

            hora_2 = ""

        elif str(hora_2).lower() in [
            "no",
            "n",
            "ninguno"
        ]:

            hora_2 = ""

    # ======================================
    # GUARDAR CONFIGURACIÓN
    # ======================================

    guardar_usuario(
        chat_id,
        usuario,
        password,
        horas,
        "1" if avisar_nuevas else "0",
        "1" if avisos_diarios else "0",
        hora_1,
        hora_2
    )

    # ======================================
    # MENSAJE FINAL
    # ======================================

    enviar_mensaje(
        chat_id,
        "✅ CONFIGURACIÓN TERMINADA\n\n"
        f"🔄 Revisión de Nexus: cada {horas} hora(s)\n"
        f"🆕 Avisos de tareas nuevas: "
        f"{'Sí' if avisar_nuevas else 'No'}\n"
        f"📅 Avisos diarios: "
        f"{'Sí' if avisos_diarios else 'No'}\n\n"
        "🚀 Tu tracker ya está funcionando."
    )

    return True


# ==========================================
# OBTENER TOKEN
# ==========================================

def obtener_token(
    chat_id
):

    datos = {
        "user": obtener_usuario(chat_id),
        "password": obtener_password(chat_id)
    }

    try:

        respuesta = requests.post(
            f"{NEXUS_API}/login",
            json=datos,
            timeout=120
        )

        if not respuesta.ok:

            return None

        data = respuesta.json()

        return data.get(
            "token"
        )

    except Exception as e:

        print(
            "Error obteniendo token:",
            e
        )

        return None


# ==========================================
# OBTENER TAREAS
# ==========================================

def obtener_tareas(
    chat_id,
    token
):

    try:

        respuesta = requests.post(
            f"{NEXUS_API}/calendario",
            json={
                "user": obtener_usuario(chat_id)
            },
            timeout=120
        )

        if not respuesta.ok:

            print(
                "Error calendario:",
                respuesta.text
            )

            return []

        tareas = respuesta.json()

        if not isinstance(
            tareas,
            list
        ):

            return []

        return tareas

    except Exception as e:

        print(
            "Error obteniendo tareas:",
            e
        )

        return []


# ==========================================
# FECHA DE TAREA
# ==========================================

def fecha_tarea(
    tarea
):

    fecha = tarea.get(
        "FechaEntrega"
    )

    if not fecha:

        return None

    try:

        fecha = fecha.replace(
            "Z",
            ""
        )

        return datetime.fromisoformat(
            fecha
        )

    except:

        try:

            return datetime.fromisoformat(
                fecha.split(".")[0]
            )

        except:

            return None


# ==========================================
# CLAVE DE TAREA
# ==========================================

def clave_de_tarea(
    tarea
):

    curso = str(
        tarea.get(
            "Curso",
            ""
        )
    )

    descripcion = str(
        tarea.get(
            "Descripcion",
            ""
        )
    )

    fecha = str(
        tarea.get(
            "FechaEntrega",
            ""
        )
    )

    return (
        f"{curso}|"
        f"{descripcion}|"
        f"{fecha}"
    )


# ==========================================
# MENSAJE TAREA NUEVA
# ==========================================

def crear_mensaje_tarea_nueva(
    tarea
):

    curso = tarea.get(
        "Curso",
        "Curso desconocido"
    )

    descripcion = tarea.get(
        "Descripcion",
        "Sin descripción"
    )

    fecha = fecha_tarea(
        tarea
    )

    if fecha:

        entrega = fecha.strftime(
            "%d/%m/%Y %H:%M"
        )

    else:

        entrega = "Sin fecha"

    return (
        "🆕 NUEVA TAREA EN NEXUS\n\n"
        f"📚 {curso}\n"
        f"📝 {descripcion}\n"
        f"⏰ Entrega: {entrega}"
    )


# ==========================================
# ACTUALIZAR NEXUS
# ==========================================

def actualizar_nexus(
    chat_id
):

    print()
    print(
        "--------------------------------"
    )

    print(
        f"Actualizando Nexus para {chat_id}"
    )

    print(
        "--------------------------------"
    )

    token = obtener_token(
        chat_id
    )

    if not token:

        print(
            "No se pudo iniciar sesión."
        )

        return False

    tareas = obtener_tareas(
        chat_id,
        token
    )

    tareas_usuarios[
        str(chat_id)
    ] = tareas

    fecha_hoy = ahora().date()

    avisar_nuevas = obtener_avisar_nuevas(
        chat_id
    )

    # ======================================
    # REVISAR TAREAS
    # ======================================

    for tarea in tareas:

        clave = clave_de_tarea(
            tarea
        )

        fecha = fecha_tarea(
            tarea
        )

        if not fecha:

            if not tarea_conocida(
                chat_id,
                clave
            ):

                registrar_tarea(
                    chat_id,
                    clave
                )

            continue

        nueva = not tarea_conocida(
            chat_id,
            clave
        )

        # Guardamos TODAS como conocidas
        # para no mandar todo el semestre
        # después.

        if nueva:

            registrar_tarea(
                chat_id,
                clave
            )

        # ==================================
        # SOLO AVISAR SI VENCE HOY
        # ==================================

        if nueva and avisar_nuevas:

            if fecha.date() == fecha_hoy:

                enviar_mensaje(
                    chat_id,
                    crear_mensaje_tarea_nueva(
                        tarea
                    )
                )

                print(
                    "Nueva tarea de hoy enviada."
                )

    ultima_revision[
        str(chat_id)
    ] = time.time()

    print(
        f"Tareas encontradas: {len(tareas)}"
    )

    return True


# ==========================================
# TAREAS DE HOY
# ==========================================

def tareas_de_hoy(
    tareas
):

    fecha_hoy = ahora().date()

    resultado = []

    for tarea in tareas:

        fecha = fecha_tarea(
            tarea
        )

        if not fecha:

            continue

        if fecha.date() == fecha_hoy:

            resultado.append(
                tarea
            )

    return resultado


# ==========================================
# MENSAJE DIARIO
# ==========================================

def crear_mensaje_diario(
    tareas
):

    mensaje = (
        "🔔 TAREAS DE HOY\n\n"
        f"📅 {ahora().strftime('%d/%m/%Y')}\n\n"
    )

    for tarea in tareas:

        curso = tarea.get(
            "Curso",
            "Curso desconocido"
        )

        descripcion = tarea.get(
            "Descripcion",
            "Sin descripción"
        )

        fecha = fecha_tarea(
            tarea
        )

        if fecha:

            hora = fecha.strftime(
                "%H:%M"
            )

        else:

            hora = "Sin hora"

        mensaje += (
            f"📚 {curso}\n"
            f"📝 {descripcion}\n"
            f"⏰ Entrega: {hora}\n\n"
        )

    return mensaje


# ==========================================
# AVISOS DIARIOS
# ==========================================

def procesar_notificaciones(
    chat_id
):

    if not obtener_avisos_diarios(
        chat_id
    ):

        return

    hora_actual = ahora().strftime(
        "%H:%M"
    )

    hora_1 = obtener_hora_1(
        chat_id
    )

    hora_2 = obtener_hora_2(
        chat_id
    )

    if hora_actual not in [
        hora_1,
        hora_2
    ]:

        return

    tareas = tareas_usuarios.get(
        str(chat_id),
        []
    )

    tareas_hoy = tareas_de_hoy(
        tareas
    )

    # ======================================
    # NO HAY TAREAS
    # ======================================

    if not tareas_hoy:

        return

    fecha = ahora().strftime(
        "%Y-%m-%d"
    )

    if not notificacion_enviada(
        chat_id,
        "TAREAS_DEL_DIA",
        fecha,
        hora_actual
    ):

        mensaje = crear_mensaje_diario(
            tareas_hoy
        )

        enviado = enviar_mensaje(
            chat_id,
            mensaje
        )

        if enviado:

            registrar_notificacion(
                chat_id,
                "TAREAS_DEL_DIA",
                fecha,
                hora_actual
            )


# ==========================================
# PROCESAR TELEGRAM
# ==========================================

def procesar_telegram():

    global offset_telegram

    actualizaciones = obtener_actualizaciones(
        offset_telegram
    )

    for actualizacion in actualizaciones:

        offset_telegram = (
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

        chat_id = str(
            chat.get(
                "id",
                ""
            )
        )

        texto = mensaje.get(
            "text",
            ""
        ).strip()

        if not chat_id or not texto:

            continue

        # ==================================
        # USUARIO NUEVO
        # ==================================

        if not usuario_configurado(
            chat_id
        ):

            print(
                f"Nuevo usuario de Telegram: {chat_id}"
            )

            # Configuración inmediata
            #
            # IMPORTANTE:
            # no procesamos más mensajes de
            # este usuario en este ciclo.

            configurar_usuario(
                chat_id
            )

            actualizar_nexus(
                chat_id
            )

            enviar_mensaje(
                chat_id,
                "🟢 NEXUS TASK TRACKER INICIADO\n\n"
                "El sistema está funcionando."
            )

            continue

        # ==================================
        # COMANDOS
        # ==================================

        if texto.lower() == "/start":

            enviar_mensaje(
                chat_id,
                "🟢 Tu Nexus Task Tracker "
                "ya está configurado y funcionando."
            )

        elif texto.lower() == "/estado":

            tareas = tareas_usuarios.get(
                chat_id,
                []
            )

            enviar_mensaje(
                chat_id,
                "🟢 TRACKER ACTIVO\n\n"
                f"📚 Tareas encontradas: {len(tareas)}"
            )

        elif texto.lower() == "/actualizar":

            enviar_mensaje(
                chat_id,
                "🔄 Actualizando Nexus..."
            )

            actualizar_nexus(
                chat_id
            )

            enviar_mensaje(
                chat_id,
                "✅ Nexus actualizado."
            )


# ==========================================
# INICIAR
# ==========================================

def iniciar_scheduler():

    global offset_telegram

    print(
        "=============================="
    )

    print(
        "     NEXUS TASK TRACKER"
    )

    print(
        "=============================="
    )

    print(
        "Bot multiusuario iniciado."
    )

    # ======================================
    # LIMPIAR MENSAJES ANTIGUOS
    # ======================================

    limpiar_mensajes_pendientes()

    # ======================================
    # BUCLE PRINCIPAL
    # ======================================

    while True:

        try:

            # ------------------------------
            # TELEGRAM
            # ------------------------------

            procesar_telegram()

            # ------------------------------
            # USUARIOS CONFIGURADOS
            # ------------------------------

            from database import obtener_usuarios

            usuarios = obtener_usuarios()

            for chat_id in usuarios:

                ultima = ultima_revision.get(
                    chat_id,
                    0
                )

                intervalo = obtener_intervalo(
                    chat_id
                )

                if (
                    time.time() - ultima
                    >= intervalo
                ):

                    actualizar_nexus(
                        chat_id
                    )

                procesar_notificaciones(
                    chat_id
                )

        except KeyboardInterrupt:

            print(
                "Deteniendo Nexus Task Tracker..."
            )

            for chat_id in obtener_usuarios():

                enviar_mensaje(
                    chat_id,
                    "🔴 NEXUS TASK TRACKER DETENIDO\n\n"
                    "El programa fue detenido."
                )

            return

        except Exception as e:

            print(
                "Error general:"
            )

            print(e)

        time.sleep(1)