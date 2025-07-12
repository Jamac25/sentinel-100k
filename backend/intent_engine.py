import re
import os
import openai

class IntentEngine:
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        if self.openai_key:
            openai.api_key = self.openai_key

    def detect_intent(self, message: str) -> str:
        msg = message.lower()
        # Komentopohjaiset intentit (regex)
        if "/setgoal" in msg or "tavoite" in msg:
            return "SET_GOAL"
        if "/onboarding" in msg or "aloita onboarding" in msg:
            return "ONBOARDING"
        if "/dashboard" in msg or "dashboard" in msg or "tilannekatsaus" in msg:
            return "DASHBOARD"
        if "/start" in msg:
            return "START"
        if "/analyysi" in msg or "analyysi" in msg or "/runanalysis" in msg:
            return "RUN_ANALYSIS"
        if "/cycle" in msg or "aloita uusi sykli" in msg or "/newcycle" in msg:
            return "START_CYCLE"
        if "/week" in msg or "viikko" in msg:
            return "WEEK"
        if "/report" in msg or "raportti" in msg:
            return "REPORT"
        if "/income" in msg or "tulot" in msg:
            return "INCOME"
        if "/expenses" in msg or "menot" in msg:
            return "EXPENSES"
        if "/motivate" in msg or "motivo" in msg:
            return "MOTIVATE"
        if "/help" in msg or "apua" in msg:
            return "HELP"
        if "/settings" in msg or "asetukset" in msg:
            return "SETTINGS"
        if "/export" in msg or "vie profiili" in msg:
            return "EXPORT"
        if "/delete" in msg or "poista profiili" in msg:
            return "DELETE"
        if "/risk" in msg or "riskini" in msg or "riskianalyysi" in msg:
            return "RISK"
        # Universaali fallback: OpenAI intent tunnistus
        if self.openai_key:
            return self.openai_intent(message)
        return "UNKNOWN"

    def extract_parameters(self, message: str, intent: str) -> dict:
        params = {}
        # Regex-parametrit
        if intent in ["SET_GOAL", "INCOME", "EXPENSES"]:
            match = re.search(r"(\d+)", message)
            if match:
                params["amount"] = int(match.group(1))
        if intent == "WEEK":
            match = re.search(r"viikko\s*(\d+)", message)
            if match:
                params["week"] = int(match.group(1))
        # Universaali fallback: OpenAI parametrihaku
        if self.openai_key and not params:
            params = self.openai_parameters(message, intent)
        return params

    def openai_intent(self, message: str) -> str:
        prompt = f"Mikä on seuraavan viestin intentti? Vastaa vain yhdellä sanalla (esim. SET_GOAL, INCOME, EXPENSES, REPORT, MOTIVATE, HELP, START_CYCLE, RUN_ANALYSIS, DASHBOARD, ONBOARDING, SETTINGS, EXPORT, DELETE, RISK, UNKNOWN). Viesti: '{message}'"
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=10,
                temperature=0
            )
            intent = response.choices[0].text.strip().upper()
            return intent if intent else "UNKNOWN"
        except Exception:
            return "UNKNOWN"

    def openai_parameters(self, message: str, intent: str) -> dict:
        prompt = f"Poimi intentin '{intent}' tarvitsemat parametrit viestistä: '{message}'. Palauta JSON-muodossa. Esim. {{\"amount\": 20000}} tai {{}} jos ei löydy."
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=30,
                temperature=0
            )
            import json
            params = json.loads(response.choices[0].text.strip())
            return params if isinstance(params, dict) else {}
        except Exception:
            return {} 