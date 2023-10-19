import numpy as np
import random
import gurobipy as gp
from gurobipy import GRB

def constrs_one_switch_one_controller(my_model, controller_switch_mapping, number_of_switches):
    x = controller_switch_mapping.sum(axis=0)

    my_model.addConstrs(
        (x[i] == 1 for i in range(number_of_switches)),
        name="One_Switch_One_Controller"
    )

    return


def constrs_one_controller_ten_switches(my_model, controller_switch_mapping, number_of_controllers):
    x = controller_switch_mapping.sum(axis=1)

    my_model.addConstrs(
        (x[i] == 10 for i in range(number_of_controllers)),
        name="One_Controller_10_Switches"
    )
    return

def add_objective(my_model, controller_positions, switch_positions, controller_switch_mapping, number_of_controllers, number_of_switches, controller_controler_mapping):


    z1 = my_model.addMVar( (number_of_controllers, number_of_controllers, 2), vtype=GRB.CONTINUOUS)
    z2 = my_model.addMVar( (number_of_controllers, number_of_controllers, 2), vtype=GRB.CONTINUOUS)
    for i in range(number_of_controllers):
        for j in range(number_of_controllers):
            my_model.addConstr(
                (z1[i][j][0] == (controller_positions[i][0] - controller_positions[j][0])),
                name="Temp"
            )

            my_model.addConstr(
                (z1[i][j][1] == (controller_positions[i][1] - controller_positions[j][1])),
                name="Temp"
            )
            my_model.addGenConstrPow(z1[i][j][0], z2[i][j][0], 2)
            my_model.addGenConstrPow(z1[i][j][1], z2[i][j][1], 2)
            # my_model.addConstr(
                # ( z3[i][j] == (z2[i][j] ** 2)),
                # name="Temp"
            # )

    x1 = gp.quicksum(
        z2[i][j].sum()*controller_controller_mapping[i][j] for i in range(number_of_controllers) for j in range(number_of_controllers)
    )

    z3 = my_model.addMVar( (number_of_controllers, number_of_switches, 2), vtype=GRB.CONTINUOUS)
    z4 = my_model.addMVar( (number_of_controllers, number_of_switches, 2), vtype=GRB.CONTINUOUS)
    for i in range(number_of_controllers):
        for j in range(number_of_switches):
            my_model.addConstr(
                (z3[i][j][0] == (controller_positions[i][0] - switch_positions[j][0])),
                name="Temp"
            )

            my_model.addConstr(
                (z3[i][j][1] == (controller_positions[i][1] - switch_positions[j][1])),
                name="Temp"
            )
            my_model.addGenConstrPow(z3[i][j][0], z4[i][j][0], 2)
            my_model.addGenConstrPow(z3[i][j][1], z4[i][j][1], 2)
            # my_model.addConstr(
                # ( z3[i][j] == (z2[i][j] ** 2)),
                # name="Temp"
            # )

    x2 = gp.quicksum(
        z4[i][j].sum()*controller_switch_mapping[i][j] for i in range(number_of_controllers) for j in range(number_of_switches)
    )

    my_model.ModelSense = GRB.MINIMIZE
    my_model.setObjective(x1 + x2)
    return

if __name__ == '__main__':

    random.seed(1)
    number_of_switches = 100
    switches_positions = np.random.random_integers(0,100,size=(100,2))
    inter_switches_connections = np.random.random_integers(0,100,size=(100,100))
    inter_switches_connections = (inter_switches_connections + inter_switches_connections.T)//2

    number_of_controllers = 10
    best_latency = float('inf')

    my_model = gp.Model("Controller")
    my_model.Params.LogFile = "midsem.log"
    my_model.Params.MIPFocus = 1

    controller_switch_mapping = my_model.addMVar(
        (
            number_of_controllers,
            number_of_switches,
        ),
        vtype=GRB.BINARY,
        name="mapping",
    )

    controller_controller_mapping = my_model.addMVar(
        (
            number_of_controllers,
            number_of_controllers,
        ),
        vtype=GRB.BINARY,
        name="mapping",
    )



    controller_positions = my_model.addMVar(
        (
            number_of_controllers,
            2
        ),
        vtype=GRB.INTEGER,
        name="positions",
    )

    constrs_one_switch_one_controller(my_model, controller_switch_mapping, number_of_switches)
    constrs_one_controller_ten_switches(my_model, controller_switch_mapping, number_of_controllers)

    my_model.update()

    add_objective(my_model, controller_positions, switches_positions, 
                  controller_switch_mapping, number_of_controllers, number_of_switches, controller_controller_mapping)
    my_model.update()
    my_model.optimize()

    # my_model.computeIIS()
    # my_model.write("model.ilp")

    if(my_model.status == GRB.OPTIMAL):

        print(f"Printing Controller Positions")

        for i in range(number_of_controllers):
            print(controller_positions[i].X)

        print()

        print("Printing Controller Switch Mapping")

        for i in range(number_of_controllers):
            print(f"{controller_positions[i].X} --> ", end="")
            temp = np.where(controller_switch_mapping[i].X == 1)[0]
            print(f"{[list(x) for x in switches_positions[temp]]} ", end="")
            print()
        print()
        print("Printing Controller Controller Mapping")

        for i in range(number_of_controllers):
            print(f"{controller_positions[i].X} --> ", end="")
            temp = np.where(controller_controller_mapping[i].X == 1)[0]
            print(f"{controller_positions[temp].X} ", end="")
            print()
        print()
        print("Done!")

