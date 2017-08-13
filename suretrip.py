#!/usr/bin/python

import requests
import json
import sys
import syslog
import datetime

API_KEY  = "f3526ld5a8"

def check_availability(train_number,from_stn,to_stn,date,jclass,quota):
    check_seat ="http://api.railwayapi.com/v2/check-seat/train/%s/source/%s/dest/%s/date/%s/class/%s/quota/%s/apikey/%s/" %(str(train_number),from_stn,to_stn,date,jclass,quota,API_KEY)
    ret = 0
    try:
        data = (requests.get(check_seat)).json()
    except:
        print "UNABLE TO PARSE JSON, INTERNAL ERROR"
        return 0
    
    if "name" not in data["train"].keys():
        # Invalid train number, ticket not available
        return 0

    num_records = len(data["availability"])

    for i in range(0,num_records):
        if (data["availability"][i]['date'] == date):
            if "AVAILABLE" in data["availability"][i]['status']:
                ret = 1
            print "TRAIN NUMBER %s" %train_number
            print data["availability"][i]['status']

    print "TICKET AVAILABILITY NEXT FEW DAYS"
    for i in range(0,num_records):
        print "TRAIN NUMBER %s" %train_number
        print "DATE: %s STATUS: %s " %(data["availability"][i]['date'],data["availability"][i]['status'])

    return ret

if __name__ == "__main__":

    if(len(sys.argv) < 6):
        print "python suretrip.py <FROM STN> <TO STN> <DD-MM-YYYY> <CLASS> <QUOTA>"
        exit(0)

    from_stn = str(sys.argv[1])
    to_stn = str(sys.argv[2])
    date = str(sys.argv[3])
    jclass = str(sys.argv[4])
    quota = str(sys.argv[5])

    #today = datetime.datetime.today().strftime('%d-%m-%Y')

    trains_from_to = "http://api.railwayapi.com/v2/between/source/%s/dest/%s/date/%s/apikey/%s/" % (from_stn,to_stn,date,API_KEY)

    try:
        data = (requests.get(trains_from_to)).json()
    except:
        print "UNABLE TO PARSE JSON, PLEASE CHECK PARAMETERS"
        exit(0)

    total_trains = data["total"]

    #check if available
    for i in range(0,total_trains):
        train_number = data["trains"][i]["number"]
        ret = check_availability(train_number,from_stn,to_stn,date,jclass,quota)

    if ret == 0:
        print "LETS EXPLORE SPLIT JOURNEY ON %s" %date

    exit(0)
