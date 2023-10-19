import pandas as pd
import gurobipy as gp
import numpy as np
from gurobipy import GRB
import pandas, math
import classes_exam


def read_input_excel(file):
    second_file = "-test"
    courses = pandas.read_excel(file, "Courses" + second_file)
    columns = courses.columns
    courses_dict = {}
    student_dict = {}
    instructor_dict = {}
    venue_dict = {}
    splitted_courses_campus = []
    for value in courses.iterrows():
        value = value[1]
        if value[columns[14]] == 0:
            continue

        temp_campus = value[columns[9]].strip().split("\n")
        code = value[columns[0]].strip()
        L = int(value[columns[3]]) if not math.isnan(value[columns[3]]) else 0
        T = int(value[columns[4]]) if not math.isnan(value[columns[4]]) else 0
        P = int(value[columns[5]]) if not math.isnan(value[columns[5]]) else 0

        if len(temp_campus) > 1:
            splitted_courses_campus.append(code)
            temp_campus = {
                i.split(":")[0].strip(): i.split(":")[1].strip() for i in temp_campus
            }

            for ltp in temp_campus:
                value[columns[0]] = code + "_" + ltp
                if ltp == "L":
                    value[columns[3]] = L
                    value[columns[4]] = T
                    value[columns[5]] = 0
                else:
                    value[columns[3]] = 0
                    value[columns[4]] = 0
                    value[columns[5]] = P

                new_course = classes_exam.Course(value, columns, temp_campus[ltp])
                courses_dict[new_course.code] = new_course
                instructors = [i.strip() for i in value[columns[2]].split("\n")]
                TAs = (
                    [i.strip() for i in value[columns[12]].split("\n")]
                    if isinstance(value[columns[12]], str)
                    else []
                )

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
                        courses_dict[value[columns[0]].strip()], 0
                    )
                    new_course.add_TA(student_dict[i])
        else:
            new_course = classes_exam.Course(value, columns, temp_campus[0])
            courses_dict[new_course.code] = new_course
            instructors = [i.strip() for i in value[columns[2]].split("\n")]
            TAs = (
                [i.strip() for i in value[columns[12]].split("\n")]
                if isinstance(value[columns[12]], str)
                else []
            )

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
                student_dict[i].add_course(courses_dict[value[columns[0]].strip()], 0)
                new_course.add_TA(student_dict[i])

    registrations = pandas.read_excel(file, "Registrations" + second_file)
    columns = registrations.columns

    for value in registrations.iterrows():
        value = value[1]
        value[columns[1]] = str(value[columns[1]])
        if value[columns[1]] not in student_dict:
            new_student = classes_exam.Student(value[columns[1]])
            student_dict[new_student.rollnumber] = new_student
            # del current_student

        if value[columns[0]].strip() in splitted_courses_campus:
            student_dict[value[columns[1]]].add_course(
                courses_dict[value[columns[0]].strip() + "_L"], int(value[columns[3]])
            )
            student_dict[value[columns[1]]].add_course(
                courses_dict[value[columns[0]].strip() + "_P"], int(value[columns[3]])
            )
            courses_dict[value[columns[0]].strip() + "_L"].add_student(
                student_dict[value[columns[1]]], int(value[columns[3]])
            )
            courses_dict[value[columns[0]].strip() + "_P"].add_student(
                student_dict[value[columns[1]]], int(value[columns[3]])
            )

            if (int(value[columns[3]]) == 0) and (
                value[columns[4]]
                not in courses_dict[value[columns[0]].strip() + "_L"].groups
            ):
                courses_dict[value[columns[0]].strip() + "_L"].groups.append(
                    value[columns[4]]
                )
            if (int(value[columns[3]]) == 0) and (
                value[columns[4]]
                not in courses_dict[value[columns[0]].strip() + "_P"].groups
            ):
                courses_dict[value[columns[0]].strip() + "_P"].groups.append(
                    value[columns[4]]
                )
        else:
            if value[columns[0]].strip() in courses_dict:
                student_dict[value[columns[1]]].add_course(
                    courses_dict[value[columns[0]].strip()], int(value[columns[3]])
                )
                courses_dict[value[columns[0]].strip()].add_student(
                    student_dict[value[columns[1]]], int(value[columns[3]])
                )

                if (int(value[columns[3]]) == 0) and (
                    value[columns[4]]
                    not in courses_dict[value[columns[0]].strip()].groups
                ):
                    courses_dict[value[columns[0]].strip()].groups.append(
                        value[columns[4]]
                    )

    venues = pandas.read_excel(file, "Venues" + second_file)
    columns = venues.columns

    for value in venues.iterrows():
        value = value[1]
        current_venue = classes_exam.Venue(value, columns)
        venue_dict[str(value[columns[0]]).strip()] = current_venue
        # del current_venue

    return courses_dict, student_dict, instructor_dict, venue_dict


