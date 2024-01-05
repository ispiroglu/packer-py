import random
from time import sleep
from PIL import Image, ImageDraw, ImageFont
import os


def read_input(file_path):
    temp_path = "Original/"
    temp_path = temp_path + file_path
    if not os.path.exists(temp_path):
        print("No such file!\n")
        return None, None, None, None
    else:
        with open(temp_path, 'r') as file:
            lines = file.readlines()
        space_width, space_height = map(int, lines[1].strip().split())
        blocks = [tuple(map(int, line.strip().split())) for line in lines[2:]]
        return space_width, space_height, blocks, file_path


def initialize_matrix(width, height):
    return [[0 for _ in range(width)] for _ in range(height)]


def find_bottom_left_position(matrix, block):
    block_width, block_height = block
    for y in range(len(matrix)):
        for x in range(len(matrix[0])):
            if x + block_width <= len(matrix[0]) and y + block_height <= len(matrix):
                if all(matrix[j][i] == 0 for i in range(x, x + block_width) for j in range(y, y + block_height)):
                    return x,y
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


def get_file_input(mod, i, j):
    if mod == 0:
        file_path = input("Enter the filename: ")
    else:
        file_path = "C" + str(i) + "_" + str(j)
    return read_input(file_path)


def print_best_results(path, matrix, efficiency):
    print("\n--- Best Matrix ---")
    print_matrix(matrix)
    img_path_tmp = "Images/"
    img_path_tmp = img_path_tmp + path + ".png"
    create_image(matrix, img_path_tmp)
    print(f"Best Efficiency: {efficiency:.2%}")
    print(f"Image saved as {img_path_tmp}")


def evolve_population(population, population_size, efficiency_limit, space_width, space_height, blocks):
    generation = 0
    best_matrix = None
    best_efficiency = 0.0
    #fitness_scores = 0
    
    max_fitness_scores = 0
    while (generation == 0 or max_fitness_scores < efficiency_limit):
        print(f"\n--- Generation {generation + 1} ---")
        fitness_scores = []
        
        print("Fitness Scores:", fitness_scores)
        for i, individual in enumerate(population, 1):
            matrix, efficiency = run_algorithm_with_blocks(individual, space_width, space_height)
            fitness_scores.append(efficiency)
            print(f"Individual {i}: Efficiency: {efficiency:.2%}")
            
            # Neden tekrardan hesaplıyoruz? 
            if efficiency > best_efficiency:
                best_matrix, best_efficiency = matrix, efficiency
                # Neden tekrar hesaplıyoruz, tutsaydık ya? 
                
        max_fitness_scores = max(fitness_scores)
        top_indices = sorted(range(len(fitness_scores)), key=lambda k: fitness_scores[k], reverse=True)[
                      :population_size // 2]
        top_individuals = [population[i] for i in top_indices]
        new_population = []
        for _ in range(population_size):
            parent1, parent2 = random.sample(top_individuals, 2)
            child1, child2 = crossover(parent1, parent2)
            new_population.extend([mutate(child1, blocks), mutate(child2, blocks)])
        num_mutations_top = population_size // 2
        mutated_top_individuals = [mutate(individual, blocks) for individual in
                                   random.sample(top_individuals, num_mutations_top)]
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
    filename_temp = "gCodes/"
    filename_temp = filename_temp + filename + ".gcodes"

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
    draw_block(0, 0, space_width * cell_size, space_height * cell_size, "Square")
    connected_regions = find_connected_regions(matrix)
    for i, region in enumerate(connected_regions, start=1):
        min_x = min(x for x, _, _ in region) * cell_size
        min_y = min(y for _, y, _ in region) * cell_size
        max_x = (max(x for x, _, _ in region) + 1) * cell_size
        max_y = (max(y for _, y, _ in region) + 1) * cell_size
        draw_block(min_x, min_y, max_x, max_y, i)

    gcode.append("M03 S250")
    gcode.append("G0 X0 Y0")
    with open(filename_temp, 'w') as gcode_file:
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
        draw.text((min_x + 2, min_y + 2), str(region[0][2]).zfill(2), fill="black",
                  font=ImageFont.truetype("Verdana.ttf", font_size))
    image.save(filename)


def generateForAll():
    population_size = 10
    efficiency_limit = float(input("Enter efficiency limit: "))
    j = 1
    i = 1
    while i <= 7:
        space_width, space_height, blocks, gcode_filename = get_file_input(1, i, j)
        if not space_width is None:
            population = generate_random_blocks(blocks)
            best_matrix, best_efficiency = evolve_population(population, population_size, efficiency_limit, space_width,
                                                             space_height, blocks)
            print_best_results(gcode_filename,best_matrix, best_efficiency)
            create_gcode(best_matrix, gcode_filename, space_height, space_width)
            print(f"G-code saved as {gcode_filename}")
        j += 1
        if j == 4:
            j = 1
            i = i + 1


def generateForOne():
    space_width, space_height, blocks, gcode_filename = get_file_input(0, 0, 0)
    if not space_width is None:
        population_size = 10
        population = generate_random_blocks(blocks)
        
        efficiency_limit = float(input("Enter efficiency limit: "))
        best_matrix, best_efficiency = evolve_population(population, population_size, efficiency_limit, space_width,
                                                         space_height, blocks)
        print_best_results(gcode_filename, best_matrix, best_efficiency)
        create_gcode(best_matrix, gcode_filename, space_height, space_width)
        print(f"G-code saved as {gcode_filename}")


def main():
    if not os.path.exists("Images"):
        os.mkdir("Images")
    if not os.path.exists("gCodes"):
        os.mkdir("gCodes")

    mod = input("Enter mod:\nType 'Single' for only one file.\nType'All' for all files\n")
    if mod == 'Single':
        generateForOne()
    elif mod == 'All':
        generateForAll()
    else:
        print("undefined input.\n")


if __name__ == "__main__":
    main()
