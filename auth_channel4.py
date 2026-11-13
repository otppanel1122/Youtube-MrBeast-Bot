import os
import sys
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from dotenv import load_dotenv

load_dotenv()

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8095/"
SCOPES = "https://www.googleapis.com/auth/youtube.upload"

auth_code = None

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        parsed_url = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed_url.query)
        
        if "code" in params:
            auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"""
            <html>
            <body style="font-family:sans-serif; text-align:center; padding:50px; background:#121212; color:#fff;">
                <h1 style="color:#4CAF50;">&#10004; Channel Authentication Successful!</h1>
                <p>Your new YouTube Channel has been authorized. You can close this window and return to the chat.</p>
            </body>
            </html>
            """)
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"No authorization code received.")
            
    def log_message(self, format, *args):
        pass

def exchange_code(code):
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI
    }
    r = requests.post(token_url, data=data, timeout=30)
    if r.status_code == 200:
        tokens = r.json()
        return tokens.get("refresh_token")
    else:
        print("[ERROR] Token exchange failed:", r.status_code, r.text)
        return None

def main():
    global auth_code
    print("=" * 65)
    print("🔑 NEW MRBEAST CHANNEL - OAUTH AUTHORIZATION")
    print("=" * 65)
    
    auth_params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,
        "access_type": "offline",
        "prompt": "consent"
    }
    auth_url = f"https://accounts.google.com/o/oauth2/auth?{urllib.parse.urlencode(auth_params)}"
    
    print("\n[STEP 1] Please click or open this link in your browser to authorize:")
    print(auth_url)
    print("\n[STEP 2] Waiting for callback on http://localhost:8095/ ...\n")
    
    server = HTTPServer(("localhost", 8095), OAuthCallbackHandler)
    while not auth_code:
        server.handle_request()
        
    print("\n[SUCCESS] Authorization code received! Exchanging for Refresh Token...")
    refresh_token = exchange_code(auth_code)
    
    if refresh_token:
        print("=" * 65)
        print("🎉 REFRESH TOKEN CAPTURED:")
        print(refresh_token)
        print("=" * 65)
        
        lines = []
        if os.path.exists(".env"):
            with open(".env", "r", encoding="utf-8") as f:
                lines = [l for l in f.readlines() if not l.startswith("YOUTUBE_REFRESH_TOKEN=")]
        lines.append(f"YOUTUBE_REFRESH_TOKEN={refresh_token}\n")
        with open(".env", "w", encoding="utf-8") as f:
            f.writelines(lines)
        print("Saved refresh token to .env file.")
        return refresh_token
    else:
        print("[FAILED] Could not obtain refresh token.")
        sys.exit(1)

if __name__ == "__main__":
    main()
