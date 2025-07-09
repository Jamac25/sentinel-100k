# 🔑 OPENAI API KEY SETUP RENDER-PALVELUSSA

## ❌ ONGELMA
OpenAI API avain ei toimi Render-palvelussa, koska se puuttuu ympäristömuuttujista.

## ✅ RATKAISU

### 1. Mene Render-paneeliin
- Avaa: https://dashboard.render.com/
- Kirjaudu sisään
- Etsi "sentinel-100k" palvelu

### 2. Lisää OpenAI API avain
1. Klikkaa "sentinel-100k" palvelua
2. Mene "Environment" välilehdelle
3. Etsi "OPENAI_API_KEY" rivi
4. Klikkaa "Add" tai "Edit"
5. Lisää oikea OpenAI API avain (alkaa "sk-...")
6. Tallenna muutokset

### 3. Käynnistä palvelu uudelleen
1. Mene "Manual Deploy" välilehdelle
2. Klikkaa "Deploy latest commit"
3. Odota että palvelu käynnistyy uudelleen

### 4. Testaa toimivuus
```bash
curl -X POST "https://sentinel-100k.onrender.com/api/v1/chat/enhanced?user_email=test@example.com" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hei, kerro talousvinkkejä"}'
```

## 🔍 DEBUGGING

### Tarkista API avain
```bash
curl -X GET "https://sentinel-100k.onrender.com/health"
```

### Tarkista debug-tiedot
Vastauksessa pitäisi näkyä:
```json
{
  "debug": {
    "openai_key_available": true,
    "openai_key_length": 51,
    "openai_key_starts_with": "sk-..."
  }
}
```

## 🚨 VIRHEILMOITUKSET

Jos API avain puuttuu:
```json
{
  "response": "❌ OpenAI API avain puuttuu tai on virheellinen. Ota yhteyttä ylläpitoon.",
  "error": "OPENAI_API_KEY_MISSING"
}
```

Jos API virhe:
```json
{
  "response": "❌ OpenAI API virhe: [virheviesti]",
  "error": "OPENAI_API_ERROR"
}
```

## ✅ KUN TOIMII

Kun OpenAI API avain on lisätty oikein:
- Vastaukset ovat henkilökohtaisia ja älykkäitä
- `openai_used: true` vastauksessa
- `model: "gpt-3.5-turbo"` vastauksessa
- Ei fallback-tilaa

## 📞 APUA

Jos ongelmat jatkuvat:
1. Tarkista että API avain on oikea
2. Tarkista että palvelu on käynnistynyt uudelleen
3. Tarkista Render-lokit virheiden varalta 