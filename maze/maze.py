import sys
import time
import tracemalloc

###############################################################################################
# Class: Node
# Description:
# This is the class used for each cell in the Maze.
#
#
###############################################################################################
    
class Node():
    def __init__(self, state, parent, action, cost_actual = 0, cost_estimated = 0, depth = 0):        
        self.state = state
        self.parent = parent
        self.action = action

        # Cost Variables needed for algorithms
        self.cost_actual = cost_actual
        self.cost_estimated = cost_estimated
        self.cost_total = cost_actual + cost_estimated

        # Depth Variable needed for Iterative algorithms
        self.depth = depth


###############################################################################################
# Class: StackFrontier
# Description:
# Creates a Stack list object for the algorithms to use as their frontier object.
#
#
###############################################################################################

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


###############################################################################################
# Class: QueueFrontier
# Description:
# Inherits from the StackFrontier class
# Creates a Queue list object for the algorithms to use as their frontier object.
#
###############################################################################################

class QueueFrontier(StackFrontier):

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node


###############################################################################################
# Class: PriorityQueueFrontier
# Description:
# Inherits from the QueueFrontier class
# Creates a Priority Queue list object for the algorithms to use as their frontier object.
#
###############################################################################################

class PriorityQueueFrontier(QueueFrontier):

    def add(self, node):
        self.frontier.append(node)

        # Sort the queue by cost_total
        self.frontier.sort(key=lambda n: n.cost_total)


    ###############################################################################################
    # Function: get_node
    # Description:
    # Based on the provided state, returns the matching node from the frontier.
    #
    # Input:    state       The state to check existing node objects against
    # Output:   Node        The node matching the supplied state
    ###############################################################################################
    def get_node(self, state):

        # for loop to go through the nodes in the queue
        for node in self.frontier:

            # If the new node/state is already in the frontier
            if node.state == state:

                # return the node
                return node

        # Return None
        return None


    ###############################################################################################
    # Function: solve_maze
    # Description:
    # Based on the provided algorithm:
    #       * determines which class object type to set as the frontier
    #       * determines whether an iterative approach is required and what that approach will be
    # Uses a performance timer.
    # Uses a memory allocation tracer.
    # Calls the solve() function.
    # Calls the print_info() function.
    #
    # Input:    string     Which algorithm is being used to solve the maze
    # Output:   N/A
    ###############################################################################################
    def replace(self, old_node, new_node):

        # Get the index value for the old node
        index = self.frontier.index(old_node)

        # Replace the old node with the new node
        self.frontier[index] = new_node

        # Sort the queue by cost_total
        self.frontier.sort(key=lambda n: n.cost_total)


