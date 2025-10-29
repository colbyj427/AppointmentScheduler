# AppointmentScheduler

This is an appointment scheduler program. It uses a test API.
The steps of the program are:

1. Retrieve the initial state of the calendar.
2. Retrieve the next appointment to be scheduled.
3. Schedule the appointment at the next available slot following constraints.
4. Repeat steps 2-3 until no more appointment requests exist.

# Constraints

## Program Constraints
- Can only request the initial state of the schedule once per run of the program. 

## Scheduling Constraints
- Appointments may only be scheduled on the hour.
- Appointments can be scheduled as early as 8 am UTC and as late as 4 pm UTC.
- Appointments may only be scheduled on weekdays during the months of November and December.
- Appointments can be scheduled on holidays.
- For a given doctor, you may only have one appointment scheduled per hour (though different doctors may have appointments at the same time).
- For a given patient, each appointment must be separated by at least one week. For example, if Bob Smith has an appointment on 11/17 you may schedule another appointment on or before 11/10 or on or after 11/24.
- Appointments for new patients may only be scheduled for 3 pm and 4 pm.

# Implementation Notes

- Start by resetting the calendar.
- Get the initial calendar to begin.
- Loop until no appointment request is returned, or another end case if found.
- Check if the appointment is for a new patient.
- Check if the appt is in November or December and on a weekend.
- Check for the earliest appt. from a preferred doctor that satisfies constraints.
- Keep record of the last appointment for each patient, so the next can be scheduled at least a week later.
