import os
import utils
import pandas as pd
import numpy as np
import classes

violations = 0
terminal_size = os.get_terminal_size()[0]

def constr_One_Venue_One_Course(schedule, parameters: classes.Params):
    global violations
    x1 = np.sum(schedule[
        :,
        :,
        : parameters.venue_types[parameters.venue_types_list[0]],
        parameters.full_sem_courses + parameters.pre_half_sem_courses,
    ], axis=3)
    constraint_violation = False
    for i in range(parameters.number_of_working_days):
        for j in range(parameters.slots):
            for k in range(parameters.venue_types[parameters.venue_types_list[0]]):
                if x1[i, j, k] > 1:
                    constraint_violation = True
                    violations += 1

    if constraint_violation:
        print("One_Venue_One_Course_Pre_Sem Violated")
    x1 = np.sum(schedule[
        :,
        :,
        : parameters.venue_types[parameters.venue_types_list[0]],
        parameters.full_sem_courses + parameters.post_half_sem_courses,
    ], axis=3)

    for i in range(parameters.number_of_working_days):
        for j in range(parameters.slots):
            for k in range(parameters.venue_types[parameters.venue_types_list[0]]):
                if x1[i, j, k] > 1:
                    print("One_Venue_One_Course_Post_Sem Violated")
                    violations += 1

    return


def constr_No_course_Overlap_Student(schedule, parameters: classes.Params):
    global violations

    x1 = np.sum(schedule, axis=2)
    print("*" + "".center(terminal_size - 2, "-") + "*")
    print("|" + f"No_core_course_Overlap_Student Violations".center(terminal_size - 2, ) + "|")
    print("*" + "".center(terminal_size - 2, "-") + "*")

    for i in range(parameters.number_of_working_days):
        for j in range(parameters.slots):
            for index, basket in enumerate(parameters.baskets_core):
                if np.sum(x1[i, j, np.array(basket)]) > 1:
                    if parameters.basket_number_of_students_core[index] < 100:
                        print("|" + f"{parameters.course_list[basket[0]]} | {parameters.course_list[basket[1]]} : {parameters.basket_students_core[index]}".center(terminal_size-2, ) + "|")
                        violations += 1

    print("*" + "".center(terminal_size - 2, "-") + "*\n")
    return


def constr_No_course_Overlap_Professor(schedule, parameters: classes.Params):
    global violations

    x1 = np.sum(schedule, axis=2)
    # x1 = np.sum(schedule[
        # :, :, :, parameters.full_sem_courses + parameters.pre_half_sem_courses
    # ], axis=2)
    # x2 = np.sum(schedule[
    #     :, :, :, parameters.full_sem_courses + parameters.post_half_sem_courses
    # ], axis=2)

    print("*" + "".center(terminal_size - 2, "-") + "*")
    print("|" + f"No_course_Overlap_Professor_Pre_Sem Violations".center(terminal_size - 2, ) + "|")
    print("*" + "".center(terminal_size - 2, "-") + "*")

    my_list = set()

    for i in range(parameters.number_of_working_days):
        for j in range(parameters.slots):
            x1[i, j][np.where(x1[i, j] > 1)] = 1
            # x2[i, j][np.where(x2[i, j] > 1)] = 1
            for k in range(parameters.number_of_instructors):
                    if np.sum(x1[i, j] * parameters.instructors_Courses[k]) > 1:
                        actual = np.intersect1d(np.where(x1[i, j] == 1), np.where(parameters.instructors_Courses[k] == 1))
                        actual = [parameters.course_list[t] for t in actual]
                        actual = ",".join(actual)
                        my_list.add("|" + f" {days[i]} {j} {parameters.instructor_list[k]} -> {actual}".center(terminal_size - 2, ) + "|")
                        violations += 1

    print("".join(my_list))
    print("*" + "".center(terminal_size - 2, "-") + "*\n")

    return


def constr_One_Slot_Course_Once(schedule, parameters: classes.Params):
    global violations
    x1 = np.sum(schedule, axis=2)

    # print("*" + "".center(terminal_size - 2, "-") + "*")
    # print("|" + f"One_Slot_Course_Once Violations".center(terminal_size - 2, ) + "|")
    # print("*" + "".center(terminal_size - 2, "-") + "*")

    for i in range(parameters.number_of_working_days):
        for j in range(parameters.slots):
            for k in range(parameters.number_of_courses):
                if x1[i, j, k] > 1:
                    violations += 1

    # print("*" + "".center(terminal_size - 2, "-") + "*\n")

    return


