from flask import Blueprint, jsonify, request, send_file
import Util
from flask_cors import cross_origin


main = Blueprint('main', __name__)

@main.route('/update_schedule', methods=['POST'])
@cross_origin()
def update_schedule():
    f = request.files['file']
    status = Util.writeToJson(f)
    return Util.readFromJson('schedule.json')

@main.route('/')
@cross_origin()
def display_schedule():
    f = 'schedule.json'
    return Util.readFromJson(f)

@main.route('/get-employee-schedule', methods=['POST'])
@cross_origin()
def getEmployeeSchedule():
    emp = request.get_json()
    try:
        return send_file(Util.exportPersonalSchedule('schedule.json', emp["employee"]), attachment_filename=f'{emp["employee"]}.csv', as_attachment=True)
    except Exception as e:
        return str(e)

@main.route('/holidays')
@cross_origin()
def getHolidays():
    f = 'holidays.json'
    return Util.readFromJson(f)

@main.route('/nightlogs')
@cross_origin()
def nightlogs():
    f = 'nightlog.json'
    return Util.readFromJson(f)

@main.route('/nightlogsubmition', methods=['POST'])
@cross_origin()
def nightlogsubmition():
    return Util.nightlogsubmition(request.get_json())

@main.route('/viewnightlog', methods=['POST'])
@cross_origin()
def viewnightlog():
    return Util.viewnightlog(request.get_json())

@main.route('/deletenightlog', methods=['POST'])
@cross_origin()
def deletenightlog():
    return Util.deletenightlog(request.get_json())

@main.route('/editnightlog', methods=['POST'])
@cross_origin()
def editnightlog():
    return Util.editnightlog(request.get_json())

@main.route('/editnightlogsubmition', methods=['POST'])
@cross_origin()
def editnightlogsubmition():
    return Util.editnightlogsubmition(request.get_json())
