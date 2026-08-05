import sys

from crossword import *


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


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # Get the overlap result
        overlap = self.crossword.overlaps(x, y)

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

                # For loop through the variable's neighbours
                for y in self.crossword.neighbours(var):

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

                # For loop through x's neighbours
                for z in self.crossword.neighbours(x):

                    # Check that z does not equal y
                    if z != y:
                
                        # Add the pair in reverse order to arcs_list
                        arcs_list.append((z, x))

        # Return true as the list is empty
        return True


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
                    overlap = self.crossword.overlaps(x_var, y_var)
        
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

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        raise NotImplementedError

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        raise NotImplementedError


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