def lecture_splitting(
    courses_dict, campus_list, venue_campus, venue_types, venue_setups
):
    with open("Results/Course_Rollnumbers.txt", "w") as file:
        pass

    temp_values = [value for value in courses_dict.values()]
    splitted_courses = []
    for course in temp_values:
        splitting = True
        strength_factor = math.ceil(
            course.get_strength() / 10
        )

        if splitting and (course.L + course.T) > 0:
            temp_split = []
            new_strength = math.ceil(course.get_strength() / strength_factor)
            temp_students_list = set(
                sorted(course.students.keys(), key=lambda x: x.rollnumber)
            )
            tas = set(course.TAs)
            temp_students_list = list(temp_students_list - tas)
            tas = list(tas)

            new_strength -= len(tas)

            for i in range(strength_factor):
                new_course = course.copy()
                new_course.code = new_course.code + "_" + str(i+1) + "/" + str(strength_factor)
                new_course.P = 0

                temp_split.append(new_course.code)

                new_course.students = {
                    j: course.students[j]
                    for j in temp_students_list[
                        new_strength * i : new_strength * i + new_strength
                    ]
                    + tas
                }
                courses_dict[new_course.code] = new_course

                with open("Results/Course_Rollnumbers.txt", "a") as file:
                    file.write(f"\n{new_course.code} : { {i.rollnumber:priority for i,priority in new_course.students.items()} }\n")

                for student, priority in new_course.students.items():
                    student.add_course(new_course, priority)

                for instructor in new_course.instructors:
                    instructor.add_course(new_course)
            course.L = 0
            course.T = 0
            if course.P == 0:
                for student in course.students:
                    del student.courses[course]
                for instructor in course.instructors:
                    instructor.courses.remove(course)
                del courses_dict[course.code]
            
            splitted_courses.append(temp_split)

    del temp_values, tas
    return splitted_courses


def make_baskets(parameters: classes_exam.Params):
    # least_priority = int(np.max(parameters.student_course_priority))
    least_priority = 1

    parameters.baskets_core = []
    parameters.baskets_elective = []
    temp = []
    parameters.basket_number_of_students = []
    parameters.basket_number_of_students_core = []

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
                temp = [courses_core_1[i], courses_core_1[j]]
                if temp not in parameters.baskets_core:
                    parameters.baskets_core.append(temp)
                    parameters.basket_number_of_students_core.append(1)

        for i in range(len(courses_core_2)):
            for j in range(i + 1, len(courses_core_2)):
                temp = [courses_core_2[i], courses_core_2[j]]
                if temp not in parameters.baskets_core:
                    parameters.baskets_core.append(temp)
                    parameters.basket_number_of_students_core.append(1)

        for i in range(len(courses_elective_1)):
            for j in range(i + 1, len(courses_elective_1)):
                temp = [courses_elective_1[i], courses_elective_1[j]]
                if temp not in parameters.baskets_elective + parameters.baskets_core:
                    parameters.baskets_elective.append(temp)
                    parameters.basket_number_of_students.append(1)
                else:
                    if temp in parameters.baskets_elective:
                        parameters.basket_number_of_students[
                            parameters.baskets_elective.index(temp)
                        ] += 1

        for i in range(len(courses_elective_2)):
            for j in range(i + 1, len(courses_elective_2)):
                temp = [courses_elective_2[i], courses_elective_2[j]]
                if temp not in parameters.baskets_elective + parameters.baskets_core:
                    parameters.baskets_elective.append(temp)
                    parameters.basket_number_of_students.append(1)
                else:
                    if temp in parameters.baskets_elective:
                        parameters.basket_number_of_students[
                            parameters.baskets_elective.index(temp)
                        ] += 1

    with open("Results/baskets.txt", "w") as f:
        f.write(f"Core Courses:\n\n")
        for i, (x, y) in enumerate(parameters.baskets_core):
            f.write(f"{parameters.course_list[x],parameters.course_list[y]}\n")
        f.write(f"\nElective Courses:\n\n")
        for i, (x, y) in enumerate(parameters.baskets_elective):
            f.write(
                f"{parameters.course_list[x],parameters.course_list[y]} : {parameters.basket_number_of_students[i]}\n"
            )
    return


