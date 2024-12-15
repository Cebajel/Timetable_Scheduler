import pandas as pd
from itertools import chain
import gurobipy as gp
import numpy as np
from gurobipy import GRB
import pandas, math
import classes
import random

def read_input_excel(file):
    # second_file = ""
    second_file = "-test"
    courses_dict = {}
    student_dict = {}
    instructor_dict = {}
    venue_dict = {}
    lab_courses = {}

    courses = pandas.read_excel(file, "Courses" + second_file)
    columns = courses.columns

    for value in courses.iterrows():
        value = value[1]
        # temp_campus = value[columns[9]].strip().split("\n")
        code = value[columns[0]].strip()
        L = int(value[columns[3]]) if not math.isnan(value[columns[3]]) else 0
        T = int(value[columns[4]]) if not math.isnan(value[columns[4]]) else 0
        P = int(value[columns[5]]) if not math.isnan(value[columns[5]]) else 0
        if L+T != 0:
            value[columns[0]] = code + "_L"

            new_course = classes.Course(value, columns)
            courses_dict[new_course.code] = new_course
            instructors = [i.strip() for i in value[columns[2]].split("\n")]
            TAs = [i.strip() for i in value[columns[12]].split("\n")] if isinstance(value[columns[12]], str) else []

            for i in instructors:
                if i not in instructor_dict:
                    new_instructor = classes.Instructor(i)
                    instructor_dict[i] = new_instructor
                new_course.add_instructor(instructor_dict[i])
                instructor_dict[i].add_course(new_course)

            for i in TAs:
                if i not in student_dict:
                    new_TA = classes.Student(i)
                    student_dict[new_TA.rollnumber] = new_TA
                student_dict[i].add_course(
                    courses_dict[code + "_L"], 0
                )
                new_course.add_TA(student_dict[i])
        
        if P != 0:
            lab_courses[code] = []
            for num in range(1, P+1):
                value[columns[0]] = code + f"_P{num}"
                new_course = classes.Course(value, columns, False)
                lab_courses[code].append(new_course.code)
                courses_dict[new_course.code] = new_course
                instructors = [i.strip() for i in value[columns[2]].split("\n")]
                TAs = [i.strip() for i in value[columns[12]].split("\n")] if isinstance(value[columns[12]], str) else []

                for i in instructors:
                    if i not in instructor_dict:
                        new_instructor = classes.Instructor(i)
                        instructor_dict[i] = new_instructor
                    new_course.add_instructor(instructor_dict[i])
                    instructor_dict[i].add_course(new_course)

                for i in TAs:
                    if i not in student_dict:
                        new_TA = classes.Student(i)
                        student_dict[new_TA.rollnumber] = new_TA
                    student_dict[i].add_course(
                        courses_dict[code + f"_P{num}"], 0
                    )
                    new_course.add_TA(student_dict[i])

    # print({code:course.get_LTP() for code,course in courses_dict.items()})
    # print([f"{i.rollnumber} : { {course.code:priority for course,priority in i.courses.items()} }" for i in student_dict.values()])
    # exit(1)

    registrations = pandas.read_excel(file, "Registrations" + second_file)
    columns = registrations.columns

    for value in registrations.iterrows():
        value = value[1]
        value[columns[1]] = str(value[columns[1]])
        if value[columns[1]] not in student_dict:
            new_student = classes.Student(value[columns[1]])
            student_dict[new_student.rollnumber] = new_student

        current_code = value[columns[0]].strip()

        if current_code + "_L" in courses_dict:
            student_dict[value[columns[1]]].add_course(
                courses_dict[current_code + "_L"], int(value[columns[3]])
            )
            courses_dict[current_code + "_L"].add_student(
                student_dict[value[columns[1]]], int(value[columns[3]])
            )

            # For printing purposes
            if (int(value[columns[3]]) == 0) and (
                value[columns[4]]
                not in courses_dict[current_code + "_L"].groups
            ):
                courses_dict[current_code + "_L"].groups.append(
                    value[columns[4]]
                )

        if current_code + "_P" in courses_dict:
            student_dict[value[columns[1]]].add_course(
                courses_dict[current_code + "_P"], int(value[columns[3]])
            )
            courses_dict[current_code + "_P"].add_student(
                student_dict[value[columns[1]]], int(value[columns[3]])
            )
            # For printing purposes
            if (int(value[columns[3]]) == 0) and (
                value[columns[4]]
                not in courses_dict[current_code + "_P"].groups
            ):
                courses_dict[current_code + "_P"].groups.append(
                    value[columns[4]]
                )
        
        if current_code in lab_courses:
            for course in lab_courses[current_code]:
                student_dict[value[columns[1]]].add_course(
                courses_dict[course], int(value[columns[3]])
                )
                courses_dict[course].add_student(
                    student_dict[value[columns[1]]], int(value[columns[3]])
                )
                # For printing purposes
                if (int(value[columns[3]]) == 0) and (
                    value[columns[4]]
                    not in courses_dict[course].groups
                ):
                    courses_dict[course].groups.append(
                        value[columns[4]]
                    )

    venues = pandas.read_excel(file, "Venues" + second_file)
    columns = venues.columns

    for value in venues.iterrows():
        value = value[1]
        current_venue = classes.Venue(
            str(value[columns[0]]).strip(),
            value[columns[4]],
            value[columns[5]],
            value[columns[6]],
        )
        venue_dict[str(value[columns[0]]).strip()] = current_venue

    return courses_dict, student_dict, instructor_dict, venue_dict, lab_courses


