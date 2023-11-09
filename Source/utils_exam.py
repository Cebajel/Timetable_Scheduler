import pandas as pd
from itertools import chain
import gurobipy as gp
import numpy as np
from gurobipy import GRB
import pandas, math
import classes_exam
import random

def read_input_excel(file):
    second_file = "-test"
    courses_dict = {}
    student_dict = {}
    instructor_dict = {}
    venue_dict = {}

    courses = pandas.read_excel(file, "Courses" + second_file)
    columns = courses.columns

    for value in courses.iterrows():
        value = value[1]
        # temp_campus = value[columns[9]].strip().split("\n")
        code = value[columns[0]].strip()
        L = int(value[columns[3]]) if not math.isnan(value[columns[3]]) else 0
        T = int(value[columns[4]]) if not math.isnan(value[columns[4]]) else 0
        # P = int(value[columns[5]]) if not math.isnan(value[columns[5]]) else 0
        if L+T != 0:
            value[columns[0]] = code

            new_course = classes_exam.Course(value, columns)
            courses_dict[new_course.code] = new_course
            instructors = [i.strip() for i in value[columns[2]].split("\n")]
            TAs = [i.strip() for i in value[columns[12]].split("\n")] if isinstance(value[columns[12]], str) else []

            for i in instructors:
                if i not in instructor_dict:
                    new_instructor = classes_exam.Instructor(i)
                    instructor_dict[i] = new_instructor
                new_course.add_instructor(instructor_dict[i])
                instructor_dict[i].add_course(new_course)

            for i in TAs:
                if i not in student_dict:
                    new_TA = classes_exam.Student(i)
                    student_dict[new_TA.rollnumber] = new_TA
                student_dict[i].add_course(
                    courses_dict[code], 0
                )
                new_course.add_TA(student_dict[i])
        
    registrations = pandas.read_excel(file, "Registrations" + second_file)
    columns = registrations.columns

    for value in registrations.iterrows():
        value = value[1]
        value[columns[1]] = str(value[columns[1]])
        if value[columns[1]] not in student_dict:
            new_student = classes_exam.Student(value[columns[1]])
            student_dict[new_student.rollnumber] = new_student

        current_code = value[columns[0]].strip()

        if current_code in courses_dict:
            student_dict[value[columns[1]]].add_course(
                courses_dict[current_code], int(value[columns[3]])
            )
            courses_dict[current_code].add_student(
                student_dict[value[columns[1]]], int(value[columns[3]])
            )

    venues = pandas.read_excel(file, "Venues" + second_file)
    columns = venues.columns

    for value in venues.iterrows():
        value = value[1]
        current_venue = classes_exam.Venue(
            str(value[columns[0]]).strip(),
            value[columns[1]],
            value[columns[2]],
            value[columns[3]],
            value[columns[4]],
            value[columns[5]],
            value[columns[6]],
        )
        venue_dict[str(value[columns[0]]).strip()] = current_venue

    return courses_dict, student_dict, instructor_dict, venue_dict


