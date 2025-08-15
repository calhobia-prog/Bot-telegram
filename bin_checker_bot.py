import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "7872625090:AAEGnskwJJhZOiTMhz2sA1JSqB2MrO2q2v4"  # coloque o token do BotFather aqui

def consultar_bin_binlist(bin_number):
    url = f"https://lookup.binlist.net/{bin_number}"
    try:
        r = requests.get(url, headers={"Accept-Version": "3"}, timeout=5)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None

def consultar_bin_antipublic(bin_number):
    url = f"https://bins.antipublic.cc/bins/{bin_number}"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            return {
                'scheme': data.get('scheme', 'N/A'),
                'type': data.get('type', 'N/A'),
                'brand': data.get('brand', 'N/A'),
                'bank': {'name': data.get('bank', 'N/A')},
                'country': {
                    'alpha2': data.get('country', ''),
                    'name': data.get('country_name', 'N/A')
                }
            }
    except:
        pass
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! Me envie um BIN (mínimo 6 dígitos) para consulta.")

async def consultar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bin_number = ''.join(filter(str.isdigit, update.message.text))
    if len(bin_number) < 6:
        await update.message.reply_text("⚠️ Digite pelo menos 6 números.")
        return

    resultado = consultar_bin_binlist(bin_number)
    if not resultado:
        resultado = consultar_bin_antipublic(bin_number)

    if not resultado:
        await update.message.reply_text("❌ Erro ao buscar dados em ambas as APIs.")
        return

    bandeira = resultado.get('scheme', 'N/A').capitalize()
    tipo = resultado.get('type', 'N/A')
    nivel = resultado.get('brand', 'N/A')
    banco = resultado.get('bank', {}).get('name', 'N/A')
    pais = resultado.get('country', {}).get('name', 'N/A')
    codigo_pais = resultado.get('country', {}).get('alpha2', '').lower()

    flag = f"🇦🇷" if codigo_pais == "ar" else f":flag_{codigo_pais}:" if codigo_pais else ""

    resposta = (
        f"💳 **BIN:** {bin_number}\n"
        f"🏳️ **Bandeira:** {bandeira}\n"
        f"📄 **Tipo:** {tipo}\n"
        f"🔰 **Nível:** {nivel}\n"
        f"🏦 **Banco:** {banco}\n"
        f"🌍 **País:** {pais} {flag}"
    )

    await update.message.reply_text(resposta, parse_mode="Markdown")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, consultar))
    app.run_polling()

if __name__ == "__main__":
    main()
