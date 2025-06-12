import sqlite3

def create_inventory_table():
    con = sqlite3.connect('spotify.db')
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            track TEXT,
            rarity TEXT,
            preview_url TEXT,
            album_image TEXT,
            UNIQUE(user, track)
        )
    """)
    con.commit()
    con.close()

def initalize_db():
    con = sqlite3.connect('spotify.db')
    cur = con.cursor()
    # create table statement
    cur.execute("CREATE TABLE IF NOT EXISTS artist(name, num_albums, popularity, top_tracks)") # include if not exists to bypass the "table already exists" error message
    create_inventory_table()

# Replaces curly quotes with straight quotes and trims whitespace
def normalize(text):
    return text.replace("’", "'").replace("‘", "'").strip()

def insert_artist(name, num_albums, popularity, top_tracks):
    con = sqlite3.connect('spotify.db')
    with con:
        con.execute("INSERT INTO artist(name, num_albums, popularity, top_tracks) VALUES(?, ?, ?, ?)", (name, num_albums, popularity, top_tracks))
    con.commit()
    con.close()

def get_all_artists():
    con = sqlite3.connect('spotify.db')
    cur = con.cursor()
    
    cur.execute("SELECT name, num_albums, popularity, top_tracks FROM artist")
    rows = cur.fetchall()
    con.close()
    return rows

def print_artists_data():
    con = sqlite3.connect('spotify.db')
    cur = con.cursor()
    for row in cur.execute("SELECT name, num_albums, popularity, top_tracks FROM artist"):
        print(row)

def artist_in_db(name):
    con = sqlite3.connect('spotify.db')
    cur = con.cursor()   

    cur.execute("SELECT 1 FROM artist WHERE name = ?", (name,))
    exists = cur.fetchone() is not None
    con.close()
    return exists

def delete_artist(name):
    con = sqlite3.connect('spotify.db')
    cur = con.cursor()

    cur.execute("DELETE FROM artist WHERE name = ?", (name,))  
    con.commit()
    con.close()

def delete_db():
    con = sqlite3.connect('spotify.db')
    cur = con.cursor() 

    cur.execute("DELETE FROM artist")

    con.commit()
    con.close()

def drop_db():
    con = sqlite3.connect('spotify.db')
    cur = con.cursor() 

    cur.execute("DROP TABLE IF EXISTS artist")
    cur.execute("""
        CREATE TABLE artist (
            name TEXT,
            num_albums INTEGER,
            popularity REAL,
            top_tracks TEXT
        )
    """)

    con.commit()
    con.close()

def add_to_inventory(user, track, rarity, preview_url, album_image):
    track = normalize(track)
    con = sqlite3.connect('spotify.db')
    with con:
        con.execute("""
            INSERT INTO inventory (user, track, rarity, preview_url, album_image)
            VALUES (?, ?, ?, ?, ?)
        """, (user, track, rarity, preview_url, album_image))
    con.commit()
    con.close()

def get_inventory(user):
    con = sqlite3.connect('spotify.db')
    cur = con.cursor()
    cur.execute("SELECT track, rarity, preview_url, album_image FROM inventory WHERE user = ?", (user,))
    rows = cur.fetchall()
    con.close()

    return [(normalize(row[0]), row[1], row[2], row[3]) for row in rows]

def drop_inventory_table():
    con = sqlite3.connect('spotify.db')
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS inventory")
    con.commit()
    con.close()

def delete_from_inventory(user, track):
    track = normalize(track)  # 👈 normalize here too for consistency
    con = sqlite3.connect('spotify.db')
    with con:
        con.execute("DELETE FROM inventory WHERE user = ? AND track = ?", (user, track))
    con.commit()
    con.close()

def print_inventory():
    con = sqlite3.connect('spotify.db')
    cur = con.cursor()
    for row in cur.execute("SELECT * FROM inventory"):
        print("DB ROW:", row)
    con.close()

# initalize_db()

# drop_inventory_table()
# delete_db()
# print_artists_data()
# print_inventory()