def make_baskets(parameters: classes_exam.Params):
    least_priority = int(np.max(parameters.student_course_priority))
    # least_priority = 1

    temp = []
    parameters.baskets_core = []
    parameters.baskets_elective = []
    parameters.basket_students_core = []
    parameters.basket_students_elective = []
    parameters.basket_number_of_students_core = []
    parameters.basket_number_of_students_elective = []

    for k in range(parameters.number_of_students):
        courses_core_1 = list(
            np.intersect1d(
                parameters.full_sem_courses + parameters.pre_half_sem_courses,
                np.where(parameters.student_course_priority[k] == 0)[0],
            )
        )
        courses_elective_1 = []
        for priority in range(1, least_priority + 1):
            courses_elective_1 = courses_elective_1 + list(
                np.intersect1d(
                    parameters.full_sem_courses + parameters.pre_half_sem_courses,
                    np.where(parameters.student_course_priority[k] == priority)[0],
                )
            )
        courses_core_2 = list(
            np.intersect1d(
                parameters.full_sem_courses + parameters.post_half_sem_courses,
                np.where(parameters.student_course_priority[k] == 0)[0],
            )
        )
        courses_elective_2 = []
        for priority in range(1, least_priority + 1):
            courses_elective_2 = courses_elective_2 + list(
                np.intersect1d(
                    parameters.full_sem_courses + parameters.post_half_sem_courses,
                    np.where(parameters.student_course_priority[k] == priority)[0],
                )
            )
        courses_core_1 = sorted(courses_core_1)
        courses_core_2 = sorted(courses_core_2)
        courses_elective_1 = sorted(courses_elective_1)
        courses_elective_2 = sorted(courses_elective_2)

        for i in range(len(courses_core_1)):
            for j in range(i + 1, len(courses_core_1)):
                temp = {courses_core_1[i], courses_core_1[j]}
                if temp not in parameters.baskets_core:
                    parameters.baskets_core.append(temp)
                    parameters.basket_number_of_students_core.append(1)
                    parameters.basket_students_core.append([parameters.student_list[k]])
                else:
                    if parameters.student_list[k] not in parameters.basket_students_core[parameters.baskets_core.index(temp)]:
                        parameters.basket_students_core[parameters.baskets_core.index(temp)].append(parameters.student_list[k])

                        parameters.basket_number_of_students_core[
                            parameters.baskets_core.index(temp)
                        ] += 1

        for i in range(len(courses_core_2)):
            for j in range(i + 1, len(courses_core_2)):
                temp = {courses_core_2[i], courses_core_2[j]}
                if temp not in parameters.baskets_core:
                    parameters.baskets_core.append(temp)
                    parameters.basket_number_of_students_core.append(1)
                    parameters.basket_students_core.append([parameters.student_list[k]])
                else:
                    if parameters.student_list[k] not in parameters.basket_students_core[parameters.baskets_core.index(temp)]:
                        parameters.basket_students_core[parameters.baskets_core.index(temp)].append(parameters.student_list[k])

                        parameters.basket_number_of_students_core[
                            parameters.baskets_core.index(temp)
                        ] += 1

        for i in range(len(courses_elective_1)):
            for j in range(i + 1, len(courses_elective_1)):
                temp = {courses_elective_1[i], courses_elective_1[j]}
                if temp not in parameters.baskets_elective + parameters.baskets_core:
                    parameters.baskets_elective.append(temp)
                    parameters.basket_number_of_students_elective.append(1)
                    parameters.basket_students_elective.append([parameters.student_list[k]])
                else:
                    if temp in parameters.baskets_elective:
                        if parameters.student_list[k] not in parameters.basket_students_elective[parameters.baskets_elective.index(temp)]:
                            parameters.basket_students_elective[parameters.baskets_elective.index(temp)].append(parameters.student_list[k])

                            parameters.basket_number_of_students_elective[
                                parameters.baskets_elective.index(temp)
                            ] += 1

        for i in range(len(courses_elective_2)):
            for j in range(i + 1, len(courses_elective_2)):
                temp = {courses_elective_2[i], courses_elective_2[j]}
                if temp not in parameters.baskets_elective + parameters.baskets_core:
                    parameters.baskets_elective.append(temp)
                    parameters.basket_number_of_students_elective.append(1)
                    parameters.basket_students_elective.append([parameters.student_list[k]])
                else:
                    if temp in parameters.baskets_elective:
                        if parameters.student_list[k] not in parameters.basket_students_elective[parameters.baskets_elective.index(temp)]:
                            parameters.basket_students_elective[parameters.baskets_elective.index(temp)].append(parameters.student_list[k])

                            parameters.basket_number_of_students_elective[
                                parameters.baskets_elective.index(temp)
                            ] += 1


    with open("Results/baskets.txt", "w") as f:
        f.write(f"Core Courses:\n\n")
        for i, (x, y) in enumerate(parameters.baskets_core):
            f.write(f"{parameters.course_list[x],parameters.course_list[y]}\n")
        f.write(f"\nElective Courses:\n\n")
        for i, (x, y) in enumerate(parameters.baskets_elective):
            f.write(
                f"{parameters.course_list[x],parameters.course_list[y]} : {parameters.basket_number_of_students_core[i]}\n"
            )
    return


