import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "cameras.db"

class Database:
    def __init__(self):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        cur = self.conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS cameras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nvr TEXT NOT NULL,
            canal TEXT NOT NULL,
            nome TEXT NOT NULL,
            ip TEXT NOT NULL,
            local TEXT NOT NULL,
            status TEXT DEFAULT 'DESCONHECIDO',
            ultima_mudanca TEXT
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            camera_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            data_hora TEXT NOT NULL,
            FOREIGN KEY(camera_id) REFERENCES cameras(id)
        )
        """)

        self.conn.commit()

    def add_camera(self, nvr, canal, nome, ip, local):
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO cameras (nvr, canal, nome, ip, local, status)
            VALUES (?, ?, ?, ?, ?, 'DESCONHECIDO')
        """, (nvr, canal, nome, ip, local))
        self.conn.commit()

    def update_camera(self, camera_id, nvr, canal, nome, ip, local):
        cur = self.conn.cursor()
        cur.execute("""
            UPDATE cameras
            SET nvr=?, canal=?, nome=?, ip=?, local=?
            WHERE id=?
        """, (nvr, canal, nome, ip, local, camera_id))
        self.conn.commit()

    def delete_camera(self, camera_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM historico WHERE camera_id=?", (camera_id,))
        cur.execute("DELETE FROM cameras WHERE id=?", (camera_id,))
        self.conn.commit()

    def get_camera(self, camera_id):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM cameras WHERE id=?", (camera_id,))
        row = cur.fetchone()
        return dict(row) if row else None

    def get_cameras(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM cameras ORDER BY nvr, CAST(canal AS INTEGER), nome")
        return [dict(r) for r in cur.fetchall()]

    def update_status(self, camera_id, new_status):
        cam = self.get_camera(camera_id)
        if not cam:
            return

        old_status = cam["status"]
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        if old_status != new_status:
            cur = self.conn.cursor()
            cur.execute("""
                UPDATE cameras
                SET status=?, ultima_mudanca=?
                WHERE id=?
            """, (new_status, now, camera_id))

            cur.execute("""
                INSERT INTO historico (camera_id, status, data_hora)
                VALUES (?, ?, ?)
            """, (camera_id, new_status, now))

            self.conn.commit()

    def get_history(self):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT h.status, h.data_hora, c.nome, c.ip
            FROM historico h
            JOIN cameras c ON c.id = h.camera_id
            ORDER BY h.id DESC
        """)
        return [dict(r) for r in cur.fetchall()]
