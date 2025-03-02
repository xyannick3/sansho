import sqlite3
import time

DB_PATH = "bot/services/sansho.db"

###########SETUP DATABASE##################################

def setup_database() :
    """
    Creates the database table if it doesn't exist
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
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS shames (
                   user_id INTEGER PRIMARY KEY,
                   guild_id INTEGER NOT NULL,
                   unmute_time INTEGER NOT NULL
                   )
                   ''')
    conn.commit()
    conn.close()

###########MUTE DATABASE INTERACTIONS######################

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
    current_time = int(time.time())
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, guild_id FROM mutes WHERE unmute_time <= ?", (current_time,))
    expired_mutes = cursor.fetchall()
    conn.close()
    return expired_mutes


###########SHAME DATABASE INTERACTIONS#####################


def add_shame(user_id: int, guild_id: int, duration: int):
    """
    Stores a shame record in the database.
    """
    unmute_time = int(time.time()) + duration # when the guy will be unmuted
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO shames (user_id, guild_id, unmute_time) VALUES (?, ?, ?)",
                   (user_id,guild_id,unmute_time))
    conn.commit()
    conn.close()

def remove_shame(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM shames WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def get_expired_shames():
    current_time = int(time.time())
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, guild_id FROM shames WHERE unmute_time <= ?", (current_time,))
    expired_shames = cursor.fetchall()
    conn.close()
    return expired_shames