def initialize_parameters(file_name):
    courses_dict, student_dict, instructor_dict, venue_dict = read_input_excel(
        file_name
    )
    number_of_students = len(student_dict)
    number_of_instructors = len(instructor_dict)
    number_of_venues = len(venue_dict)
    number_of_working_days = 6
    slots = 2
    campus_list = sorted(set([i.campus_type for i in venue_dict.values()]))
    number_of_campuses = len(campus_list)
    student_list = list(sorted(student_dict.keys()))
    instructor_list = list(sorted(instructor_dict.keys()))
    # venue_list = list(
    #     sorted(
    #         venue_dict.keys(),
    #         key=lambda x: (venue_dict[x].type, venue_dict[x].campus_type),
    #     )
    # )
    venue_list = list(
        sorted(
            venue_dict.keys(),
            key=lambda x: venue_dict[x].number_of_setups
        )
    )

    venue_types = np.array([venue_dict[i].type for i in venue_list])
    venue_setups = np.array([venue_dict[i].number_of_setups for i in venue_list])
    venue_campus = np.array(
        [campus_list.index(venue_dict[i].campus_type) for i in venue_list]
    )

    course_list = list(sorted(courses_dict.keys()))
    course_campus = np.array(
        [campus_list.index(courses_dict[i].campus_type) for i in course_list]
    )
    number_of_courses = len(courses_dict)
    # course_lab = np.zeros((number_of_courses, 2))
    course_group_size = np.zeros(number_of_courses)
    course_venue_type = np.zeros(number_of_courses)
    students_Courses = np.zeros((number_of_students, number_of_courses))
    instructors_Courses = np.zeros((number_of_instructors, number_of_courses))
    course_credits = np.zeros(number_of_courses)
    student_course_priority = np.zeros((number_of_students, number_of_courses)) - 1
    non_minor_core_course = np.zeros((number_of_students, number_of_courses))
    full_sem_courses = []
    pre_half_sem_courses = []
    post_half_sem_courses = []


    for i, j in enumerate(student_list):
        for course in student_dict[j].courses:
            course_index = course_list.index(course.code)
            type_of_course = student_dict[j].courses[course]
            student_course_priority[i][course_index] = type_of_course
            non_minor_core_course[i][course_index] = 1 if type_of_course == 0 else 0

    non_minor_core_course = np.sum(non_minor_core_course, axis=0)
    non_minor_core_course = np.where(non_minor_core_course == 0, 0, 1)

    for i, j in enumerate(student_list):
        for k in student_dict[j].courses:
            students_Courses[i][course_list.index(k.code)] = 1

    for i, j in enumerate(instructor_list):
        for k in instructor_dict[j].courses:
            instructors_Courses[i][course_list.index(k.code)] = 1

    course_strength = np.sum(students_Courses, axis=0)

    for i, j in enumerate(course_list):
        course_group_size[i] = courses_dict[j].group_size
        course_venue_type[i] = courses_dict[j].venue_type

        course_credits[i] = courses_dict[j].get_credits()

        if courses_dict[j].minor:
            non_minor_core_course[i] = 2

        if course_strength[i] == 0:
            course_credits[i] = 0

        my_type = courses_dict[j].duration

        if my_type == "F":
            full_sem_courses.append(i)
        elif my_type == "H1":
            pre_half_sem_courses.append(i)
        else:
            post_half_sem_courses.append(i)

    venue_capacity = np.array([venue_dict[venue].capacity for venue in venue_list])

    course_venue_capacity = []
    course_bifercations = []
    for index in range(number_of_campuses):
        temp = np.where(course_campus == index)[0]
        # print(temp)
        course_bifercations.append(temp)
        venue_temp = np.where(venue_campus == index)[0]
        course_venue_capacity.append(np.sum(venue_capacity[venue_temp]))

    # total_venue_capacity = 0
    # for venue in venue_list:
    #     if venue_dict[venue].type == 0:
    #         total_venue_capacity += venue_dict[venue].capacity

    parameters = classes_exam.Params()
    parameters.number_of_working_days = number_of_working_days
    parameters.slots = slots
    parameters.number_of_courses = number_of_courses
    parameters.number_of_venues = number_of_venues
    parameters.number_of_students = number_of_students
    parameters.instructors_Courses = instructors_Courses
    parameters.number_of_instructors = number_of_instructors
    parameters.course_credits = course_credits
    parameters.venue_dict = venue_dict
    parameters.venue_list = venue_list
    parameters.course_list = course_list
    parameters.venue_setups = venue_setups
    parameters.course_strength = course_strength
    parameters.full_sem_courses = full_sem_courses
    parameters.pre_half_sem_courses = pre_half_sem_courses
    parameters.post_half_sem_courses = post_half_sem_courses
    parameters.venue_types = venue_types
    # parameters.course_lab = course_lab
    parameters.course_venue_type = course_group_size
    parameters.course_group_size = course_group_size
    parameters.student_course_priority = student_course_priority
    parameters.non_minor_core_course = non_minor_core_course
    parameters.campus_list = campus_list
    parameters.number_of_campuses = number_of_campuses
    parameters.course_campus = course_campus
    parameters.venue_campus = venue_campus
    parameters.student_list = student_list
    parameters.courses_dict = courses_dict
    parameters.student_dict = student_dict
    parameters.instructor_dict = instructor_dict
    parameters.venue_dict = venue_dict
    parameters.instructor_list = instructor_list
    make_baskets(parameters)

    parameters.course_venue_capacity = course_venue_capacity
    parameters.course_bifercations = course_bifercations

    return parameters


