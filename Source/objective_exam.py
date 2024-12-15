from gurobipy import GRB
import numpy as np
import classes_exam

def obj_minimize_unique_venues(my_model, schedule, parameters : classes_exam.Params, index, priority):
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


def obj_one_day_one_exam(my_model, schedule, parameters : classes_exam.Params, index, priority):
    x = schedule.sum(axis=1)

    # z = my_model.addMVar((parameters.number_of_students, parameters.number_of_working_days), vtype=GRB.BINARY)

    # for student in range(parameters.number_of_students):
    #     for i in range(parameters.number_of_working_days):
    #         if np.where(parameters.student_course_priority[student] != -1)[0].size > 0:
    #             my_model.addConstr(
    #                 ((z[student, i].item() == 1) >>  (x[i, np.where(parameters.student_course_priority[student] != -1)[0]].sum() <= 1)),
    #                 name = "One_Day_One_Exam_Constraint_1"
    #             )

    #             my_model.addConstr(
    #                 ((z[student, i].item() == 0) >>  (x[i, np.where(parameters.student_course_priority[student] != -1)[0]].sum() >= 2)),
    #                 name = "One_Day_One_Exam_Constraint_2"
    #             )
    # , index=index, priority=priorityx
    z = my_model.addMVar((len(parameters.baskets_core), parameters.number_of_working_days), vtype=GRB.BINARY)

    for b, basket in enumerate(parameters.baskets_core):
        for i in range(parameters.number_of_working_days):
            my_model.addConstr(
                ((z[b, i].item() == 0) >> (x[i, np.array(list(basket))].sum() <= 1)),
                name = "One_Day_One_Exam_Constraint_1"
            )

            my_model.addConstr(
                ((z[b, i].item() == 1) >> (x[i, np.array(list(basket))].sum() >= 2)),
                name = "One_Day_One_Exam_Constraint_2"
            )

    my_model.setObjective((z.sum(axis=1)*np.array(parameters.basket_number_of_students_core)).sum())
    return


def add_objectives(my_model, schedule, parameters : classes_exam.Params):
    my_model.ModelSense = GRB.MINIMIZE
    

    # obj_minimize_unique_venues(my_model, schedule, parameters, 0, 1)
    obj_one_day_one_exam(my_model, schedule, parameters, 0, 1)
    my_model.update()
    return
