from re import A
from utils import read_input_excel
import numpy as np

# a = np.arange(10)
# print(np.where(a < 5), a)



# courses_list, student_list, instructor_list, venue_list = read_input_excel("Data.xlsx")
# for i in courses_list:
#     print(courses_list[i].get_code(), str(courses_list[i].get_students_list()[0].get_rollnumber()) + " " +
#                                       courses_list[i].get_students_list()[0].get_course_list()[0].get_code()
#
#     if courses_list[i].get_students_list() else None)

# for i in courses_list:
#     print(courses_list[i].get_code())
#
#     for j in courses_list[i].get_instructor_list():
#         print(j.get_name())
#         for k in j.get_course_list():
#             print(k.get_code(), end=", ")
#         print()
#     print()
#
#     for j in courses_list[i].get_students_list():
#         print(j.get_rollnumber())
#         for k in j.get_course_list():
#             print(k.get_code(), end=", ")
#         print()
#     print()

# for i in sorted(student_list.keys(), key=lambda x: int(x)):
#     print(student_list[i].get_rollnumber())

# for i, j in enumerate(sorted(courses_list.keys())):
#     print(i, courses_list[j].get_code())

# print(sorted(["9234", "11001"]))

# for i in student_list:
#     print(student_list[i].get_rollnumber())
#     for j in student_list[i].get_course_list():
#         print(j.get_code(), end=", ")
#     print()

# for i in instructor_list:
#     print(instructor_list[i].get_name())
#     for j in instructor_list[i].get_course_list():
#         print(j.get_code(), end=", ")
#     print()

# for i in venue_list:
#     print(venue_list[i].get_name(), venue_list[i].get_capacity())

# venue_list = list(sorted(venue_list.keys(), key=lambda x: venue_list[x].get_type()))
# print(venue_list)
