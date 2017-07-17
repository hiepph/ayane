import time


class History:
    def __init__(self, db_conn, db_cur):
        self.db_conn = db_conn
        self.db_cur = db_cur


    def remember(self, message, flag):
        self.db_cur.execute("INSERT INTO history (message, flag, created_at) VALUES (%s, %s, CURRENT_TIME);",
                            (message, flag))
        self.db_conn.commit()

    def latest(self):
        self.db_cur.execute("SELECT * FROM history ORDER BY id DESC LIMIT(1);")
        return self.db_cur.fetchone()
