from pulp import *
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# solver = COIN_CMD(path="/usr/bin/cbc",threads=8) # solver

def bakery():
    # Input file is called ./bakery.txt
    input_filename = './bakery.txt'
    
    with open(input_filename) as file:
        pastry_file = file.readlines()
    
    n = len(pastry_file) 
    
    pastry = {} # dict to contain the bakery info
    for i in range(n):
        pastry_type = pastry_file[i].split() # e.g. for i = 0 we get ['0', '4800', '9600', '600']
        pastry[i] = {"PRE": int(pastry_type[1]),
                    "DLN": int(pastry_type[2]),
                    "BAK": int(pastry_type[3])}
        
    # problem
    prob = LpProblem("Bakery's Oven", LpMinimize)

    # variables
    f = LpVariable("Total Finishing Time", lowBound=0) # objective variable
    s = LpVariable.dicts("s", range(n), lowBound=0) # starting time
    x = LpVariable.dicts("x", [(i, j) for i in range(n) for j in range(n)], cat="Binary") # big-M variable

    # objective
    prob += f
    
    # possible suitable value for M
    M = pastry[1]["BAK"] + pastry[1]["DLN"] #27600

    # add constraints
    for i in range(n):
        prob += s[i] + pastry[i]["BAK"] <= pastry[i]["DLN"] # each pastry finishes before the deadline
        prob += s[i] >= pastry[i]["PRE"] # each pastry starts only when ready for baking
        prob += f >= s[i] + pastry[i]["BAK"] # finishing time is maximal
        for j in range(n):
            if j > i:
                # big-M constraints
                prob += s[i] + pastry[i]["BAK"] <= s[j] + M * x[(i,j)]
                prob += s[j] + pastry[j]["BAK"] <= s[i] + M * (1 - x[(i,j)])


    # solve the problem
    # prob.solve(solver)
    prob.solve()

    retval = {}
    for i in list(pastry.keys()):
        retval[f"s_{i}"] = s[i].value()
    
    # plot
    with plt.style.context("bmh"):

        # font definition and other stuff
        plt.rcParams['font.family'] = 'serif'
        plt.rcParams['font.serif'] = 'Ubuntu'
        plt.rcParams['font.monospace'] = 'Ubuntu Mono'
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.labelsize'] = 10
        plt.rcParams['axes.labelweight'] = 'bold'
        plt.rcParams['xtick.labelsize'] = 8
        plt.rcParams['ytick.labelsize'] = 8
        plt.rcParams['legend.fontsize'] = 10
        plt.rcParams['figure.titlesize'] = 12
        
        start_times = [s[i].value() for i in range(n)] # start times from solution

        # list of colors for each pastry
        colors = ["#FFD93D", # pre
                "#FF8400", # baking (normal)
                "#4F200D", # deadline
                "#FAFF00", # baking whenever ready for it
                "#FF0500", # deadline whenever baking ends
                "#7BFF00" # edge case: bake when ready and ends with deadline
                ]
        
        # Gantt chart
        fig, (ax, ax1) = plt.subplots(2, figsize=(16.5,6), gridspec_kw={'height_ratios':[8, 1.3]})
        
        for i in range(n):
            if pastry[i]["PRE"] == start_times[i] and start_times[i] + pastry[i]["BAK"] == pastry[i]["DLN"]: 
                ax.broken_barh([(start_times[i]/3600, pastry[i]["BAK"]/3600)], (i, 0.95), facecolors=colors[5], edgecolors="black") # edge case
            elif start_times[i] + pastry[i]["BAK"] == pastry[i]["DLN"]:
                ax.broken_barh([(start_times[i]/3600, pastry[i]["BAK"]/3600)], (i, 0.95), facecolors=colors[4], edgecolors="black") # deadline whenever baking ends 
            elif pastry[i]["PRE"] == start_times[i] :
                ax.broken_barh([(start_times[i]/3600, pastry[i]["BAK"]/3600)], (i, 0.95), facecolors=colors[3], edgecolors="black") # baking whenever ready for it
            else: 
                ax.broken_barh([(start_times[i]/3600, pastry[i]["BAK"]/3600)], (i, 0.95), facecolors=colors[1], edgecolors="black") # baking (normal)
                
            ax.broken_barh([(pastry[i]["PRE"]/3600, start_times[i]/3600 - pastry[i]["PRE"]/3600)], (i, 0.95), facecolors = colors[0], edgecolors = "black") # pre
            ax.broken_barh([((start_times[i]/3600 + pastry[i]["BAK"]/3600), pastry[i]["DLN"]/3600 - start_times[i]/3600 - pastry[i]["BAK"]/3600)], (i, 0.95), facecolors=colors[2], edgecolors="black") # waiting time
            ax.text(start_times[i]/3600+pastry[i]["BAK"]/7200, i+0.5, f"{i}", ha="center", va="center") # pastry ID
        
        # decorations        
        ax.set_xlabel("Hours (from midnight)", fontweight = "bold")
        ax.set_ylabel("Pastry", fontweight = "bold")
        ax.set_yticks(range(n))
        ax.set_yticklabels("")
        ax.set_xlim([-0.1, 8])
        ax.set_ylim([-0.1, n+0.1])
        ax.text(0,18, "NOTE: please, consult the recipe manual for each pastry's baking time.", style = "italic")
        time_hours = int(prob.objective.value()/3600)
        time_minutes = int((prob.objective.value()/3600 - time_hours)*60)
        ax.axvline(x = prob.objective.value()/3600, color = "blue")
        ax.text(x = prob.objective.value()/3600 + 0.075, y = 7.2, s = f"Optimal Finishing Time\n{time_hours}:{time_minutes}AM", color = "blue")
        plt.suptitle('Bakery Schedule', fontweight = "bold")
        
        
        # legends
        legend_elements = [Patch(facecolor=colors[0], label='Pastry is Ready for Baking', edgecolor="black"),
                        Patch(facecolor=colors[2], label='Maximum Deadline For Pastry\'s Finishing Time', edgecolor="black"),
                        Patch(facecolor=colors[1], label='Baking Time (normal)', edgecolor="black"),
                        Patch(facecolor=colors[3], label = "Baking Time (begin baking when ready for it)", edgecolor="black"),
                        Patch(facecolor=colors[4], label = "Baking Time (end baking at deadline)", edgecolor="black"),
                        Patch(facecolor=colors[5], label="Baking Time (begin when ready and end at deadline)", edgecolor="black")
                        ]
        
        legend = ax1.legend(handles=legend_elements, loc='upper center', ncol=3, frameon=True)
        plt.setp(legend.get_texts())
        
        ax1.spines['right'].set_visible(False)
        ax1.spines['left'].set_visible(False)
        ax1.spines['top'].set_visible(False)
        ax1.spines['bottom'].set_visible(False)
        ax1.set_xticks([])
        ax1.set_yticks([])
        
    # Write visualization to the correct file:
    visualization_filename = './visualization.png'
    plt.savefig(visualization_filename)

    return retval
