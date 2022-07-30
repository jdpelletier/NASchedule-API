import pandas as pd
from datetime import timezone, datetime, timedelta
import json
import requests
from dateutil.relativedelta import relativedelta
from calendar import Calendar
import time


def writeToJson(f):

    df = pd.read_excel(f)
    df = df.rename(columns=df.iloc[0]).drop(df.index[0])
    df['Date'] = df['Date'].dt.tz_localize(timezone(timedelta(hours=-10))) #convert to HST
    df.columns.values[5] = "Holiday"
    df.columns.values[6] = "Summit Staff"
    df.columns.values[7] = "Waimea Cars in Use"
    df.columns.values[8] = "Hilo Cars in Use"
    df.columns.values[9] = "Remote OAs"

    df = df.drop(df.columns[7], axis=1)
    df = df.drop(df.columns[7], axis=1)

    # holidays = df.loc[df['Holiday'] == "X"]
    # holidays.reset_index(drop=True, inplace=True)
    # holidays = holidays.to_json(orient='records')
    # parsed_holidays = json.loads(holidays)
    #
    # with open('holidays.json', 'w', encoding='utf-8') as f:
    #     json.dump(parsed_holidays, f, ensure_ascii=False, indent=4)

    # df = df.drop(df.columns[5], axis=1)
    df = df.loc[:,:"Remote OAs"]


    df = df.to_json(orient='records')
    parsed = json.loads(df)

    with open('schedule.json', 'w', encoding='utf-8') as f:
        json.dump(parsed, f, ensure_ascii=False, indent=4)

    return 200

def readFromJson(f):

    with open(f) as json_file:
        data = json.load(json_file)

    return json.dumps(data)

def readFromTelSched():
    today = datetime.now()
    previousMonth = today-relativedelta(months=1)
    startyear = previousMonth.year
    startmonth = previousMonth.month
    lastyear = (today+relativedelta(months=4)).year
    lastmonth = (today+relativedelta(months=4)).month
    dates = []
    dates.append(previousMonth.strftime("%Y-%m"))
    dates.append(today.strftime("%Y-%m"))
    for i in range(1,4):
        day = today+relativedelta(months=i)
        dates.append(day.strftime("%Y-%m"))
    print(dates)

    nightstaff = []
    for d in dates:
        response = requests.get(f"https://www.keck.hawaii.edu/software/db_api/telSchedule.php?cmd=getNightStaff&date={d}")
        data = response.json()
        nightstaff.append(data)

    nightstaff=nightstaff[0]+nightstaff[1]+nightstaff[2]+nightstaff[3]+nightstaff[4]
    nightstaff[:] = [x for x in nightstaff if "oa" in x["Type"] or "na" in x["Type"]]

    nas = [x for x in nightstaff if "na" in x["Type"]]
    na_names = []
    for n in nas:
        name = n["FirstName"][0] + n["LastName"][0]
        if name not in na_names:
            na_names.append(name)

    schedule = []
    for i in range(startmonth,lastmonth):
        for d in [x for x in Calendar().itermonthdates(startyear, i) if x.month == i]: #todo add checks for different years
            night = {}
            night["DOW"] = d.strftime('%A')[:3]
            night["Date"] = datetime.fromtimestamp(time.mktime(d.timetuple())).timestamp()*1000
            summit_staff = 0
            remote_oa = 0
            for name in na_names:
                night[name] = None
            for staff in nightstaff:
                s_date = datetime.strptime(staff["Date"], '%Y-%m-%d').date()
                if s_date > d:
                    break
                if s_date == d:
                    if "r" in staff["Type"]:
                        remote_oa += 1
                    elif "oao" not in staff["Type"]:
                        summit_staff += 1

                    if "na" in staff["Type"]:
                        name = staff["FirstName"][0] + staff["LastName"][0]
                        night[name] = staff["Type"].upper()
            if summit_staff == 0:
                break
            night["Holiday"] = None #todo get holidays
            night["Summit Staff"] = summit_staff
            night["Remote OAs"] = remote_oa
            schedule.append(night)

    return(json.dumps(night))


def exportPersonalSchedule(f, employee):
    df = pd.read_json('schedule.json')
    for col in df:
        if col != employee and col != 'Date':
            df = df.drop(columns=col)
    df['just_date'] = df['Date'].dt.date
    df.rename(columns={'just_date':'Start Date', employee:'Subject'}, inplace=True)
    df = df.drop(columns='Date')

    work_days = ['NAH', 'NA1', 'NAH2', 'HQ', 'SD']
    location = []
    for ind in df.index:
        current = df['Subject'][ind]
        if current not in work_days:
            df.drop(ind, inplace=True)
        elif current.startswith('N') or current == 'SD':
            location.append('Summit')
        elif current == 'HQ':
            location.append('Headquarters')
        else:
            location.append('No location')

    df['Location'] = location

    subject = df.pop('Subject')
    df.insert(0, 'Subject', subject)
    df.to_csv(f'{employee}.csv', index=False)
    return f'{employee}.csv'

def nightlogsubmition(nightlog):
    with open('nightlog.json', 'r', encoding='utf-8') as f:
        str = f.read()
        data = []
        try:
            data = json.loads(str)
        except json.decoder.JSONDecodeError:
            data = []
        data.append(nightlog)
    with open('nightlog.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

def viewnightlog(nightlog):
    logid = nightlog["LogID"]
    with open('nightlog.json', 'r', encoding='utf-8') as f:
        str = f.read()
        data = json.loads(str)
    for log in data:
        if log["LogID"] == logid:
            return json.dumps(log)
    return  json.dumps({'success':False}), 404, {'ContentType':'application/json'}

def deletenightlog(nightlog):
    logid = nightlog["LogID"]
    with open('nightlog.json', 'r', encoding='utf-8') as f:
        str = f.read()
        data = json.loads(str)
    for i in range(len(data)):
        if data[i]["LogID"] == logid:
            data.pop(i)
            break
    with open('nightlog.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return json.dumps(data)

def editnightlogsubmition(nightlog):
    logid = nightlog["LogID"]
    with open('nightlog.json', 'r', encoding='utf-8') as f:
        str = f.read()
        data = []
        try:
            data = json.loads(str)
        except json.decoder.JSONDecodeError:
            data = []
        for i in range(len(data)):
            if data[i]["LogID"] == logid:
                data.pop(i)
                break
        data.append(nightlog)
    with open('nightlog.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
