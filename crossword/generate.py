import sys

from crossword import *
import time
import copy


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())


    # ============================================================
    # Function Name: enforce_node_consistency
    # Purpose: Remove words from each variable’s domain that do not
    #          match the variable’s required length.
    # Notes: Unary constraint enforcement.
    # ============================================================

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # For loop through the domains dictionary variable
        for var, values in self.domains.items():

            # Create a new set for values
            possible_words = set()

            # For loop through each var's set of words (values)
            for v in values:

                # Check if the word length equals that of the var's length
                if len(v) == var.length:

                    # Add the word to the new set
                    possible_words.add(v)

            # Set the var's value to be the new set
            self.domains[var] = possible_words


    # ============================================================
    # Function Name: revise
    # Purpose: Enforce arc consistency between variables x and y by
    #          removing values from x’s domain that have no matching
    #          value in y’s domain at the overlap position.
    # Notes: Returns True if domain of x was changed.
    # ============================================================

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # Get the overlap result
        overlap = self.crossword.overlaps[(x, y)]

        # Check if overlap exists
        if overlap is None:

            # Return false as there is no overlap
            # This means that no changes will occur
            return False

        # Get the overlap indexes
        x_index, y_index = overlap        

        # Set a revised variable
        revised = False

        # Create a new set for values
        new_words = set()        

        # For each word in the set of values for x
        for x_value in self.domains[x]:
        
            # For each word in the set of values for y
            for y_value in self.domains[y]:
        
                # Check if the letter at the index values match
                if x_value[x_index] == y_value[y_index]:
        
                    # Add the word to the new set
                    new_words.add(x_value)

                    # Break out of the current loop as a match has been found
                    break
                
        # Check if the new set of words is smaller than the old set
        if len(new_words) < len(self.domains[x]):

            # Set x's value to be the new set
            self.domains[x] = new_words
        
            # Update revised to true
            revised = True
        
        # Return revised
        return revised


    # ============================================================
    # Function Name: ac3
    # Purpose: Enforce arc consistency across all variable pairs.
    # Notes: Implements the AC-3 algorithm using a queue of arcs.
    # ============================================================

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        # If arcs equals None
        if arcs is None:

            # Create a temporary list for arcs
            arcs_list = []

            # For loop through the domains dictionary variable
            for var in self.domains.keys():

                # For loop through the variable's neighbors
                for y in self.crossword.neighbors(var):

                    # Add the pair to arcs_list
                    arcs_list.append((var, y))

        # Else arcs is not None
        else:

            # Create a tempory list using the provided arcs
            arcs_list = arcs

        # While loop to go through the temporary list and enforce arc consistency
        # Runs until the list is empty
        while arcs_list:

            # Retrieve the first pair in the list
            x, y = arcs_list.pop(0)

            # If revise updates domains
            if self.revise(x, y):

                # Check if the domain for x is empty
                if not self.domains[x]:

                    # Return false as an error has been detected
                    return False

                # For loop through x's neighbors
                for z in self.crossword.neighbors(x):

                    # Check that z does not equal y
                    if z != y:
                
                        # Add the pair in reverse order to arcs_list
                        arcs_list.append((z, x))

        # Return true as the list is empty
        return True


    # ============================================================
    # Function Name: assignment_complete
    # Purpose: Check whether all crossword variables have assigned
    #          values in the assignment dictionary.
    # Notes: Completeness check only; does not verify consistency.
    # ============================================================

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """

        # Check if assignment has the same number of variables as domain doees
        if len(assignment.keys()) == len(self.domains.keys()):

            # Return true to indicate that assignment is complete
            return True

        # else the numbers are not the same
        else:

            # Return false to indicate that assignment is not complete
            return False


    # ============================================================
    # Function Name: consistent
    # Purpose: Verify that the current assignment is valid:
    #          - All words are distinct
    #          - All overlapping letters match
    # Notes: Does not check completeness.
    # ============================================================

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        # Create a set from the assignment's values
        words = set(assignment.values())

        # Check if all words are distinct
        if len(words) != len(assignment.values()):

            # Return false as it is inconsistent
            return False

        # For loop through the assignment variables
        for x_var in assignment.keys():

            # Inner For loop through the assignment variables
            for y_var in assignment.keys():

                # If x_var does not equal y_var
                if x_var != y_var:

                    # Get the overlap result
                    overlap = self.crossword.overlaps[(x_var, y_var)]
        
                    # Check if overlap exists
                    if overlap is None:
                    
                        # Continue to the next variable
                        continue
                        
                    # Get the overlap indexes
                    x_index, y_index = overlap

                    # Check that the letter at the overlap point is the same
                    if assignment[x_var][x_index] != assignment[y_var][y_index]:

                        # Return false as there is an inconsistency
                        return False

        # return true as it is consistent
        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        raise NotImplementedError


    # ============================================================
    # Function Name: select_unassigned_variable
    # Purpose: Select the next unassigned variable using MRV 
    #          (minimum remaining values).
    #          If there is a tie break, select using DH
    #          If there is still a tie break, pick one of the tied ones
    # Notes: Used for heuristics backtracking
    # ============================================================

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # Create a temporary dictionary
        unassigned_list = dict()

        # Step 1 - Get the number of values

        # For loop through the crossword variables
        for var in self.crossword.variables:
        
            # Check that it isn't in the assignment dictionary
            if var not in assignment.keys():
        
                # Add the variable to the temporary dictionary 
                # with the number of values in the domain for that variable
                unassigned_list[var] = len(self.domains[var])

        # Get the minimum number from unassigned_list
        min_number = min(unassigned_list.values())

        # Step 2 - Perform MRV

        # Create a MRV candidates list
        candidates_mrv = []

        # For loop through the unassigned_list dictionary
        for var in unassigned_list.keys():

            # Check if the value equals the min_number
            if unassigned_list[var] == min_number:

                # Add to the MRV candidates list
                candidates_mrv.append(var)

        # Check that there is only one entry
        if len(candidates_mrv) == 1:

            # return the variable
            return candidates_mrv[0]

        # Step 3 - Perform DH for tie breaker       

        # Create a degree list
        degree_list = dict()

        # For loop through the candidates_mrv list to build a degree list
        for var in candidates_mrv:
        
            # Add the variable with it's degree value
            degree_list[var] = len(self.crossword.neighbors(var))

        # Find and set the max degree value
        max_degree = max(degree_list.values())

        # Create a DH candidates list
        candidates_dh = []

        # For loop through the degree_list dictionary to find candidates
        for var in degree_list.keys():

            # Check if the degree is equal to the max degree
            if degree_list[var] == max_degree:

                # Add to DH candidates list
                candidates_dh.append(var)
        
        # Check that there is only one entry
        if len(candidates_dh) == 1:
        
            # return the variable
            return candidates_dh[0]

        # Step 3 - Perform additional tie breaker

        # Arbitarily return the first entry in the DH candidate list
        return candidates_dh[0]
        


    # ============================================================
    # Function Name: backtrack
    # Purpose: Run both naive and heuristic backtracking searches,
    #          measure performance, and print results.
    # Notes: Resets domains between runs; stores timing and counts.
    # ============================================================

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # Create a copy of the original domains
        original_domains = copy.deepcopy(self.domains)

        # Initialise variables for the backtrack and attempt counts
        self.naive_backtrack_count = 0
        self.naive_attempt_count = 0
        self.heuristic_backtrack_count = 0        
        self.heuristic_attempt_count = 0

        # Start a timer
        start_time = time.perf_counter()

        # Perform the naive backtrack search
        self.naive_search = self.perform_backtrack(assignment)

        # End the timer
        end_time = time.perf_counter()

        # Calculate the length of time it took in milliseconds
        self.naive_total_time = (end_time - start_time) * 1000

        # Ensure that the domains are set to the original version
        self.domains = copy.deepcopy(original_domains)

        # Start a timer
        start_time = time.perf_counter()
        
        # Perform the naive backtrack search
        self.heuristic_search = self.perform_backtrack(dict())
        
        # End the timer
        end_time = time.perf_counter()
        
        # Calculate the length of time it took in milliseconds
        self.heuristic_total_time = (end_time - start_time) * 1000

        # Print the search info
        self.print_info()

        return self.naive_search


    # ============================================================
    # Function Name: perform_backtrack
    # Purpose: Recursive backtracking solver:
    #          - Select next variable
    #          - Try domain values
    #          - Check consistency
    #          - Recurse or backtrack
    # Notes: Counts attempts and backtracks for benchmarking.
    # ============================================================

    def perform_backtrack(self, assignment):
        """
        Method to Perform the actual backtrack search
        """        
       
        # Step 1 - Check if the assignment is complete

        # If assignment_complete is true
        if self.assignment_complete(assignment):

            # If it is complete, return the assignment
            return assignment

        # Step 2 - Select an unassigned variable

        # Set the next unassigned variable ready for use
        var = self.next_unassigned_variable(assignment)

        # Step 3 - Try each value in the domain for the selected variable

        # For loop through the values for the selected variable in domains
        for value in self.domains[var]:

            # Set the assignment variable value to this value
            assignment[var] = value

            # Update the naive attempt count
            self.naive_attempt_count += 1

            # Step 4 - Check current assignment consistency

            # If assignment is consistent
            if self.consistent(assignment):

                # Step 5 - Recursive processing
                # Perform backtracking for the next variable

                # Set a result variable for capturing the result of the next run
                result = self.perform_backtrack(assignment)

                # Check if result is not None
                if result is not None:

                    # Return the result
                    return result

            # Step 6 - Remove assignment (backtrack)

            # Remove the current assignment variable value
            del assignment[var]

            # Update the naive backtrack count
            self.naive_backtrack_count += 1

        # Step 7 - No solution found

        # There are no more viable variables not variable values
        # Return None to indicate that no solution was found
        return None


    # ============================================================
    # Function Name: next_unassigned_variable
    # Purpose: Select the next unassigned variable using naive
    #          ordering (first variable not yet assigned).
    # Notes: Used for naive backtracking; heuristics will replace it.
    # ============================================================

    def next_unassigned_variable(self, assignment):
        """
        Method to select an unassigned variable
        This does not involve any ordering of the unassigned variables
        """
        
        # For loop through the crossword variables
        for var in self.crossword.variables:

            # Check that it isn't in the assignment dictionary
            if var not in assignment.keys():

                # Return the variable
                return var


    # ============================================================
    # Function Name: print_info
    # Purpose: Display timing, attempt counts, backtrack counts,
    #          and solutions for both naive and heuristic searches.
    # Notes: Saves output images for both searches.
    # ============================================================

    def print_info(self):

        # Print message saying which search is being done
        print("Solving with Naive Backtracking search:\n")

        # Check if the naive search failed
        if self.naive_search is None:

            # Print that there is no solution
            print("No solution using naive backtracking search.\n\n")

        # else the search succeeded
        else:

            # Print the search time
            print(f"Naive Search Time: {self.naive_total_time:.4f} ms")

            # Print the total backtrack count
            print(f"Naive Total Backtrack Count: {self.naive_backtrack_count}")

            # Print the total attempts count
            print(f"Naive Total Attempts Count: {self.naive_attempt_count}")

            # Print the solved crossword
            print("Naive Search Solution:")
            self.print(self.naive_search)

            # Create the solution output file
            self.save(self.naive_search, "naive_search.png")

        # Print message saying which search is being done
        print("\n\nSolving with Heuristic Backtracking search:\n")
        
        # Check if the heuristic search failed
        if self.heuristic_search is None:
        
            # Print that there is no solution
            print("No solution using heuristic backtracking search.\n\n")
        
        # else the search succeeded
        else:
        
            # Print the search time
            print(f"Heuristic Search Time: {self.heuristic_total_time:.4f} ms")
        
            # Print the total backtrack count
            print(f"Heuristic Total Backtrack Count: {self.heuristic_backtrack_count}")

            # Print the total attempts count
            print(f"Heuristic Total Attempt Count: {self.heuristic_attempt_count}")
        
            # Print the solved crossword
            print("Heuristic Search Solution:")
            self.print(self.heuristic_search)

            # Create the solution output file
            self.save(self.heuristic_search, "heuristic_search.png")

            # Print a couple of empty lines
            print("\n\n")


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
