#!/usr/bin/env zsh

#sets virtual env for cron tab
source //Users/brianabroussard/src/MYgraine_Project/venv/bin/activate

#sourcing twilio keys in secrets.sh
source //Users/brianabroussard/src/MYgraine_Project/secrets.sh



#run twilio program to notify users
python //Users/brianabroussard/src/MYgraine_Project/send_sms.py