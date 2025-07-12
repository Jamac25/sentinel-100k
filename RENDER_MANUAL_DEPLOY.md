# 🚀 RENDER MANUAL DEPLOY OHJEET

## ❌ ONGELMA
Render-palvelussa on vanha koodi käytössä, vaikka uusi koodi on pushattu GitHubiin.

## ✅ RATKAISU: MANUAALINEN DEPLOY

### 1. Mene Render-paneeliin
- Avaa: https://dashboard.render.com/
- Kirjaudu sisään
- Etsi "sentinel-100k" palvelu

### 2. Käynnistä manuaalinen deploy
1. Klikkaa "sentinel-100k" palvelua
2. Mene "Manual Deploy" välilehdelle
3. Klikkaa "Deploy latest commit"
4. Odota että build valmistuu (2-5 minuuttia)

### 3. Tarkista build-lokit
1. Mene "Logs" välilehdelle
2. Tarkista että build onnistui
3. Etsi virheitä tai varoituksia

### 4. Testaa toimivuus
```bash
# Testaa debug-endpoint
curl -X GET "https://sentinel-100k.onrender.com/debug/openai"

# Testaa AI-chat
curl -X POST "https://sentinel-100k.onrender.com/api/v1/chat/enhanced?user_email=test@example.com" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hei, kerro talousvinkkejä"}'
```

## 🔍 ODOTETUT TULOKSET

### Debug-endpoint vastaus:
```json
{
  "openai_key_available": true,
  "openai_key_length": 51,
  "openai_key_starts_with": "sk-FXA8BE",
  "openai_key_is_test": false,
  "environment_vars": {
    "OPENAI_API_KEY": "✅ Set",
    "openAI": "❌ Not set",
    "OPENAI_KEY": "❌ Not set"
  },
  "final_key": "✅ Valid"
}
```

### AI-chat vastaus:
```json
{
  "response": "Henkilökohtainen AI-vastaus...",
  "model": "gpt-3.5-turbo",
  "openai_used": true,
  "ai_used": true
}
```

## 🚨 VIRHEILMOITUKSET

Jos debug-endpoint palauttaa "Not Found":
- Render ei ole vielä päivittänyt koodia
- Käynnistä manuaalinen deploy

Jos OpenAI API avain puuttuu:
- Tarkista että `OPENAI_API_KEY` on lisätty ympäristömuuttujiin
- Tarkista että avain on oikea (alkaa "sk-...")

Jos build epäonnistuu:
- Tarkista build-lokit virheiden varalta
- Tarkista että requirements.txt on oikein

## 📞 APUA

Jos ongelmat jatkuvat:
1. Tarkista Render-palvelun lokit
2. Varmista että GitHub-repo on oikein
3. Kokeile uudelleenkäynnistystä 