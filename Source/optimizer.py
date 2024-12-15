# from gurobipy import GRB
import utils
import objective

least_working_days = 7
slots = 9

parameters = utils.initialize_parameters("Data/Test_data_2.xlsx")
my_model, schedule = utils.initialize_model(parameters)
my_model.update()
parameters.number_of_working_days = least_working_days
parameters.slots = slots

utils.add_constrs(my_model, schedule, parameters)

# my_model.read(f"Models/{least_working_days}.mps")
objective.add_objectives(my_model, schedule, parameters)
my_model.read(f"Solutions/{least_working_days}.sol")
my_model.optimize()
# if (my_model.status == GRB.OPTIMAL) or (my_model.status == GRB.TIME_LIMIT) or (my_model.status == GRB.INTERRUPTED):
utils.print_time_table(my_model, schedule, parameters, "Results/test_optimized_time_table.txt", extra="_optimized")
