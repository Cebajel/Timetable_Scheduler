from gurobipy import GRB
import utils_exam
import numpy as np
import objective_exam

# file = input("Give path to input dataExcel file: ")
# "Data/Latest_Data.xlsx"
parameters = utils_exam.initialize_parameters("Data/Latest_Data.xlsx")

# temp1 = int(input("Give number of days of timetable: "))
parameters.number_of_working_days = 6
# temp2 = int(input("Give number of slots of timetable: "))
parameters.slots = 2
# parameters.allowed_students = []
# for student in range(parameters.number_of_students):
#     temp = len(np.where(parameters.student_course_priority[student] == 0)[0])
#     if temp <= 4:
#         parameters.allowed_students.append(student)
# 
# print(parameters.allowed_students)
# exit(1)

my_model, schedule = utils_exam.initialize_model(parameters)
my_model.update()


constrs = utils_exam.add_constrs(my_model, schedule, parameters)

# flag = bool(input("Do you want to add objective? (True/False): "))
# if flag == "True":
objective_exam.add_objectives(my_model, schedule, parameters)
my_model.optimize()

try:
    utils_exam.print_time_table(my_model, schedule, parameters, f"Results/exam_test_time_table_{parameters.number_of_working_days}.txt")
except:
    pass

# if (my_model.status == GRB.INFEASIBLE) or (my_model.status == GRB.INTERRUPTED):   
#     if (my_model.status == GRB.INFEASIBLE) or (my_model.status == GRB.INTERRUPTED):
#             my_model.computeIIS()
#             my_model.write("model.ilp")
    