from pulp import *

# define the problem
prob = LpProblem("prob", LpMinimize)

# decision variables
x = [LpVariable(f"x{i}", 0, None) for i in range(1, 70)]

# objective function
prob += lpSum(x)

# reading the file
contract_relationship = []
with open("./hw1-03.txt", "r") as file:
    for line in file:
        contract_relationship.append(list(map(int, line.split())))

# adding all constraints of the type x_i + x_j >= 2
for i in range(len(contract_relationship)):
    prob += x[contract_relationship[i][0] - 1] + x[contract_relationship[i][1] - 1] >= 2
              
status = prob.solve(GLPK(msg = 0))

# output
for x in prob.variables():
    print(f"representatives from company {x.name[1:]} : {x.varValue}")
    
print(f"Total number of representatives involved: {value(prob.objective)}")

# correct