def course_splitting(
    courses_dict, lab_courses
):
    temp_values = [value for value in courses_dict.values()]
    splitted_courses = {}
    for course in temp_values:

        if course.divisions > 1:
            divisions = course.divisions
            new_strength = math.ceil((course.get_strength() - course.get_number_of_tas()) / divisions)
            splitted_courses[course.code] = []
        else:
            continue

        temp_students_list = set(
            sorted(course.students.keys(), key=lambda x: x.rollnumber)
        )

        tas = set(course.TAs)
        temp_students_list = list(temp_students_list - tas)
        tas = list(tas)

        for i in range(1, divisions):
            new_course = classes.Course(orig=course)
            new_course.code = new_course.code + "_" + str(i)

            new_course.students = {
                j : course.students[j]
                for j in temp_students_list[
                    new_strength * i : new_strength * i + new_strength
                ] + tas
            }
            courses_dict[new_course.code] = new_course
            with open("Results/Course_Rollnumbers.txt", "a") as file:
                file.write(
                    f"\n{new_course.code} : { {i.rollnumber:priority for i,priority in new_course.students.items()} }\n"
                )

            for student, priority in new_course.students.items():
                student.add_course(new_course, priority)

            for instructor in new_course.instructors:
                instructor.add_course(new_course)
            
            splitted_courses[course.code].append(new_course.code)

        my_key = course.code.split("_")[0]
        if my_key in lab_courses and course.code.split("_")[1][0] == "P":
            courses = lab_courses[my_key]
            for div in range(1, divisions):
                lab_courses[my_key+f"_{div}"] = [temp_course+f"_{div}" for temp_course in courses]
            del lab_courses[my_key]
            
        for student in course.students:
            del student.courses[course]
        for instructor in course.instructors:
            instructor.courses.remove(course)
        del courses_dict[course.code]

    # del temp_values, tas
    return splitted_courses