def initialize_parameters(file_name):
    courses_dict, student_dict, instructor_dict, venue_dict = read_input_excel(
        file_name
    )
    number_of_students = len(student_dict)
    number_of_instructors = len(instructor_dict)
    number_of_venues = len(venue_dict)
    number_of_working_days = 5
    slots = 2
    venue_types = {}
    venue_type_campus = {}
    campus_list = sorted(set([i.campus_type for i in venue_dict.values()]))
    number_of_campuses = len(campus_list)

    for _, venue in venue_dict.items():
        temp1 = venue.type
        temp2 = venue.campus_type
        if temp1 in venue_types:
            venue_types[temp1] += 1
        else:
            venue_types[temp1] = 1

        if temp1 not in venue_type_campus:
            venue_type_campus[temp1] = {i: 0 for i in range(number_of_campuses)}

        venue_type_campus[temp1][campus_list.index(temp2)] += 1

    venue_types_list = list(sorted(venue_types.keys()))
    lab_types_list = venue_types_list[1:]
    student_list = list(sorted(student_dict.keys()))
    instructor_list = list(sorted(instructor_dict.keys()))
    venue_list = list(
        sorted(
            venue_dict.keys(),
            key=lambda x: (venue_dict[x].type, venue_dict[x].campus_type),
        )
    )
    venue_setups = np.array([[venue_dict[i].seater_1, venue_dict[i].seater_2, venue_dict[i].seater_3, venue_dict[i].number_of_setups] for i in venue_list])
    venue_campus = np.array(
        [campus_list.index(venue_dict[i].campus_type) for i in venue_list]
    )

    splitted_courses = lecture_splitting(
        courses_dict, campus_list, venue_campus, venue_types, venue_setups
    )

    course_list = list(sorted(courses_dict.keys()))
    course_campus = np.array(
        [campus_list.index(courses_dict[i].campus_type) for i in course_list]
    )
    number_of_courses = len(courses_dict)
    course_lab = np.zeros((number_of_courses, 2))
    students_Courses = np.zeros((number_of_students, number_of_courses))
    instructors_Courses = np.zeros((number_of_instructors, number_of_courses))
    course_credits = np.zeros((number_of_courses, 3))
    student_course_priority = np.zeros((number_of_students, number_of_courses)) - 1
    non_minor_core_course = np.zeros((number_of_students, number_of_courses))
    full_sem_courses = []
    pre_half_sem_courses = []
    post_half_sem_courses = []

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
        course_lab[i][0] = courses_dict[j].group_size
        course_lab[i][1] = courses_dict[j].lab_type

        L, T, P = courses_dict[j].get_LTP()
        course_credits[i][0] = L
        course_credits[i][1] = T
        course_credits[i][2] = P
        # course_credits[i][2] = 0

        if courses_dict[j].minor:
            non_minor_core_course[i] = 2

        if course_strength[i] == 0:
            course_credits[i][0] = 0
            course_credits[i][1] = 0
            course_credits[i][2] = 0

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

    course_credits = np.c_[course_credits, np.sum(course_credits, axis=1)]

    splitted_courses = [ np.array([course_list.index(sub_course) for sub_course in course]) for course in splitted_courses ]

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
    parameters.venue_types_list = venue_types_list
    parameters.lab_types_list = lab_types_list
    parameters.course_lab = course_lab
    parameters.student_course_priority = student_course_priority
    parameters.non_minor_core_course = non_minor_core_course
    parameters.venue_type_campus = venue_type_campus
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

    return parameters


