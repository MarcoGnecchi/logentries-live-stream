import json
import os
import requests
import sys
import time
import logging
import argparse

# Logentries REST API GET Query
# Documentation: https://docs.logentries.com/docs/get-query

class LogEntriesDownloader:

    def __init__(self, query, logkey, apikey, output):

        self.output = output
        self.apikey = apikey
        self.logKey = logkey
        self.query = query

    def start(self):
        head_of_queue="https://rest.logentries.com/query/live/logs/%s/?query=where(%s)" % (self.logKey, self.query)
        url = head_of_queue
        while True:
            response = self.make_request(url)
            self.handle_response(response)
            try:
                if 'links' in response.json():
                    logging.debug('Moving to next item in the queue')
                    url = response.json()['links'][0]['href']
            except:
                logging.error("Error while processing response:%s\nReset url to head" % sys.exc_info()[0])
                url = head_of_queue

            # Wait 5 seconds between requests
            time.sleep(5)

    def save_log_to_file(self, log):
        logging.info("Saving message to file:%s" % log)
        with open(self.output, "a+") as logs_file:
            logs_file.write(log + '\n')

    def handle_response(self, response):
        if response.status_code == 200:
            events = response.json()['events']
            if len(events) > 0:
                logging.info("Found %i events, saving them to file" % len(events))
                for message in events:
                    self.save_log_to_file(message['message'])
            else:
                logging.info("New message not found or empty. Will keep trying")
            return
        if response.status_code == 202:
            logging.info('HTTP code 202, continue request')
            return
        if response.status_code > 202:
            logging.info('Error status code %s' % response.status_code)
            return

    def make_request(self, provided_url=None):
        headers = {'x-api-key': self.apikey}
        response = requests.get(provided_url, headers=headers)
        return response


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='Poll logs from logentries')
    parser.add_argument('--apikey', help='API key with permission to access the logs', required=True)
    parser.add_argument('--logkey', help='The ID of the logs', required=True)
    parser.add_argument('--query', help='The query to run on the log stream', required=True)
    parser.add_argument('--output', help='Output file', required=True)
    args = parser.parse_args()
    logging.info("Starting with query:%s for log %s" % (args.query, args.logkey))
    logentries = LogEntriesDownloader(args.query, args.logkey, args.apikey, args.output)
    logentries.start()
