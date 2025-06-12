import requests
from flask import Flask, session, redirect, request, send_from_directory, jsonify
from auth import get_auth_url, generate_code_verifier, SECRET_KEY, exchange_code_for_token
import db
import spotify_api_logic
import random

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY

# 🔐 OAuth routes
@app.route("/")
def index():
    if "access_token" in session:
        return redirect("/user")
    else:
        return redirect("/login")

@app.route("/login")
def login():
    if 'verifier' not in session:
        session['verifier'] = generate_code_verifier()
    url = get_auth_url(session['verifier'])
    return redirect(url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    verifier = session.get("verifier")

    if not code or not verifier:
        return "Missing code or verifier", 400

    token_response = exchange_code_for_token(code, verifier)

    if "access_token" not in token_response:
        return f"Error: {token_response}", 400

    access_token = token_response["access_token"]
    session["access_token"] = access_token

    # Fetch user profile
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://api.spotify.com/v1/me", headers=headers)
    if response.status_code != 200:
        return "Failed to fetch user profile", 500

    user_data = response.json()
    session["spotify_user_id"] = user_data["id"]
    session["spotify_display_name"] = user_data["display_name"]
    session["spotify_images"] = user_data.get("images", [])

    return redirect("/user")

@app.route("/user")
def profile():
    if "access_token" not in session:
        return redirect("/login")
    return send_from_directory("static", "main.html")

@app.route("/user-data")
def user_data():
    if "access_token" not in session or "spotify_user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    return jsonify({
        "id": session["spotify_user_id"],
        "display_name": session["spotify_display_name"],
        "images": session.get("spotify_images", [])
    })

# 🎨 Artist Routes
@app.route("/artists", methods=["GET", "POST"])
def artists():
    if "access_token" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    token = session["access_token"]

    if request.method == "GET":
        artists = []
        for artist in db.get_all_artists():
            artists.append({
                "name": artist[0],
                "num_albums": artist[1],
                "popularity": artist[2],
                "top_tracks": artist[3]
            })
        return jsonify(artists)

    else:
        data = request.get_json()
        if not data or "artist_name" not in data:
            return jsonify({"error": "artist_name is required"}), 400

        artist_name = data["artist_name"]
        artist_result = spotify_api_logic.search_for_artist(token, artist_name)

        if artist_result is None:
            return jsonify({"error": "Artist not found on Spotify"}), 404

        real_name = artist_result['name']
        artist_id = artist_result['id']

        if db.artist_in_db(real_name):
            return jsonify({"error": f"Artist '{real_name}' already exists in the database."}), 409

        num_albums = spotify_api_logic.get_num_artist_albums(token, artist_id)
        avg_popularity = spotify_api_logic.get_avg_pop_score(token, artist_id)
        top_tracks = spotify_api_logic.get_artists_top_tracks_string(token, artist_id)

        db.insert_artist(real_name, num_albums, avg_popularity, top_tracks)

        return jsonify({"message": f"Artist '{real_name}' added successfully."}), 201

@app.route("/artists/<name>", methods=["DELETE"])
def delete_artist(name):
    if "access_token" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    if not db.artist_in_db(name):
        return jsonify({"error": f"Artist '{name}' does not exist in the database."}), 404

    db.delete_artist(name)
    return jsonify({"message": f"Artist '{name}' deleted successfully."}), 200

# 🎲 Blind Box Route
@app.route("/blindbox/<name>", methods=["POST"])
def artist_blindbox(name):
    token = session.get("access_token")
    if not token:
        return jsonify({"error": "Unauthorized"}), 401

    artist = spotify_api_logic.search_for_artist(token, name)
    if not artist:
        return jsonify({"error": "Artist not found"}), 404

    artist_id = artist["id"]
    track_list = spotify_api_logic.get_artists_top_tracks(token, artist_id)

    if not track_list:
        return jsonify({"error": "No top tracks found for this artist."}), 500

    selected_tracks = random.sample(track_list, min(len(track_list), 5))

    box_results = []
    for track in selected_tracks:
        popularity = track["popularity"]
        rarity = (
            "Epic" if popularity >= 80 else
            "Rare" if popularity >= 60 else
            "Common"
        )
        box_results.append({
            "track": track["name"],
            "rarity": rarity,
            "preview_url": track.get("preview_url"),
            "album_image": track["album"]["images"][0]["url"] if track["album"]["images"] else None
        })

    return jsonify({
        "artist": artist["name"],
        "box_results": box_results
    })

# 🎒 Inventory Routes
@app.route("/inventory", methods=["GET", "POST", "DELETE"])
def inventory():
    user = session.get("spotify_user_id")
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == "POST":
        data = request.get_json()
        if not data or "track" not in data:
            return jsonify({"error": "Missing track name"}), 400

        try:
            db.add_to_inventory(
                user=user,
                track=data["track"],
                rarity=data.get("rarity", "Unknown"),
                preview_url=data.get("preview_url"),
                album_image=data.get("album_image")
            )
            return jsonify({"message": f"{data['track']} saved to inventory."}), 201
        except:
            return jsonify({"error": f"{data['track']} is already in your inventory."}), 409

    elif request.method == "GET":
        inventory = db.get_inventory(user)
        cards = [{
            "track": row[0],
            "rarity": row[1],
            "preview_url": row[2],
            "album_image": row[3]
        } for row in inventory]
        return jsonify(cards)

    elif request.method == "DELETE":
        data = request.get_json()
        if not data or "track" not in data:
            return jsonify({"error": "Missing track name"}), 400

        try:
            db.delete_from_inventory(user, data["track"])
            return jsonify({"message": f"{data['track']} removed from inventory."}), 200
        except:
            return jsonify({"message": f"{data['track']} was already removed."}), 200

if __name__ == "__main__":
    db.initalize_db()
    app.run(debug=True)