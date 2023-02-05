import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler
import datetime

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

#Set prompt to send daily when /start command is issued
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id #get current chat's id
    send_time = datetime.time(hour=3, minute=25, second=40) #Time to send prompt. Currently 8pm SGT
    await context.bot.send_message(chat_id=chat_id, text="You will now receive daily prompts!")
    context.job_queue.run_daily(send_prompt, time=send_time, chat_id=chat_id)

#Message displayed when user sends an unrecognised command to the bot
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Please use /config to change your settings!")

#Sends content to the chat
async def send_prompt(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    await context.bot.send_message(job.chat_id, text="How is everyone doing?") #Send message
    await context.bot.send_poll(chat_id=job.chat_id, 
        question="How are you feeling now?", 
        options=["Terrible :(", "Not great", "I'm fine", "Pretty good!", "Feeling great!"],
        is_anonymous=False,
        allows_multiple_answers=False) #Send poll


if __name__ == '__main__':
    application = ApplicationBuilder().token('6177789852:AAH8rbGi-RIMtnWWrypoglE6ffZxPsd08yY').build()
    
    start_handler = CommandHandler('start', start)
    help_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), help)

    application.add_handler(start_handler)
    application.add_handler(help_handler)
    
    application.run_polling()