def initialize_model(parameters: classes_exam.Params):
    my_model = gp.Model("Timetable")
    my_model.Params.LogFile = "m.log"
    # my_model.setParam("LogToConsole", 0)
    my_model.Params.Threads = 1
    my_model.Params.TimeLimit = float("infinity")

    schedule = my_model.addMVar(
        (
            parameters.number_of_working_days,
            parameters.slots,
            parameters.number_of_venues,
            parameters.number_of_courses,
        ),
        vtype=GRB.BINARY,
        name="time",
    )
    return my_model, schedule


def constr_No_course_Overlap_Student(my_model, schedule, parameters: classes_exam.Params):
    x1 = schedule.sum(axis=2)

    for i in range(parameters.number_of_working_days):
        for j in range(parameters.slots):
            for basket in parameters.baskets_core:
                my_model.addConstr(
                    x1[i, j, np.array(basket)].sum() <= 1,
                    name="No_core_course_Overlap_Student",
                )

    return


def constr_Total_Credits_of_core_Course(my_model, schedule, parameters: classes_exam.Params):

    x1 = schedule.sum(axis=2)
    x2 = x1.sum(axis=1)
    x2 = x2.sum(axis=0)
    my_model.addConstrs(
        (
            (x2[i] == parameters.course_credits[i, -1])
            for i in range(parameters.number_of_courses)
        ),
        name="Total_Credits_of_core_Course",
    )
    return


