#!/usr/bin/python3
import RPi.GPIO as GPIO
import time
import datetime
import Queue
import bme280
import os


def tip_event(channel):
    timestamp = datetime.datetime.utcnow()
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
    tipping_bucket_file = open('/home/pi/PiRainSensors/data/tipping_bucket/' + strdate + '.txt', 'w+')
    optical_bucket_file = open('/home/pi/PiRainSensors/data/optical_bucket/' + strdate + '.txt', 'w+')
    metdata_file = open('/home/pi/PiRainSensors/data/metdata/' + strdate + '.txt', 'w+')
    return tipping_bucket_file, optical_bucket_file, metdata_file

def write_queue_element(element):
    timestr = element[0].strftime('%H:%M:%S.%f')
    if element[1] == tipping_bucket_pin:
        tipping_count = 0
        tipping_bucket_file.write('%s,%d\n' %(timestr, tipping_count))
    elif element[1] == optical_bucket_pin:
        optical_count = 0
        optical_bucket_file.write('%s,%d\n' %(timestr, optical_count))

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
logged_day = datetime.datetime.utcnow().day
q = Queue.Queue()
tipping_count = 0
optical_count = 0
while True:
    # If the day has changed, let's close the old and start new logfiles
    current_day = datetime.datetime.utcnow().day
    if logged_day != current_day:
        logged_day = current_day
        tipping_count = 0
        optical_count = 0
        tipping_bucket_file.close()
        optical_bucket_file.close()
        metdata_file.close()
        tipping_bucket_file, optical_bucket_file, metdata_file = open_dayfile()

    # See if it's time to read the T,RH,P and log it if so
    current_minute = datetime.datetime.utcnow().minute
    if current_minute != logged_minute:
        # Time to log!
        logged_minute = current_minute
        temperature, pressure, humidity = bme280.readBME280All()
        ts = datetime.datetime.utcnow().strftime('%H:%M')
        metdata_file.write("%s,%.2f,%.2f,%.2f\n" %(ts, temperature, pressure, humidity))
        metdata_file.flush()
        tipping_bucket_file.flush()
        optical_bucket_file.flush()
        os.fsync(metdata_file.fileno())
        os.fsync(tipping_bucket_file.fileno())
        os.fsync(optical_bucket_file.fileno())
    else:
        time.sleep(5)
        print("Checking to see if I need to log the T,RH,P sensor")

    while not q.empty():
        print write_queue_element(q.get())
tipping_bucket_file.close()
optical_bucket_file.close()
metdata_file.close()