def constr_Course_only_Once_a_day(schedule, parameters: classes.Params):
    global violations
    x1 = np.sum(schedule[:, :, : parameters.venue_types[parameters.venue_types_list[0]], :], axis=2)
    for i in range(parameters.number_of_working_days):
        for j in range(parameters.slots):
            x1[i, j][np.where(x1[i, j] > 1)[0]] = 1
    x2 = np.sum(x1, axis=1)

    print("*" + "".center(terminal_size - 2, "-") + "*")
    print("|" + f"Course_only_Once_a_day_0 Violations".center(terminal_size - 2, ) + "|")
    print("*" + "".center(terminal_size - 2, "-") + "*")

    for i in range(parameters.number_of_working_days):
        for j in range(parameters.number_of_courses):
            if x2[i, j] > 1:
                print("|" + f"{days[i]} -> {parameters.course_list[j]}".center(terminal_size - 2, ) + "|")
                violations += 1

    print("*" + "".center(terminal_size - 2, "-") + "*\n")

    x1 = np.sum(schedule[:, :, parameters.venue_types[parameters.venue_types_list[0]] : , :], axis=2)
    for i in range(parameters.number_of_working_days):
        for j in range(parameters.slots):
            x1[i, j][np.where(x1[i, j] > 1)[0]] = 1
    x2 = np.sum(x1, axis=1)

    print("*" + "".center(terminal_size - 2, "-") + "*")
    print("|" + f"Course_only_Once_a_day_1 Violations".center(terminal_size - 2, ) + "|")
    print("*" + "".center(terminal_size - 2, "-") + "*")

    for i in range(parameters.number_of_working_days):
        for j in range(parameters.number_of_courses):
            if (x2[i, j] > (parameters.course_credits[j, -2] + 1)):
                print("|" + f"{days[i]} -> {parameters.course_list[j]}".center(terminal_size - 2, ) + "|")
                violations += 1
    
    print("*" + "".center(terminal_size - 2, "-") + "*\n")
    return


def constr_venue_setups(schedule, parameters: classes.Params):
    global violations
    x1 = np.sum(schedule, axis=1)
    x1 = np.sum(x1, axis=0)

    print("*" + "".center(terminal_size - 2, "-") + "*")
    print("|" + f"venue_setups Violations".center(terminal_size - 2, ) + "|")
    print("*" + "".center(terminal_size - 2, "-") + "*")

    for i in range(parameters.number_of_venues):
        for j in range(parameters.number_of_courses):
            if (parameters.course_strength[j] > parameters.venue_setups[i] * parameters.course_lab[j][0]):
                if (x1[i, j] != 0):
                    print("|" + f"{parameters.venue_list[i]} [{parameters.venue_setups[i] * parameters.course_lab[j][0]}] -> {parameters.course_list[j]} [{parameters.course_strength[j]}]".center(terminal_size - 2) + "|")
                    violations += 1
    print("*" + "".center(terminal_size - 2, "-") + "*\n")
    return


def constr_Total_Credits_of_core_Course(schedule, parameters: classes.Params):
    global violations
    x1 = np.sum(schedule, axis=2)
    x2 = np.sum(x1, axis=1)
    x2 = np.sum(x2, axis=0)

    print("*" + "".center(terminal_size - 2, "-") + "*")
    print("|" + f"Total_Credits_of_core_Course Violations".center(terminal_size - 2, ) + "|")
    print("*" + "".center(terminal_size - 2, "-") + "*")

    for i in range(parameters.number_of_courses):
        if (x2[i] < parameters.course_credits[i, -1]) and x2[i] != 0:
            print("|" + f"{parameters.course_list[i]} -> {x2[i]} < {parameters.course_credits[i, -1]}".center(terminal_size - 2,) + "|")
            violations += 1

    print("*" + "".center(terminal_size - 2, "-") + "*\n")
    return


def constr_Total_lab_hours_of_Course(schedule, parameters: classes.Params):
    global violations
    my_sum = parameters.venue_types[parameters.venue_types_list[0]]

    print("*" + "".center(terminal_size - 2, "-") + "*")
    print("|" + f"Total_lab_hours_of_Course Violations".center(terminal_size - 2, ) + "|")
    print("*" + "".center(terminal_size - 2, "-") + "*")

    lab_req = []
    illegal_req = []

    for lab in parameters.lab_types_list:
        x1 = schedule[:, :, my_sum : my_sum + parameters.venue_types[lab], :]
        my_sum += parameters.venue_types[lab]
        x2 = np.sum(x1, axis=2)
        x2 = np.sum(x2, axis=1)
        x2 = np.sum(x2, axis=0)
        for i in range(parameters.number_of_courses):
            if parameters.course_lab[i][1] == lab:
                if (x2[i] < parameters.course_credits[i, -2]):
                    lab_req.append("|" + f"{parameters.course_list[i]} -> {x2[i]} < {parameters.course_credits[i, -2]}".center(terminal_size - 2,) + "|")
                    violations += 1
            else:
                if (x2[i] != 0):
                    illegal_req.append("|" + f"{parameters.course_list[i]} -> {x2[i]} != 0".center(terminal_size - 2,) + "|")
                    violations += 1
    
    print("".join(lab_req), end="")
    print("".join(illegal_req), end="")
    print("*" + "".center(terminal_size - 2, "-") + "*\n")

    return


