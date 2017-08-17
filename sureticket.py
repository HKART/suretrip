import requests
import json
import sys
import datetime

API_KEY = "gljm72gcc1"

class trip_param:
    source = ''
    dest = ''
    date = ''
    cls = ''
    quota = ''

class train_route:
    scharr = ''
    schdep = ''
    distance = ''
    day = ''
    stn_code = ''
    stn_name = ''

class train_details:
    name = ''
    number = ''
    cls = []
    start = ''
    end = ''
    route = []

route_trains_list = []

def fill_train_list(journey_data):

    train_list_url ="http://api.railwayapi.com/v2/between/source/%s/dest/%s/date/%s/apikey/%s/" % (journey_data.source,journey_data.dest,journey_data.date,API_KEY)
    
    try:
        train_list = (requests.get(train_list_url)).json()
    except:
        print "Failed to parse JSON, Internal Error "
        return -1

    try:
        total_trains = train_list["total"]
        
        for i in range(0,total_trains):
            train_obj = train_details()
            train_obj.name = str(train_list["trains"][i]['name'])
            train_obj.number = str(train_list["trains"][i]['number'])
            train_obj.start = str(train_list["trains"][i]['from_station']['code'])
            train_obj.end = str(train_list["trains"][i]['to_station']['code'])
            num_class = len(train_list['trains'][i]['classes'])
            for j in range(0,num_class):
                train_obj.cls.append(train_list["trains"][i]["classes"][j]['code'])
            
            route_trains_list.append(train_obj)

    except:
        print "API-KEY expired, Renew the KEY."
        return -1

    return 0

def fill_train_route(source,dest):
    num_trains = len(route_trains_list)
    for i in range(0,num_trains):
        train_obj = route_trains_list[i]
        train_number = route_trains_list[i].number
        explore_route_url = "http://api.railwayapi.com/v2/route/train/%s/apikey/%s/" %(train_number,API_KEY)
        try:
            explore_route = (requests.get(explore_route_url)).json()
        except:
            print "Failed to parse JSON explore-route"
            return -1

        num_records = len(explore_route['route'])
        for j in range(0,num_records):
            route = train_route()
            route.stn_name = explore_route['route'][j]['station']['name']
            route.stn_code = explore_route['route'][j]['station']['code']
            if dest == route.stn_code:
                break
            route.scharr = explore_route['route'][j]['scharr']
            route.schdep = explore_route['route'][j]['schdep']
            route.distance = explore_route['route'][j]['distance']
            route.day = explore_route['route'][j]['day']
            train_obj.route.append(route)

    return 0


def check_tkt_available(cls,quota,date):
    available = 0
    num_trains = len(route_trains_list)
    for i in range(0,num_trains):
        train_number = route_trains_list[i].number
        train_name = route_trains_list[i].name
        from_stn = route_trains_list[i].start
        to_stn = route_trains_list[i].end
        check_seat_url ="http://api.railwayapi.com/v2/check-seat/train/%s/source/%s/dest/%s/date/%s/class/%s/quota/%s/apikey/%s/" %(train_number,from_stn,to_stn,date,cls,quota,API_KEY)
        try:
            check_seat = (requests.get(check_seat_url)).json()
        except:
            print "Failed to parse JSON 'check-seat' "
            return -1

        num_records = len(check_seat["availability"])
        for j in range(0,num_records):
            if(date == check_seat["availability"][j]['date']):
                if (("AVAILABLE" in check_seat["availability"][j]['status']) and ("NOT" not in check_seat["availability"][j]['status'])) or ("RAC" in check_seat["availability"][j]['status']):
                    available = 1

            print "TRAIN NUMBER[%s] TRAIN NAME[%s] STN-FROM[%s] STN-TO[%s] DATE[%s] CLASS[%s] QUOTA[%s] STATUS[%s]" %(train_number,train_name,from_stn,to_stn,check_seat["availability"][j]['date'],cls,quota,check_seat["availability"][j]['status'])
    return available

def explore_max_distance_source_const(cls,quota,date):
    available = 0
    num_trains = len(route_trains_list)
    for i in range(0,num_trains):
        train_number = route_trains_list[i].number
        train_name = route_trains_list[i].name
        from_stn = route_trains_list[i].start
        end_stn = route_trains_list[i].end
        num_route = len(route_trains_list[i].route)
        route_obj = route_trains_list[i].route
        for j in range(num_route-1,0,-1):
            to_stn = route_obj[j].stn_code
            if from_stn == to_stn:
                continue
            if end_stn == to_stn:
                continue
            check_seat_url ="http://api.railwayapi.com/v2/check-seat/train/%s/source/%s/dest/%s/date/%s/class/%s/quota/%s/apikey/%s/" %(train_number,from_stn,to_stn,date,cls,quota,API_KEY)
            try:
                check_seat = (requests.get(check_seat_url)).json()
            except:
                print "Failed to parse JSON 'check-seat' "
                return -1
            print check_seat_url
            num_records = len(check_seat["availability"])
            for k in range(0,num_records):
                if(date == check_seat["availability"][k]['date']):
                    if (("AVAILABLE" in check_seat["availability"][k]['status']) and ("NOT" not in check_seat["availability"][k]['status'])) or ("RAC" in check_seat["availability"][k]['status']):
                        available = 1
                        print "TRAIN NUMBER[%s] TRAIN NAME[%s] STN-FROM[%s] STN-TO[%s] DATE[%s] CLASS[%s] QUOTA[%s] STATUS[%s]" %(train_number,train_name,from_stn,to_stn,check_seat["availability"][k]['date'],cls,quota,check_seat["availability"][k]['status'])

                        break
    return available

if __name__ == "__main__":

    if(len(sys.argv) < 6):
        print "python sureticket.py <FROM STN-CODE> <TO STN-CODE> <DD-MM-YYYY> <CLASS> <QUOTA>"
        exit(0)

    journey_data = trip_param()

    journey_data.source = str(sys.argv[1])
    journey_data.dest = str(sys.argv[2])
    journey_data.date = str(sys.argv[3])
    journey_data.cls = str(sys.argv[4])
    journey_data.quota = str(sys.argv[5])

    ret = fill_train_list(journey_data)
    if ret == -1:
        print "Internal Error."
        exit(1)

    ret = check_tkt_available(journey_data.cls,journey_data.quota,journey_data.date)
    if ret != 1:
        print "Direct Train ticket is not available on %s for quota %s and class %s." %(journey_data.date,journey_data.quota,journey_data.cls)

    else:
        # Ticket available so return from prog
        exit(0)
    
    ret = fill_train_route(journey_data.source,journey_data.dest)
    if ret != 0:
        print "Internal Error"
        exit(1)
    explore_max_distance_source_const(journey_data.cls,journey_data.quota,journey_data.date)
    exit(0)
