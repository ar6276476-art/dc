from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import ConnectEvent, DisconnectEvent
import requests
import time
import os

# ⚙️ CONFIG
USERNAME = "supelpr_"
WEBHOOK = os.environ.get("DISCORD_WEBHOOK_URL", "")
SESSION_ID = os.getenv("SESSION_ID", "")
SIGN_API_KEY = os.getenv("EULER_API_KEY", "")
PROXY_URL = os.getenv("PROXY_URL", "")

en_vivo = False

# Convert proxy format: host:port:user:pass → http://user:pass@host:port
def build_proxy_url(raw):
    if not raw:
        return None
    # Strip http:// prefix if present but format is wrong (no @ sign)
    cleaned = raw
    if raw.startswith("http://") and "@" not in raw:
        cleaned = raw[len("http://"):]
    if "@" in cleaned:
        return cleaned if cleaned.startswith("http") else f"http://{cleaned}"
    parts = cleaned.split(":")
    if len(parts) >= 4:
        host, port, user = parts[0], parts[1], parts[2]
        password = ":".join(parts[3:])
        return f"http://{user}:{password}@{host}:{port}"
    return raw

_proxy = build_proxy_url(PROXY_URL)
proxies = {"http://": _proxy, "https://": _proxy} if _proxy else None

client = TikTokLiveClient(unique_id=USERNAME, sign_api_key=SIGN_API_KEY, proxies=proxies)

# 🔐 Inject session cookie into the HTTP client
if SESSION_ID:
    client.http.cookies["sessionid"] = SESSION_ID
    print("🔐 SESSION_ID aplicado")

if SIGN_API_KEY:
    print("✅ Signing API key aplicado")

if PROXY_URL:
    print("🌐 Proxy aplicado")


def enviar_discord():
    data = {
        "content": "@everyone",
        "embeds": [
            {
                "title": "🔥 POLLITOWAZA EN VIVO 🔥",
                "description": "¡Está en directo ahora mismo!\n\n👉 Entra ya antes que termine",
                "url": f"https://www.tiktok.com/@{USERNAME}/live",
                "color": 10181046,
                "author": {
                    "name": "Pollitowaza",
                    "url": f"https://www.tiktok.com/@{USERNAME}"
                },
                "image": {
                    "url": "https://i.imgur.com/tu_banner.png"
                },
                "footer": {
                    "text": "Notificación automática • TikTok Live"
                }
            }
        ]
    }

    try:
        requests.post(WEBHOOK, json=data)
        print("✅ Notificación enviada a Discord")
    except Exception as e:
        print("❌ Error enviando a Discord:", e)


@client.on(ConnectEvent)
async def on_connect(event):
    global en_vivo
    if not en_vivo:
        print("🔴 LIVE DETECTADO")
        enviar_discord()
        en_vivo = True


@client.on(DisconnectEvent)
async def on_disconnect(event):
    global en_vivo
    print("⚫ Live terminado")
    en_vivo = False


# 🔁 LOOP PRO (RECONEXIÓN AUTOMÁTICA)
while True:
    try:
        print("🔄 Intentando conectar...")
        client.run()
    except Exception as e:
        print("⚠️ Error, reconectando...", e)
        time.sleep(10)
