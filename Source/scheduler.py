from gurobipy import GRB
import utils
import objective

# parameters = utils.initialize_parameters("Data/Latest_Data.xlsx")
parameters = utils.initialize_parameters("Data/Test_data_2.xlsx")
# parameters = utils.initialize_parameters("Data/Test_data.xlsx")

best_model, best_schedule = None, None
least_working_days = None
compromised_least_working_days = None
best_compromised_model, best_compromised_schedule = None, None
parameters.number_of_working_days = 5
parameters.slots = 8
# while parameters.number_of_working_days >= 1:
# while True:

my_model, schedule = utils.initialize_model(parameters)
my_model.update()

# constrs, sec_constrs
utils.add_constrs(my_model, schedule, parameters)

# utils.add_constrs(my_model, schedule, parameters)

#  + sec_constrs
# total_constrs = constrs

# objective.feasibility_objective(my_model, schedule, parameters)

# relax = my_model.relax()

# my_model.setObjective(schedule.sum(), sense=GRB.MINIMIZE)
# my_model.update()
# objective.add_objectives(my_model, schedule, number_of_working_days, slots, number_of_venues, number_of_courses)

# relax.optimize()
# relax.write(
        # f"Solutions/{parameters.number_of_working_days}.sol"
    # )
# utils.round_off(parameters)
# my_model.read(f"Solutions/{parameters.number_of_working_days}.sol")

my_model.optimize()

# print(my_model.status)

if (my_model.status == GRB.OPTIMAL) or (my_model.status == GRB.TIME_LIMIT):
# try:
    utils.print_time_table(my_model, schedule, parameters, f"Results/test_time_table_{parameters.number_of_working_days}.txt")
# except:
    # pass
    # least_working_days = parameters.number_of_working_days
    # best_model = my_model
    # best_schedule = schedule
    # break
    # continue

if (my_model.status == GRB.INFEASIBLE) or (my_model.status == GRB.INTERRUPTED):   
    print(f"\nNothing is impossible!")
    print(f"number_of_working_days : {parameters.number_of_working_days}\n")
    # my_model.printStats()
    # if parameters.number_of_working_days < 5:
    #     break

    # while total_constrs:
    #     constraint = total_constrs.pop()
    #     my_model.remove(constraint)
    #     my_model.update()
    #     # my_model.printStats()
    #     my_model.optimize()
    #     # my_model.status == GRB.INTERRUPTED
    #     if my_model.status == GRB.OPTIMAL:
    #         utils.print_time_table(my_model, schedule, parameters, "Results/test_compromised_time_table.txt")
    #         compromised_least_working_days = parameters.number_of_working_days
    #         parameters.number_of_working_days -= 1
    #         best_compromised_model = my_model
    #         best_compromised_schedule = schedule
    #         break
    # else:
    #     if (my_model.status == GRB.INFEASIBLE) or (my_model.status == GRB.INTERRUPTED):
    #         my_model.computeIIS()
    #         my_model.write("model.ilp")
            # break
        # my_model.printStats()
        # number_of_working_days -= 1
    # continue
    if (my_model.status == GRB.INFEASIBLE) or (my_model.status == GRB.INTERRUPTED):
            my_model.computeIIS()
            my_model.write("model.ilp")
    

# if least_working_days:
#     parameters.number_of_working_days = least_working_days
#     objective.add_objectives(best_model, best_schedule, parameters)
#     best_model.optimize()
#     # if (best_model.status == GRB.OPTIMAL) or (best_model.status == GRB.TIME_LIMIT) or (best_model.status == GRB.INTERRUPTED):
#     utils.print_time_table(best_model, best_schedule, parameters, "Results/test_optimized_time_table.txt")
        
# if compromised_least_working_days:
#     parameters.number_of_working_days = compromised_least_working_days
#     objective.add_objectives(best_compromised_model, best_compromised_schedule, parameters)
#     best_compromised_model.optimize()
#     # if (best_compromised_model.status == GRB.OPTIMAL) or (best_compromised_model.status == GRB.TIME_LIMIT) or (best_compromised_model.status == GRB.INTERRUPTED):
#     utils.print_time_table(best_compromised_model, best_compromised_schedule, parameters, "Results/test_optimized_compromized_time_table.txt")
# timetable = schedule.values()