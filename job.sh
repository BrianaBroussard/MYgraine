
#activating virtual env
echo "source /Users/brianabroussard/src/MYgraine_Project/venv/bin/activate"

#sourcing twilio keys in secrets.sh
echo "source //Users/brianabroussard/src/MYgraine_Project/secrets.sh"

#run twilio program to notify users
echo "python3 //Users/brianabroussard/src/MYgraine_Project/send_sms.py"


#cron tab runs this program daily at midnight 

#this isnt working?