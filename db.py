import firebase_admin
from firebase_admin import credentials, db
import os
from dotenv import load_dotenv

load_dotenv()

cred = credentials.Certificate("./serviceAccountKey.json")
firebase_admin.initialize_app(cred, {'databaseURL':os.getenv('DB_URL')})

#initialise database - only run once
def init():
    ref = db.reference("/")
    ref.set({
        "Schedules": {
            "test" : {
                "id" : 1,
                "freq" : 3,
                "level" : 1
            }
        }
    })

#add or edit schedule
def push(id, freq=3, level=1):
    ref = db.reference("/Schedules")

    #edit existing schedule if any
    for key, value in ref.get().items():
        if(value["id"] == id):
            ref.child(key).update({"freq" : freq, "level" : level})
            return
    #Else, push new entry
    ref.push().set({
        "id" : id,
        "freq" : freq,
        "level" : level
    })

#unschedule 
def delete(id):
    ref = db.reference("/Schedules")
    schedules = ref.get()
    for key, value in schedules.items():
        if(value["id"] == id):
            ref.child(key).set({})

def get_schedules():
    ref = db.reference("/Schedules")
    schedules = ref.get()
    return schedules