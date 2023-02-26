from pulp import *

# decision variables
x = LpVariable("x", -10, None)
y = LpVariable("y", None, 10)

# define the linear program
prob = LpProblem("prob", LpMinimize) 

# objective function
prob += 122 * x + 143 * y

# constraints
prob += 3 * x + 2 * y <= 10
prob += 12 * x + 14 * y >= -12.5
prob += 2 * x + 3 * y >= 3
prob += 5 * x - 6 * y >= -100

# solution
status = prob.solve(GLPK(msg = 0))

# check tight constraints
tight = []
if value(x) == -10:
    tight.append(1)
if value(y) == 10:
    tight.append(2)
if 3 * value(x) + 2 * value(y) == 10:
    tight.append(3)
if 12 * value(x) + 14 * value(y) == -12.5:
    tight.append(4)
if 2 * value(x) + 3 * value(y) == 3:
    tight.append(5)
if 5 * value(x) - 6 * value(y) == -100:
    tight.append(6)

# output
print(f"Optimal solution: x = {value(x)} y = {value(y)}")
print(f"Objective value: {value(prob.objective)}")
print("Tight constraints:", end = " ")
for a in tight:
    print(a, end = " ")
    
# correct
