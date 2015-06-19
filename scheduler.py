import json
import itertools
from operator import itemgetter
from collections import namedtuple


def load_instructors():
    with open('data/instructors.json') as data_file:
        data = json.load(data_file)

        instructors = {}

        for instructor in data:
            instructors[instructor["first_name"] +
                        " " + instructor["last_name"]] = instructor
        return(instructors)


def load_classes():
    with open('data/classes.json') as data_file:
        data = json.load(data_file)

        crn_key = {}

        for course in data:
            crn_key[course["crn"]] = course
        return crn_key

classlist = load_classes()
instructorlist = load_instructors()


def get_class_crns(class_titles):
    schedule = {}
    for title in class_titles:
        schedule[title] = []
        for key, value in classlist.items():
            course = value["course"]
            if course[0] == '*':
                course = course[2:]
            elif course[0] == '#':
                course = course[2:]
            if course.startswith(title):
                schedule[title].append(key)
    return schedule


def get_class_from_crn(crn):
    return classlist[str(crn)]


def get_possible_schedules(crn_target_list):
    schedules = []
    for schedule in itertools.product(*crn_target_list.values()):
        schedules.append(schedule)
    return schedules

def get_possible_class_data(crn_list):
    schedules = []

    for schedule in schedules_crns:
        classes = []
        for crn in schedule:
            classes.append(get_class_from_crn(str(crn)))
        schedules.append(classes)
    return schedules

crn_target_list = get_class_crns(["MATH-001A", "PHYS-002A"])

schedules = get_possible_class_data(get_possible_schedules(crn_target_list))



def is_possible(meetings_rect):
    meetings_by_days = {
        "Monday": [],
        "Tuesday": [],
        "Wednesday": [],
        "Thursday": [],
        "Friday": [],
        "Saturday": []
    }
    for meeting_rect in meetings_rect:
        meetings_by_days[meeting_rect[0]].append(meeting_rect[1])
    for day_str, day in meetings_by_days.items():
        start = []
        end = []
        for time in day:
            start.append(time.start)
            end.append(time.end)
        start.sort()
        end.sort()
        counter = 0
        while len(start) > 0:
            if start[0] < end[0]:
                start.pop(0)
                counter += 1
            else:
                end.pop(0)
                counter -= 1
            if counter >= 2:
                return False
    return True

def expand_meetings(meetings):
    meetings_rect = []

    for meeting in meetings:
        for meeting_rect in itertools.product(meeting.days, [meeting.time]):
            meetings_rect.append(meeting_rect)
    return meetings_rect

def find_possible(schedules):
    possible = []
    for schedule in schedules:
        schedule = {"rating": 0, "classes": schedule}
        rating_counter = 0
        schedule["rating"] = 0
        Meeting = namedtuple("Meeting", "days time")
        Time = namedtuple("Time", "start end")
        meetings = []
        for class_data in schedule["classes"]:
            for meeting in class_data["meetings"]:
                rating_counter += 1
                schedule["rating"] += float(instructorlist[
                    meeting["instructor"]["first_name"] +
                    " " + meeting["instructor"]["last_name"]]["rating"])
                time = meeting["time"]
                if time != "TBA":
                    start_raw = time["start"]
                    start = start_raw["hours"]*100 + start_raw["minutes"]
                    end_raw = time["end"]
                    end = end_raw["hours"] * 100 + end_raw["minutes"]
                    meetings.append(Meeting(meeting["days"], Time(start, end)))
        schedule["rating"] /= rating_counter * 5 / 100
        schedule["rating"] = round(schedule["rating"], 4)

        meetings_rect = expand_meetings(meetings)

        if is_possible(meetings_rect):
            for course in schedule["classes"]:
                print(course["crn"])
            possible.append(schedule)
    return possible


possible = sorted(find_possible(schedules), key=itemgetter('rating'), reverse=True)

with open('output.json', 'w') as out:
    json.dump(possible, out, indent=2)
