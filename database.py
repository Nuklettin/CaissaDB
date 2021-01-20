import os
import urllib.parse as urlparse
import psycopg2
from flask import flash
from passlib.hash import pbkdf2_sha256 as hasher


class Database:
    def __init__(self):
        self

    def new_player(self, username, password):
        hashedPass = hasher.hash(password)
        url = urlparse.urlparse(os.environ['DATABASE_URL'])
        dbname = url.path[1:]
        user = url.username
        password = url.password
        host = url.hostname
        port = url.port

        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )

        cur = conn.cursor()
        query = "SELECT username FROM player WHERE username = '" + username + "';"
        cur.execute(query)
        record = cur.fetchall()
        for row in record:
            if row is not None:
                flash("User already exists!")
                return 0
        cur.execute("""WITH data AS( INSERT INTO player (username, password) VALUES (%s,%s) RETURNING user_id) 
                            INSERT INTO elo (elo_id) SELECT * FROM data;""", (username, hashedPass))
        conn.commit()

    def play_match(self, white_player, black_player, time_format, pgn):
        url = urlparse.urlparse(os.environ['DATABASE_URL'])
        dbname = url.path[1:]
        user = url.username
        password = url.password
        host = url.hostname
        port = url.port

        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        cur = conn.cursor()
        query = "SELECT title FROM player WHERE username = '" + white_player + "' OR username = '" + black_player + "';"
        cur.execute(query)
        record = cur.fetchall()
        is_titled = False
        for row in record:
            if row is not None:
                is_titled = True

        query = "SELECT user_id FROM player WHERE username = '" + white_player + "';"
        cur.execute(query)
        record = cur.fetchall()
        for row in record:
            white_player = row[0]

        query = "SELECT user_id FROM player WHERE username = '" + black_player + "';"
        old_black = black_player
        changed = False
        cur.execute(query)
        record = cur.fetchall()
        for row in record:
            black_player = row[0]
        if black_player != old_black:
            changed = True
        if black_player is not None and white_player is not None and changed is True:
            if time_format == 'blitz':
                cur.execute("""WITH data AS( INSERT INTO match (white_player, black_player, titled, time_format, pgn) VALUES (%s,%s,%s,%s,%s) RETURNING white_player) 
                                UPDATE elo SET elo_blitz = elo_blitz + 5 WHERE elo_id = (SELECT * FROM data);""",
                            (white_player, black_player, is_titled, time_format, pgn))
            if time_format == 'bullet':
                cur.execute("""WITH data AS( INSERT INTO match (white_player, black_player, titled, time_format, pgn) VALUES (%s,%s,%s,%s,%s) RETURNING white_player) 
                                UPDATE elo SET elo_bullet = elo_bullet + 5 WHERE elo_id = (SELECT * FROM data);""",
                            (white_player, black_player, is_titled, time_format, pgn))
            if time_format == 'rapid':
                cur.execute("""WITH data AS( INSERT INTO match (white_player, black_player, titled, time_format, pgn) VALUES (%s,%s,%s,%s,%s) RETURNING white_player) 
                                UPDATE elo SET elo_rapid = elo_rapid + 5 WHERE elo_id = (SELECT * FROM data);""",
                            (white_player, black_player, is_titled, time_format, pgn))
            if time_format == 'classic':
                cur.execute("""WITH data AS( INSERT INTO match (white_player, black_player, titled, time_format, pgn) VALUES (%s,%s,%s,%s,%s) RETURNING white_player) 
                                UPDATE elo SET elo_classic = elo_classic + 5 WHERE elo_id = (SELECT * FROM data);""",
                            (white_player, black_player, is_titled, time_format, pgn))
        conn.commit()

    def delete_player(self, username):
        url = urlparse.urlparse(os.environ['DATABASE_URL'])
        dbname = url.path[1:]
        user = url.username
        password = url.password
        host = url.hostname
        port = url.port

        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        cur = conn.cursor()
        query = "WITH data AS( DELETE FROM player WHERE username = '" + username + "' RETURNING user_id) DELETE FROM elo WHERE elo_id = (SELECT * FROM data);"
        cur.execute(query)
        conn.commit()

    def rankings(self, time_format):
        url = urlparse.urlparse(os.environ['DATABASE_URL'])
        dbname = url.path[1:]
        user = url.username
        password = url.password
        host = url.hostname
        port = url.port

        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        cur = conn.cursor()
        query = "SELECT elo_" + time_format + ", elo_id, DENSE_RANK() OVER(ORDER BY elo_" + time_format + " DESC) FROM elo";
        cur.execute(query)
        records = cur.fetchall()
        conn.commit()
        return records

    def matches(self, time_format):
        url = urlparse.urlparse(os.environ['DATABASE_URL'])
        dbname = url.path[1:]
        user = url.username
        password = url.password
        host = url.hostname
        port = url.port

        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        cur = conn.cursor()
        query = "SELECT white_player,black_player, DENSE_RANK() OVER(ORDER BY match_id) FROM match WHERE time_format = '" + time_format + "';"
        cur.execute(query)
        records = cur.fetchall()
        conn.commit()
        return records

    #
    # def delete_match(self, match_id):
    #     url = urlparse.urlparse(os.environ['DATABASE_URL'])
    #     dbname = url.path[1:]
    #     user = url.username
    #     password = url.password
    #     host = url.hostname
    #     port = url.port
    #
    #     conn = psycopg2.connect(
    #         dbname=dbname,
    #         user=user,
    #         password=password,
    #         host=host,
    #         port=port
    #     )
    #     cur = conn.cursor()
    #     query = "DELETE FROM match WHERE match_id = " + match_id + ";"
    #     cur.execute(query)
    #     conn.commit()
