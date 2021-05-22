import requests
import datetime
import logging
import json
import time
from twython import Twython, TwythonError

from auth import consumer_key, consumer_secret, access_token, access_token_secret

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cowin_application")

class CowinSlots:
    def __init__(self):
        self.today = datetime.date.today().strftime('%d-%m-%Y')
        # self.tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%d-%m-%Y')
        # self.dates = [self.today, self.tomorrow]
        self.url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id=294&date={date}"
        self.header = {'Accept-Language': 'en_US', 'accept': 'application/json','User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, ''like Gecko) Chrome/90.0.4430.93 Safari/537.36'}

    @property
    def get_slots(self):
        yield requests.get(self.url.format(date=self.today), headers=self.header).json()
        # for date in self.dates:
        #     yield requests.get(self.url.format(date), headers=self.header).json()

class Notify(CowinSlots):
    def notify_available_slots(self):
        final = []
        twitter = Twython(
            consumer_key,
            consumer_secret,
            access_token,
            access_token_secret
        )
        for data in next(self.get_slots)['centers']:
            for session in data['sessions']:
                if session['min_age_limit'] == 18 and (session['available_capacity'] >0 and session['available_capacity_dose1'] >0):
                    logger.info("slot opened for %s for %s", data['name'], session['date'])
                    hospitals = (
                        f"{data['pincode']} on {session['date']} Type: {session['vaccine']}\n"
                        f"Age: {session['min_age_limit']} Hospital: {data['name']}\n"
                        f"capacity: {session['available_capacity']}(dose1: {session['available_capacity_dose1']}, dose2: {session['available_capacity_dose2']})"
                    )
                    try:
                        logger.info("Tweeted message %s", hospitals)
                        twitter.update_status(status=hospitals)
                    except TwythonError as e:
                        logger.info("Duplicate message exception. Ignoring")


if __name__ == "__main__":
    while(True):
        try :
            notify = Notify()
            notify.notify_available_slots()
        except Exception as e:
            logger.warn("sleeping for 12 additional seconds as exception: %s", e)
            time.sleep(12)
            message = f"**************EXCEPTION OCCURES {e} at {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}****************"
            #TODO : If you need to write the logs into a text file, Uncomment the code and change the location
            # with open("C:\\Users\\pradeepk3\\Desktop\\cowin\\log.txt", "a") as myfile:
            #     myfile.write(message)
            #     myfile.write("\n")
        logger.info("Waiting for 4 seconds............")
        time.sleep(4)
