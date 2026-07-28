import sys
import time
import tracemalloc

class Node():
    def __init__(self, state, parent, action, cost_actual = 0, cost_estimated = 0):        
        self.state = state
        self.parent = parent
        self.action = action

        # Cost Variables needed for algorithms
        self.cost_actual = cost_actual
        self.cost_estimated = cost_estimated
        self.cost_total = cost_actual + cost_estimated


class StackFrontier():
    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node



class QueueFrontier(StackFrontier):

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node

class Maze():

    def __init__(self, filename):

        # Read file and set height and width of maze
        with open(filename) as f:
            contents = f.read()

        # Validate start and goal
        if contents.count("A") != 1:
            raise Exception("maze must have exactly one start point")
        if contents.count("B") != 1:
            raise Exception("maze must have exactly one goal")

        # Determine height and width of maze
        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

        # Keep track of walls
        self.walls = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    if contents[i][j] == "A":
                        self.start = (i, j)
                        row.append(False)
                    elif contents[i][j] == "B":
                        self.goal = (i, j)
                        row.append(False)
                    elif contents[i][j] == " ":
                        row.append(False)
                    else:
                        row.append(True)
                except IndexError:
                    row.append(False)
            self.walls.append(row)

        self.solution = None

        # Store the filename without the file type
        self.filename = filename.removesuffix(".txt")


    def print(self):
        solution = self.solution[1] if self.solution is not None else None
        print()
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    print("█", end="")
                elif (i, j) == self.start:
                    print("A", end="")
                elif (i, j) == self.goal:
                    print("B", end="")
                elif solution is not None and (i, j) in solution:
                    print("*", end="")
                else:
                    print(" ", end="")
            print()
        print()


    def neighbors(self, state):
        row, col = state
        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1))
        ]

        result = []
        for action, (r, c) in candidates:
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                result.append((action, (r, c)))
        return result


    def solve(self):
        """Finds a solution to maze, if one exists."""

        # Keep track of number of states explored - set to zero
        self.num_explored = 0

        # Set a Step Cost, since all steps cost the same
        self.step_cost = 1

        # Ensure that the solution variables are empty
        self.solution = None
        self.solution_moves = []
        self.path_length = 0
        self.path_cost = 0

        # Initialize frontier to just the starting position
        start = Node(state=self.start, parent=None, action=None)
        self.frontier.add(start)

        # Initialize an empty explored set
        self.explored = set()

        # Keep looping until solution found
        while True:

            # If nothing left in frontier, then no path
            if self.frontier.empty():
                self.solution = None
                return False

            # Choose a node from the frontier
            node = self.frontier.remove()
            self.num_explored += 1

            # If node is the goal, then we have a solution
            if node.state == self.goal:

                # Set the node as the goal node
                goal_node = node

                # Set the actual cost of the goal node as the path cost
                self.path_cost = goal_node.cost_actual

                actions = []
                cells = []
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)

                # Dictionary for converting actions to L-U-R-D format
                action_map = {
                    "up": "U",
                    "down": "D",
                    "left": "L",
                    "right": "R"
                }
                
                # Store a L-U-R-D formatted list for the solution
                self.solution_moves = [action_map[a] for a in actions]

                # Calculate path length
                self.path_length = len(cells)                

                return True

            # Mark node as explored
            self.explored.add(node.state)

            # Add neighbors to frontier
            for action, state in self.neighbors(node.state):
                if not self.frontier.contains_state(state) and state not in self.explored:
                    # Add the step cost to the current actual cost
                    child_cost_actual = node.cost_actual + self.step_cost
                    # Create the child with the new actual cost of reaching it
                    child = Node(state=state, parent=node, action=action, cost_actual=child_cost_actual)
                    self.frontier.add(child)

    def solve_maze(self):
        """Finds a solution to maze, if one exists."""
        """Uses different algorithms"""

        print("Solving...")

        """Using BFS algorithm"""         
        # Set the frontier variable   
        self.frontier = QueueFrontier()

        print("Solving with BFS algorithm")

        # Start a timer
        start_time = time.perf_counter()

        # Start memory allocation tracing
        tracemalloc.start()

        # Perform the search
        self.result = self.solve()

        # End the timer
        end_time = time.perf_counter()

        # Get the current and peak memory allocation
        self.memory_current, self.memory_peak = tracemalloc.get_traced_memory()

        # Stop memory allocation tracing
        tracemalloc.stop()

        # Calculate the length of time it took in milliseconds
        self.total_time = (end_time - start_time) * 1000

        # Print the results of the algorithm's search
        self.print_info("BFS")

        """Using DFS algorithm"""
        # Set the frontier variable
        self.frontier = StackFrontier()

        print("Solving with DFS algorithm")

        # Start a timer
        start_time = time.perf_counter()
        
        # Start memory allocation tracing
        tracemalloc.start()

        # Perform the search
        self.result = self.solve()

        # End the timer
        end_time = time.perf_counter()
        
        # Get the current and peak memory allocation
        self.memory_current, self.memory_peak = tracemalloc.get_traced_memory()
        
        # Stop memory allocation tracing
        tracemalloc.stop()
        
        # Calculate the length of time it took in milliseconds
        self.total_time = (end_time - start_time) * 1000
        
        # Print the results of the algorithm's search
        self.print_info("DFS")


    def print_info(self, algorithm):

        # Check if the result is false
        if not self.result:
            print(f"No solution found using the {algorithm} algorithm")

        # Print the algorithm's time
        print(f"Time {algorithm} algorithm took to solve the maze: {self.total_time:.4f} ms ")

        # Print the algorithm's memory usage
        print(f"{algorithm} algorithm had a peak memory usage of: {self.memory_peak} bytes")

        print("States Explored:", self.num_explored)

        # Print the length of the solution path
        print("Solution Path Length:", self.path_length)

        # Print the cost of the solution path
        print("Solution Path Cost:", self.path_cost)

        # Print the solution path
        print("Solution Moves: ", "-".join(self.solution_moves))

        print(f"Solution using {algorithm}:")
        self.print()
        self.output_image(f"{algorithm}_{self.filename}.png", show_explored=True)



    def output_image(self, filename, show_solution=True, show_explored=False):
        from PIL import Image, ImageDraw
        cell_size = 50
        cell_border = 2

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.width * cell_size, self.height * cell_size),
            "black"
        )
        draw = ImageDraw.Draw(img)

        solution = self.solution[1] if self.solution is not None else None
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):

                # Walls
                if col:
                    fill = (40, 40, 40)

                # Start
                elif (i, j) == self.start:
                    fill = (255, 0, 0)

                # Goal
                elif (i, j) == self.goal:
                    fill = (0, 171, 28)

                # Solution
                elif solution is not None and show_solution and (i, j) in solution:
                    fill = (220, 235, 113)

                # Explored
                elif solution is not None and show_explored and (i, j) in self.explored:
                    fill = (212, 97, 85)

                # Empty cell
                else:
                    fill = (237, 240, 252)

                # Draw cell
                draw.rectangle(
                    ([(j * cell_size + cell_border, i * cell_size + cell_border),
                      ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)]),
                    fill=fill
                )

        img.save(filename)


if len(sys.argv) != 2:
    sys.exit("Usage: python maze.py maze.txt")

m = Maze(sys.argv[1])
print("Maze:")
m.print()

m.solve_maze()

