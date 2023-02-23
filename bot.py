import logging
import random
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler
import datetime
from prompts import *
from db import push
import os
from cards import cards

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

#Set prompt to send daily when /start command is issued
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    text = "Hello! How many prompts would you like me to send per week?"
    buttons = [
        [
            InlineKeyboardButton()
        ]
    ]
    '''
    chat_id = update.effective_chat.id #get current chat's id
    send_time = datetime.time(hour=12, minute=00, second=00) #Time to send prompt. Currently 8pm SGT
    push(chat_id, 3, 2)
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    for job in current_jobs:
        job.schedule_removal()
    context.job_queue.run_daily(send_sharing, time=send_time, days=(1,), chat_id=chat_id, data = 2, name=str(chat_id))
    context.job_queue.run_daily(send_poll, time=send_time, days=(3,), chat_id=chat_id, data = 2, name=str(chat_id))
    context.job_queue.run_daily(send_activity, time=send_time, days=(5,), chat_id=chat_id, data = 2, name=str(chat_id))
    await context.bot.send_message(chat_id=chat_id, text="You will now receive prompts periodically!")

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

async def send_activity(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    difficulty = job.data
    if(difficulty == 1):
        msg = random.choice(activitiesL1)
    elif(difficulty == 2):
        msg = random.choice(activitiesL2)
    else:
        msg = random.choice(activitiesL3)
    await context.bot.send_message(job.chat_id, text = "It's almost the weekends! Here's a challenge activity for you: \n\n*" + msg + "*", parse_mode='Markdown')
    
async def send_sharing(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    difficulty = job.data
    if(difficulty == 1):
        msg = random.choice(sharingL1)
    elif(difficulty == 2 or difficulty == 3):
        msg = random.choice(sharingL2)
    await context.bot.send_message(job.chat_id, text = "It's the start of a new week! Let's share something with everyone else: \n\n*" + msg + "*", parse_mode='Markdown')

async def send_poll(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    difficulty = job.data
    msg = random.choice(pollL1)
    await context.bot.send_poll(chat_id=job.chat_id, 
        question=msg[0], 
        options=msg[1],
        is_anonymous=False,
        allows_multiple_answers=False)

async def send_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id #get current chat's id
    card = random.choice(cards)
    await context.bot.send_photo(chat_id=chat_id, photo=card,
    caption="Credits: Check out [TableTalk by Vessels](https://tabletalkbyvessels.com/)!", parse_mode='Markdown')

if __name__ == '__main__':
    application = ApplicationBuilder().token(os.getenv('TELEGRAM_TOKEN')).build()
    
    start_handler = CommandHandler('start', start)
    card_handler = CommandHandler('card', send_card)
    help_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), help)

    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(card_handler)
    
    application.run_polling()