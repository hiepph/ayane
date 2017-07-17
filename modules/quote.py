def quote_info(q):
    return '(%s) *%s* - %s' % (q['id'], q['content'], q['author'])


class Quote:
    def __init__(self, db_conn, db_cur):
        self.db_conn = db_conn
        self.db_cur = db_cur


    def add_quote(self, author, content):
        self.db_cur.execute("INSERT INTO quotes (author, content, created_at) VALUES (%s, %s, CURRENT_TIME);",
                            (author, content))
        self.db_conn.commit()

    def latest_quote(self):
        self.db_cur.execute("SELECT * FROM quotes ORDER BY id DESC LIMIT(1);")
        return quote_info(self.db_cur.fetchone())

    def random_quote(self, author=None):
        if author == None:
            self.db_cur.execute("SELECT * FROM quotes ORDER BY random()")
        else:
            self.db_cur.execute("SELECT * FROM quotes WHERE author='%s' ORDER BY random()" % author)

        quote = self.db_cur.fetchone()
        if quote == None:
            return "Not found"
        else:
            return quote_info(quote)

    def list_quotes(self, author=None):
        if author == None:
            self.db_cur.execute("SELECT * FROM quotes ORDER BY id DESC;")
        else:
            self.db_cur.execute("SELECT * FROM quotes WHERE author='%s' ORDER BY id DESC" % author)

        quotes = self.db_cur.fetchall()
        if len(quotes) == 0:
            return "Not found"
        else:
            return "\n".join(map(quote_info, quotes))

    def quote(self, qid):
        self.db_cur.execute("SELECT * FROM quotes WHERE id=%s LIMIT(1);" % qid)
        q = self.db_cur.fetchone()
        if q == None:
            return "Not found"
        else:
            return quote_info(q)

    def delete_quote(self, qid):
        self.db_cur.execute("DELETE FROM quotes WHERE id=%s" % qid)
        self.db_conn.commit()