def initialize_model(parameters: classes_exam.Params):
    my_model = gp.Model("Timetable")
    my_model.Params.LogFile = "m.log"
    # my_model.setParam("LogToConsole", 0)
    my_model.Params.TimeLimit = float("infinity")

    my_model.Params.MIPFocus = 1
    # my_model.Params.MinRelNodes = 1e7
    # my_model.Params.PumpPasses = 1e7
    # my_model.Params.ZeroObjNodes = 1e7
    # my_model.Params.ImproveStartNodes = 1
    my_model.Params.Presolve = 2
    # my_model.Params.Heuristics = 0.3
    # my_model.Params.NodeMethod = 2
    # my_model.Params.MIPGap = 3e-2
    schedule = my_model.addMVar(
        (
            parameters.number_of_working_days,
            parameters.slots,
            parameters.number_of_courses,
        ),
        vtype=GRB.BINARY,
        name="time",
    )
    return my_model, schedule


def constr_No_course_Overlap_Student(my_model, schedule, parameters: classes_exam.Params):
    x1 = schedule

    for i in range(parameters.number_of_working_days):
        for j in range(parameters.slots):
            for basket in parameters.baskets_core:
                my_model.addConstr(
                    x1[i, j, np.array(list(basket))].sum() <= 1,
                    name="No_core_course_Overlap_Student",
                )

    return


def constr_Total_Credits_of_core_Course(my_model, schedule, parameters: classes_exam.Params):
    x1 = schedule.sum(axis=1)
    x1 = x1.sum(axis=0)
    my_model.addConstrs(
        (
            (x1[i] == parameters.course_credits[i])
            for i in range(parameters.number_of_courses)
        ),
        name="Total_Credits_of_core_Course",
    )
    return


def constr_venue_setups(my_model, schedule, parameters: classes_exam.Params):

    for i in range(parameters.number_of_working_days):
        for j in range(parameters.slots):
                for index, courses in enumerate(parameters.course_bifercations):
                    x = schedule[:, :, courses]
                    my_model.addConstr(
                        (x[i, j]*parameters.course_strength[courses]).sum() <= parameters.course_venue_capacity[index],
                        name="Venue_Constraint"
                    )

    return


def experimental_constraint(my_model, schedule, parameters: classes_exam.Params):
    x1 = schedule.sum(axis=2)

    my_model.addConstrs(
        (
            (x1[i, j] >= x1[i, j + 1])
            for i in range(parameters.number_of_working_days)
            for j in range(parameters.slots - 1)
        ),
        name="Experimental Constraint",
    )

    return


def add_constrs(my_model, schedule, parameters):

    constr_No_course_Overlap_Student(my_model, schedule, parameters)
    print("2")

    constr_venue_setups(my_model, schedule, parameters)
    print("6")

    constr_Total_Credits_of_core_Course(my_model, schedule, parameters)
    print("7")

    experimental_constraint(my_model, schedule, parameters)
    print("14")

    print("Primary Constraints done !!!")

    my_model.update()
    return


