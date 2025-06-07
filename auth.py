from dotenv import load_dotenv
import os

load_dotenv()

client_id = os.getenv("CLIENT_ID")

print(client_id)