from rms.models import TimeZone, WorkingHour, Observation, Report

file1 = 'C:/Users/Shiva Kumar/Downloads/store status.csv'
file2 = 'C:/Users/Shiva Kumar/Downloads/menu hours.csv'
file3 = 'C:/Users/Shiva Kumar/Downloads/time zones.csv'

def store_time_zones():
    with open(file3, 'r') as f:
        lines = f.readlines()
        for line in lines[1:]:
            line = line.strip()
            line = line.split(',')
            store_id = int(line[0])
            time_zone_str = line[1]
            tz = TimeZone(store_id=store_id, time_zone_str=time_zone_str)
            tz.save()

def store_working_hours():
    with open(file2, 'r') as f:
        lines = f.readlines()
        for line in lines[1:]:
            line = line.strip()
            line = line.split(',')
            store_id = int(line[0])
            day = int(line[1])
            start = line[2]
            end = line[3]
            wh = WorkingHour(store_id=store_id, day=day, start=start, end=end)
            wh.save()

def store_observations():
    with open(file1, 'r') as f:
        lines = f.readlines()
        for line in lines[1:]:
            line = line.strip()
            line = line.split(',')
            store_id = int(line[0])
            date = line[2]
            status = line[1]
            obs = Observation(store_id=store_id, date=date, status=status)
            obs.save()
