from src import *
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, Updater
import sys

config_file = "/home/maxlkp/.telegram_config.yaml"
with open(config_file, 'r') as file:
    config = yaml.safe_load(file)

api_token = config["telegram"]["token"]
chat_id = config["telegram"]["group_id"]

help_message = "Benutzung: \n/gericht + <mensa>: Heutiges Menü der gewählten Mensa \n/gericht + <mens> + <tag> + <datum>: Menü der Mensa an diesem Datum \nBsp: /gericht vita Dienstag 03.02.2026\n Akutelle Mensen: academica, vita, bayernallee"

async def respond_gerichte_vita(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.id == chat_id:
        try:
            if len(context.args) == 3:
                mensa = context.args[0]
                day = context.args[1]
                date = context.args[2]
                gerichte = get_gerichte(mensa, day = day, date = date)
            elif len(context.args) == 1:
                mensa = context.args[0]
                gerichte = get_gerichte(mensa)
            else: pass
            output = ""
            for key, gericht in gerichte.items():
                output = output + f"{key}: {gerichte[key]} \n"
            
            user = update.effective_user.first_name
            
            response = f"Hi {user}! Ich hoffe, du bist hungrig! \nHier ist der Speiseplan der Mensa {mensa} vom {day}, {date} \nGuten Appetit!"

            await context.bot.send_message(chat_id = chat_id, text = response)
            await context.bot.send_message(chat_id = chat_id, text = output.encode('latin-1').decode('utf-8'))
            await context.bot.send_message(chat_id = chat_id, text = "Wenn du eine Umfrage zum heutigen Essen starten willst, nutze /umfrage!")
        except Exception as e:
            print(e)
            await update.message.reply_text("An error occoured.")
    else:
        await context.application.shutdown()
        sys.exit(0)

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.id == chat_id:
        await update.message.reply_text("Shutting down application.")
        await context.application.stop()
        await context.application.shutdown()
        stop_all()
        sys.exit(0)
    else:
        await context.application.stop()
        await context.application.shutdown()
        sys.exit(0)

async def poll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    questions = "Zufriedenheit mit der Mensa heute?"
    answers = ["\U00002B50", "\U00002B50\U00002B50", "\U00002B50\U00002B50\U00002B50", "\U00002B50\U00002B50\U00002B50\U00002B50", "\U00002B50\U00002B50\U00002B50\U00002B50\U00002B50"]
    await context.bot.send_poll(update.effective_chat.id, questions, answers, is_anonymous=False, allows_multiple_answers=False,)

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.id == chat_id:
        await update.message.reply_text(help_message)
    else:
        await context.application.stop()
        await context.application.shutdown()
        sys.exit(0)

async def stop_all():
    sys.exit(0)

if __name__ == '__main__':
    application = ApplicationBuilder().token(api_token).build()
    help_handler = CommandHandler("help", help)
    gericht_handler = CommandHandler('gericht', respond_gerichte_vita)
    umfrage_handler = CommandHandler("umfrage", poll)
    stop_handler = CommandHandler('stop', stop)
    application.add_handler(help_handler)
    application.add_handler(gericht_handler)
    application.add_handler(stop_handler)
    application.add_handler(umfrage_handler)
    application.run_polling()

sys.exit(0)