# cowin
Project to get cowin vaccination update

The Main purpose of this projcet is to get the cowin vaccination deatils and push the notification to Twitter.

Pre-requisites
* Python 3+
* Install the required dependenies from requirement.txt file
    - Python3 : pip3 install -r requirements.txt
    - Python2 : pip install -r requirements.txt
* Create a twitter developers account (https://developer.twitter.com/)
* Once the Twitter account is approved, Create an application in the twitter account (https://developer.twitter.com/en/portal/apps/)
* Give the application required permission(Read, Write, Direct Message) and then generate the Consumer Keys and Authentication Tokens.
* dir cowin.bat file with required locations
* Make sure the server you are planning to run in INDIA, as the cowin does not support cross region.

![image](https://user-images.githubusercontent.com/16932414/118762577-f796e080-b865-11eb-99cb-50246436f286.png)

* Steps to execute the application
1) Upadte the Keys in auth.py file
2) Run the cowin_bot.py (python cowin_bot.py)
3) If you need to schedule the application
    - Windows : Use windows scheduler and run the cowin.bat file (interval 2-5 seconds)
    - Linux : Use crontab (interval 2 -5 seconds)
