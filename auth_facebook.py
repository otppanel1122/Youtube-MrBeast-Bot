import os
import sys
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

APP_ID = "1731635695205184"
APP_SECRET = "318729cf3b1db6a53ad068d554cdded2"
REDIRECT_URI = "http://localhost:8095/"
SCOPES = "pages_show_list,pages_read_engagement,pages_manage_posts,publish_video"

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
            <body style="font-family:sans-serif; text-align:center; padding:50px; background:#1877F2; color:#fff;">
                <h1>&#10004; Facebook Page Authentication Successful!</h1>
                <p>Your Facebook Page has been connected. You can close this window and return to the chat.</p>
            </body>
            </html>
            """)
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"No authorization code received.")
            
    def log_message(self, format, *args):
        pass

def exchange_code_for_page_token(code):
    print("\n[Step 1] Exchanging authorization code for short-lived user token...")
    token_url = "https://graph.facebook.com/v20.0/oauth/access_token"
    params = {
        "client_id": APP_ID,
        "client_secret": APP_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": code
    }
    r = requests.get(token_url, params=params, timeout=30)
    if r.status_code != 200:
        print("[ERROR] Failed to get user access token:", r.text)
        return None, None
        
    user_token = r.json().get("access_token")
    print("[SUCCESS] User access token obtained.")
    
    print("\n[Step 2] Exchanging for long-lived user token...")
    long_params = {
        "grant_type": "fb_exchange_token",
        "client_id": APP_ID,
        "client_secret": APP_SECRET,
        "fb_exchange_token": user_token
    }
    r_long = requests.get(token_url, params=long_params, timeout=30)
    if r_long.status_code == 200:
        long_user_token = r_long.json().get("access_token")
        print("[SUCCESS] Long-lived user token obtained.")
    else:
        long_user_token = user_token
        
    print("\n[Step 3] Fetching managed Facebook Pages and Permanent Page Tokens...")
    accounts_url = "https://graph.facebook.com/v20.0/me/accounts"
    r_acc = requests.get(accounts_url, params={"access_token": long_user_token}, timeout=30)
    if r_acc.status_code != 200:
        print("[ERROR] Failed to fetch accounts:", r_acc.text)
        return None, None
        
    pages = r_acc.json().get("data", [])
    if not pages:
        print("[ERROR] No Facebook Pages found under this account.")
        return None, None
        
    print(f"\nFound {len(pages)} Facebook Page(s):")
    for p in pages:
        print(f" - Page: '{p.get('name')}' (ID: {p.get('id')})")
        
    # Select first page or match by name
    target_page = pages[0]
    for p in pages:
        if "fan" in p.get("name", "").lower():
            target_page = p
            break
            
    page_id = target_page.get("id")
    page_token = target_page.get("access_token")
    page_name = target_page.get("name")
    
    print("\n" + "=" * 65)
    print(f"🎉 SELECTED PAGE: {page_name} (ID: {page_id})")
    print(f"🔑 PERMANENT PAGE ACCESS TOKEN:\n{page_token}")
    print("=" * 65)
    
    # Save to .env
    env_path = ".env"
    lines = []
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            lines = [l for l in f.readlines() if not (l.startswith("FACEBOOK_PAGE_ID=") or l.startswith("FACEBOOK_PAGE_ACCESS_TOKEN="))]
    lines.append(f"FACEBOOK_PAGE_ID={page_id}\n")
    lines.append(f"FACEBOOK_PAGE_ACCESS_TOKEN={page_token}\n")
    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print("Saved FACEBOOK_PAGE_ID and FACEBOOK_PAGE_ACCESS_TOKEN to .env file.")
    
    return page_id, page_token

def main():
    global auth_code
    print("=" * 65)
    print("🔑 FACEBOOK PAGE REELS - DIRECT OAUTH AUTHORIZATION")
    print("=" * 65)
    
    auth_params = {
        "client_id": APP_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES
    }
    auth_url = f"https://www.facebook.com/v20.0/dialog/oauth?{urllib.parse.urlencode(auth_params)}"
    
    print("\n[STEP 1] Please click or open this link in your browser to authorize:")
    print(auth_url)
    print("\n[STEP 2] Waiting for callback on http://localhost:8095/ ...\n")
    
    server = HTTPServer(("localhost", 8095), OAuthCallbackHandler)
    while not auth_code:
        server.handle_request()
        
    page_id, page_token = exchange_code_for_page_token(auth_code)
    if page_id and page_token:
        print("\n[COMPLETE] Facebook Reels automation is fully authorized and ready!")
    else:
        print("\n[FAILED] Could not retrieve Page Access Token.")
        sys.exit(1)

if __name__ == "__main__":
    main()
