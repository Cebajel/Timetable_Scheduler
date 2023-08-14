import numpy as np

# number_of_labs,

# schedule, number_of_working_days, slots, number_of_venues,
#                         number_of_students, instructors_Courses, number_of_instructors, number_of_courses, course_credits,
#                         venue_setups, course_strength, full_sem_courses, pre_half_sem_courses, post_half_sem_courses,
#                         venue_types, venue_types_list, lab_types_list, course_lab, student_course_priority

def test(schedule, number_of_working_days, slots, number_of_venues, number_of_students, 
                    instructors_Courses, number_of_instructors, number_of_courses, course_credits,
                    venue_setups, course_strength, full_sem_courses, pre_half_sem_courses, post_half_sem_courses,
                    venue_types, venue_types_list, lab_types_list, course_lab, student_course_priority, non_minor_core_course):
    tick = True
    number_of_labs = number_of_venues - venue_types[venue_types_list[0]]
    values = np.rint(schedule.X)
    x1 = np.sum(values[:, :, :venue_types[venue_types_list[0]], full_sem_courses + pre_half_sem_courses], axis=3)
    for i in range(number_of_working_days):
        for j in range(slots):
            for k in range(venue_types[venue_types_list[0]]):
                if not x1[i, j, k] <= 1:
                    print("Model failed at One_Venue_One_Course_Pre_Sem")
                    print(f"values are: {(i, j, k)} and {x1[i, j, k]} ")
                    tick = False
    
    x1 = np.sum(values[:, :, :venue_types[venue_types_list[0]], full_sem_courses + post_half_sem_courses], axis=3)
    for i in range(number_of_working_days):
        for j in range(slots):
            for k in range(venue_types[venue_types_list[0]]):
                if not x1[i, j, k] <= 1:
                    print("Model failed at One_Venue_One_Course_Post_Sem")
                    print("values are: ", (i, j, k))
                    tick = False

    x1 = np.sum(values, axis=2)

    # for i in range(number_of_working_days):
    #     for j in range(slots):
    #         for k in range(number_of_students):
    #             if len(np.intersect1d(full_sem_courses + pre_half_sem_courses, np.where(core_courses[k] != 0))) != 0:
    #                 if not np.sum(x1[i, j, np.intersect1d(full_sem_courses + pre_half_sem_courses, np.where(core_courses[k] != 0))]) <= 1:
    #                     print("Model failed at No_course_Overlap_Student_Pre_Sem")
    #                     print("values are: ", (i, j, k))
    #                     tick = False

    # for i in range(number_of_working_days):
    #     for j in range(slots):
    #         for k in range(number_of_students):
    #             if len(np.intersect1d(full_sem_courses + post_half_sem_courses, np.where(core_courses[k] != 0))) != 0:
    #                 if not np.sum(x1[i, j, np.intersect1d(full_sem_courses + post_half_sem_courses, np.where(core_courses[k] == 1))]) <= 1:
    #                     print("Model failed at No_course_Overlap_Student_Post_Sem")
    #                     print("values are: ", (i, j, k))
    #                     tick = False

    for i in range(number_of_working_days):
        for j in range(slots):
            for k in range(number_of_students):
                if len(np.intersect1d(full_sem_courses + pre_half_sem_courses, np.where(student_course_priority[k] == 0))) != 0:
                    if not np.sum(x1[i, j, np.intersect1d(full_sem_courses + pre_half_sem_courses, np.where(student_course_priority[k] == 0))]) <= 1:
                        print("Model failed at No_course_Overlap_Student_Pre_Sem_Core")
                        print("values are: ", (i, j, k))
                        tick = False

    for i in range(number_of_working_days):
        for j in range(slots):
            for k in range(number_of_students):
                if len(np.intersect1d(full_sem_courses + post_half_sem_courses, np.where(student_course_priority[k] == 0))) != 0:
                    if not np.sum(x1[i, j, np.intersect1d(full_sem_courses + post_half_sem_courses, np.where(student_course_priority[k] == 0))]) <= 1:
                        print("Model failed at No_course_Overlap_Student_Post_Sem_Core")
                        print("values are: ", (i, j, k))
                        tick = False

    x1 = np.sum(values[:, :, :, full_sem_courses + pre_half_sem_courses], axis=2)
    for i in range(number_of_working_days):
        for j in range(slots):
            for k in range(number_of_instructors):
                if not np.sum(x1[i, j] * instructors_Courses[k][full_sem_courses + pre_half_sem_courses]) <= 1:
                    print("Model failed at No_course_Overlap_Professor_Pre_Sem")
                    print("values are: ", (i, j, k))
                    tick = False

    x1 = np.sum(values[:, :, :, full_sem_courses + post_half_sem_courses], axis=2)
    for i in range(number_of_working_days):
        for j in range(slots):
            for k in range(number_of_instructors):
                if not np.sum(x1[i, j] * instructors_Courses[k][full_sem_courses + post_half_sem_courses]) <= 1:
                    print("Model failed at No_course_Overlap_Professor_Post_Sem")
                    print("values are: ", (i, j, k))
                    tick = False

    x1 = np.sum(values, axis=2)
    for i in range(number_of_working_days):
        for j in range(slots):
            for k in range(number_of_courses):
                if not x1[i, j, k] <= 1:
                    print("Model failed at One_Slot_Course_Once")
                    print("values are: ", (i, j, k))
                    tick = False

    x1 = np.sum(values[:,:,:venue_types[venue_types_list[0]], :], axis=2)
    x1 = np.sum(x1, axis=1)
    for i in range(number_of_working_days):
        for j in range(number_of_courses):
            if not x1[i, j] <= 1:
                print("Model failed at Course_only_Once_a_day_0")
                print("values are: ", (i, j, k))
                tick = False

    x1 = np.sum(values, axis=2)
    x1 = np.sum(x1, axis=1)
    for i in range(number_of_working_days):
        for j in range(number_of_courses):
            if not x1[i, j] <= (course_credits[j, -2] + 1):
                print("Model failed at Course_only_Once_a_day_1")
                print("values are: ", (i, j, k))
                tick = False

    x1 = np.sum(x1, axis=0)
    for i in range(number_of_courses):
        if not x1[i] == course_credits[i, -1]:
            print("Model failed at Total_Credits_of_core_Course")
            print(f"values are: {i} and {x1[i]} and {course_credits[i, -1]}")
            tick = False
    # checks total lab hours of a course irrespective of lab or slot
    x1 = np.sum(values[:, :, venue_types[venue_types_list[0]]:, :], axis=2)
    x1 = np.sum(x1, axis=1)
    x1 = np.sum(x1, axis=0)
    for i in range(number_of_courses):
            if not x1[i] == course_credits[i, -2]:
                print("Model failed at Total_lab_hours_of_Course")
                print("values are: ", (i, j, k))
                tick = False

    x1 = np.sum(values, axis=1)
    x1 = np.sum(x1, axis=0)
    for i in range(number_of_venues):
        for j in range(number_of_courses):
            if course_strength[j] > venue_setups[i] * course_lab[j][0]:
                if not x1[i, j] == 0:
                    print("Model failed at venue_setups")
                    print("values are: ", (i, j))
                    tick = False

    x1 = values[:, :, venue_types[venue_types_list[0]]:, :]
    x2 = np.sum(x1, axis=1)
    for i in range(number_of_working_days):
        for k in range(number_of_labs):
            for l in range(number_of_courses):
                if  not ((x2[i, k, l] == course_credits[l, -2]) or (x2[i, k, l] == 0)):
                    print("Model failed at Hours_A_day_of_Lab")
                    print("values are: ", (i, j, k))
                    tick = False

    my_sum = venue_types[venue_types_list[0]]
    for lab in lab_types_list:
        total_venues = venue_types[lab]
        x1 = values[:, :, my_sum : my_sum + total_venues, :]
        x2 = np.sum(x1, axis=1)
        my_sum += total_venues

        for i in range(number_of_working_days):
            for k in range(total_venues):
                for l in range(number_of_courses):
                    cred = int(course_credits[l, -2])
                    if cred > 0:
                        tick_1 = False
                        for j in range(0, 5 - cred):
                            temp = np.sum(x1[int(i), int(j):int(j+ cred), int(k), int(l)])
                            if temp == cred:
                                tick_1 = True
                                if lab != course_lab[l][1] :
                                    print("Model failed at venue type")
                                    print("values are : ", (i, k, l))
                                    tick = False
                        
                        for j in range(4, slots + 1 - cred):
                            temp = np.sum(x1[int(i), int(j):int(j+ cred), int(k), int(l)])
                            if temp == cred:
                                tick_1 = True
                                if lab != course_lab[l][1] :
                                    print("Model failed at venue type")
                                    print("values are : ", (i, k, l))
                                    tick = False

                        if not (tick_1 or x2[i, k, l] == 0):
                            print("Model failed at lab_time")
                            print("values are: ", (i, j, k, l))
                            tick=False

    x1 = np.sum(values, axis=2)
    for _, k1 in np.ndenumerate(np.where(non_minor_core_course == 1)):
        for _, k2 in np.ndenumerate(np.where(non_minor_core_course == 2)):
            for i in range(number_of_working_days): 
                for j in range(slots):
                    if not (x1[i, j, k1] + x1[i, j, k2] <= 1):
                        print("Model failed at Minor constraint")
                        print("values are: ", (k1, k2, i, j))
                        tick=False
        
    del x1, x2

    if tick:
        print(f"\nAll tests passed!\n")

    else:
        print(f"\nModel not satisfying all constraints\n")
    
    return
