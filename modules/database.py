import sqlite3
import json
import os

class Database:
    def __init__(self, db_path="facelock.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialise la base de données SQLite."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    embedding TEXT NOT NULL
                )
            ''')
            conn.commit()

    def add_user(self, name, embedding):
        """Ajoute un utilisateur avec son embedding (vecteur converti en JSON)."""
        # embedding est une liste ou un array numpy
        if hasattr(embedding, 'tolist'):
            embedding_list = embedding.tolist()
        else:
            embedding_list = embedding
            
        embedding_json = json.dumps(embedding_list)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (name, embedding) VALUES (?, ?)", (name, embedding_json))
            conn.commit()

    def get_all_users(self):
        """Récupère tous les utilisateurs et leurs embeddings."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, embedding FROM users")
            rows = cursor.fetchall()
            
            users = []
            for row in rows:
                users.append({
                    "name": row[0],
                    "embedding": json.loads(row[1])
                })
            return users

    def delete_user(self, name):
        """Supprime un utilisateur par son nom (Droit à l'oubli)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE name = ?", (name,))
            conn.commit()
