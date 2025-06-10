import requests
from flask import Flask, session, redirect, request
from auth import get_auth_url, generate_code_verifier, SECRET_KEY, exchange_code_for_token

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY

@app.route("/")
def index():
    return redirect("/login")

# redirect to the auth URL
@app.route("/login")
def login():
    session['verifier'] = generate_code_verifier() # store in Flask session
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
        return "login successful!"
    else:
        return f"Error: {token_response}", 400
    
@app.route("/me")
def profile():
    token = session.get("access_token")
    if not token:
        return redirect("/login")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get("https://api.spotify.com/v1/me", headers=headers)

    return response.json()


app.run(debug=True)