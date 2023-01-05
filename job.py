import os 

#activating virtual env
os.system("source /Users/brianabroussard/src/MYgraine_Project/venv/bin/activate")

#sourcing twilio keys in secrets.sh
os.system("source //Users/brianabroussard/src/MYgraine_Project/secrets.sh")

#run twilio program to notify users
os.system("python3 //Users/brianabroussard/src/MYgraine_Project/send_sms.py")


#cron tab runs this program daily at midnight 
