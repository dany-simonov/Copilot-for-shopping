import sqlite3
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('shopping_bot.db', check_same_thread=False)
        self.create_tables()
        
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dialogs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            chat_id INTEGER,
            question TEXT,
            answer TEXT,
            timestamp DATETIME
        )
        ''')
        self.conn.commit()
        
    def save_dialog(self, user_id, chat_id, question, answer):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO dialogs (user_id, chat_id, question, answer, timestamp) VALUES (?, ?, ?, ?, ?)',
            (user_id, chat_id, question, answer, datetime.now())
        )
        self.conn.commit()