def make_baskets(parameters: classes.Params):
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

        # part 2
        # if len(courses_core_1) > 1 and courses_core_1 not in parameters.baskets_core:
        #     parameters.baskets_core.append(courses_core_1)

        # if len(courses_core_2) > 1 and courses_core_2 not in parameters.baskets_core:
        #     parameters.baskets_core.append(courses_core_2)

        # for i in range(len(courses_elective_1)):
        #     for j in range(i+1, len(courses_elective_1)):
        #         temp = [courses_elective_1[i], courses_elective_1[j]]
        #         if temp not in parameters.baskets_elective:
        #             parameters.baskets_elective.append(temp)
        #             parameters.basket_number_of_students.append(1)
        #         else:
        #             if temp in parameters.baskets_elective:
        #                 parameters.basket_number_of_students[parameters.baskets_elective.index(temp)] += 1

        # for i in range(len(courses_elective_2)):
        #     for j in range(i+1, len(courses_elective_2)):
        #         temp = [courses_elective_2[i], courses_elective_2[j]]
        #         if temp not in parameters.baskets_elective:
        #             parameters.baskets_elective.append(temp)
        #             parameters.basket_number_of_students.append(1)
        #         else:
        #             if temp in parameters.baskets_elective:
        #                 parameters.basket_number_of_students[parameters.baskets_elective.index(temp)] += 1

    # print(parameters.basket_number_of_students_core)
    # exit(1)

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
    courses_dict, student_dict, instructor_dict, venue_dict, lab_courses = read_input_excel(
        file_name
    )
    number_of_students = len(student_dict)
    number_of_instructors = len(instructor_dict)
    number_of_venues = len(venue_dict)
    number_of_working_days = 5
    slots = 8
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

    splitted_courses = course_splitting(
        courses_dict, lab_courses
    )

    course_list = list(sorted(courses_dict.keys()))
    course_campus = np.array(
        [campus_list.index(courses_dict[i].campus_type) for i in course_list]
    )
    lab_courses = [ [course_list.index(i) for i in courses] for courses in lab_courses.values()]
    lab_course_mapping = { lab:labs for labs in lab_courses for lab in labs}
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

    # for printing purposes
    groups = sorted(
        set(
            [
                group
                for course_object in courses_dict.values()
                for group in course_object.groups
            ]
        )
    )

    groups_courses = np.zeros((len(groups), number_of_courses))

    for i, j in enumerate(student_list):
        for course in student_dict[j].courses:
            course_index = course_list.index(course.code)
            type_of_course = student_dict[j].courses[course]
            student_course_priority[i][course_index] = type_of_course
            non_minor_core_course[i][course_index] = 1 if type_of_course == 0 else 0
    # del registrations, columns

    non_minor_core_course = np.sum(non_minor_core_course, axis=0)
    non_minor_core_course = np.where(non_minor_core_course == 0, 0, 1)

    for i, j in enumerate(student_list):
        for k in student_dict[j].courses:
            students_Courses[i][course_list.index(k.code)] = 1

    for i, j in enumerate(instructor_list):
        for k in instructor_dict[j].courses:
            instructors_Courses[i][course_list.index(k.code)] = 1

    # core_courses = np.sum(students_Courses, axis=0)
    course_strength = np.sum(students_Courses, axis=0)

    for i, j in enumerate(course_list):
        course_group_size[i] = courses_dict[j].group_size
        course_venue_type[i] = courses_dict[j].venue_type
        # course_lab[i][0] = courses_dict[j].group_size
        # course_lab[i][1] = courses_dict[j].venue_type

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

        for group in courses_dict[j].groups:
            group_index = groups.index(group)
            groups_courses[group_index][i] = 1

    course_venues = []
    course_venues_number = []

    ground_index = venue_list.index("Ground")
    nso_index = course_list.index("NO 101/NO 103_L")

    for course_index in range(number_of_courses):
        if course_index == nso_index:
            course_venues.append(np.array([ground_index]))
            course_venues_number.append(1)
            continue    
        allowed_venues = np.where(venue_campus == course_campus[course_index])[0]
        allowed_venues = np.intersect1d(allowed_venues, np.where(venue_types == course_venue_type[course_index])[0])
        allowed_venues = np.intersect1d(allowed_venues, np.where(venue_setups*course_group_size[course_index] >= course_strength[course_index])[0])
        temp_ground_index = np.where(allowed_venues == ground_index)[0]
        allowed_venues = np.delete(allowed_venues, temp_ground_index)
        course_venues.append(allowed_venues)
        course_venues_number.append(allowed_venues.size)

    course_venues_number = np.array(course_venues_number)
    course_theory = np.array([ index for index, course in enumerate(course_list) if courses_dict[course].theory])

    number_of_venue_types = len(set(list(venue_types)))

    course_bifercations = []
    for campus in range(number_of_campuses):
        for venue_type in range(number_of_venue_types):
            temp = np.where(course_campus == campus)[0]
            temp = np.intersect1d(temp, np.where(course_venue_type == venue_type)[0])
            temp_nso_index = np.where(temp == nso_index)[0]
            temp = np.delete(temp, temp_nso_index)
            course_bifercations.append(temp)

    # course_credits = np.c_[course_credits, np.sum(course_credits, axis=1)]
    # dummy_index = venue_list.index("Dummy 1")
    # print(dummy_index)
    # count = 0
    # for course in course_venues:
    #     if dummy_index in course:
    #         count += 1
    # print(count)
    # exit(0)

    parameters = classes.Params()
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
    parameters.splitted_courses = splitted_courses
    make_baskets(parameters)

    parameters.groups = groups
    parameters.groups_courses = groups_courses
    parameters.lab_courses = lab_courses
    parameters.course_venues = course_venues
    parameters.course_venues_number = course_venues_number
    parameters.course_theory = course_theory
    parameters.course_bifercations = course_bifercations
    parameters.lab_course_mapping = lab_course_mapping

    # nso_index = parameters.course_list.index("NO 101/NO 103")
    # course_list = list(np.arange(parameters.number_of_courses))
    # course_list.remove(nso_index)
    # course_list = np.array(course_list)
    # print(nso_index)
    # print(course_list)
    # print(parameters.course_list)

    # print(parameters.groups.index('UG_2023'))
    # print(parameters.groups_courses[17])
    # exit(1)

    return parameters


def initialize_model(parameters: classes.Params):
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
            # parameters.number_of_venues,
            parameters.number_of_courses,
        ),
        vtype=GRB.BINARY,
        name="time",
    )
    return my_model, schedule


def constr_One_Venue_One_Course(my_model, schedule, parameters: classes.Params):
    # x1 = schedule.sum(axis=3)
    x1 = schedule[
        :,
        :,
        : parameters.venue_types[parameters.venue_types_list[0]],
        parameters.full_sem_courses + parameters.pre_half_sem_courses,
    ].sum(axis=3)
    my_model.addConstrs(
        (
            (x1[i, j, k] <= 1)
            for i in range(parameters.number_of_working_days)
            for j in range(parameters.slots)
            for k in range(parameters.venue_types[parameters.venue_types_list[0]])
        ),
        name="One_Venue_One_Course_Pre_Sem",
    )

    x1 = schedule[
        :,
        :,
        : parameters.venue_types[parameters.venue_types_list[0]],
        parameters.full_sem_courses + parameters.post_half_sem_courses,
    ].sum(axis=3)
    my_model.addConstrs(
        (
            (x1[i, j, k] <= 1)
            for i in range(parameters.number_of_working_days)
            for j in range(parameters.slots)
            for k in range(parameters.venue_types[parameters.venue_types_list[0]])
        ),
        name="One_Venue_One_Course_Post_Sem",
    )

    return


