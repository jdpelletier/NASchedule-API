import pandas as pd
from datetime import timezone, datetime, timedelta
import json

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

    holidays = df.loc[df['Holiday'] == "X"]
    holidays.reset_index(drop=True, inplace=True)
    holidays = holidays.to_json(orient='records')
    parsed_holidays = json.loads(holidays)

    with open('holidays.json', 'w', encoding='utf-8') as f:
        json.dump(parsed_holidays, f, ensure_ascii=False, indent=4)

    df = df.drop(df.columns[5], axis=1)
    df = df.loc[:,:"Remote OAs"]


    df = df.to_json(orient='records')
    parsed = json.loads(df)

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(parsed, f, ensure_ascii=False, indent=4)

    return 200

def readFromJson(f):

    with open(f) as json_file:
        data = json.load(json_file)

    return json.dumps(data)

def exportPersonalSchedule(f, employee):
    df = pd.read_json('data.json')
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
