class InvalidInputError(Exception):
    """
    Will be raised when payload is not at the desired structure.
    """

    pass

class NoSolutionError(Exception):
    """
    Will be raised when the problem has no feasible solution.
    """
    
    pass