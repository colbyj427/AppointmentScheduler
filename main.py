from datetime import datetime, timedelta
import os
import requests

###############################
# CONSTANTS
###############################

TOKEN = os.getenv("BREVIUM_KEY")

###############################
# REQUEST FUNCTIONS
###############################

def resetCalendar():
    url = f'https://scheduling.interviews.brevium.com/api/Scheduling/Start?token={TOKEN}'
    response = requests.post(url)
    code = response.status_code
    if code == 200:
        return
    if code == 401:
        raise Exception("Invalid token.")
    else:
        raise Exception("Unknown status code returned when resetting calendar.")
    
def stopCalendar():
    url = f'https://scheduling.interviews.brevium.com/api/Scheduling/Stop?token={TOKEN}'
    response = requests.post(url)
    code = response.status_code
    if code == 200:
        return
    if code == 401:
        raise Exception("Invalid token.")
    else:
        raise Exception("Unknown status code returned when stopping calendar.")

def getInitialSchedule():
    url = f'https://scheduling.interviews.brevium.com/api/Scheduling/Schedule?token={TOKEN}'
    response = requests.get(url)
    code = response.status_code
    if code == 200:
        schedule = response.json()
        return schedule # a list of dictionaries containing appt. info
    if code == 401:
        raise Exception("Invalid token.")
    if code == 405:
        raise Exception("The calendar has already been retrieved, reset it first.")
    else:
        raise Exception("Unknown status code returned when getting initial schedule.")

def getNextRequest():
    url = f'https://scheduling.interviews.brevium.com/api/Scheduling/AppointmentRequest?token={TOKEN}'
    response = requests.get(url)
    code = response.status_code
    if code == 200:
        return False, response.json() # the bool if we reached the end or not, and the next appt info.
    if code == 204:
            return True, None
    if code == 401:
        raise Exception("Invalid token.")
    if code == 405:
        raise Exception("Stop endpoint has already been called.")
    else:
        raise Exception("Unknown status code returned when getting next request.")

def markAppointment(appt): #TODO: Test this.
    url = f'https://scheduling.interviews.brevium.com/api/Scheduling/Schedule?token={TOKEN}'
    response = requests.post(url, json=appt)
    code = response.status_code
    if code == 200:
        return
    elif code == 405:
        raise Exception("Stop endpoint has already been called.")
    elif code == 500:
        raise Exception("The schedule was unable to accomodate your requested appointment.")
    else:
        raise Exception("Unknown status code returned when marking appt: " + str(code))
    
###############################
# LOGIC FUNCTIONS
###############################

def checkOneWeek(schedule, date, patientId):
    """
    Check if the given day is at least a week from this patients other appts.
    """
    for appt in schedule:
        if appt['personId'] == patientId:
            apptDateStr = appt['appointmentTime']
            # Parse the string to datetime
            try:
                apptDate = datetime.fromisoformat(apptDateStr)
                if abs((apptDate - date).days) < 7:
                    return True
            except Exception as e:
                continue
    return False

def checkIsNovDecWeekend(date):
    """
    Check if the given date is in Nov or Dec and a weekend.
    """
    if date.month in [11, 12] and date.weekday() in [5, 6]:
        return True
    return False

def generateNextTime(time, isNew):
    """
    Given a time, ex: 2025-10-29T16:29:29.316Z in UTC, generate one hour later in business hours, 8am-4pm UTC.
    If isNew is True, limit to 3 or 4 pm only.
    Return False if no valid time can be generated following that time.
    The time must be on the hour, so 15:00, 16:00, etc.
    """
    if isNew:
        if time.hour < 15:
            time = time.replace(hour=15)
        elif time.hour == 15:
            time = time.replace(hour=16)
        else:
            # then we go to the next day, thats handled elsewhere
            return None
    if time.hour < 8:
        time = time.replace(hour=8)
    else:
        time += timedelta(hours=1)
    time = time.replace(minute=0, second=0, microsecond=0)
    return time if time.hour <= 16 else None

def checkScheduleAvailable(schedule, time, docId):
    """
    Check if the given date and docId is available in the schedule.
    """
    for appt in schedule:
        if appt['appointmentTime'] == time and appt['doctorId'] == docId:
            return False
    return True

def scheduleRequest(schedule, request):
    for day in request['preferredDays']:
        day = datetime.fromisoformat(day.replace('Z', '+00:00'))
        if checkIsNovDecWeekend(day):
            continue
        if checkOneWeek(schedule, day, request['personId']):
            continue
        potentialTime = generateNextTime(day, request['isNew'])
        while potentialTime:
            for doc in request['preferredDocs']:
                if checkScheduleAvailable(schedule, potentialTime, doc):
                    appt = {
                        "doctorId": int(doc),
                        "personId": int(request['personId']),
                        "appointmentTime": str(potentialTime.isoformat(timespec='milliseconds') + 'Z'),
                        "isNewPatientAppointment": bool(request['isNew']),
                        "requestId": int(request['requestId'])
                    }                  
                    markAppointment(appt)
                    schedule.append(appt)
                    return schedule
            potentialTime = generateNextTime(potentialTime, request['isNew'])
    raise Exception("Unable to schedule new patient with given preferences.")

def main():
    resetCalendar()
    schedule = getInitialSchedule()
    while True:
        finished, request = getNextRequest()
        if finished:
            print("All appointment requests have been processed.")  
            break
        schedule = scheduleRequest(schedule, request)
    print("End of program.")

if __name__ == "__main__":
    main()
