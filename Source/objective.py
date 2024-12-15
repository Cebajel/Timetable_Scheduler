from gurobipy import GRB
import gurobipy as gp
import classes
import numpy as np

def feasibility_objective(my_model, schedule, parameters : classes.Params):
    # x1 = schedule.sum(axis=2)
    x1 = schedule
    z1 = my_model.addMVar((len(parameters.baskets_elective), parameters.number_of_working_days, parameters.slots), vtype=GRB.BINARY)

    my_model.addConstrs(
        (((z1[i, j, k].item() == 0) >> (x1[j, k, np.array((x,y))].sum() <= 1))
         for i,(x,y) in enumerate(parameters.baskets_elective) for j in range(parameters.number_of_working_days) 
         for k in range(parameters.slots)),
         name = "Comditional_Constraint_1"
    )

    my_model.addConstrs(
        (((z1[i, j, k].item() == 1) >> (x1[j, k, np.array((x,y))].sum() >= 2))
         for i,(x,y) in enumerate(parameters.baskets_elective) for j in range(parameters.number_of_working_days) 
         for k in range(parameters.slots)),
         name = "Comditional_Constraint_2"
    )

    z1 = z1.sum(axis=2)
    z1 = z1.sum(axis=1)

    # z2 = my_model.addMVar((len(parameters.baskets_core), parameters.number_of_working_days, parameters.slots), vtype=GRB.BINARY)

    # my_model.addConstrs(
    #     (((z2[i, j, k].item() == 0) >> (x1[j, k, np.array((x,y))].sum() <= 1))
    #      for i,(x,y) in enumerate(parameters.baskets_core) for j in range(parameters.number_of_working_days) 
    #      for k in range(parameters.slots)),
    #      name = "Comditional_Constraint_1"
    # )

    # my_model.addConstrs(
    #     (((z2[i, j, k].item() == 1) >> (x1[j, k, np.array((x,y))].sum() >= 2))
    #      for i,(x,y) in enumerate(parameters.baskets_core) for j in range(parameters.number_of_working_days) 
    #      for k in range(parameters.slots)),
    #      name = "Comditional_Constraint_2"
    # )

    # z2 = z2.sum(axis=2)
    # z2 = z2.sum(axis=1)

    # my_model.setObjective((z1*np.array(parameters.basket_number_of_students)).sum() + (z2*1000).sum(), GRB.MINIMIZE)
    # my_model.setObjective((z2*1000).sum(), GRB.MINIMIZE)
    my_model.setObjective((z1*np.array(parameters.basket_number_of_students_elective)).sum(), GRB.MINIMIZE)
    my_model.update()
    return


def obj_same_venue_0(my_model, schedule, parameters : classes.Params, index, priority):
    x1 = schedule[:, :, :parameters.venue_types[0], :].sum(axis=1)
    x1 = x1.sum(axis=0)
    z1 = my_model.addMVar((parameters.venue_types[0], parameters.number_of_courses), vtype=GRB.BINARY)

    my_model.addConstrs(
        (((z1[i, j].item() == 1) >> (x1[i, j] >= np.sum(parameters.course_credits[j][:2])))
         for i in range(parameters.venue_types[0]) for j in range(parameters.number_of_courses)),
         name = "Comditional_Constraint_1"
    )

    my_model.addConstrs(
        (((z1[i, j].item() == 0) >> (x1[i, j] <= 1))
         for i in range(parameters.venue_types[0]) for j in range(parameters.number_of_courses)),
         name = "Comditional_Constraint_2"
    )

    my_model.setObjectiveN(z1.sum(), index=index, priority=priority)
    return


def obj_experimental(my_model, schedule, parameters : classes.Params, index1, priority1, index2, priority2):
    z1 = my_model.addMVar((parameters.number_of_working_days, parameters.slots-1), vtype=GRB.BINARY)
    x1 = schedule[:, :, :parameters.venue_types[0], :].sum(axis=3)
    x1 = x1.sum(axis=2)

    # my_model.addConstrs(
    #     ( ((z1[i, j].item() == 1) >> ((x1[i, j]*parameters.course_strength).sum() >= (x1[i, j + 1]*parameters.course_strength).sum())) 
    #      for i in range(parameters.number_of_working_days) for j in range(parameters.slots - 1)),
    #     name="Experimental Constraint"
    # )
    # my_model.addConstrs(
    #     ( ((z1[i, j].item() == 0) >> ((x1[i, j]*parameters.course_strength).sum() <= (x1[i, j + 1]*parameters.course_strength).sum() - 1)) 
    #      for i in range(parameters.number_of_working_days) for j in range(parameters.slots - 1)),
    #     name="Experimental Constraint"
    # )

    my_model.addConstrs(
        ( ((z1[i, j].item() == 1) >> (x1[i, j] >= x1[i, j + 1]))
         for i in range(parameters.number_of_working_days) for j in range(parameters.slots - 1)),
        name="Experimental Constraint"
    )
    my_model.addConstrs(
        ( ((z1[i, j].item() == 0) >> (x1[i, j] <= x1[i, j + 1] - 1)) 
         for i in range(parameters.number_of_working_days) for j in range(parameters.slots - 1)),
        name="Experimental Constraint"
    )

    z2 = my_model.addMVar((parameters.number_of_working_days, parameters.slots-1), vtype=GRB.BINARY)
    
    x2 = schedule[:, :, parameters.venue_types[0]:, :].sum(axis=3)
    x2 = x2.sum(axis=2)

    # my_model.addConstrs(
    #     ((x2[i, j] <= x2[i, j+1]) for i in range(parameters.number_of_working_days) for j in range(parameters.slots - 1)),
    #     name="Experimental Constraint"
    # )

    my_model.addConstrs(
        ( ((z2[i, j].item() == 1) >> (x2[i, j] <= x2[i, j + 1])) 
         for i in range(parameters.number_of_working_days) for j in range(parameters.slots - 1)),
        name="Experimental Constraint"
    )
    my_model.addConstrs(
        ( ((z2[i, j].item() == 0) >> (x2[i, j] - 1 >= x2[i, j + 1])) 
         for i in range(parameters.number_of_working_days) for j in range(parameters.slots - 1)),
        name="Experimental Constraint"
    )

    my_model.setObjectiveN(z1.sum(), index=index1, priority=priority1)
    my_model.setObjectiveN(z2.sum(), index=index2, priority=priority2)

    return


