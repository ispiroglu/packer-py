from cProfile import run
from rectpack import newPacker, PackingBin
import matplotlib.pyplot as plt
import random

def random_color():
    return (random.random(), random.random(), random.random())

def plot_solution(packed_rectangles, bin_width, bin_height, rectangle_size):
    plt.figure()
    ax = plt.gca()
    count = 0
    for rect in packed_rectangles:
        count += 1
        x, y, w, h = rect[1], rect[2], rect[3], rect[4]
        rect = plt.Rectangle((x, y), w, h, linewidth=1, edgecolor='r', facecolor=random_color())
        ax.add_patch(rect)

    #write count to title
    plt.suptitle("Bütün Dikdörtgenler Sayisi: "  + str(rectangle_size), fontsize=12)
    plt.title("Yerleştirilen Dikdörtgenler Sayisi: " + str(count))    
    plt.xlim(0, bin_width)
    plt.ylim(0, bin_height)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()


def run_test(file_name, algo):

    # file_name = "Original/C1_1"  # Replace "txt" with the actual file extension if different
    rectangles = []
    size = 0
    bin_width, bin_height = 0,0
    try:
        with open(file_name, 'r') as file:
            size = int(file.readline().strip('\n'))
            line = file.readline().strip()#'\n' gerekebilir
            bin_width,bin_height = map(int,line.split())
            rectangles = [(int(x), int(y)) for x, y in (line.split() for line in file)]
        # print("Successfully read the file and created the array of tuples:", rectangles)
    except FileNotFoundError:
        print(f"Error: File '{file_name}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    # print("Number of rectangles: " + str(len(rectangles)))
        # Create a new packer BBF
    packer = newPacker(
        rotation=True,
        bin_algo=algo
    )

    # Add rectangles to pack
    for r in rectangles:
        packer.add_rect(*r)

    # Add a single bin with the size of the area
    packer.add_bin(bin_width, bin_height)

    # Pack the rectangles
    packer.pack()

    # Get the packed rectangles
    packed_rectangles = packer.rect_list()
    
    plot_solution(packed_rectangles, bin_width, bin_height,size)
    return len(packed_rectangles)

# algos = [PackingBin.BNF, PackingBin.BFF,  PackingBin.BBF, PackingBin.Global]
algosStr = ["BNF", "BFF", "BBF", "Global"]
results = {}

if __name__ == "__main__":
    basename = "Original/C"
    for i in range (1,8):
        for j in range (1,4):

            filename = basename + str(i) + "_" + str(j)
            # print("Testing: ", str(i) + "_" + str(j))
            total_count = 0
           
            #for algo in algos:
            #    total_count = 0
            #    for _ in range(100):
            #       count = run_test(filename, algo)
            #       total_count = total_count + count
            #    results[algosStr[algo]] = total_count / 100
            run_test(filename, PackingBin.Global)      
            # print(results)
            

            
           
           
           
            