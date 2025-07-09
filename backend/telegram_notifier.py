import os
import requests
import time

class TelegramNotifier:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.api_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def send(self, user_id: str, message: str):
        data = {"chat_id": user_id, "text": message}
        try:
            r = requests.post(self.api_url, data=data)
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def send_weekly_report(self, user_id: str):
        msg = "🗒️ Viikkoraporttisi on valmis! Säästösi etenevät hienosti."
        return self.send(user_id, msg)

    def send_night_analysis(self, user_id: str):
        msg = "🌙 Yöllinen analyysi suoritettu. Kaikki kunnossa!"
        return self.send(user_id, msg)

    def send_watchdog_alert(self, user_id: str):
        msg = "⚠️ Watchdog-hälytys: Tarkista taloutesi!"
        return self.send(user_id, msg)

    def send_motivation(self, user_id: str):
        msg = "🚀 Päivän motivaatioviesti: Jatka samaan malliin!"
        return self.send(user_id, msg)

    def send_bulk(self, user_ids, message):
        for uid in user_ids:
            self.send(uid, message)
            time.sleep(0.5)  # Rate limit 