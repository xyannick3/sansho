import sqlite3
import time

DB_PATH = "bot/services/sansho.db"

def setup_database() :
    """
    Creaes the database table if it doesn't exist
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS mutes (
                    user_id INTEGER PRIMARY KEY,
                    guild_id INTEGER NOT NULL,
                    unmute_time INTEGER NOT NULL
                   )
                   ''')
    conn.commit()
    conn.close()

def add_mute(user_id: int, guild_id: int, duration: int):
    """
    Stores a mute record in the database.
    """
    unmute_time = int(time.time()) + duration # when the guy will be unmuted
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO mutes (user_id, guild_id, unmute_time) VALUES (?, ?, ?)",
                   (user_id,guild_id,unmute_time))
    conn.commit()
    conn.close()

def remove_mute(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM mutes WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_expired_mutes():
    current_time = int(time.tim())
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, guild_id FROM mutes WHERE unmute_time <= ?", (current_time))
    expired_mutes = cursor.fetchall()
    conn.close()
    return expired_mutes