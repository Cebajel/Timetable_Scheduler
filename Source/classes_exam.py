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
    def __init__(self, value=None, columns=None, lecture=True, orig=None):
        if orig:
            self.copy_constructor(orig)
        else:
            self.non_copy_constructor(value, lecture, columns)

    def non_copy_constructor(self, value, lecture, columns):
        self.code = value[columns[0]].strip()
        self.name = value[columns[1]].strip()
        self.instructors = []
        self.students = {}
        self.TAs = []
        self.groups = []
        self.theory = lecture
        # L = int(value[columns[3]]) if not math.isnan(value[columns[3]]) else 0
        # T = int(value[columns[4]]) if not math.isnan(value[columns[4]]) else 0
        # P = int(value[columns[5]]) if not math.isnan(value[columns[5]]) else 0
        if lecture:
            self.C = 1
        else:
            self.C = 1
        self.duration = value[columns[6]].strip() if isinstance(value[columns[6]], str) else 'F'
        self.minor = True if value[columns[7]].strip() == 'Yes' else False
        self.mode = value[columns[8]].strip() if isinstance(value[columns[8]], str) else 'Offline'
        temp_campus = value[columns[9]].split("\n")
        if len(temp_campus) == 1:
            self.campus_type = temp_campus[0]
        else:
            temp_campus = {
                i.split(":")[0].strip(): i.split(":")[1].strip() for i in temp_campus
            }
            if lecture:
                self.campus_type = temp_campus["L"]
            else:
                self.campus_type = temp_campus["P"]

        self.group_size = int(value[columns[10]]) if not math.isnan(value[columns[10]]) else 1
        if lecture:
            self.venue_type = 0
        else:
            self.venue_type = int(value[columns[11]]) if not math.isnan(value[columns[11]]) else 1

        if isinstance(value[columns[13]], int):
            self.divisions = int(value[columns[13]])
        elif isinstance(value[columns[13]], str):
            temp = value[columns[13]].strip()
            temp = temp.split("\n")
            temp = {i.split(":")[0].strip() : int(i.split(":")[1]) for i in temp}
            if lecture:
                self.divisions = temp["L"]
            else:
                self.divisions = temp["P"]
        else:
            self.divisions = 1
        return
    
    def copy_constructor(self, orig):
        self.code = orig.code
        self.name = orig.name
        self.instructors = [i for i in orig.instructors]
        self.students = {student : priority for student, priority in orig.students.items()}
        self.TAs = [i for i in orig.TAs]
        self.groups = [i for i in orig.groups]
        self.C = orig.C
        self.duration = orig.duration
        self.minor =orig.minor
        self.mode = orig.mode
        self.campus_type = orig.campus_type
        self.groups = orig.groups
        self.group_size = orig.group_size
        self.venue_type = orig.venue_type
        self.divisions = orig.divisions
        self.theory = orig.theory
        return

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

    def get_credits(self):
        return self.C

    def get_strength(self):
        return len(self.students)
    
    def get_number_of_tas(self):
        return len(self.TAs)
    
    # def get_params(self) :
    #     params = {}
    #     params["code"] = self.code
    #     params["name"] = self.name
    #     params["instructors"] = None
    #     params["L"] = self.L
    #     params["T"] = self.T
    #     params["P"] = self.P
    #     params["duration"] = self.duration
    #     params["minor"] = "Yes" if self.minor else "No"
    #     params["mode"] = self.mode
    #     params["campus_type"] = self.campus_type
    #     params["group_size"] = self.group_size
    #     params["lab_type"] = self.lab_type
    #     params["TAs"] = None
    #     params["Number of divisions"] = f"L : {self.division_l}\n P : {self.division_p}"
    #     return params
    

    # def copy(self) :
    #     value = self.get_params()
    #     # print({key : type(ivalue) for key, ivalue in value.items()})
    #     new_course = Course(value, list(value.keys()), self.campus_type)
    #     new_course.groups = self.groups
    #     new_course.instructors = [i for i in self.instructors]
    #     new_course.students = {student : priority for student, priority in self.students.items()}
    #     new_course.TAs = self.TAs
    #     return new_course
    

class Venue:
    def __init__(self, name, seater_1, seater_2, seater_3, number_of_setups, type, campus_type):
        """venue type: 0 for classroom and 1 for lab"""
        self.capacity = int(seater_1) + int(seater_2) + (int(seater_3) * 2)
        self.name = name.strip()
        self.number_of_setups = int(number_of_setups) if not math.isnan(number_of_setups) else float('inf')
        self.type = int(type)
        self.campus_type = campus_type


class Params:
    def __init__(self):
        self.number_of_working_days = None
        self.slots = None
        self.number_of_venues = None
        self.number_of_courses = None
        self.number_of_students = None
        self.instructors_Courses = None
        self.number_of_instructors = None
        self.course_credits = None
        self.courses_dict = None
        self.venue_dict = None
        self.venue_list = None
        self.course_list = None
        self.venue_setups = None
        self.course_strength = None
        self.full_sem_courses = None
        self.pre_half_sem_courses = None
        self.post_half_sem_courses = None
        self.venue_types = None
        # self.course_lab = None
        self.course_venue_type = None
        self.course_group_size = None
        self.student_course_priority = None
        self.non_minor_core_course = None
        self.campus_list = None
        self.number_of_campuses = None
        self.course_campus = None
        self.venue_campus = None
        self.student_list = None
        self.student_dict = None
        self.instructor_dict = None
        self.venue_dict = None
        self.instructor_list = None
        self.baskets_core = None
        self.baskets_elective = None
        self.basket_number_of_students_core = None
        self.basket_number_of_students_elective = None
        self.basket_students_core = None
        self.basket_students_elective = None
        self.course_venue_capacity = None
        self.course_bifercations = None
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