def constrs_Non_Minor_Core_Course(schedule, parameters: classes.Params):
    global violations
    x1 = np.sum(schedule, axis=2)
    for _, k1 in np.ndenumerate(np.where(parameters.non_minor_core_course == 1)[0]):
        for _, k2 in np.ndenumerate(np.where(parameters.non_minor_core_course == 2)[0]):
            for i in range(parameters.number_of_working_days):
                for j in range(parameters.slots):
                    if (x1[i, j, k1] + x1[i, j, k2] > 1):
                        print("Non_Minor_Core_Course Violated")
                        violations += 1

    return


def constrs_Course_Campus(schedule, parameters: classes.Params):
    global violations
    x = np.sum(schedule, axis=1)
    x = np.sum(x, axis=0)

    print("*" + "".center(terminal_size - 2, "-") + "*")
    print("|" + f"Campus_Constraint Violations".center(terminal_size - 2, ) + "|")
    print("*" + "".center(terminal_size - 2, "-") + "*")

    for i in range(parameters.number_of_venues):
        for j in range(parameters.number_of_courses):
            if parameters.venue_campus[i] != parameters.course_campus[j]:
                if (x[i, j] != 0):
                    print("|" + f"{parameters.course_list[j]} [{parameters.campus_list[parameters.course_campus[j]]}] -> [{parameters.campus_list[parameters.venue_campus[i]]}]".center(terminal_size - 2,) + "|")
                    violations += 1

    print("*" + "".center(terminal_size - 2, "-") + "*\n")

    return


def constrs_Student_Campus(schedule, parameters: classes.Params):
    global violations
    x = np.sum(schedule, axis=2)
    x[np.where(x > 1)[0]] = 0

    print("*" + "".center(terminal_size - 2, "-") + "*")
    print("|" + f"Student_Campus_Constraint Violations".center(terminal_size - 2, ) + "|")
    print("*" + "".center(terminal_size - 2, "-") + "*")

    viol_dict = {}

    for student in range(parameters.number_of_students):
        student_courses = parameters.student_course_priority[student]
        student_courses = np.where(student_courses != -1)[0]
        for campus in range(parameters.number_of_campuses):
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

            if (len(current_campus_student_courses) * not_current_campus_student_courses.size > 0):
                    for i in range(parameters.number_of_working_days):
                        for j in range(parameters.slots - 1):
                            for k in current_campus_student_courses:
                                if (x[i, j, k] == 1):
                                    if (np.sum(x[i, j + 1, not_current_campus_student_courses]) != 0):
                                        actual = np.intersect1d(np.where(x[i, j + 1, : ] == 1)[0], not_current_campus_student_courses)
                                        strings = []
                                        for course in actual:
                                            strings.append(f"{parameters.course_list[course]} [{parameters.campus_list[parameters.course_campus[course]]}]")
                                        strings = ",".join(strings)
                                        temp = f"{days[i]} {j} {parameters.course_list[k]} [{parameters.campus_list[parameters.course_campus[k]]}] -> {strings}"
                                        if temp in viol_dict:
                                            viol_dict[temp].append(parameters.student_list[student])
                                        else:
                                            viol_dict[temp] = [parameters.student_list[student]]
                                        violations += 1

    for key,value in viol_dict.items():
        if len(value) < 10:
            print("|" + f"{key} : {value}".center(terminal_size - 2,) + "|")
    print("*" + "".center(terminal_size - 2, "-") + "*\n")
    return


def constrs_Professor_Campus(schedule, parameters: classes.Params):
    global violations
    x = np.sum(schedule, axis=2)

    print("*" + "".center(terminal_size - 2, "-") + "*")
    print("|" + f"Professor_Campus_Constraint Violations".center(terminal_size - 2, ) + "|")
    print("*" + "".center(terminal_size - 2, "-") + "*")

    viol_dict = {}

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

            if (len(current_campus_instructor_courses) * not_current_campus_instructor_courses.size > 0):
                for i in range(parameters.number_of_working_days):
                    for j in range(parameters.slots - 1):
                        for k in current_campus_instructor_courses:
                            if (x[i, j, k] == 1):
                                if (np.sum(x[i, j + 1, not_current_campus_instructor_courses]) != 0):
                                    actual = np.intersect1d(np.where(x[i, j + 1, : ] == 1)[0], not_current_campus_instructor_courses)
                                    strings = []
                                    for course in actual:
                                        strings.append(f"{parameters.course_list[course]} [{parameters.campus_list[parameters.course_campus[course]]}]")
                                    strings = ",".join(strings)
                                    temp = f"{days[i]} {j} {parameters.course_list[k]} [{parameters.campus_list[parameters.course_campus[k]]}] -> {strings}"
                                    if temp in viol_dict:
                                        viol_dict[temp] += 1
                                    else:
                                        viol_dict[temp] = 1
                                    violations += 1
                                    violations += 1

    for key,value in viol_dict.items():
        print("|" + f"{key} : {value}".center(terminal_size - 2,) + "|")
    print("*" + "".center(terminal_size - 2, "-") + "*\n")

    return