def constr_No_course_Overlap_Student(my_model, schedule, parameters: classes.Params):
    x1 = schedule

    for i in range(parameters.number_of_working_days):
        for j in range(parameters.slots):
            for basket in parameters.baskets_core:
                my_model.addConstr(
                    x1[i, j, np.array(list(basket))].sum() <= 1,
                    name="No_core_course_Overlap_Student",
                )

    return


def constr_No_course_Overlap_Professor(my_model, schedule, parameters: classes.Params):
    x1 = schedule[
        :, :, parameters.full_sem_courses + parameters.pre_half_sem_courses
    ]
    x2 = schedule[
        :, :, parameters.full_sem_courses + parameters.post_half_sem_courses
    ]
    for i in range(parameters.number_of_working_days):
        for j in range(parameters.slots):
            for k in range(parameters.number_of_instructors):
                my_model.addConstr(
                    (
                        x1[i, j]
                        * parameters.instructors_Courses[k][
                            parameters.full_sem_courses
                            + parameters.pre_half_sem_courses
                        ]
                    ).sum()
                    <= 1,
                    name="No_course_Overlap_Professor_Pre_Sem",
                )

                my_model.addConstr(
                    (
                        x2[i, j]
                        * parameters.instructors_Courses[k][
                            parameters.full_sem_courses
                            + parameters.post_half_sem_courses
                        ]
                    ).sum()
                    <= 1,
                    name="No_course_Overlap_Professor_Post_Sem",
                )

    return


def constr_One_Slot_Course_Once(my_model, schedule, parameters: classes.Params):
    x1 = schedule
    my_model.addConstrs(
        (
            (x1[i, j, k] <= 1)
            for i in range(parameters.number_of_working_days)
            for j in range(parameters.slots)
            for k in range(parameters.number_of_courses)
        ),
        name="One_Slot_Course_Once",
    )
    return


def constr_Course_only_Once_a_day(my_model, schedule, parameters: classes.Params):
    x2 = schedule.sum(axis=1)
    my_model.addConstrs(
        (
            (x2[i, j] <= 1)
            for i in range(parameters.number_of_working_days)
            for j in range(parameters.number_of_courses)
        ),
        name="Course_only_Once_a_day_0",
    )

    return


def constr_Total_Credits_of_core_Course(my_model, schedule, parameters: classes.Params):
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


def constr_Total_lab_hours_of_Course(my_model, schedule, parameters: classes.Params):
    my_sum = parameters.venue_types[parameters.venue_types_list[0]]
    for lab in parameters.lab_types_list:
        x1 = schedule[:, :, my_sum : my_sum + parameters.venue_types[lab], :]
        my_sum += parameters.venue_types[lab]
        x2 = x1.sum(axis=2)
        x2 = x2.sum(axis=1)
        x2 = x2.sum(axis=0)
        my_model.addConstrs(
            (
                (x2[i] == parameters.course_credits[i])
                if parameters.course_lab[i][1] == lab
                else (x2[i] == 0)
                for i in range(parameters.number_of_courses)
            ),
            name="Total_lab_hours_of_Course",
        )
    return


def constr_venue_setups(my_model, schedule, parameters: classes.Params):
    # x1 = schedule.sum(axis=1)
    # x1 = x1.sum(axis=0)
    # my_model.addConstrs(
    #     (
    #         (x1[i, j] == 0)
    #         for i in range(parameters.number_of_venues)
    #         for j in range(parameters.number_of_courses)
    #         if parameters.course_strength[j]
    #         > parameters.venue_setups[i] * parameters.course_lab[j][0]
    #     ),
    #     name="venue_setups",
    # )

    for i in range(parameters.number_of_working_days):
        for j in range(parameters.slots):
            for courses in parameters.course_bifercations:
                course_set = np.intersect1d(courses, parameters.course_theory)
                x = schedule[:, :, course_set]
                allowed_venues = parameters.course_venues_number[course_set]

                values = sorted(list(set(list(allowed_venues))))
                for num in values:
                    temp = np.where(allowed_venues <= num, 1, 0)
                    my_model.addConstr(
                        (x[i, j]*temp).sum() <= num,
                        name="Venue_Constraint"
                    )

    return


