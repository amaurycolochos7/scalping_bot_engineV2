"""
Sistema de gestión de keys de acceso
"""
import sqlite3
import secrets
import string
from datetime import datetime, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Directorio de datos
DATA_DIR = Path(__file__).parent / 'data'
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / 'access_keys.db'

# Duraciones disponibles (en horas)
DURATIONS = {
    1: ("24 horas", 24),
    2: ("3 días", 72),
    3: ("10 días", 240),
    4: ("15 días", 360),
    5: ("1 mes", 720),
    6: ("3 meses", 2160),
    7: ("6 meses", 4320),
}


def get_db_connection():
    """Obtiene conexión a la base de datos"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Inicializa las tablas de la base de datos"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tabla de keys
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS access_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            duration_hours INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            activated_at TIMESTAMP,
            user_id INTEGER,
            status TEXT DEFAULT 'pending'
        )
    ''')
    
    # Tabla de usuarios autorizados
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS authorized_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            chat_id INTEGER NOT NULL,
            username TEXT,
            key_id INTEGER,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (key_id) REFERENCES access_keys(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("✅ Base de datos de keys inicializada")


def generate_key(duration_option: int) -> tuple:
    """
    Genera una nueva key de acceso
    
    Args:
        duration_option: Número de opción (1-7)
    
    Returns:
        Tuple (key, duration_label, duration_hours)
    """
    if duration_option not in DURATIONS:
        raise ValueError(f"Opción inválida: {duration_option}")
    
    duration_label, duration_hours = DURATIONS[duration_option]
    
    # Generar key única
    chars = string.ascii_uppercase + string.digits
    key_parts = [
        ''.join(secrets.choice(chars) for _ in range(6)),
        ''.join(secrets.choice(chars) for _ in range(6)),
        ''.join(secrets.choice(chars) for _ in range(6))
    ]
    key = '-'.join(key_parts)
    
    # Guardar en base de datos
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO access_keys (key, duration_hours, status)
        VALUES (?, ?, 'pending')
    ''', (key, duration_hours))
    
    conn.commit()
    conn.close()
    
    logger.info(f"✅ Key generada: {key} ({duration_label})")
    return key, duration_label, duration_hours


def validate_key(key: str) -> dict:
    """
    Valida si una key existe y está disponible
    
    Args:
        key: Key a validar
    
    Returns:
        Dict con información de la key o None si no es válida
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, duration_hours, status
        FROM access_keys
        WHERE key = ? AND status = 'pending'
    ''', (key,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row['id'],
            'duration_hours': row['duration_hours'],
            'duration_label': get_duration_label(row['duration_hours'])
        }
    return None


def get_duration_label(hours: int) -> str:
    """Convierte horas a etiqueta legible"""
    if hours <= 24:
        return f"{hours} hora(s)"
    elif hours < 720:
        return f"{hours // 24} día(s)"
    else:
        return f"{hours // 720} mes(es)"


def activate_key(key: str, user_id: int, chat_id: int, username: str = None) -> dict:
    """
    Activa una key para un usuario
    
    Args:
        key: Key a activar
        user_id: ID del usuario de Telegram
        chat_id: Chat ID de Telegram
        username: Username de Telegram (opcional)
    
    Returns:
        Dict con información de activación o None si falla
    """
    key_info = validate_key(key)
    if not key_info:
        return None
    
    now = datetime.now()
    expires_at = now + timedelta(hours=key_info['duration_hours'])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Actualizar key como activada
        cursor.execute('''
            UPDATE access_keys
            SET activated_at = ?, user_id = ?, status = 'active'
            WHERE id = ?
        ''', (now, user_id, key_info['id']))
        
        # Insertar o actualizar usuario autorizado
        cursor.execute('''
            INSERT OR REPLACE INTO authorized_users 
            (user_id, chat_id, username, key_id, expires_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, chat_id, username, key_info['id'], expires_at))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Key activada para usuario {user_id} hasta {expires_at}")
        
        return {
            'expires_at': expires_at,
            'duration_label': key_info['duration_label']
        }
    
    except Exception as e:
        conn.rollback()
        conn.close()
        logger.error(f"❌ Error activando key: {e}")
        return None


def is_user_authorized(user_id: int) -> dict:
    """
    Verifica si un usuario tiene acceso activo
    
    Args:
        user_id: ID del usuario de Telegram
    
    Returns:
        Dict con info si autorizado, None si no
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT expires_at
        FROM authorized_users
        WHERE user_id = ? AND expires_at > datetime('now')
    ''', (user_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        expires_at = datetime.fromisoformat(row['expires_at'])
        remaining = expires_at - datetime.now()
        return {
            'expires_at': expires_at,
            'remaining': remaining
        }
    return None


def get_authorized_chat_ids() -> list:
    """
    Obtiene lista de chat_ids con acceso activo
    
    Returns:
        Lista de chat_ids autorizados
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT chat_id
        FROM authorized_users
        WHERE expires_at > datetime('now')
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    return [row['chat_id'] for row in rows]


def cleanup_expired():
    """Limpia keys y usuarios expirados"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Marcar keys expiradas
    cursor.execute('''
        UPDATE access_keys
        SET status = 'expired'
        WHERE status = 'active'
        AND id IN (
            SELECT key_id FROM authorized_users
            WHERE expires_at <= datetime('now')
        )
    ''')
    
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    
    if affected > 0:
        logger.info(f"🧹 {affected} keys marcadas como expiradas")
    
    return affected


def get_all_keys() -> list:
    """Obtiene todas las keys (para administración)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT key, duration_hours, created_at, activated_at, user_id, status
        FROM access_keys
        ORDER BY created_at DESC
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


# Inicializar DB al importar el módulo
init_db()