def constrs_nso(schedule, parameters: classes.Params):
    global violations
    ground_index = parameters.venue_list.index("Ground")
    nso_index = parameters.course_list.index("NO101/NO103")
    # only in last slot
    x1 = np.sum(schedule[:, : parameters.slots - 1, ground_index, nso_index])
    if x1 != 0:
        print("NSO_Constraint 1 Violated")
        violations += 1

    # no other course can use ground
    course_list = list(np.arange(parameters.number_of_courses))
    course_list.remove(nso_index)
    course_list = np.array(course_list)
    x2 = np.sum(schedule[:, :, ground_index, course_list])
    if x2 != 0:
        print("NSO_Constraint Violated")
        violations += 1

    return


def sec_constrs_course_having_same_venue(schedule, parameters: classes.Params):
    global violations
    x = np.sum(schedule[:, :, : parameters.venue_types[0], :], axis=1)
    x = np.sum(x, axis=0)

    y = x.T

    print("*" + "".center(terminal_size - 2, "-") + "*")
    print("|" + f"Same Venue Constraint Violations".center(terminal_size - 2, ) + "|")
    print("*" + "".center(terminal_size - 2, "-") + "*")

    for index,course in enumerate(y):
        if np.where(course > 0)[0].size > 1:
            actual = np.where(course > 0)[0]
            actual = ",".join([parameters.venue_list[venue] for venue in actual])
            print("|" + f"{parameters.course_list[index]} -> {actual}".center(terminal_size - 2,) + "|")
            violations += 1

    print("*" + "".center(terminal_size - 2, "-") + "*\n")

    return


def experimental_constraint(schedule, parameters: classes.Params):
    global violations
    nso_index = parameters.course_list.index("NO101/NO103")
    course_list = list(np.arange(parameters.number_of_courses))
    course_list.remove(nso_index)
    course_list = np.array(course_list)

    x1 = schedule[:, :, : parameters.venue_types[0], course_list].sum(axis=3)
    x1 = x1.sum(axis=2)
    for i in range(parameters.number_of_working_days):
        for j in range(parameters.slots - 1):
            if (x1[i, j] < x1[i, j + 1]):
                print("Experimental Constraint Violated")
                violations += 1

    return


def test_each_constraint(schedule, parameters):
    constr_One_Venue_One_Course(schedule, parameters)

    constr_No_course_Overlap_Student(schedule, parameters)

    constr_No_course_Overlap_Professor(schedule, parameters)

    constr_One_Slot_Course_Once(schedule, parameters)

    constr_Course_only_Once_a_day(schedule, parameters)

    constr_venue_setups(schedule, parameters)

    constr_Total_Credits_of_core_Course(schedule, parameters)

    constr_Total_lab_hours_of_Course(schedule, parameters)

    constrs_Non_Minor_Core_Course(schedule, parameters)

    constrs_Course_Campus(schedule, parameters)

    constrs_Student_Campus(schedule, parameters)

    constrs_Professor_Campus(schedule, parameters)

    # experimental_constraint(schedule, parameters)
    # print("14")

    # constrs_nso(schedule, parameters)
    # print("15")

    sec_constrs_course_having_same_venue(schedule, parameters)
    # print("16")

    return


if __name__ == "__main__":
    parameters = utils.initialize_parameters("Data/Latest_Data.xlsx")
    parameters.number_of_working_days = 5
    parameters.slots = 8
    df = pd.read_excel("Data/notes.xlsx", "Sheet1")

    timetable = np.zeros((parameters.number_of_working_days, parameters.slots, parameters.number_of_venues, parameters.number_of_courses))
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']

    for value in df.iterrows():
        value = value[1]
        day_index = days.index(value[0])
        course_index = parameters.course_list.index(value[1])
        my_slot = int(value[2])
        venue_index = parameters.venue_list.index(value[4])
        timetable[day_index][my_slot][venue_index][course_index] = 1

    test_each_constraint(timetable, parameters)
    print(f"Total observed violations are : {violations}")