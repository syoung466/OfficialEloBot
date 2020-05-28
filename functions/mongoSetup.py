from pymongo import MongoClient
import os
from dotenv import load_dotenv

def mongoSetup(user, passwd):

    try:
        mongo_db = MongoClient(f'mongodb://{user}:{passwd}@ds159840.mlab.com:59840/heroku_s95bk7vx?retryWrites=false')
        db = mongo_db['heroku_s95bk7vx']
        elobot_usg = db['elobot_usg']       
        print("Connected to Mongo succesfully!")  
        return elobot_usg          
        
    except Exception as e:
        print(e)

        