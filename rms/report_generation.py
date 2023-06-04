import pytz
import csv
import threading
from datetime import datetime,timedelta
from rms.models import TimeZone, WorkingHour, Observation, Report

# curr time and date - taken to be max of data provided as suggested in the problem statement
curr_time = '18:13:22'
curr_date = '2023-01-25'

# converts time_str to time in UTC
def convertToUTC(time_str,time_zone_str):

    src_tz = pytz.timezone(time_zone_str)
    dest_tz = pytz.timezone('UTC')

    time_obj = datetime.strptime(time_str, '%H:%M:%S')
    localized_time = src_tz.localize(time_obj)

    utc_time = localized_time.astimezone(dest_tz)

    return utc_time.strftime('%H:%M:%S')

# converts time_str(UTC) to time in 'time_zone_str' timezone
def convertFromUTC(time_str,time_zone_str):
    src_tz = pytz.timezone('UTC')
    dest_tz = pytz.timezone(time_zone_str)

    time_obj = datetime.strptime(time_str, '%H:%M:%S')
    localized_time = src_tz.localize(time_obj)

    time = localized_time.astimezone(dest_tz)

    return time.strftime('%H:%M:%S')

# generates the report and stores in a csv file
def generate_report(file_name,id):

    csv_file = open(file_name, 'w')
    writer = csv.writer(csv_file)
    writer.writerow(['store_id', 'uptime_last_hour', 'uptime_last_day', 'uptime_last_week', 'downtime_last_hour', 'downtime_last_day', 'downtime_last_week'])

    i = 0 
    for obj in TimeZone.objects.all():
        whs = working_hours(obj.store_id)
        if len(whs) == 0: continue

        last_week_uptime = 0
        last_week_downtime = 0
        last_day_uptime = 0
        last_day_downtime = 0

        # iterating through each day in lat week
        for j in range(1,8):
            date = datetime.strptime(curr_date, '%Y-%m-%d')
            date = date - timedelta(days=j)
            date = date.strftime('%Y-%m-%d')
            times = calc_time_for_day(obj.store_id,date,whs, obj.time_zone_str)
            if j == 1:
                last_day_uptime += times[0]
                last_day_downtime += times[1]
            last_week_uptime += times[0]
            last_week_downtime += times[1]
        i += 1
        uptime_last_hour,downtime_last_hour = calc_time_for_hour(obj.store_id,obj.time_zone_str,whs)
        writer.writerow([obj.store_id, uptime_last_hour, last_day_uptime, last_week_uptime, downtime_last_hour, last_day_downtime, last_week_downtime])
    
    # updating the status of report object
    Report.objects.filter(id=id).update(status='complete')

    # cnt, nf_cnt- 11091 2468

# running the funtion in a seperate thread to prevent it from blocking the main thread
def generate_report_async(file_name,report_id):
    thread = threading.Thread(target=generate_report, args=(file_name,report_id))
    thread.start()

# calculates uptime and downtime for last hour
def calc_time_for_hour(store_id,time_zone_str,whs):
    
    day = datetime.strptime(curr_date, '%Y-%m-%d').weekday()
    
    # convert curr_time from utc to local time zone
    ct = convertFromUTC(curr_time,time_zone_str)

    # if work hours are not available or if the current time is not within work hours, return [0,0]
    if whs[day] == 0 or ct > whs[day][1] or ct < whs[day][0]: return [0,0]

    start_time = whs[day][0]
    # setting end_time to current time instead of end of work hours
    end_time = ct
    

    obs = [[convertFromUTC(obs.date[11:19],time_zone_str),obs.status] for obs in Observation.objects.filter(store_id=store_id, date__startswith=curr_date)]
    obs = [ob for ob in obs if ob[0] >= start_time and ob[0] <= end_time]
    obs.sort(key = lambda x: x[0])

    # print(obs)

    up_time = 0
    down_time = 0
    diff = 0
    prev = ct

    # iterating through the list of timestamps until the diff btw curr_time and timestamps is not ge than 1 hour
    for i in range(len(obs)-1,-1,-1):
        if diff >= 3600: break
        curr_diff = (datetime.strptime(prev, '%H:%M:%S') - datetime.strptime(obs[i][0], '%H:%M:%S')).total_seconds()
        if obs[i][1] == 'active': up_time += curr_diff
        else: down_time += curr_diff

        prev = obs[i][0]
        diff += curr_diff

    return [min(up_time/3600,1),min(down_time/3600,1)]

#  calculates uptime and donwtime for given day
def calc_time_for_day(store_id,date,whs,time_zone_str):
    
    # get day of week from date(YYYY-MM-DD)
    day = datetime.strptime(date, '%Y-%m-%d').weekday()

    # if store is closed on given day return [0,0]
    if whs[day] == 0: return [0,0]

    start_time = whs[day][0]
    end_time = whs[day][1]

    # obs - list of [time,status] for given day
    obs = [[convertFromUTC(obs.date[11:19],time_zone_str),obs.status] for obs in Observation.objects.filter(store_id=store_id, date__startswith=date)]

    # filter obs based on start_time and end_time
    obs = [ob for ob in obs if ob[0] >= start_time and ob[0] <= end_time]
    
    # appending start_time and end_time to obs
    obs.append([start_time,'active'])    
    obs.append([end_time,'inactive'])

    # sort obs based on time
    obs.sort(key = lambda x: x[0])

    up_time = 0
    down_time = 0

    # prev - previous timestamp, status - status of previous timestamp
    status = 'active'
    prev = start_time

    # iterate through each timestamp and calculate the diff btw current and previous timestamps
    for ob in obs:
        diff = datetime.strptime(ob[0], '%H:%M:%S') - datetime.strptime(prev, '%H:%M:%S')

        if status == 'active': up_time += diff.total_seconds()/3600
        else: down_time += diff.total_seconds()/3600

        status = ob[1]
        prev = ob[0]
    return [up_time,down_time]

# returns the working hours of a store (local time zone)
def working_hours(store_id):
    whs_objs = WorkingHour.objects.filter(store_id=store_id)
    if(len(whs_objs) == 0): return []

    whs = [0 for _ in range(7)]

    for obj in whs_objs:
        whs[obj.day] = [obj.start,obj.end]

    return whs
