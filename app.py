import requests
from flask import Flask, session, redirect, request, send_from_directory, jsonify
from auth import get_auth_url, generate_code_verifier, SECRET_KEY, exchange_code_for_token

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY

@app.route("/")
def index():
    if "access_token" in session:
        return redirect("/user")
    else:
        return redirect("/login")

# redirect to the auth URL
@app.route("/login")
def login():
    if 'verifier' not in session:
        session['verifier'] = generate_code_verifier()
    url = get_auth_url(session['verifier'])
    return redirect(url)

# catch the redirect
@app.route("/callback")
def callback():
    code = request.args.get("code")
    verifier = session.get("verifier")

    if not code or not verifier:
        return "Missing code or verifier", 400
    
    token_response = exchange_code_for_token(code, verifier)

    if "access_token" in token_response:
        session['access_token'] = token_response['access_token']
        return redirect("/user") # redirects user to their profile
    else:
        return f"Error: {token_response}", 400
    
@app.route("/user")
def profile():
    if "access_token" not in session:
        return redirect("/login")
    return send_from_directory("static", "main.html")


@app.route("/user-data")
def user_data():
    token = session.get("access_token")
    if not token:
        return jsonify({"error": "Unauthorized"}), 401
    
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get("https://api.spotify.com/v1/me", headers=headers)

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch profile"}), 500
    
    return response.json()


app.run(debug=True)