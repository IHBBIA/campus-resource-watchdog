import os
import time
import requests
from datetime import datetime

TARGET_URL = os.getenv("TARGET_URL", "http://192.168.64.2")
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")
CHAT_ID = os.getenv("CHAT_ID", "YOUR_TELEGRAM_CHAT_ID_HERE")
CHECK_INTERVAL = 10

server_is_up = True

def send_telegram_alert(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_msg = f"[{timestamp}]\n{message}"
    print(formatted_msg)

    if BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        print("Alert skipped: Set BOT_TOKEN and CHAT_ID environment variables.")
        return

    url = "https://api." + "telegram.org" + f"/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": formatted_msg}
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code != 200:
            print(f"Telegram API error: {response.text}")
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")

if __name__ == "__main__":
    print(f"Starting Campus Watchdog monitoring {TARGET_URL}...")
    while True:
        try:
            start_time = time.time()
            response = requests.get(TARGET_URL, timeout=3)
            latency_ms = round((time.time() - start_time) * 1000, 1)

            if response.status_code == 200:
                if not server_is_up:
                    send_telegram_alert(
                        f"✅ RESOLVED: Campus Resource Hub is back online!\n"
                        f"Response Time: {latency_ms}ms"
                    )
                    server_is_up = True
                else:
                    print(f"OK - Status 200 | Latency: {latency_ms}ms")
            else:
                if server_is_up:
                    send_telegram_alert(
                        f"⚠️ SERVICE DEGRADED: Campus Resource Hub returned HTTP {response.status_code}.\n"
                        f"User Impact: Students may see broken lab availability data.\n"
                        f"Action Needed: Inspect Nginx logs on VM1-Server."
                    )
                    server_is_up = False

        except requests.exceptions.RequestException:
            if server_is_up:
                send_telegram_alert(
                    f"🚨 CRITICAL OUTAGE: Campus Resource Hub ({TARGET_URL}) is offline!\n"
                    f"User Impact: Students cannot check 3D printer or study pod availability.\n"
                    f"Next Step: Verify VM1-Server status and run 'sudo systemctl restart nginx'."
                )
                server_is_up = False

        time.sleep(CHECK_INTERVAL)