def constr_venue_setups(my_model, schedule, parameters: classes_exam.Params):
    x1 = schedule.sum(axis=1)
    x1 = x1.sum(axis=0)

    y = my_model.addMVar(
            (
                parameters.number_of_working_days,
                parameters.slots,
                parameters.number_of_venues,
            ),
            vtype=GRB.BINARY,
        )
    
    for i in range(parameters.number_of_working_days):
        for j in range(parameters.slots):
            for k in range(parameters.number_of_venues):
                my_model.addConstr(
                    ((y[i, j, k].item() == 1) >> (schedule[i, j, k].sum() >= 1)),
                    name = "Conditional_Constraint_Sum_1"
                )

                my_model.addConstr(
                    ((y[i, j, k].item() == 0) >> (schedule[i, j, k].sum() == 0)),
                    name = "Conditional_Constraint_Sum_1"
                )

                my_model.addConstr(
                    (
                        (y[i, j, k].item() == 1) >>
                    ((parameters.venue_setups[k][0] + parameters.venue_setups[k][1] + 2*parameters.venue_setups[k][2]) >= (parameters.course_strength*schedule[i, j, k]).sum())
                    ),
                    name = "Venue_Setups"
                )

                for course in parameters.splitted_courses:
                    my_model.addConstr(
                        (
                            (y[i, j, k].item() == 1) >>
                        ((parameters.venue_setups[k][0] // 2 + parameters.venue_setups[k][1] + parameters.venue_setups[k][2]) >= (parameters.course_strength[course]*schedule[i, j, k, course]).sum())
                        ),
                        name = "Venue_Setups"
                    )
    return


def constrs_Course_Campus(my_model, schedule, parameters: classes_exam.Params):
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


def constr_One_Day_One_Exam(my_model, schedule, parameters: classes_exam.Params):

    x = schedule.sum(axis=2)
    x = x.sum(axis=1)
    # for student in range(parameters.number_of_students):
    for student in parameters.allowed_students:
        my_model.addConstrs(
            ( (x[i, np.where(parameters.student_course_priority[student] == 0)[0]].sum() <= 1)
            for i in range(parameters.number_of_working_days)
            if np.where(parameters.student_course_priority[student] == 0)[0].size > 0),
            name = "One_Day_One_Exam_Constraint"
        )
    return


def constr_All_sub_Courses_In_One_Slot(my_model, schedule, parameters: classes_exam.Params):
    x = schedule.sum(axis=2)
    y = my_model.addMVar(
        (
            parameters.number_of_working_days,
            parameters.slots,
            len(parameters.splitted_courses)
        ),
        vtype=GRB.BINARY,
    )

    for i in range(parameters.number_of_working_days):
        for j in range(parameters.slots):
            for k, course in enumerate(parameters.splitted_courses):
                my_model.addConstr(
                    ((y[i, j, k].item() == 1) >> (x[i, j, course].sum() == len(course)) ),
                    name="All_Sub_Course_In_One_Slot"
                )

                my_model.addConstr(
                    ((y[i, j, k].item() == 0) >> (x[i, j, course].sum() == 0)),
                    name="All_Sub_Course_In_One_Slot"
                )


def add_constrs(my_model, schedule, parameters):

    constr_All_sub_Courses_In_One_Slot(my_model, schedule, parameters)

    constr_No_course_Overlap_Student(my_model, schedule, parameters)

    constr_venue_setups(my_model, schedule, parameters)

    constr_Total_Credits_of_core_Course(my_model, schedule, parameters)

    constrs_Course_Campus(my_model, schedule, parameters)

    # constr_One_Day_One_Exam(my_model, schedule, parameters)

    print("Primary Constraints done !!!")

    my_model.update()
    return


def print_time_table(my_model, schedule, parameters: classes_exam.Params, file, extra=""):
    print(f"number_of_working_days : {parameters.number_of_working_days}\n")
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    printing_format = {}
    slots_utilized = 0
    unique_venues = {campus: set() for campus in parameters.campus_list}
    try:
        schedule[0, 0, 0, 0].X
    except:
        try:
            my_model.Params.SolutionNumber = 1
        except:
            print("No optimized solution found!")
            return
        
    with pd.ExcelWriter(f"Results/Exam_Output_{parameters.number_of_working_days}.xlsx", engine="openpyxl") as writer:
        df = pd.DataFrame(
            columns=["Day"] + [f"Slot {i}" for i in range(1, parameters.slots + 1)]
        )
        for i in range(parameters.number_of_working_days):
            temp = {}
            for j in range(parameters.slots):
                # number_of_venues-number_of_labs,
                temp[j] = []
                slot_not_empty = False
                for k in range(parameters.number_of_venues):
                    for l in range(parameters.number_of_courses):
                        # if my_model.getVarByName('time[%d,%d,%d,%d]' % (i, j, k, l)).X == 1:
                        if schedule[i, j, k, l].X == 1:
                            slot_not_empty = True

                            temp[j].append(
                                f"{parameters.course_list[l]} : {parameters.venue_list[k]} Strength : {parameters.course_strength[l]}"
                            )
                            unique_venues[
                                parameters.campus_list[parameters.venue_campus[k]]
                            ].add(k)
                            if l in printing_format:
                                printing_format[l].append(
                                    f"{days[i]}{j + 1} {[parameters.venue_list[k]]} Strength : {parameters.course_strength[l]}"
                                )
                            else:
                                printing_format[l] = [
                                    f"{days[i]}{j + 1} {[parameters.venue_list[k]]} Strength : {parameters.course_strength[l]}"
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

    for campus, venue_set in unique_venues.items():
        print(
            f"Campus {campus} : Venues {[parameters.venue_list[i] for i in venue_set]}\n  number of venues used : {len(venue_set)}\n"
        )
    print(f"number of slots utilized : {slots_utilized}\n")

    values = schedule.X
    values = np.sum(values, axis=2)
    values = np.sum(values, axis=1)
    count = 0
    for student in range(parameters.number_of_students):
        temp = np.sum(values[:, np.where(parameters.student_course_priority[student] == 0)[0]], axis=1)
        for i in range(parameters.number_of_working_days):
            if temp[i] > 1:
                count += 1

    print(count)

    with open(file, "w") as f:
        for course, time in printing_format.items():
            f.write(f"{parameters.course_list[course]} : {', '.join(time)}\n")

    return
