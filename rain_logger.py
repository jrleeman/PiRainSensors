#!/usr/bin/python3
import RPi.GPIO as GPIO
import time
import datetime
import Queue


def tip_event(channel):
    time = datetime.datetime.utcnow()
    if channel == tipping_bucket_pin:
        # Add to tipping bucket log
        q.put([timestamp, channel])
        print("Tipping Bucket Tipped!")

    elif channel == optical_bucket_pin:
        # Add to optical bucket log
        q.put([timestamp, channel])
        print("Optcial Bucket Tipped!")

    else:
        # How did we get here?
        print("Unknown event channel - How did we get here?")


def open_dayfile():
    timestamp = time = datetime.datetime.utcnow()
    strdate = timestamp.strftime('%m-%d-%Y')
    tipping_bucket_file = open('data/tipping_bucket/' + strdate + '.txt', 'wa')
    optical_bucket_file = open('data/optical_bucket/' + strdate + '.txt', 'wa')
    metdata_file = open('data/metdata/' + strdate + '.txt', 'wa')
    return tipping_bucket_file, optical_bucket_file, metdata_file

tipping_bucket_pin = 7  # Red wire
optical_bucket_pin = 8  # Orange wire

print("Setting up GPIO pins")
GPIO.setmode(GPIO.BCM)
GPIO.setup(tipping_bucket_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(optical_bucket_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(tipping_bucket_pin, GPIO.FALLING, callback=tip_event, bouncetime=100)
GPIO.add_event_detect(optical_bucket_pin, GPIO.FALLING, callback=tip_event, bouncetime=100)
print("GPIO setup complete")

print("Starting data files")
tipping_bucket_file, optical_bucket_file, metdata_file = open_dayfile()

logged_minute = datetime.datetime.utcnow().minute
logged_data = datetime.datetime.utcnow().day
q = Queue.Queue()

while True:
    # If the day has changed, let's close the old and start new logfiles
    tipping_bucket_file.close()
    optical_bucket_file.close()
    metdata_file.close()
    tipping_bucket_file, optical_bucket_file, metdata_file = open_dayfile()

    # See if it's time to read the T,RH,P and log it if so
    current_minute = datetime.datetime.utcnow().minute
    if current_minute != logged_minute:
        # Time to log!
        temperature, pressure, humidity = bme280.readBME280All()
        metdata_file.write("%.2f,%.2f,%.2f\n" %(temperature, pressure, humidity))
    else:
        time.sleep(5)
        print("Checking to see if I need to log the T,RH,P sensor")

tipping_bucket_file.close()
optical_bucket_file.close()
metdata_file.close()
