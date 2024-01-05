
import rectangle_packing_solver as rps
from main import read_rectangles

# Define a problem

rectangles, size, bin_width, bin_height = read_rectangles("Original/C1_1")
rectangles = [{"width": rect[0], "height": rect[1], "rotatable": True} for rect in rectangles]


problem = rps.Problem(
rectangles=rectangles)
print("problem:", problem)

# Find a solution
print("\n=== Solving without width/height constraints ===")

solution = rps.Solver().solve(
    problem=problem, 
    height_limit=bin_height, 
    width_limit=bin_width,  
    simanneal_minutes=.3, 
    simanneal_steps=10000, 
    show_progress=True
    )
# print("solution:", solution)

# Visualization (to floorplan.png)
rps.Visualizer().visualize(solution=solution, path="./floorplan.png")

# [Other Usages]
# We can also give a solution width (and/or height) limit, as well as progress bar and random seed
#print("\n=== Solving with width/height constraints ===")
#solution = rps.Solver().solve(problem=problem, simanneal_minutes=)
#print("solution:", solution)
#rps.Visualizer().visualize(solution=solution, path="./floorplan_limit.png")