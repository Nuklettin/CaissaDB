from movie import Player
from flask import flash, render_template, redirect
from passlib.hash import pbkdf2_sha256 as hasher
import psycopg2
import os
from urllib.parse import urlparse


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

        if time_format == 'blitz':
            cur.execute("""WITH data AS( INSERT INTO match (white_player, black_player, titled, time_format, pgn) VALUES (%s,%s,%s,%s,%s) RETURNING user_id) 
                    UPDATE elo SET elo_blitz = elo_blitz + 5 WHERE elo_id = SELECT * FROM data;""",
                        (white_player, black_player, is_titled, time_format, pgn))
        if time_format == 'bullet':
            cur.execute("""WITH data AS( INSERT INTO match (white_player, black_player, titled, time_format, pgn) VALUES (%s,%s,%s,%s,%s) RETURNING user_id) 
                            UPDATE elo SET elo_bullet = elo_bullet + 5 WHERE elo_id = (SELECT * FROM data);""",
                        (white_player, black_player, is_titled, time_format, pgn))
        if time_format == 'rapid':
            cur.execute("""WITH data AS( INSERT INTO match (white_player, black_player, titled, time_format, pgn) VALUES (%s,%s,%s,%s,%s) RETURNING user_id) 
                            UPDATE elo SET elo_rapid = elo_rapid + 5 WHERE elo_id = (SELECT * FROM data);""",
                        (white_player, black_player, is_titled, time_format, pgn))
        if time_format == 'classic':
            cur.execute("""WITH data AS( INSERT INTO match (white_player, black_player, titled, time_format, pgn) VALUES (%s,%s,%s,%s,%s) RETURNING user_id) 
                            UPDATE elo SET elo_classic = elo_classic + 5 WHERE elo_id = (SELECT * FROM data);""",
                        (white_player, black_player, is_titled, time_format, pgn))

        conn.commit()
