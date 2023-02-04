import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler
import datetime

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    await context.bot.send_message(chat_id=update.effective_chat.id, text="You will now receive daily prompts!")
    context.job_queue.run_daily(send_prompt, time=datetime.time(hour=12, minute=00, second=00), chat_id=chat.id)

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Please use /config to change your settings!")

async def send_prompt(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    print(job.chat_id)
    await context.bot.send_message(job.chat_id, text="How is everyone doing?")


if __name__ == '__main__':
    application = ApplicationBuilder().token('6177789852:AAH8rbGi-RIMtnWWrypoglE6ffZxPsd08yY').build()
    
    start_handler = CommandHandler('start', start)
    help_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), help)

    application.add_handler(start_handler)
    application.add_handler(help_handler)
    
    application.run_polling()