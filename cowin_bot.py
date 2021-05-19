import requests
import datetime
import logging
from twython import Twython

from auth import consumer_key, consumer_secret, access_token, access_token_secret


logger = logging.getLogger("cowin")

class CowinSlots:
    def __init__(self):
        self.today = datetime.date.today().strftime('%d-%m-%Y')
        self.tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%d-%m-%Y')
        # self.dayafter = (datetime.date.today() + datetime.timedelta(days=2)).strftime('%d-%m-%Y')
        # self.dayafter1 = (datetime.date.today() + datetime.timedelta(days=3)).strftime('%d-%m-%Y')
        self.dates = [self.today, self.tomorrow]
        self.url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id=294&date={0}"
        self.header = {'Accept-Language': 'en_US', 'accept': 'application/json','User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, ''like Gecko) Chrome/90.0.4430.93 Safari/537.36'}

    def get_response(self):
        for date in self.dates:
            yield requests.get(self.url.format(date), headers=self.header).json()

    def get_available_slots(self, results):
        final = []
        for result in results:
            for data in result['centers']:
                if data['pincode'] in [560011, 560041, 560078, 560076, 560020]:
                    for session in data['sessions']:
                        if session['min_age_limit']==18 and session['available_capacity_dose1'] >0:
                            hospitals = {
                                "pincode" : data['pincode'],
                                "date" : session['date'],
                                "age" : session['min_age_limit'],
                                "dose1" : session['available_capacity_dose1'],
                                "dose2" : session['available_capacity_dose2'],
                                "name" : data['name'],
                                "address": data['address'],
                                "time": datetime.datetime.now().strftime('%H:%M:%S')
                            }
                            final.append(hospitals)
        return final

    def send_twitter_notification(self, message):
        twitter = Twython(
            consumer_key,
            consumer_secret,
            access_token,
            access_token_secret
        )
        twitter.update_status(status=message)
        logger.warn("Tweeted message %s", message)

if __name__ == "__main__":
    try :
        cowin = CowinSlots()
        results = list(cowin.get_response())
        response = cowin.get_available_slots(results)
        if response:
            cowin.send_twitter_notification(response)
        else:
            logger.warn("There were no slots opened for 18-44 at time : %s", datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
    except Exception as e:
        response = logger.warn("The exception is %s", e)