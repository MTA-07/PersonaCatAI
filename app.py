import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

app = Flask(__name__)


OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

MODEL = os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini")

if not OPENROUTER_API_KEY:
    raise SystemExit("OPENROUTER_API_KEY tanımlı değil. Terminalde: $env:OPENROUTER_API_KEY=\"anahtarın\"")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    default_headers={"X-Title": "PersonaChat AI"},
)

PERSONAS = [
    {
        "id": "komik",
        "name": "Komik Arkadaş",
        "description": "Mizah dolu, samimi ve esprili cevaplar verir.",
        "icon": "😂",
        "color": "#d9822b",
        "system_prompt": "Sen esprili, mizah duygusu yüksek ve samimi bir arkadaşsın. Yanıtların eğlenceli ve şakacı olsun."
    },
    {
        "id": "ciddi",
        "name": "Ciddi Asistan",
        "description": "Profesyonel, net, kısa ve iş odaklı konuşur.",
        "icon": "💼",
        "color": "#4f6b9a",
        "system_prompt": "Sen profesyonel, resmi ve iş odaklı bir asistansın. Net, kısa ve gereksiz laf kalabalığı yapmadan yanıt ver."
    },
    {
        "id": "felsefeci",
        "name": "Felsefeci",
        "description": "Derin, düşündürücü ve sorgulayıcı bakış açıları sunar.",
        "icon": "🏛️",
        "color": "#9a7fb0",
        "system_prompt": "Sen antik çağlardan beri yaşayan bilge bir felsefecisin. Sorulara derin, sorgulayıcı ve felsefi bakış açılarıyla yaklaş."
    },
    {
        "id": "npc",
        "name": "Oyun NPC'si",
        "description": "Fantastik bir RPG oyunundaki bilge bir karakter gibi konuşur.",
        "icon": "⚔️",
        "color": "#c4623a",
        "system_prompt": "Sen fantastik bir RPG oyunundaki görev veren bilge bir NPC'sin (Non-Player Character). Oyuncuya bir macera evrenindeymiş gibi hitap et."
    },
    {
        "id": "bilim",
        "name": "Bilim İnsanı",
        "description": "Mantıklı, analitik, açıklayıcı ve teknik cevaplar verir.",
        "icon": "🔬",
        "color": "#2f8a7a",
        "system_prompt": "Sen analitik, bilimsel verilere önem veren bir bilim insanısın. Cevapların mantıklı ve açıklayıcı olsun."
    }
]

@app.route("/")
def home():
    return render_template("index.html", personas=PERSONAS)

@app.route("/chat/<persona_id>")
def chat(persona_id):
    selected_persona = next((p for p in PERSONAS if p["id"] == persona_id), None)
    if not selected_persona:
        return "Karakter bulunamadı!", 404
    return render_template("chat.html", persona=selected_persona, personas=PERSONAS)

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json()
    user_message = data.get("message")
    persona_id = data.get("persona_id")

    persona = next((p for p in PERSONAS if p["id"] == persona_id), None)
    system_prompt = persona["system_prompt"] if persona else "Sen yardımcı bir asistansın."

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        bot_reply = response.choices[0].message.content
    except Exception as e:
        print(f"API Hatası: {e}")
        bot_reply = "Üzgünüm, şu an bağlantıda bir aksaklık var. Lütfen API anahtarını ve model adını kontrol et!"

    return jsonify({"status": "success", "reply": bot_reply})

if __name__ == "__main__":
    app.run(debug=True)