import sqlite3
from datetime import datetime


DB_NAME = "tracker.db"


# ==========================================
# CONEXIÓN
# ==========================================

def conectar():

    return sqlite3.connect(
        DB_NAME
    )


# ==========================================
# CREAR TABLAS
# ==========================================

def crear_tablas():

    conn = conectar()

    cursor = conn.cursor()

    # ======================================
    # CONFIGURACIÓN POR USUARIO
    # ======================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            chat_id TEXT PRIMARY KEY,
            nexus_user TEXT NOT NULL,
            nexus_password TEXT NOT NULL,
            intervalo_nexus REAL NOT NULL,
            avisar_nuevas TEXT NOT NULL,
            avisos_diarios TEXT NOT NULL,
            hora_1 TEXT NOT NULL,
            hora_2 TEXT NOT NULL,
            fecha_registro TEXT NOT NULL
        )
    """)

    # ======================================
    # NOTIFICACIONES
    # ======================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notificaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT NOT NULL,
            tarea TEXT NOT NULL,
            fecha_entrega TEXT NOT NULL,
            horario TEXT NOT NULL,
            fecha_envio TEXT NOT NULL,
            UNIQUE(
                chat_id,
                tarea,
                fecha_entrega,
                horario
            )
        )
    """)

    # ======================================
    # TAREAS CONOCIDAS
    # ======================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tareas_conocidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT NOT NULL,
            clave TEXT NOT NULL,
            fecha_registro TEXT NOT NULL,
            UNIQUE(chat_id, clave)
        )
    """)

    conn.commit()

    conn.close()


# ==========================================
# USUARIOS
# ==========================================

def usuario_configurado(chat_id):

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT chat_id
        FROM usuarios
        WHERE chat_id = ?
    """, (
        str(chat_id),
    ))

    resultado = cursor.fetchone()

    conn.close()

    return resultado is not None


def guardar_usuario(
    chat_id,
    nexus_user,
    nexus_password,
    intervalo_nexus,
    avisar_nuevas,
    avisos_diarios,
    hora_1,
    hora_2
):

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO usuarios
        (
            chat_id,
            nexus_user,
            nexus_password,
            intervalo_nexus,
            avisar_nuevas,
            avisos_diarios,
            hora_1,
            hora_2,
            fecha_registro
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        str(chat_id),
        nexus_user,
        nexus_password,
        float(intervalo_nexus),
        str(avisar_nuevas),
        str(avisos_diarios),
        hora_1,
        hora_2,
        datetime.now().isoformat()
    ))

    conn.commit()

    conn.close()


def obtener_usuario(chat_id):

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT nexus_user
        FROM usuarios
        WHERE chat_id = ?
    """, (
        str(chat_id),
    ))

    resultado = cursor.fetchone()

    conn.close()

    if resultado is None:
        return ""

    return resultado[0]


def obtener_password(chat_id):

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT nexus_password
        FROM usuarios
        WHERE chat_id = ?
    """, (
        str(chat_id),
    ))

    resultado = cursor.fetchone()

    conn.close()

    if resultado is None:
        return ""

    return resultado[0]


def obtener_intervalo(chat_id):

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT intervalo_nexus
        FROM usuarios
        WHERE chat_id = ?
    """, (
        str(chat_id),
    ))

    resultado = cursor.fetchone()

    conn.close()

    if resultado is None:
        return 7200

    return int(
        float(resultado[0]) * 60 * 60
    )


def obtener_avisar_nuevas(chat_id):

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT avisar_nuevas
        FROM usuarios
        WHERE chat_id = ?
    """, (
        str(chat_id),
    ))

    resultado = cursor.fetchone()

    conn.close()

    if resultado is None:
        return False

    return resultado[0] == "1"


def obtener_avisos_diarios(chat_id):

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT avisos_diarios
        FROM usuarios
        WHERE chat_id = ?
    """, (
        str(chat_id),
    ))

    resultado = cursor.fetchone()

    conn.close()

    if resultado is None:
        return False

    return resultado[0] == "1"


def obtener_hora_1(chat_id):

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT hora_1
        FROM usuarios
        WHERE chat_id = ?
    """, (
        str(chat_id),
    ))

    resultado = cursor.fetchone()

    conn.close()

    if resultado is None:
        return ""

    return resultado[0]


def obtener_hora_2(chat_id):

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT hora_2
        FROM usuarios
        WHERE chat_id = ?
    """, (
        str(chat_id),
    ))

    resultado = cursor.fetchone()

    conn.close()

    if resultado is None:
        return ""

    return resultado[0]


# ==========================================
# TAREAS CONOCIDAS
# ==========================================

def tarea_conocida(
    chat_id,
    clave
):

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT id
        FROM tareas_conocidas
        WHERE chat_id = ?
        AND clave = ?
    """, (
        str(chat_id),
        clave
    ))

    resultado = cursor.fetchone()

    conn.close()

    return resultado is not None


def registrar_tarea(
    chat_id,
    clave
):

    conn = conectar()

    cursor = conn.cursor()

    try:

        cursor.execute("""
            INSERT INTO tareas_conocidas
            (
                chat_id,
                clave,
                fecha_registro
            )
            VALUES (?, ?, ?)
        """, (
            str(chat_id),
            clave,
            datetime.now().isoformat()
        ))

        conn.commit()

    except sqlite3.IntegrityError:

        pass

    conn.close()


# ==========================================
# NOTIFICACIONES
# ==========================================

def notificacion_enviada(
    chat_id,
    tarea,
    fecha_entrega,
    horario
):

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT id
        FROM notificaciones
        WHERE chat_id = ?
        AND tarea = ?
        AND fecha_entrega = ?
        AND horario = ?
    """, (
        str(chat_id),
        tarea,
        fecha_entrega,
        horario
    ))

    resultado = cursor.fetchone()

    conn.close()

    return resultado is not None


def registrar_notificacion(
    chat_id,
    tarea,
    fecha_entrega,
    horario
):

    conn = conectar()

    cursor = conn.cursor()

    try:

        cursor.execute("""
            INSERT INTO notificaciones
            (
                chat_id,
                tarea,
                fecha_entrega,
                horario,
                fecha_envio
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            str(chat_id),
            tarea,
            fecha_entrega,
            horario,
            datetime.now().isoformat()
        ))

        conn.commit()

    except sqlite3.IntegrityError:

        pass

    conn.close()


# ==========================================
# OBTENER TODOS LOS USUARIOS
# ==========================================

def obtener_usuarios():

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT chat_id
        FROM usuarios
    """)

    resultados = cursor.fetchall()

    conn.close()

    return [
        str(resultado[0])
        for resultado in resultados
    ]
