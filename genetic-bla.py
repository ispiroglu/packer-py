import random
from PIL import Image, ImageDraw, ImageFont

def read_input(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    space_width, space_height = map(int, lines[1].strip().split())
    blocks = [tuple(map(int, line.strip().split())) for line in lines[2:]]
    return space_width, space_height, blocks

def initialize_matrix(width, height):
    return [[0 for _ in range(width)] for _ in range(height)]

def find_bottom_left_position(matrix, block):
    block_width, block_height = block
    for y in range(len(matrix)):
        for x in range(len(matrix[0])):
            if x + block_width <= len(matrix[0]) and y + block_height <= len(matrix):
                if all(matrix[j][i] == 0 for i in range(x, x + block_width) for j in range(y, y + block_height)):
                    return (x, y)
    return None

def place_block(matrix, block, block_number):
    position = find_bottom_left_position(matrix, block)
    if position is not None:
        x, y = position
        block_width, block_height = block
        for i in range(x, x + block_width):
            for j in range(y, y + block_height):
                matrix[j][i] = block_number

def print_matrix(matrix):
    for row in matrix:
        print(" ".join(str(cell).zfill(2) if cell != 0 else "00" for cell in row))

def calculate_efficiency(matrix):
    total_area = len(matrix) * len(matrix[0])
    non_zero_area = total_area - sum(row.count(0) for row in matrix)
    if total_area == 0:
        efficiency = 0
    else:
        efficiency = non_zero_area / total_area
    return efficiency

def generate_random_blocks(blocks):
    random_blocks_lists = [random.sample(blocks, len(blocks)) for _ in range(10)]
    return random_blocks_lists

def run_algorithm_with_blocks(blocks_list, space_width, space_height):
    matrix = initialize_matrix(space_width, space_height)
    block_number = 1
    for block in blocks_list:
        place_block(matrix, block, block_number)
        block_number += 1
    efficiency = calculate_efficiency(matrix)
    return matrix, efficiency

def crossover(parent1, parent2):
    crossover_point = random.randint(0, len(parent1) - 1)
    child1 = parent1[:crossover_point] + [block for block in parent2 if block not in parent1[:crossover_point]]
    child2 = parent2[:crossover_point] + [block for block in parent1 if block not in parent2[:crossover_point]]
    return child1, child2

def mutate(blocks_list, blocks):
    mutated_list = blocks_list.copy()
    index1, index2 = random.sample(range(len(mutated_list)), 2)
    temp = mutated_list[index1]
    mutated_list[index1] = mutated_list[index2]
    mutated_list[index2] = temp
    return mutated_list
    
def get_file_input():
    file_path = input("Enter the file path: ")
    return read_input(file_path)
    
def print_best_results(matrix, efficiency):
    print("\n--- Best Matrix ---")
    print_matrix(matrix)
    image_filename = "best_matrix.png"
    create_image(matrix, image_filename)
    print(f"Best Efficiency: {efficiency:.2%}")
    print(f"Image saved as {image_filename}")

def evolve_population(population, population_size, efficiency_limit, space_width, space_height, blocks):
    generation = 0
    best_matrix = None
    best_efficiency = 0.0

    while generation == 0 or max(fitness_scores) < efficiency_limit:
        print(f"\n--- Generation {generation + 1} ---")
        for i, individual in enumerate(population, 1):
            _, efficiency = run_algorithm_with_blocks(individual, space_width, space_height)
            print(f"Individual {i}: Efficiency: {efficiency:.2%}")
            if efficiency > best_efficiency:
                best_matrix, best_efficiency = run_algorithm_with_blocks(individual, space_width, space_height)
        fitness_scores = [run_algorithm_with_blocks(individual, space_width, space_height)[1] for individual in population]
        top_indices = sorted(range(len(fitness_scores)), key=lambda k: fitness_scores[k], reverse=True)[:population_size // 2]
        top_individuals = [population[i] for i in top_indices]
        new_population = []
        for _ in range(population_size):
            parent1, parent2 = random.sample(top_individuals, 2)
            child1, child2 = crossover(parent1, parent2)
            new_population.extend([mutate(child1, blocks), mutate(child2, blocks)])
        num_mutations_top = population_size // 2
        mutated_top_individuals = [mutate(individual, blocks) for individual in random.sample(top_individuals, num_mutations_top)]
        population = mutated_top_individuals + new_population[:population_size // 2]
        generation += 1

    return best_matrix, best_efficiency
    
def find_connected_regions(matrix):
    connected_regions = []
    visited = [[False] * len(matrix[0]) for _ in range(len(matrix))]

    def explore_connected_component(start_i, start_j, number):
        connected_component = []
        stack = [(start_i, start_j)]
        while stack:
            i, j = stack.pop()
            if 0 <= i < len(matrix) and 0 <= j < len(matrix[0]) and matrix[i][j] == number and not visited[i][j]:
                connected_component.append((j, i, number))
                visited[i][j] = True
                stack.append((i, j + 1))  # Move right
                stack.append((i + 1, j))  # Move down
        return connected_component
    for number in range(1, max(max(row) for row in matrix) + 1):
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                if matrix[i][j] == number and not visited[i][j]:
                    connected_component = explore_connected_component(i, j, number)
                    connected_regions.append(connected_component)
    return connected_regions

def create_gcode(matrix, filename, space_height, space_width):
    cell_size = 4
    gcode = []

    def move_to(x, y):
        gcode.append("M03 S250")
        gcode.append("G4 P0.5")
        gcode.append(f"G0 X{x} Y{y}")
        gcode.append("M03 S90")
        gcode.append("G4 P0.5")

    def draw_block(min_x, min_y, max_x, max_y, block_number):
        move_to(min_x, min_y)
        gcode.append(f"G1 X{max_x} Y{min_y} ; Block {block_number}")
        gcode.append(f"G1 X{max_x} Y{max_y} ; Block {block_number}")
        gcode.append(f"G1 X{min_x} Y{max_y} ; Block {block_number}")
        gcode.append(f"G1 X{min_x} Y{min_y} ; Block {block_number}")

    gcode.append("G1 F1000 ; Set units to millimeters")
    gcode.append("G21 ; Set units to millimeters")
    gcode.append("G90 ; Use absolute positioning")
    draw_block(0, 0, space_width*cell_size, space_height*cell_size, "Square")
    connected_regions = find_connected_regions(matrix)
    for i, region in enumerate(connected_regions, start=1):
        min_x = min(x for x, _, _ in region) * cell_size
        min_y = min(y for _, y, _ in region) * cell_size
        max_x = (max(x for x, _, _ in region) + 1) * cell_size
        max_y = (max(y for _, y, _ in region) + 1) * cell_size
        draw_block(min_x, min_y, max_x, max_y, i)

    gcode.append("M03 S250")
    gcode.append("G0 X0 Y0")
    with open(filename, 'w') as gcode_file:
        for line in gcode:
            gcode_file.write(line + '\n')

def create_image(matrix, filename):
    cell_size = 20
    font_size = 16  # Adjust the font size as needed
    image_width = len(matrix[0]) * cell_size
    image_height = len(matrix) * cell_size
    image = Image.new("RGB", (image_width, image_height), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, 0, image_width - 1, image_height - 1], outline="black", width=1)
    connected_regions = find_connected_regions(matrix)
    for region in connected_regions:
        min_x = min(x for x, _, _ in region) * cell_size
        min_y = min(y for _, y, _ in region) * cell_size
        max_x = (max(x for x, _, _ in region) + 1) * cell_size
        max_y = (max(y for _, y, _ in region) + 1) * cell_size
        width = max_x - min_x
        height = max_y - min_y
        draw.rectangle([min_x, min_y, min_x + width, min_y + height], outline="black", width=1)
        draw.text((min_x + 2, min_y + 2), str(region[0][2]).zfill(2), fill="black", font=ImageFont.truetype("arial.ttf", font_size))
    image.save(filename)

def main():
    space_width, space_height, blocks = get_file_input()
    population_size = 10
    population = generate_random_blocks(blocks)
    efficiency_limit = float(input("Enter efficiency limit: "))
    best_matrix, best_efficiency = evolve_population(population, population_size, efficiency_limit, space_width, space_height, blocks)
    print_best_results(best_matrix, best_efficiency)
    gcode_filename = "best_matrix.gcode"
    create_gcode(best_matrix, gcode_filename, space_height, space_width)
    print(f"G-code saved as {gcode_filename}")

if __name__ == "__main__":
    main()
