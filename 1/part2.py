from pulp import *

# decision variables
x1 = LpVariable("x1", 0, 1)
x2 = LpVariable("x2", 0, 1)
x3 = LpVariable("x3", 0, 1)
x4 = LpVariable("x4", 0, 1)
x5 = LpVariable("x5", 0, 1)
x6 = LpVariable("x6", 0, 1)

# objective function variable
x0 = LpVariable("x0", None, None)

# define problem
prob = LpProblem("OptimalStrategy", LpMaximize)

# objective function
prob += x0

# constraints given by payoff matrix (for the first player)
"""
[
    [0, 2, -1, -1, -1, -1],
    [-2, 0, 2, -1, -1, -1],
    [1, -2, 0, 2, -1, -1],
    [1, 1, -2, 0, 2, -1],
    [1, 1, 1, -2, 0, 2],
    [1, 1, 1, 1, -2, 0]
]
"""
# prob += x0 <= 2*x2 - x3 - x4 - x5 - x6
# prob += x0 <= -2*x1 + 2*x3 - x4 - x5 - x6
# prob += x0 <= x1 - 2*x2 + 2*x4 - x5 - x6
# prob += x0 <= x1 + x2 - 2*x3 + 2*x5 - x6
# prob += x0 <= x1 + x2 + x3 - 2*x4 + 2*x6
# prob += x0 <= x1 + x2 + x3 + x4 - 2*x5
# prob += x1 + x2 + x3 + x4 + x5 + x6 == 1

prob += x0 <= -2*x2 + x3 + x4 + x5 + x6
prob += x0 <=  2*x1 - 2*x3 + x4 + x5 + x6
prob += x0 <= -x1 + 2*x2 - 2*x4 + x5 + x6
prob += x0 <= -x1 -x2 + 2*x3 - 2*x5 + x6
prob += x0 <= -x1 -x2 -x3 + 2*x4 -2*x6
prob += x0 <= -x1 -x2 -x3 -x4 +2*x5
prob += x1 + x2 + x3 + x4 + x5 + x6 == 1

# solve
status = prob.solve(GLPK(msg = 0))

# output
i = 1
for variable in prob.variables()[1:]:
    print(f"x{i}: {value(variable)}", end = " ")
    i += 1
print(f"obj: {value(prob.objective)}")

# correct