def constrs_Allowed_Lab_Time(my_model, schedule, parameters: classes.Params):
    # my_sum = parameters.venue_types[parameters.venue_types_list[0]]
    # for lab in parameters.lab_types_list:
    #     total_venues = parameters.venue_types[lab]
    #     x1 = schedule[:, :, my_sum : my_sum + total_venues, :]
    #     x2 = x1.sum(axis=1)
    #     my_sum += total_venues

    #     y = my_model.addMVar(
    #         (
    #             parameters.number_of_working_days,
    #             total_venues,
    #             parameters.number_of_courses,
    #             parameters.slots + 1,
    #         ),
    #         vtype=GRB.BINARY,
    #     )

    #     my_model.addConstrs(
    #         (
    #             (gp.quicksum(y[i, j, k, l] for l in range(parameters.slots + 1)) == 1)
    #             for i in range(parameters.number_of_working_days)
    #             for j in range(total_venues)
    #             for k in range(parameters.number_of_courses)
    #             if parameters.course_lab[k][1] == lab
    #         ),
    #         name="indicator_0",
    #     )

    #     for i in range(parameters.number_of_working_days):
    #         for k in range(total_venues): 
    #             for l in range(parameters.number_of_courses):
    #                 for t in range(0, parameters.slots + 1 - int(parameters.course_credits[l])):
    #                     if int(parameters.course_credits[l]) > 0 and parameters.course_lab[l][1] == lab:
    #                         my_model.addConstr(
    #                             ( (y[i, k, l, t].item() == 1) >> (gp.quicksum(x1[i, j, k, l] for j in range(t, t + int(parameters.course_credits[l]))) == int(parameters.course_credits[l])) )
    #                                 , name="Allowed_Lab_Time_0")
                            
    #                         my_model.addConstr(
    #                             ( (y[i, k, l, t].item() == 1) >> (gp.quicksum(x1[i, j, k, l] for j in chain(range(0, t), range(t + int(parameters.course_credits[l]), parameters.slots))) == 0) )
    #                                 , name="Allowed_Lab_Time_1")
                                    


    #     for i in range(parameters.number_of_working_days):
    #         for j in range(total_venues):
    #             for l in range(parameters.number_of_courses):
    #                 if int(parameters.course_credits[l]) > 0 and parameters.course_lab[l][1] == lab:
    #                     my_model.addConstr( gp.quicksum(y[i, j, l, t] for t in range(5 - int(parameters.course_credits[l]), 4)) == 0, name="indicator_1" )
    #                     my_model.addConstr( gp.quicksum(y[i, j, l, t] for t in range(parameters.slots + 1 - int(parameters.course_credits[l]), parameters.slots)) == 0, name="indicator_2" )

    for courses in parameters.lab_courses:
        for i in range(parameters.number_of_working_days):
            for index in range(len(courses) - 1):
                for j in chain(range(3), range(4, parameters.slots - 1)):
                    my_model.addConstr(
                        (schedule[i, j, courses[index]].item() == 1) >> (schedule[i, j+1, courses[index + 1]] == 1),
                        name="Allowed_Lab_Time_0"
                    )
                
                my_model.addConstr(
                    (schedule[i, 3, courses[index]] == 0),
                    name="No_lab_at_break"
                )

                my_model.addConstr(
                    (schedule[i, parameters.slots - 1, courses[index]] == 0),
                    name="No_lab_at_break"
                )

            for index in range(len(courses) - 1, 0, -1):
                for j in chain(range(parameters.slots - 1, 4, -1), range(3, 0, -1)):
                    my_model.addConstr(
                        (schedule[i, j, courses[index]].item() == 1) >> (schedule[i, j-1, courses[index - 1]] == 1),
                        name="Allowed_Lab_Time_1"
                    )
                
                my_model.addConstr(
                    (schedule[i, 4, courses[index]] == 0),
                    name="No_lab_at_break"
                )

                my_model.addConstr(
                    (schedule[i, 0, courses[index]] == 0),
                    name="No_lab_at_break"
                )

    return


def constrs_Non_Minor_Core_Course(my_model, schedule, parameters: classes.Params):
    for _, k1 in np.ndenumerate(np.where(parameters.non_minor_core_course == 1)[0]):
        for _, k2 in np.ndenumerate(np.where(parameters.non_minor_core_course == 2)[0]):
            my_model.addConstrs(
                (
                    (schedule[i, j, k1] + schedule[i, j, k2] <= 1)
                    for i in range(parameters.number_of_working_days)
                    for j in range(parameters.slots)
                ),
                name="Non_Minor_Core_Course",
            )

    return


def constrs_Course_Campus(my_model, schedule, parameters: classes.Params):
    x = schedule.sum(axis=1)
    x = x.sum(axis=0)
    my_model.addConstrs(
        (
            (x[i, j] == 0)
            for i in range(parameters.number_of_venues)
            for j in range(parameters.number_of_courses)
            if parameters.venue_campus[i] != parameters.course_campus[j]
        ),
        name="Campus_Constraint",
    )

    return


