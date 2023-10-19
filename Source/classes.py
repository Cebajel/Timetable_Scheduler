import math

class Student:
    def __init__(self, roll):
        self.rollnumber = roll
        self.courses = {}

    def add_course(self, course, priority):
        self.courses[course] = priority
        return


class Instructor:
    def __init__(self, name):
        self.name = name.strip()
        self.courses = []

    def add_course(self, x):
        self.courses.append(x)
        return


class Course:
    def __init__(self, value, columns, campus_type):
        self.code = value[columns[0]].strip()
        self.name = value[columns[1]].strip()
        self.instructors = []
        self.students = {}
        self.TAs = []
        self.groups = []
        self.L = int(value[columns[3]]) if not math.isnan(value[columns[3]]) else 0
        self.T = int(value[columns[4]]) if not math.isnan(value[columns[4]]) else 0
        self.P = int(value[columns[5]]) if not math.isnan(value[columns[5]]) else 0
        # print(type(self.L), type(self.T), type(self.P))
        # print(self.L, self.T, self.P)
        self.duration = value[columns[6]].strip() if isinstance(value[columns[6]], str) else 'F'
        # self.minor = True if isinstance(value[columns[7]], str) else False
        self.minor = True if value[columns[7]].strip() == 'Yes' else False
        self.mode = value[columns[8]].strip() if isinstance(value[columns[8]], str) else 'Offline'
        # temp_campus = value[columns[9]].split("\n")
        self.campus_type = campus_type
        # self.campus_type = int(value[columns[9]]) if not math.isnan(value[columns[9]]) else 0 

        self.group_size = int(value[columns[10]]) if not math.isnan(value[columns[10]]) else 1
        self.lab_type = int(value[columns[11]]) if not math.isnan(value[columns[11]]) else 1

        if isinstance(value[columns[13]], int):
            self.division_l = int(value[columns[13]])
            self.division_p = int(value[columns[13]])
        elif isinstance(value[columns[13]], str):
            temp = value[columns[13]].strip()
            temp = temp.split("\n")
            temp = {i.split(":")[0].strip() : int(i.split(":")[1]) for i in temp}
            self.division_l = temp["L"]
            self.division_p = temp["P"]
            # print(self.division_l, self.division_p)
        else:
            self.division_l = 1
            self.division_p = 1
        # print(len(value[columns[9]].split("\n")), end=" ")


    def add_student(self, student, priority):
        self.students[student] = priority
        return

    def add_instructor(self, x):
        self.instructors.append(x)
        return
    
    def add_TA(self, TA):
        self.students[TA] = 0
        self.TAs.append(TA)
        return

    def get_LTP(self):
        return self.L, self.T, self.P

    def get_strength(self):
        return len(self.students)
    
    def get_params(self) :
        params = {}
        params["code"] = self.code
        params["name"] = self.name
        params["instructors"] = None
        params["L"] = self.L
        params["T"] = self.T
        params["P"] = self.P
        params["duration"] = self.duration
        params["minor"] = "Yes" if self.minor else "No"
        params["mode"] = self.mode
        params["campus_type"] = self.campus_type
        params["group_size"] = self.group_size
        params["lab_type"] = self.lab_type
        params["TAs"] = None
        params["Number of divisions"] = f"L : {self.division_l}\n P : {self.division_p}"
        return params
    

    def copy(self) :
        value = self.get_params()
        # print({key : type(ivalue) for key, ivalue in value.items()})
        new_course = Course(value, list(value.keys()), self.campus_type)
        new_course.groups = self.groups
        new_course.instructors = [i for i in self.instructors]
        new_course.students = {student : priority for student, priority in self.students.items()}
        new_course.TAs = self.TAs
        return new_course
    

class Venue:
    def __init__(self, name, number_of_setups, type, campus_type):
        """venue type: 0 for classroom and 1 for lab"""
        self.name = name.strip()
        self.number_of_setups = int(number_of_setups) if not math.isnan(number_of_setups) else float('inf')
        self.type = int(type)
        self.campus_type = campus_type


class Params:
    number_of_working_days = None
    slots = None
    number_of_venues = None
    number_of_courses = None
    number_of_students = None
    instructors_Courses = None
    number_of_instructors = None
    course_credits = None
    courses_dict = None
    venue_dict = None
    venue_list = None
    course_list = None
    venue_setups = None
    course_strength = None
    full_sem_courses = None
    pre_half_sem_courses = None
    post_half_sem_courses = None
    venue_types = None
    venue_types_list = None
    lab_types_list = None
    course_lab = None
    student_course_priority = None
    non_minor_core_course = None
    venue_type_campus = None
    campus_list = None
    number_of_campuses = None
    course_campus = None
    venue_campus = None
    student_list = None
    student_dict = None
    instructor_dict = None
    venue_dict = None
    instructor_list = None
    baskets_core = None
    baskets_elective = None
    basket_number_of_students = None
    basket_number_of_students_core = None
    basket_students_core = None
    basket_students_elective = None
    groups = None
    groups_courses = None
    # baskets_core = None
    # baskets_elective = None

    # def __init__(self) -> None:
    #     pass

#     def __repr__(self) -> str:
#         return f"number_of_working_days = {self.number_of_working_days}\n\
# slots = {self.slots} \n\
# number_of_venues = {self.number_of_venues} \n\
# number_of_courses = {self.number_of_courses} \n\
# number_of_students = {self.number_of_students} \n\
# instructors_Courses = {self.instructors_Courses} \n\
# number_of_instructors = {self.number_of_instructors} \n\
# course_credits = {self.course_credits} \n\
# venue_dict = {self.venue_dict} \n\
# venue_list = {self.venue_list} \n\
# course_list = {self.course_list} \n\
# venue_setups = {self.venue_setups} \n\
# course_strength = {self.course_strength} \n\
# full_sem_courses = {self.full_sem_courses} \n\
# pre_half_sem_courses = {self.pre_half_sem_courses} \n\
# post_half_sem_courses = {self.post_half_sem_courses} \n\
# venue_types = {self.venue_types} \n\
# venue_types_list = {self.venue_types_list} \n\
# lab_types_list = {self.lab_types_list} \n\
# course_lab = {self.course_lab} \n\
# student_course_priority = {self.student_course_priority} \n\
# non_minor_core_course = {self.non_minor_core_course}"