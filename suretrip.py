#!/usr/bin/python

import requests
import json
import sys
import syslog
import datetime

API_KEY  = "gljm72gcc1"

def check_availability(train_number,train_name,from_stn,to_stn,date,jclass,quota):
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
            if (("AVAILABLE" in data["availability"][i]['status']) and ("NOT" not in data["availability"][i]['status'])) or ("RAC" in data["availability"][i]['status']):
                ret = 1
                print "TRAIN NUMBER[%s] TRAIN NAME[%s] STN-FROM[%s] STN-TO[%s] DATE[%s] CLASS[%s] QUOTA[%s] STATUS[%s] "%(train_number,train_name,from_stn,to_stn,date,jclass,quota,data["availability"][i]['status'])

    #print "TICKET AVAILABILITY NEXT FEW DAYS"
    #for i in range(0,num_records):
    #    print "TRAIN NUMBER %s" %train_number
    #    print "DATE: %s STATUS: %s " %(data["availability"][i]['date'],data["availability"][i]['status'])

    return ret

def explore_route(train_number,train_name,from_stn,to_stn,date,jclass,quota):
    explore_route = "http://api.railwayapi.com/v2/route/train/%s/apikey/%s/" %(train_number,API_KEY)
    try:
        data = (requests.get(explore_route)).json()
    except:
        print "UNABLE TO PARSE JSON, INTERNAL ERROR"
        return 0
    num_records = len(data['route'])
    i = 0
    for i in range(0,num_records):
        between_stn_code = data['route'][i]['station']['code']
        between_stn_name = data['route'][i]['station']['name']
        distance = data['route'][i]['distance']

        if(from_stn != between_stn_code):
            print "%s %s %s %s" %(from_stn, between_stn_code,between_stn_name,distance)
            #print "from stn %s to stn %s " %(from_stn,between_stn)
            ret = check_availability(train_number,train_name,from_stn,between_stn_code,date,jclass,quota)
            if ret == 1:
                return 1
            if between_stn_code == to_stn:
                break

    #reset counter
    i = 0
    for i in range(0,num_records):
        between_stn_code = data['route'][i]['station']['code']
        between_stn_name = data['route'][i]['station']['name']
        distance = data['route'][i]['distance']
        if(from_stn != between_stn_code):

            if between_stn_code == to_stn:
                break
            print "%s %s %s %s" %(between_stn_code,between_stn_name,to_stn,distance)
            ret = check_availability(train_number,train_name,between_stn_code,to_stn,date,jclass,quota)
            if ret == 1:
                return 1

    return 0


if __name__ == "__main__":

    if(len(sys.argv) < 6):
        print "python suretrip.py <FROM STN> <TO STN> <DD-MM-YYYY> <CLASS> <QUOTA>"
        exit(0)

    ret = 0

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
        train_name = data["trains"][i]['name']
        rt = check_availability(train_number,train_name,from_stn,to_stn,date,jclass,quota)
        ret = ret + rt

    if ret == 0:
        #reset counter
        i = 0
        print "LETS EXPLORE SPLIT JOURNEY ON %s" %date
        for i in range(0,total_trains):
            train_number = data["trains"][i]["number"]
            train_name = data["trains"][i]['name']
            source =  data["trains"][i]['from_station']['code']
            print "train_number %s train_name %s source %s dest %s" %(train_name,train_number,source,to_stn)
            ret = explore_route(train_number,train_name,source,to_stn,date,jclass,quota)

            if ret == 1:
                break

    exit(0)
