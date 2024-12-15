# don't add constraints while reading the solution!
# from gurobipy import GRB
# import gurobipy as gp
import utils

parameters = utils.initialize_parameters("Data/Test_data_2.xlsx")
# parameters = utils.initialize_parameters("Data/Test_data.xlsx")
parameters.number_of_working_days = 7
parameters.slots = 9

my_model, schedule = utils.initialize_model(parameters)
constrs = utils.add_constrs(my_model, schedule, parameters)
my_model.Params.Heuristics = 1
my_model.update()
my_model.read(f"Solutions/{parameters.number_of_working_days}.sol")
my_model.optimize()

extra = "_temp"
file = "Results/temp_timetable"

my_model.write(f"Solutions/{parameters.number_of_working_days}"+extra+".sol")
# my_model.write(f"Models/{parameters.number_of_working_days}"+extra+".mps")
print("\nYesssssss!")
print(f"number_of_working_days : {parameters.number_of_working_days}\n")
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
printing_format_1 = {}
printing_format_2 = {}
printing_format_2_lab = {}

slots_utilized = 0
unique_venues = {campus:set() for campus in parameters.campus_list}

for i in range(parameters.number_of_working_days):
    for j in range(parameters.slots):
        # number_of_venues-number_of_labs, 
        slot_not_empty = False
        for k in range(parameters.number_of_venues):
            for l in range(parameters.number_of_courses):
                if my_model.getVarByName('time[%d,%d,%d,%d]' % (i, j, k, l)).X == 1:
                    slot_not_empty = True
                    unique_venues[parameters.campus_list[parameters.venue_campus[k]]].add(k)
                    if parameters.course_list[l] in printing_format_1:
                        printing_format_1[parameters.course_list[l]].append(str(days[i]) + str(j+1) + " [" + parameters.venue_dict[parameters.venue_list[k]].name + "]")
                    else:
                        printing_format_1[parameters.course_list[l]] = [str(days[i]) + str(j+1) + " [" + parameters.venue_dict[parameters.venue_list[k]].name + "]"]

                    # add_on = ""
                    if k < parameters.venue_types[0]:
                    #     add_on = "_Practical"
                        if parameters.course_list[l] in printing_format_2:
                            printing_format_2[parameters.course_list[l]].append(str(days[i]) + str(j+1))
                        else:
                            printing_format_2[parameters.course_list[l]] = [str(days[i]) + str(j+1)]
                    else:
                        if parameters.course_list[l] in printing_format_2_lab:
                            printing_format_2_lab[parameters.course_list[l]].append(str(days[i]) + str(j+1))
                        else:
                            printing_format_2_lab[parameters.course_list[l]] = [str(days[i]) + str(j+1)]

        if slot_not_empty:
            slots_utilized += 1
# print(f"number of working days utilized : {parameters.number_of_working_days}")
for campus,venue_set in unique_venues.items():
    print(f"Campus {campus} : Venues {[parameters.venue_list[i] for i in venue_set]}\n  number of venues used : {len(venue_set)}\n")
print(f"number of slots utilized : {slots_utilized}\n")

combination_frequency = {}

for combination1 in printing_format_2.values():
    frequency = 0
    if ",".join(combination1) not in combination_frequency:
        for combination2 in printing_format_2.values():
            if combination1 == combination2:
                frequency += 1
        combination_frequency[",".join(combination1)] = frequency

print(f"combination_frequency : {combination_frequency}")

combinations = sorted(combination_frequency.keys(), key = lambda x : combination_frequency[x], reverse=True)
alloted_combinations = []
combination_slot = {}
vacant_slot = 1

for combination in combinations:
    one = combination.split(",")
    one = set(one)
    unique = True
    for temp in combination_slot:
        temp = temp.split(",")
        temp = set(temp)
        if one & temp:
            unique = False
            break
    if unique:
        combination_slot[combination] = vacant_slot
        vacant_slot += 1
        alloted_combinations.append(combination)


with  open(file+"_1.txt", "w")  as f:
    for course, time in printing_format_1.items():
        f.write(f"{course} : {', '.join(time)}\n")

with  open(file+"_2.txt", "w")  as f:
    for course, slot in combination_slot.items():
        f.write(f"{course} : {slot}\n")
