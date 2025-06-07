from dotenv import load_dotenv
import os
import base64
import hashlib
import re
import requests
import urllib.parse

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
REDIRECT_URI = os.getenv("REDIRECT_URI")
TOKEN_URL = "https://accounts.spotify.com/api/token"

# generate a code verifier (source: https://www.stefaanlippens.net/oauth-code-flow-pkce.html)
def generate_code_verifier():
    raw = base64.urlsafe_b64encode(os.urandom(40)).decode('utf-8')
    code_verifier = re.sub('[^a-zA-Z0-9]+', '', raw)
    return code_verifier

# PKCE code challenge
def generate_code_challenge(verifier):
    hashed = hashlib.sha256(verifier.encode('utf-8')).digest()
    challenge = base64.urlsafe_b64encode(hashed).decode('utf-8')
    code_challenge = challenge.replace('=', '')
    return code_challenge

# request user authorization

def get_auth_url(verifier):
    challenge = generate_code_challenge(verifier)
    auth_URL = "https://accounts.spotify.com/authorize"
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "scope": "playlist-modify-private playlist-modify-public user-read-private user-read-email",
        "code_challenge_method": "S256",
        "code_challenge": challenge,
        "redirect_uri": REDIRECT_URI,
    }
    return f"{auth_URL}?{urllib.parse.urlencode(params)}"

def exchange_code_for_token(code, verifier):
    data = {
        "grant-type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "code_verifier": verifier
    }

    response = requests.post(TOKEN_URL, data=data)
    return response.json()