def constrs_Student_Campus(my_model, schedule, parameters: classes.Params):
    y = my_model.addMVar(
        (
            parameters.number_of_working_days,
            parameters.slots,
            parameters.number_of_courses,
        ),
        vtype=GRB.BINARY,
    )
    my_model.addConstrs(
        (
            schedule[i, j, k] == y[i, j, k]
            for i in range(parameters.number_of_working_days)
            for j in range(parameters.slots)
            for k in range(parameters.number_of_courses)
        ),
        name="Conditional_Constraint",
    )

    for student in range(parameters.number_of_students):
        student_courses = parameters.student_course_priority[student]
        student_courses = np.where(student_courses != -1)[0]
        for campus in range(parameters.number_of_campuses):
            # print(parameters.campus_list[campus])
            current_campus_courses = np.where(parameters.course_campus == campus)[0]
            not_current_campus_courses = np.where(parameters.course_campus != campus)[0]
            current_campus_student_courses = list(
                np.intersect1d(student_courses, current_campus_courses)
            )
            current_campus_student_courses = np.intersect1d(
                student_courses, current_campus_courses
            )
            not_current_campus_student_courses = np.intersect1d(
                student_courses, not_current_campus_courses
            )

            if (
                len(current_campus_student_courses)
                * not_current_campus_student_courses.size
                > 0
            ):
                my_model.addConstrs(
                    (
                        ((y[i, j, k].item() == 1) >> (gp.quicksum(schedule[i, j + 1, not_current_campus_student_courses]) == 0))
                        for i in range(parameters.number_of_working_days)
                        for j in chain(range(3), range(4, parameters.slots - 1)) # separate breaks
                        for k in current_campus_student_courses
                    ),
                    name="Student_Campus_Constraint",
                )

    return


def constrs_Professor_Campus(my_model, schedule, parameters: classes.Params):
    # x = schedule.sum(axis=2)
    x = schedule
    y = my_model.addMVar(
        (
            parameters.number_of_working_days,
            parameters.slots,
            parameters.number_of_courses,
        ),
        vtype=GRB.BINARY,
    )
    my_model.addConstrs(
        (
            x[i, j, k] == y[i, j, k]
            for i in range(parameters.number_of_working_days)
            for j in range(parameters.slots)
            for k in range(parameters.number_of_courses)
        ),
        name="Conditional_Constraint",
    )

    for instructor in range(parameters.number_of_instructors):
        instructor_courses = parameters.instructors_Courses[instructor]
        instructor_courses = np.where(instructor_courses == 1)[0]
        for campus in range(parameters.number_of_campuses):
            current_campus_courses = np.where(parameters.course_campus == campus)[0]
            not_current_campus_courses = np.where(parameters.course_campus != campus)[0]
            current_campus_instructor_courses = list(
                np.intersect1d(instructor_courses, current_campus_courses)
            )
            current_campus_instructor_courses = np.intersect1d(
                instructor_courses, current_campus_courses
            )
            not_current_campus_instructor_courses = np.intersect1d(
                instructor_courses, not_current_campus_courses
            )

            if (
                len(current_campus_instructor_courses)
                * not_current_campus_instructor_courses.size
                > 0
            ):
                my_model.addConstrs(
                    (
                        ((y[i, j, k].item() == 1) >> (gp.quicksum(x[i, j + 1, not_current_campus_instructor_courses]) == 0))
                        for i in range(parameters.number_of_working_days)
                        for j in chain(range(3), range(4, parameters.slots - 1)) # separate breaks
                        for k in current_campus_instructor_courses
                    ),
                    name="Professor_Campus_Constraint",
                )

    return


def sec_constrs_non_overlapping_periods(my_model, schedule, parameters: classes.Params):
    classrooms = parameters.venue_types[parameters.venue_types_list[0]]
    x = schedule[:, :, :classrooms, :]
    x = x.sum(axis=2)
    x = x.sum(axis=0)

    constraint = my_model.addConstrs(
        (
            x[i, j] <= 1
            for i in range(parameters.slots)
            for j in range(parameters.number_of_courses)
        ),
        name="Sec_Constraint_Of_Non_Overlapping_Slots",
    )
    return constraint


def sec_constrs_core_courses_before_break(
    my_model, schedule, parameters: classes.Params
):
    x1 = np.where(parameters.student_course_priority == 0, 1, 0)
    x1 = np.sum(x1, axis=0)
    x1 = np.where(x1 > 0)
    x1 = x1[0]
    number_of_core_courses = len(x1)
    # x1 contains indices for core courses

    x1 = schedule[:, (parameters.slots - 1) :, :, x1]
    x1 = x1.sum(axis=2)
    x1 = x1.sum(axis=1)
    x1 = x1.sum(axis=0)

    constraint = my_model.addConstrs(
        ((x1[i] == 0) for i in range(number_of_core_courses)),
        name="Sec_Constraint_Of_Core_Courses_In_Morning",
    )
    return constraint


def sec_constrs_course_having_same_venue(
    my_model, schedule, parameters: classes.Params):
    x = schedule[:, :, : parameters.venue_types[0], :].sum(axis=1)
    x = x.sum(axis=0)
    y = my_model.addMVar(
        (parameters.venue_types[0], parameters.number_of_courses), vtype=GRB.BINARY
    )

    constraint = []
    constraint.append(
        my_model.addConstrs(
            (
                ((y[i, j].item() == 1) >> (x[i, j] ==  np.sum(parameters.course_credits[j])))
                for i in range(parameters.venue_types[0])
                for j in range(parameters.number_of_courses)
            ),
            name="Conditional Constraint_1",
        )
    )

    constraint.append(
        my_model.addConstrs(
            (
                ((y[i, j].item() == 0) >> (x[i, j] == 0))
                for i in range(parameters.venue_types[0])
                for j in range(parameters.number_of_courses)
            ),
            name="Conditional Constraint_2",
        )
    )

    return constraint


