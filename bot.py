import logging
import random
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler
import datetime
from prompts import *
from db import push, get_schedules, delete
import os
from cards import card_links

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

#Set prompt to send daily when /start command is issued
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id #get current chat's id
    send_time = datetime.time(hour=12, minute=00, second=00) #Time to send prompt. Currently 8pm SGT
    push(chat_id, 3, 2)
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    if current_jobs:
        await context.bot.send_message(chat_id=chat_id, text="I've already been started - look out for prompts every Monday, Wednesday, and Friday!\n\nIf you want me to take a break, please use the /stop command.")
    else:
        context.job_queue.run_daily(send_sharing, time=send_time, days=(1,), chat_id=chat_id, data = 2, name=str(chat_id))
        context.job_queue.run_daily(send_poll, time=send_time, days=(3,), chat_id=chat_id, data = 2, name=str(chat_id))
        context.job_queue.run_daily(send_activity, time=send_time, days=(5,), chat_id=chat_id, data = 2, name=str(chat_id))
        await context.bot.send_message(chat_id=chat_id, text="Great! See you every Monday, Wednesday, and Friday :)")

#stop the bot from sending prompts
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    if current_jobs:
        for job in current_jobs:
            job.schedule_removal()
        delete(chat_id)
        await context.bot.send_message(chat_id=chat_id, text="(Yawn) I'll go take a nap!")
    else:
        await context.bot.send_message(chat_id=chat_id, text="I am asleep at the moment - use /start to wake me up!")


async def send_activity(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    difficulty = job.data
    if(difficulty == 1):
        msg = random.choice(activitiesL1)
    elif(difficulty == 2):
        msg = random.choice(activitiesL2)
    else:
        msg = random.choice(activitiesL3)
    await context.bot.send_message(job.chat_id, text = "HAPPY FRIDAY EVERYONE!!! My family and I are so glad that the weekend is finally here we're having tea tree leaves for breakfast🤤 I hope everyone is doing okay after the long week☺️ Here's what we're planning to do over the weekend! \n\n*" + msg + "*", parse_mode='Markdown')
    
async def send_sharing(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    difficulty = job.data
    if(difficulty == 1):
        msg = random.choice(sharingL1)
    elif(difficulty == 2 or difficulty == 3):
        msg = random.choice(sharingL2)
    await context.bot.send_message(job.chat_id, 
                                   text = "knock knock! it's Frank here:\") I hope everyone has been having a good week, I just thought of a question this morning when I woke up and thought you might like it💭 \n\n*" 
                                   + msg + "*", parse_mode='Markdown')

async def send_poll(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    difficulty = job.data
    msg = random.choice(pollL1)
    await context.bot.send_message(chat_id=job.chat_id, text = "hello again it's Frank!🐹 I just woke up from a nap,,, Wednesdays always make me sleepy🥱 Anyways...here's a fun question to start your day🥳🥳")
    await context.bot.send_poll(chat_id=job.chat_id, 
        question=msg[0], 
        options=msg[1],
        is_anonymous=False,
        allows_multiple_answers=False)

async def send_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id #get current chat's id
    card = random.choice(card_links)
    await context.bot.send_photo(chat_id=chat_id, photo=card,
    caption="Credits: Check out [TableTalk by Vessels](https://tabletalkbyvessels.com/)!", parse_mode='Markdown')

async def restore_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    schedules = get_schedules()
    for key, schedule in schedules.items():
        chat_id = schedule["id"]
        send_time = datetime.time(hour=12, minute=00, second=00) #Time to send prompt. Currently 8pm SGT
        current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
        for job in current_jobs:
            job.schedule_removal()
        context.job_queue.run_daily(send_sharing, time=send_time, days=(1,), chat_id=chat_id, data = schedule["level"], name=str(chat_id))
        context.job_queue.run_daily(send_poll, time=send_time, days=(3,), chat_id=chat_id, data = schedule["level"], name=str(chat_id))
        context.job_queue.run_daily(send_activity, time=send_time, days=(5,), chat_id=chat_id, data = schedule["level"], name=str(chat_id))
    chat_id = update.effective_chat.id #get current chat's id
    await context.bot.send_message(chat_id, text = "Update successful!")

if __name__ == '__main__':
    application = ApplicationBuilder().token(os.getenv('TELEGRAM_TOKEN')).build()
    
    card_handler = CommandHandler('card', send_card)
    start_handler = CommandHandler('start', start)
    update_handler = CommandHandler('restore_queue', restore_queue)
    stop_handler = CommandHandler('stop', stop)

    application.add_handler(start_handler)
    application.add_handler(card_handler)
    application.add_handler(update_handler)
    application.add_handler(stop_handler)
    

    application.run_polling()