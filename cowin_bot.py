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
        self.tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%d-%m-%Y')
        #TODO : Uncomment the below dates and add it seld.dates list if we need to search for additional two days
        # self.dayafter = (datetime.date.today() + datetime.timedelta(days=2)).strftime('%d-%m-%Y')
        # self.dayafter1 = (datetime.date.today() + datetime.timedelta(days=3)).strftime('%d-%m-%Y')
        self.dates = [self.today, self.tomorrow]
        self.url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id=294&date={0}"
        self.header = {'Accept-Language': 'en_US', 'accept': 'application/json','User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, ''like Gecko) Chrome/90.0.4430.93 Safari/537.36'}

    def get_response(self):
        for date in self.dates:
            yield requests.get(self.url.format(date), headers=self.header).json()

    def get_available_slots(self, response):
        final = []
        for result in response:
            for data in result['centers']:
                for session in data['sessions']:
                    slot_flag = False
                    if session['min_age_limit'] == 18:
                        if session['available_capacity'] >0 or session['available_capacity_dose1'] >0 or  session['available_capacity_dose2'] >0:
                            slot_flag = True
                        #TODO : Uncomment this section if you need data for 45+ second dose also
                        # elif session['min_age_limit'] == 45:
                        #   if session['available_capacity'] >0 or session['available_capacity_dose1'] >0 or  session['available_capacity_dose2'] >0:
                        #       slot_flag = True
                        if slot_flag:
                            logger.info("slot opened for %s for %s", data['name'], session['date'])
                            hospitals = (
                                f"{data['pincode']} ON {session['date']} Type: {session['vaccine']}\n"
                                f"Age: {session['min_age_limit']} Hospital: {data['name']}\n"
                                f"capacity: {session['available_capacity']}(dose1: {session['available_capacity_dose1']}, dose2: {session['available_capacity_dose2']})"
                                )
                            final.append(hospitals)
        return final

    def send_twitter_notification(self, messages):
        twitter = Twython(
            consumer_key,
            consumer_secret,
            access_token,
            access_token_secret
        )
        for message in messages:
            logger.info("Tweeted message %s", message)
            try:
                twitter.update_status(status=message)
            except TwythonError as e:
                logger.info("Duplicate message exception. Ignoring")

if __name__ == "__main__":
    while(True):
        try :
            cowin = CowinSlots()
            response = list(cowin.get_response())
            results = cowin.get_available_slots(response)
            if results:
                    cowin.send_twitter_notification(results)
                #message = f"TWeeted the message for 18-44 at time : {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
            else:
                logger.info("There were no slots opened for 18-44 at time : %s", datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
                #message = f"There were no slots opened for 18-44 at time : {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
        except Exception as e:
                logger.warn("The exception is %s", e)
                logger.info("*************sleeping for 10 additional seconds due to exception***************")
                #message = f"**************EXCEPTION OCCURES {e} at {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}****************"
                time.sleep(10)
        #TODO : If you need to write the logs into a text file, Uncomment the code and change the location
        # with open("C:\\Users\\pradeepk3\\Desktop\\cowin\\log.txt", "a") as myfile:
        #     myfile.write(message)
        #     myfile.write("\n")
        logger.info("Waiting for 9 seconds............")
        time.sleep(9)
