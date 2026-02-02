from src import *
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, Updater, JobQueue
import sys
import random

config_file = "/home/maxlkp/.telegram_config.yaml"
with open(config_file, 'r') as file:
    config = yaml.safe_load(file)

api_token = config["telegram"]["token"]
chat_id = config["telegram"]["group_id"]

help_message = "Benutzung: \nMenü der Mensa an Datum: \n/gericht + <mensa> (opt: + <Tag> + <datum>, sonst Heute) \nBsp: /gericht vita Dienstag 03.02.2026 \nFrage, wer mit in die Mensa will: \n/wannmensa (optional: <uhrzeit 1> + <uhreit 2> + ...) \nAkutelle unterstützte Mensen: \nacademica, vita, bayernallee \nhttps://github.com/MaxLKP/mensa_bot/"

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
                date, day = get_day_date()
                gerichte = get_gerichte(mensa, day = day, date = date)
            else: pass
            output = ""
            for key, gericht in gerichte.items():
                output = output + f"{key}: {gerichte[key]} \n"
            
            user = update.effective_user.first_name
            
            response = f"Hi {user}! Ich hoffe, du bist hungrig! \nHier ist der Speiseplan der Mensa {mensa} vom {day}, {date} \nGuten Appetit!"

            await context.bot.send_message(chat_id = chat_id, text = response)
            await context.bot.send_message(chat_id = chat_id, text = output.encode('latin-1').decode('utf-8'))
            await context.bot.send_message(chat_id = chat_id, text = "Wenn du das heutige Menü bewerten willst, nutze /umfrage!\nWenn du wissen willst, wer mitkommt, nutze /wannmensa")
        except Exception as e:
            print(e)
            await update.message.reply_text("An error occoured.")
    else:
        await context.application.shutdown()
        sys.exit(0)

async def mensa_update(context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        mensa = random.choice(["vita", "academica", "bayernallee"])
        date, day = get_day_date()
        gerichte = get_gerichte("academica", day = day, date = date)
        output = ""
        for key, gericht in gerichte.items():
            output = output + f"{key}: {gerichte[key]} \n"
        response = f"Hallo an Alle! Der Mensa Bot ist jetzt aktiv. \nNutze /help für mögliche Befehle.\nVorab: Es ist {day}, der {date}. Hier sind die heutigen Gerichte der Mensa {mensa}."
        if "Schnitzel" in output or "schnitzel" in output:
            response = response + "\nUnd gute Nachrichten! Es ist Schnitzeltag!"
        else: pass
        await context.bot.send_message(chat_id = chat_id, text = response)
        await context.bot.send_message(chat_id = chat_id, text = output.encode('latin-1').decode('utf-8'))
        await context.bot.send_message(chat_id = chat_id, text = "Hunger bekommen?\nWenn du wissen willst, wer mitkommt, nutze /wannmensa\nWenn du das heutige Menü bewerten willst, nutze /umfrage!")
    except Exception as e:
        print(e)
        await context.bot.send_message(chat_id = chat_id, text = "An error occoured.")

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

async def wann_mensa(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.id == chat_id:
        question = f"{update.effective_user.first_name} möchte in die Mensa gehen! Wer ist dabei?"
        if len(context.args) != 0 and len(context.args) >= 2:
            umfrage = []
            for möglichkeit in context.args:
                umfrage.append(möglichkeit)
            await context.bot.send_poll(update.effective_chat.id, question, umfrage, is_anonymous=False, allows_multiple_answers=False)
        elif len(context.args) == 1:
            text = f"{update.effective_user.first_name} möchte um {context.args[0]} in die Mensa gehen! Wer ist dabei?"
            await context.bot.send_message(chat_id = chat_id, text = text)
        else: 
            text = f"{update.effective_user.first_name} möchte in die Mensa gehen! Wer ist dabei?"
            await context.bot.send_message(chat_id = chat_id, text = text)
    else:
        await context.application.stop()
        await context.application.shutdown()
        sys.exit(0)

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.id == chat_id:
        await context.bot.send_message(chat_id = chat_id, text = help_message)
    else:
        await context.application.stop()
        await context.application.shutdown()
        sys.exit(0)

async def send_welcome(context: ContextTypes.DEFAULT_TYPE) -> None:
    date, day = get_day_date()
    welcome = f"Hallo! Es ist {day}, der {date}. \nDer Bot ist jetzt einsatzbereit!\nBenutze /help für Hilfe."
    await context.bot.send_message(chat_id = chat_id, text = welcome)

async def send_goodbye(context: ContextTypes.DEFAULT_TYPE) -> None:
    goodbye = f"Der Bot wurde vom Host beendet. See you soon!"
    await context.bot.send_message(chat_id = chat_id, text = goodbye)

async def stop_all():
    sys.exit(0)

if __name__ == '__main__':
        application = ApplicationBuilder().token(api_token).build()
        try:
            #application.job_queue.run_once(send_welcome, 0)
            application.job_queue.run_once(mensa_update, 0)
            help_handler = CommandHandler("help", help)
            gericht_handler = CommandHandler('gericht', respond_gerichte_vita)
            umfrage_handler = CommandHandler("umfrage", poll)
            wann_handler = CommandHandler("wannmensa", wann_mensa)
            stop_handler = CommandHandler('stop', stop)
            application.add_handler(help_handler)
            application.add_handler(gericht_handler)
            application.add_handler(stop_handler)
            application.add_handler(umfrage_handler)
            application.add_handler(wann_handler)
            application.run_polling()
        except KeyboardInterrupt:
            application.job_queue.run_once(send_goodbye, 0)
            application.stop()
            application.shutdown()