def obj_same_venue_1(my_model, schedule, parameters : classes.Params, index, priority):
    x1 = schedule[:, :, :parameters.venue_types[0], :].sum(axis=1)
    x1 = x1.sum(axis=0)
    z1 = my_model.addMVar((parameters.venue_types[0], parameters.number_of_courses), vtype=GRB.BINARY)

    my_model.addConstrs(
        (((z1[i, j].item() == 1) >> (x1[i, j] >= np.sum(parameters.course_credits[j][:2])))
         for i in range(parameters.venue_types[0]) for j in range(parameters.number_of_courses)),
         name = "Comditional_Constraint_1"
    )

    my_model.addConstrs(
        (((z1[i, j].item() == 0) >> (x1[i, j] <= 1))
         for i in range(parameters.venue_types[0]) for j in range(parameters.number_of_courses)),
         name = "Comditional_Constraint_2"
    )

    my_model.setObjectiveN(z1.sum(), index=index, priority=priority)
    return


def obj_pair_half_semester_courses(my_model, schedule, parameters : classes.Params, index, priority):
    x1 = schedule.sum(axis=3)

    z1 = my_model.addMVar((parameters.number_of_working_days, parameters.slots, parameters.number_of_venues), vtype=GRB.BINARY)

    my_model.addConstrs(
        ( ((z1[i, j, k].item() == 1) >> (x1[i, j, k] == 2)) for i in range(parameters.number_of_working_days) for j in range(parameters.slots) 
         for k in range(parameters.number_of_venues)), name="indic_1"
    )

    my_model.addConstrs(
        ( ((z1[i, j, k].item() == 0) >> (x1[i, j, k] <= 1)) for i in range(parameters.number_of_working_days) for j in range(parameters.slots) 
         for k in range(parameters.number_of_venues)), name="indic_0"
    )

    my_model.setObjectiveN(z1.sum(), index=index, priority=priority)

    return


def obj_maximize_free_slots(my_model, schedule, parameters : classes.Params, index, priority):
    x1 = schedule.sum(axis=3)
    x1 = x1.sum(axis=2)

    z1 = my_model.addMVar((parameters.number_of_working_days, parameters.slots), vtype=GRB.BINARY)
    my_model.addConstrs(
        ((z1[i, j].item() == 1) >> (x1[i, j] == 0) for i in range(parameters.number_of_working_days) for j in range(parameters.slots)),
        name="indic_1"
    )

    my_model.addConstrs(
        ((z1[i, j].item() == 0) >> (x1[i, j] >= 1) for i in range(parameters.number_of_working_days) for j in range(parameters.slots)),
        name="indic_0"
    )

    my_model.setObjectiveN(z1.sum(), index=index, priority=priority)

    return


def obj_minimize_unique_venues(my_model, schedule, parameters : classes.Params, index, priority):
    x1 = schedule.sum(axis=3)
    x1 = x1.sum(axis=1)
    x1 = x1.sum(axis=0)
    z1 = my_model.addMVar((parameters.number_of_venues,), vtype=GRB.BINARY)

    my_model.addConstrs(
        ((z1[i].item() == 1) >> (x1[i] == 0) for i in range(parameters.number_of_venues)),
        name="indic_1"
    )

    my_model.addConstrs(
        ((z1[i].item() == 0) >> (x1[i] >= 1) for i in range(parameters.number_of_venues)),
        name="indic_0"
    )

    my_model.setObjectiveN(z1.sum(), index=index, priority=priority)

    return

# def printing_func(my_model, schedule, parameters : classes.Params):
#     if (my_model.status == GRB.OPTIMAL) or (my_model.status == GRB.TIME_LIMIT):
#         try:
#             utils.print_time_table(my_model, schedule, parameters, "test_optimized_time_table.txt")
#         except:
#             print("Optimization done. If you think output could be optimized further try to increase optimization time.")


def add_objectives(my_model, schedule, parameters : classes.Params):
    my_model.ModelSense = GRB.MAXIMIZE
    
    obj_maximize_free_slots(my_model, schedule, parameters, 0, 4)
    obj_minimize_unique_venues(my_model, schedule, parameters, 1, 3)
    # obj_same_venue_0(my_model, schedule, parameters, 2, 2)
    # obj_experimental(my_model, schedule, parameters, 3, 1, 4, 0) #0,2 1,1
    # obj_pair_half_semester_courses(my_model, schedule, parameters, 1, 0)
    my_model.update()
    return
