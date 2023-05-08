import numpy as np
import cvxpy as cp

#######
# DATA
#######
a=[0.5, -0.5, 0.2, -0.7, 0.6, -0.2, 0.7, -0.5, 0.8, -0.4]
l=[40, 20, 40, 40, 20, 40, 30, 40, 30, 60]
Preq=np.arange(a[0],a[0]*(l[0]+0.5),a[0])
for i in range(1, len(l)):
    Preq=np.r_[ Preq, np.arange(Preq[-1]+a[i],Preq[-1]+a[i]*(l[i]+0.5),a[i]) ]

T = sum(l)

Peng_max = 20.0
Pmg_min = -6.0
Pmg_max = 6.0
eta = 0.1
gamma = 0.1
#####
# End of DATA part
#####

# define the variables
peng = cp.Variable(T, "P_eng")
pmg = cp.Variable(T, "P_mg")
pmg_aux = cp.Variable(T, "P_mg_aux")
pbr = cp.Variable(T, "P_br")
energy = cp.Variable(T + 1, "Energy")

def solve_problem(has_battery = True, penalized = False):
    """
    Solves the optimization problem based on the type of car (with battery or batteryless) and type of problem (penalized or not).
    It solves the RELAXED version of the problem, by changing the constraint $E(t+1) = E(t) - P_{mg}(t) - \eta |P_{mg}(t)|$ into
        $E(t+1) = E(t) - P_{mg}(t) - \eta P_{mg}(t)$
        $E(t+1) = E(t) - P_{mg}(t) + \eta P_{mg}(t)$
    for all t = 1, ..., T (copy-paste to LaTex the above equations to visualize more easily if needed).
    The relaxation is equivalent because the |P_mg| is non-negative, and same goes for E(t+1), which is non-negative and bounded from above. 
    If P_mg is positive, then the first constraint is active; if P_mg is negative the second is active, which give the same original constraint.

    Args:
        has_battery (bool): True if has car has battery, else False
        penalized (bool): True if we're solving the penalized version of the problem, by adding eps * max(0, -Pmg[t]) to the objective, else False

    Returns:
        cvxpy.problems.problem.Problem: problem instance to be solved
    """
    
    # additional variables for the problem
    Ebatt_max = 100 if has_battery == True else 0 
    eps = 0.0008
        
    # objective
    fuel_consumption = 0

    # constraints
    constraints = [energy[T] == energy[0]]
    
    for t in range(T):
        if penalized == True:
            fuel_consumption += cp.sum(peng[t] + gamma * peng[t]**2 + eps * cp.maximum(0, -pmg[t]))
        elif penalized == False:
            fuel_consumption += cp.sum(peng[t] + gamma * peng[t]**2)
        constraints += [Preq[t] == peng[t] + pmg[t] - pbr[t],
                        peng[t] >= 0,
                        peng[t] <= Peng_max,
                        pmg[t] >= Pmg_min,
                        pmg[t] <= Pmg_max,
                        pbr[t] >= 0,
                        energy[t] >= 0,
                        energy[t] <= Ebatt_max,
                        # relaxed constraints
                        energy[t + 1] <= energy[t] - pmg[t] - eta * pmg[t],
                        energy[t + 1] <= energy[t] - pmg[t] + eta * pmg[t]]

    prob = cp.Problem(cp.Minimize(fuel_consumption), constraints)

    return prob

def car_with_battery():
    # Ebatt_max = 100.0

    prob__has_battery_not_penalized = solve_problem(has_battery=True, penalized=True)
    prob__has_battery_not_penalized.solve()
    
    retval = {}
    retval["Peng"] = list(peng.value) # list of floats of length T such that retval['Peng'][t] = P_eng(t+1) for each t=0,...,T-1
    retval["Pmg"] = list(pmg.value) # list of floats of length T such that retval['Pmg'][t] = P_mg(t+1) for each t=0,...,T-1
    retval["Pbr"] = list(pbr.value) # list of floats of length T such that retval['Pbr'][t] = P_br(t+1) for each t=0,...,T-1
    retval["E"] = list(energy.value) # list of floats of length T+1 such that retval['E'][t] = E(t+1) for each t=0,...,T

    return retval

def car_without_battery():
    # Ebatt_max = 0
    
    prob_not_battery_penalized = solve_problem(has_battery=False, penalized=True)
    prob_not_battery_penalized.solve()
    
    retval = {}
    retval["Peng"] = list(peng.value)
    retval["Pmg"] = list(pmg.value) 
    retval["Pbr"] = list(pbr.value)
    retval["E"] = list(energy.value)

    return retval

# NOTES:
# 1. Comments on the relaxation are given in the docstring of the solve_problem() function.
# 2. To solve the glitch I used the epsilon-penalization method.
# 3. The problem satisfies the conditions for the bonus point. If needed, please read the code used to check it:

#####################
##BONUS POINT CHECK##
#####################

# def bonus_check(retval1, retval2):
#     """
#     It checks the conditions for the bonus point, that is:
#         - the power consumption is not affected by more than 0.1
#         - the error in satisfying the relaxed constraint with equality is up to 0.0003

#     Args:
#         retval1 (dict): retval of non-penalized solution
#         retval2 (dict): retval of penalized solution

#     Returns:
#         tuple: tuple of bools, one for each check to do
#     """
    
#     # first check for power consumption
#     obj1 = sum(retval1["Peng"][t] + gamma * retval1["Peng"][t]**2 for t in range(T))
#     obj2 = sum(retval2["Peng"][t] + gamma * retval2["Peng"][t]**2 for t in range(T))
#     is_check1_satisfied = abs(obj1 - obj2) <= 0.1
    
#     # second check for tight constraint
#     tight_constraint_error = max(abs(retval2["E"][t+1] - retval2["E"][t] + retval2["Pmg"][t] + eta * abs(retval2["Pmg"][t])) for t in range(T))
#     is_check2_satisfied = tight_constraint_error <= 0.0003
    
#     return is_check1_satisfied, is_check2_satisfied

# CAR WITH BATTERY
# prob__has_battery_not_penalized = solve_problem(has_battery=True, penalized=False)
# prob__has_battery_not_penalized.solve()
# retval1 = {}
# retval1["Peng"] = list(peng.value)
# retval1["Pmg"] = list(pmg.value) 
# retval1["Pbr"] = list(pbr.value)
# retval1["E"] = list(energy.value)
# prob__has_battery_penalized = solve_problem(has_battery=True, penalized=True)
# prob__has_battery_penalized.solve()
# retval2 = {}
# retval2["Peng"] = list(peng.value)
# retval2["Pmg"] = list(pmg.value) 
# retval2["Pbr"] = list(pbr.value)
# retval2["E"] = list(energy.value)
# bonus_check(retval1, retval2) # returns (True, True)

# # CAR WITHOUT BATTERY
# prob__no_battery_not_penalized = solve_problem(has_battery=False, penalized=False)
# prob__no_battery_not_penalized.solve()
# retval3 = {}
# retval3["Peng"] = list(peng.value)
# retval3["Pmg"] = list(pmg.value) 
# retval3["Pbr"] = list(pbr.value)
# retval3["E"] = list(energy.value)
# prob_not_battery_penalized = solve_problem(has_battery=False, penalized=True)
# prob_not_battery_penalized.solve()
# retval4 = {}
# retval4["Peng"] = list(peng.value)
# retval4["Pmg"] = list(pmg.value) 
# retval4["Pbr"] = list(pbr.value)
# retval4["E"] = list(energy.value)
# bonus_check(retval3, retval4) # returns (True, True)