def calculate_venues(schedule, parameters: classes_exam.Params):
    timetable = np.zeros((parameters.number_of_working_days, parameters.slots, parameters.number_of_courses)) - 1
    for i in range(parameters.number_of_working_days):
        for j in range(parameters.slots):
            lab_size = {}
            alloted_venues = []
            scheduled_courses = np.where(schedule[i, j].X == 1)[0]
            scheduled_theory_courses = np.intersect1d(scheduled_courses, parameters.course_theory)
            scheduled_theory_courses = sorted(scheduled_theory_courses, key=lambda x: parameters.course_strength[x], reverse=True)
            scheduled_lab_courses = [i for i in scheduled_courses if i not in scheduled_theory_courses]

            temp = scheduled_lab_courses.copy()

            for course in scheduled_lab_courses:
                if course == parameters.lab_course_mapping[course][0]:
                    lab_size[course] = len(parameters.lab_course_mapping[course])
                else:
                    first_lab = parameters.lab_course_mapping[course][0]
                    first_venue = timetable[i][j-parameters.lab_course_mapping[course].index(course)][first_lab]
                    if first_venue == -1:
                        print(i, j)
                        print(parameters.lab_course_mapping[course])
                        print(course)
                        print("Not correct!")
                    timetable[i][j][course] = first_venue
                    alloted_venues.append(first_venue)
                    temp.remove(course)
            scheduled_lab_courses = temp
            scheduled_lab_courses = sorted(scheduled_lab_courses, key=lambda x:lab_size[x], reverse=True)
            for course in scheduled_theory_courses:
                for venue in parameters.course_venues[course]:
                    if venue not in alloted_venues:
                        timetable[i][j][course] = venue
                        alloted_venues.append(venue)
                        break

            for course in scheduled_lab_courses:
                for venue in parameters.course_venues[course]:
                    # if venue not in alloted_venues:
                        timetable[i][j][course] = venue
                        alloted_venues.append(venue)
                        break

    return timetable


def print_time_table(my_model, schedule, parameters: classes_exam.Params, file, extra=""):
    # my_model.write(f"Models/{parameters.number_of_working_days}"+extra+".mps")
    print("\nYesssssss!")
    print(f"number_of_working_days : {parameters.number_of_working_days}\n")
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    printing_format = {}
    slots_utilized = 0
    # unique_venues = {campus: set() for campus in parameters.campus_list}
    try:
        schedule[0,0,0,0].X
    except:
        try:
            my_model.Params.SolutionNumber = 1
        except:
            print("No optimized solution found!")
            return
        
    # my_model.write(
        # f"Solutions/{parameters.number_of_working_days}" + extra + ".sol"
    # )

    # timetable = calculate_venues(schedule, parameters)

    df = pd.DataFrame(
        columns=["Day"] + [f"Slot {i}" for i in range(1, parameters.slots + 1)]
    )
    with pd.ExcelWriter(f"Results/Exam_Output_{parameters.number_of_working_days}.xlsx", engine="openpyxl") as writer:
        for i in range(parameters.number_of_working_days):
            temp = {}
            for j in range(parameters.slots):
                # number_of_venues-number_of_labs,
                temp[j] = []
                slot_not_empty = False
                # for k in range(parameters.number_of_venues):
                for l in range(parameters.number_of_courses):
                    # if my_model.getVarByName('time[%d,%d,%d,%d]' % (i, j, k, l)).X == 1:
                    # if schedule[i, j, k, l].X == 1:
                    if schedule[i, j, l].X == 1:
                        slot_not_empty = True
                        # k = int(schedule[i, j, l])
                            # f"{parameters.course_list[l]} : {parameters.venue_list[k]}"
                        temp[j].append(
                            f"{parameters.course_list[l]}"
                        )
                        # unique_venues[
                        #     parameters.campus_list[parameters.venue_campus[k]]
                        # ].add(k)
                        if l in printing_format:
                            printing_format[l].append(
                                str(days[i])
                                + str(j + 1)
                                # + " ["
                                # + parameters.venue_list[k]
                                # + "]"
                            )
                        else:
                            printing_format[l] = [
                                str(days[i])
                                + str(j + 1)
                                # + " ["
                                # + parameters.venue_list[k]
                                # + "]"
                            ]
                if slot_not_empty:
                    slots_utilized += 1

            dict_1 = {"Day": [f"{days[i]}"]}
            for slot in range(parameters.slots):
                dict_1[f"Slot {slot+1}"] = ["\n".join(temp[slot])]
            temp_df = pd.DataFrame(dict_1)
            df = pd.concat([df, temp_df], ignore_index=True)
        df.to_excel(writer, sheet_name=f"University Timetable", index=False)
        writer.save()

    print(f"number of working days utilized : {parameters.number_of_working_days}")
    # for campus, venue_set in unique_venues.items():
    #     print(
    #         f"Campus {campus} : Venues {[parameters.venue_list[i] for i in venue_set]}\n  number of venues used : {len(venue_set)}\n"
    #     )
    print(f"number of slots utilized : {slots_utilized}\n")

    with open(file, "w") as f:
        for course, time in printing_format.items():
            f.write(f"{parameters.course_list[course]} : {', '.join(time)}\n")

    return