def experimental_constraint(my_model, schedule, parameters: classes.Params):
    nso_index = parameters.course_list.index("NO 101/NO 103_L")
    course_list = list(np.arange(parameters.number_of_courses))
    course_list.remove(nso_index)
    course_list = np.array(course_list)

    x1 = schedule[:, :, course_list].sum(axis=2)

    my_model.addConstrs(
        (
            (x1[i, j] >= x1[i, j + 1])
            for i in range(parameters.number_of_working_days)
            for j in range(parameters.slots - 1)
        ),
        name="Experimental Constraint",
    )

    return


def constrs_nso(my_model, schedule, parameters: classes.Params):
    # ground_index = parameters.venue_list.index("Ground")
    nso_index = parameters.course_list.index("NO 101/NO 103_L")
    # only in last slot
    # x1 = schedule[:, : parameters.slots - 1, ground_index, nso_index].sum()
    x1 = schedule[:, : parameters.slots - 1, nso_index].sum()
    my_model.addConstr(x1 == 0, name="NSO_Constraint")

    # no other course can use ground
    # course_list = list(np.arange(parameters.number_of_courses))
    # course_list.remove(nso_index)
    # course_list = np.array(course_list)
    # x2 = schedule[:, :, ground_index, course_list].sum()
    # my_model.addConstr(x2 == 0, name="NSO_Constraint")

    return


# at most 1 slot with overlapping lab and theory


def Constrs_Combined_Slots(my_model, schedule, parameters: classes.Params):
    x1 = schedule[:, :, : parameters.venue_types[0], :].sum(axis=3)
    x1 = x1.sum(axis=2)
    x2 = schedule[:, :, parameters.venue_types[0] :, :].sum(axis=3)
    x2 = x2.sum(axis=2)

    y1 = my_model.addMVar(
        (parameters.number_of_working_days, parameters.slots), vtype=GRB.BINARY
    )
    y2 = my_model.addMVar(
        (parameters.number_of_working_days, parameters.slots), vtype=GRB.BINARY
    )

    my_model.addConstrs(
        (
            ((y1[i, j].item() == 1) >> (x1[i, j] >= 1))
            for i in range(parameters.number_of_working_days)
            for j in range(parameters.slots)
        ),
        name="Conditional_Constraint",
    )

    my_model.addConstrs(
        (
            ((y1[i, j].item() == 0) >> (x1[i, j] == 0))
            for i in range(parameters.number_of_working_days)
            for j in range(parameters.slots)
        ),
        name="Conditional_Constraint",
    )

    my_model.addConstrs(
        (
            ((y2[i, j].item() == 1) >> (x2[i, j] >= 1))
            for i in range(parameters.number_of_working_days)
            for j in range(parameters.slots)
        ),
        name="Conditional_Constraint",
    )

    my_model.addConstrs(
        (
            ((y2[i, j].item() == 0) >> (x2[i, j] == 0))
            for i in range(parameters.number_of_working_days)
            for j in range(parameters.slots)
        ),
        name="Conditional_Constraint",
    )

    constraint = my_model.addConstrs(
        (
            ((y1[i] * y2[i]).sum() <= 1)
            for i in range(parameters.number_of_working_days)
        ),
        name="Combined_Slots_Constraint",
    )

    return constraint


def add_constrs(my_model, schedule, parameters):
    # constr_One_Venue_One_Course(my_model, schedule, parameters)
    print(f"\n1")

    # constrs = constr_No_course_Overlap_Student(my_model, schedule, parameters)
    constr_No_course_Overlap_Student(my_model, schedule, parameters)
    print("2")

    constr_No_course_Overlap_Professor(my_model, schedule, parameters)
    print("3")

    # constr_One_Slot_Course_Once(my_model, schedule, parameters)
    print("4")

    constr_Course_only_Once_a_day(my_model, schedule, parameters)
    print("5")

    constr_venue_setups(my_model, schedule, parameters)
    print("6")

    constr_Total_Credits_of_core_Course(my_model, schedule, parameters)
    print("7")

    # constr_Total_lab_hours_of_Course(my_model, schedule, parameters)
    print("8")

    constrs_Allowed_Lab_Time(my_model, schedule, parameters)
    print("9")

    constrs_Non_Minor_Core_Course(my_model, schedule, parameters)
    print("10")

    # constrs_Course_Campus(my_model, schedule, parameters)
    print("11")

    constrs_Student_Campus(my_model, schedule, parameters)
    print("12")

    constrs_Professor_Campus(my_model, schedule, parameters)
    print("13")

    # experimental_constraint(my_model, schedule, parameters)
    # print("14")

    # constrs_nso(my_model, schedule, parameters)
    # print("15")

    print("Primary Constraints done !!!")
    # sec_constrs = []
    # sec_constrs.append(sec_constrs_non_overlapping_periods(my_model, schedule, parameters))

    # sec_constrs.append(sec_constrs_course_having_same_venue(my_model, schedule, parameters))
    # sec_constrs_course_having_same_venue(my_model, schedule, parameters)
    # print("16")

    # sec_constrs.append(Constrs_Combined_Slots(my_model, schedule, parameters))
    # print(f"17\n")

    # # sec_constrs.append(sec_constrs_core_courses_before_break(my_model, schedule, slots, student_course_priority))
    # # print(12)
    # print("Done !")

    my_model.update()
    # my_model.tune()
    # return constrs, sec_constrs
    # constrs = []
    # return constrs
    return