###############################################################################################
# Class: Maze
# Description:
# Reads in a txt file and creates the Maze
# Determines which class to use for which algorithm
# Performs the algorithm searching to solve the maze
# Outputs the results of the algorithm searching
#
###############################################################################################

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


    ###############################################################################################
    # Function: solve
    # Description:
    # Searches for a solution to the maze using the already set frontier
    # Based on a provided depth limit and/or algorithm:
    #       * performs the search only to the specified depth
    #       * performs additional steps for the specified algorithm
    #
    # Input:    int     (optional)     What the depth limit is 
    #           string  (optional)     Which algorithm is being used to solve the maze
    #           int     (optional)     What the f limit is
    # Output:   bool    Whether a solution was found
    ###############################################################################################

    def solve(self, depth_limit = None, algorithm = None, f_limit = None):
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

        # Check that the algorithm is not "IDA*"
        if not algorithm == "IDA*":
            # Initialize frontier to just the starting position
            start = Node(state=self.start, parent=None, action=None)
            self.frontier.add(start)

        # Check that the algorithm is "IDA*"
        if algorithm == "IDA*":

            # Add the starting node to the frontier
            self.frontier.add(self.f_start)

        # Initialize an empty explored dictionary
        # This use to be 'self.explored = set()'
        # But it was changed to accommodate the A* algorithms.
        self.explored = {}

        # Keep looping until solution found
        while True:

            # If nothing left in frontier, then no path
            if self.frontier.empty():
                self.solution = None
                return False

            # Choose a node from the frontier
            node = self.frontier.remove()
            self.num_explored += 1
            self.total_explored += 1

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
            self.explored[node.state] = node

            # Add neighbors to frontier
            for action, state in self.neighbors(node.state):

                # Add the step cost to the current actual cost
                child_cost_actual = node.cost_actual + self.step_cost

                # Calculate the heuristic value for this node
                child_cost_estimate = self.heuristic_value(state)

                # Create the child with the new actual cost of reaching it and the depth of the child
                child = Node(state=state, parent=node, action=action, cost_actual=child_cost_actual, 
                                 cost_estimated=child_cost_estimate, depth=node.depth + 1)
                
                
                if not self.frontier.contains_state(state) and state not in self.explored:

                    # Check if the algorithm is "IDA*"
                    if algorithm == "IDA*":

                        # Check if the f_limit has been reached
                        if child.cost_total > f_limit:

                            # Don't add the child to the frontier
                            # Check if the child's total_cost is lower than the next_f_limit
                            # Need to track the smallest f that exceeded the f_limit
                            if child.cost_total < self.next_f_limit:

                                # Update next_f_limit
                                self.next_f_limit = child.cost_total

                                # Continue the function
                                continue
                        else :

                            # Add the child to the frontier
                            self.frontier.add(child)

                    else :

                        # Check if the limit has been reached
                        if depth_limit is None or child.depth <= depth_limit:

                            # Add the child to the frontier
                            self.frontier.add(child)

                # Else if the algorithm is 'A*' and the state is already in the frontier
                elif algorithm == "A*" and self.frontier.contains_state(state):

                    # Retrieve the existing node
                    existing_node = self.frontier.get_node(state)

                    # Check if the new total cost is lower
                    if child.cost_total < existing_node.cost_total:

                        # Replace the existing node
                        self.frontier.replace(existing_node, child)

                # Else if the algorithm is 'A*' and the state is already in the explored set
                elif algorithm == "A*" and state in self.explored:

                    # Retrieve the existing node
                    existing_node = self.explored[state]

                    # Check if the new total cost is lower
                    if child.cost_total < existing_node.cost_total:

                        # Remove the node from the explored set
                        del self.explored[state]

                        # Add the new version of the node to frontier
                        self.frontier.add(child)


    ###############################################################################################
    # Function: solve_maze
    # Description:
    # Based on the provided algorithm:
    #       * determines which class object type to set as the frontier
    #       * determines whether an iterative approach is required and what that approach will be
    # Uses a performance timer.
    # Uses a memory allocation tracer.
    # Calls the solve() function.
    # Calls the print_info() function.
    #
    # Input:    string     Which algorithm is being used to solve the maze
    # Output:   N/A
    ###############################################################################################

    def solve_maze(self, algorithm):
        """Finds a solution to maze, if one exists."""
        """Sets variables and function calls based on the algorithm to be used"""

        print("Solving...")

        """Select the correct frontier class to use"""         
        # Set the frontier variable for non-iterative algorithms
        if algorithm == "BFS":
            self.frontier = QueueFrontier()

        elif algorithm == "DFS":
            self.frontier = StackFrontier()

        elif algorithm == "A*":
            self.frontier = PriorityQueueFrontier()

        print(f"Solving with {algorithm} algorithm")

        # Start a timer
        start_time = time.perf_counter()

        # Start memory allocation tracing
        tracemalloc.start()

        # Check if the algorithm is an iterative one
        if algorithm == "IDS":

            # Initialise limit as zero
            limit = 0

            # Initialise total explored
            self.total_explored = 0

            # Determine the maximum possible path length
            max_depth = self.height * self.width

            # While loop to perform the iterative search
            # Only stop if the limit becomes higher than the max_depth
            # This prevents infinite loops.
            while limit <= max_depth:

                # Set the frontier variable
                self.frontier = StackFrontier()

                # Perform the search with the current depth limit
                self.result = self.solve(depth_limit=limit)

                # Check if result is true
                if self.result:

                    # Break out of while loop
                    break

                # Increase limit by 1
                limit += 1

        elif algorithm == "IDA*":

            # Creat the starting node object
            self.f_start = Node(state=self.start, parent=None, action=None, cost_estimated=self.heuristic_value(self.start))

            # Initialise the f-limit value
            f_limit = self.f_start.cost_total

            # Initialise total explored
            self.total_explored = 0

            # While loop to perform the iterative search
            while True:

                # Set the frontier variable
                self.frontier = StackFrontier()

                # Set the next f limit to infinity
                self.next_f_limit = float("inf")

                # Perform the search with the current f limit
                self.result = self.solve(algorithm="IDA*", f_limit=f_limit)

                # Check if result is true
                if self.result:

                    # Break out of while loop
                    break

                # Check if next_f_limit is infinity
                if self.next_f_limit == float("inf"):

                    # Break out of while loop as there is no better f_limit
                    break

                # Change f_limit to be the next_f_limit value
                f_limit = self.next_f_limit

        # Otherwise just perform the search
        else:

            # Initialise total explored
            self.total_explored = 0

            # Perform the search
            self.result = self.solve(algorithm=algorithm)

        # End the timer
        end_time = time.perf_counter()

        # Get the current and peak memory allocation
        self.memory_current, self.memory_peak = tracemalloc.get_traced_memory()

        # Stop memory allocation tracing
        tracemalloc.stop()

        # Calculate the length of time it took in milliseconds
        self.total_time = (end_time - start_time) * 1000

        # Print the results of the algorithm's search
        self.print_info(algorithm)        


    ###############################################################################################
    # Function: heuristic_value
    # Description:
    # Calculates how many steps are required from the state's cell to reach the goal.
    # This calcuation assumes that there are no walls blocking the path.
    #
    # Input:    state   The state for which the heuristic value needs to be calculated
    # Output:   int     The number of steps to get from this state to the goal state
    ###############################################################################################

    def heuristic_value(self, state):

        # Get the cell's row and column number from state
        row, col = state

        # Get the goal's row and column number from the goal variable
        goal_row, goal_col = self.goal

        # Get the absolute values for how many rows and columns to move through
        count_row = abs(row - goal_row)
        count_col = abs(col - goal_col)

        # Return the total steps from the cell to the goal
        return count_row + count_col



    ###############################################################################################
    # Function: print_info
    # Description:
    # Prints various information/stats regarding the search for the maze solution 
    # for the supplied algorithm
    # Calls the print() function
    # Calls the output_image() function
    #
    # Input:    string     Which algorithm was used to solve the maze
    # Output:   N/A
    ###############################################################################################

    def print_info(self, algorithm):

        # Check if the result is false
        if not self.result:
            print(f"No solution found using the {algorithm} algorithm")

        # Print the algorithm's time
        print(f"Time {algorithm} algorithm took: {self.total_time:.4f} ms ")

        # Print the algorithm's memory usage
        print(f"{algorithm} algorithm had a peak memory usage of: {self.memory_peak} bytes")

        print("States Explored:", self.num_explored)

        # Check if the algorithm is iterative
        if algorithm == "IDS" or algorithm == "IDA*":

            # Print total States Explored
            print("Total States Explored:", self.total_explored)

        # Check if the result is true
        if self.result:

            # Print the length of the solution path
            print("Solution Path Length:", self.path_length)

            # Print the cost of the solution path
            print("Solution Path Cost:", self.path_cost)

            # Print the solution path
            print("Solution Moves: ", "-".join(self.solution_moves))

            print(f"Solution using {algorithm}:")
            self.print()

            # Check if the algorithm contains a '*'
            if algorithm.__contains__("*"):

                # Strip out the '*' from the algorithm's name
                name = algorithm.strip("*")

                # Output the image
                self.output_image(f"{name}_{self.filename}.png", show_explored=True)

            # Otherwise output the image
            else:    
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

"""Using BFS algorithm"""
m.solve_maze("BFS")

"""Using DFS algorithm"""
m.solve_maze("DFS")

"""Using IDS algorithm"""
m.solve_maze("IDS")

"""Using A* algorithm"""
m.solve_maze("A*")

"""Using IDA* algorithm"""
m.solve_maze("IDA*")
