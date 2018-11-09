# Logentries poller
A **working** script to pull live streams from logentries
To get the LOG key: 
 - go to logentries dashboard, 
 - select the log set that contains the log you're interested in, it will shows all the logs in the right panel.
 - You'll see a "log key" label on the right side of the page, click on it and it will display the log key
   
# General use:
`python get_logs.py --apikey ${API_KEY} --logkey ${LOG_KEY} --query foo=bar --output messages.log`