def print_each_group(my_model, schedule, parameters: classes.Params):
    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    with pd.ExcelWriter(
        f"Results/Output_{parameters.number_of_working_days}.xlsx", engine="openpyxl"
    ) as writer:
        for group_i, group in enumerate(parameters.groups):
            df = pd.DataFrame(
                columns=["Day"] + [f"Slot {i}" for i in range(1, parameters.slots + 1)]
            )
            courses = list(np.where(parameters.groups_courses[group_i] == 1)[0])
            if len(courses) > 0:
                for i in range(parameters.number_of_working_days):
                    temp = {}
                    for j in range(parameters.slots):
                        temp[j] = []
                        for k in range(parameters.number_of_venues):
                            for l in courses:
                                if schedule[i, j, k, l].X == 1:
                                    temp[j].append(
                                        f"{parameters.course_list[l]} : {parameters.venue_list[k]}"
                                    )
                    dict_1 = {"Day": [f"{days[i]}"]}
                    for slot in range(parameters.slots):
                        dict_1[f"Slot {slot+1}"] = ["\n".join(temp[slot])]
                    temp_df = pd.DataFrame(dict_1)
                    df = pd.concat([df, temp_df], ignore_index=True)
            df.to_excel(writer, sheet_name=f"{group}", index=False)
        writer.save()
    return


# css_alt_rows = 'background-color: powderblue; color: black;'
# css_indexes = 'background-color: steelblue; color: white;'
#
# (df.style.apply(lambda col: np.where(col.index % 2, css_alt_rows, None)) # alternating rows
#          .applymap_index(lambda _: css_indexes, axis=0) # row indexes (pandas 1.4.0+)
#          .applymap_index(lambda _: css_indexes, axis=1) # col indexes (pandas 1.4.0+)
# ).to_excel('styled.xlsx', engine='openpyxl')

def round_off(parameters: classes.Params):
    my_list = []
    with open(f"Solutions/{parameters.number_of_working_days}.sol", "r") as f:
        my_list.extend(f.readlines())
    for index,l in enumerate(my_list):
        temp = l.split()
        if temp[0] != '#':
            temp[-1] = float(temp[-1])
            if random.random() > temp[-1]:
                temp[-1] = f"1\n"
            else:
                temp[-1] = f"0\n"
            my_list[index] = " ".join(temp)

    with open(f"Solutions/{parameters.number_of_working_days}.sol", "w") as f:
        f.writelines(my_list)    

    return


def calculate_venues(schedule, parameters: classes.Params):
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


def print_time_table(my_model, schedule, parameters: classes.Params, file, extra=""):
    # my_model.write(f"Models/{parameters.number_of_working_days}"+extra+".mps")
    print("\nYesssssss!")
    print(f"number_of_working_days : {parameters.number_of_working_days}\n")
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    printing_format = {}
    slots_utilized = 0
    unique_venues = {campus: set() for campus in parameters.campus_list}
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

    timetable = calculate_venues(schedule, parameters)

    df = pd.DataFrame(
        columns=["Day"] + [f"Slot {i}" for i in range(1, parameters.slots + 1)]
    )
    with pd.ExcelWriter(f"Results/Output_{parameters.number_of_working_days}.xlsx", engine="openpyxl") as writer:
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
                    if timetable[i, j, l] != -1:
                        slot_not_empty = True
                        k = int(timetable[i, j, l])
                            # f"{parameters.course_list[l]} : {parameters.venue_list[k]}"
                        temp[j].append(
                            f"{parameters.course_list[l]} : {parameters.venue_list[k]}"
                        )
                        unique_venues[
                            parameters.campus_list[parameters.venue_campus[k]]
                        ].add(k)
                        if l in printing_format:
                            printing_format[l].append(
                                str(days[i])
                                + str(j + 1)
                                + " ["
                                + parameters.venue_list[k]
                                + "]"
                            )
                        else:
                            printing_format[l] = [
                                str(days[i])
                                + str(j + 1)
                                + " ["
                                + parameters.venue_list[k]
                                + "]"
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
    for campus, venue_set in unique_venues.items():
        print(
            f"Campus {campus} : Venues {[parameters.venue_list[i] for i in venue_set]}\n  number of venues used : {len(venue_set)}\n"
        )
    print(f"number of slots utilized : {slots_utilized}\n")

    with open(file, "w") as f:
        for course, time in printing_format.items():
            f.write(f"{parameters.course_list[course]} : {', '.join(time)}\n")

    # print_each_group(my_model, schedule, parameters)

    # check.test(schedule, parameters)

    return
