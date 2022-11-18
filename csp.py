import copy
class GraphColorCSP(object):
    def __init__(self, variables, colors, adjacency):
        self.domains = {}
        self.variables = variables
        self.colors = colors
        for var in variables:
            self.domains[var] = copy.deepcopy(colors)
        self.adjacency = adjacency
    
    # Make sure that assignment does not violate any constraints
    def constraint_consistent(self, var1, color1, var2, color2):
        if (color1 != color2) and (var2 in self.adjacency[var1]):
            return True
        if var2 not in self.adjacency[var1]:
            return True
        return False 
    
    # Make sure that assignment assigns values to all variables
    def is_complete(self, assignment):
        variables_in_assignment = []
        for var in list(assignment.keys()):
            variables_in_assignment.append(var)
        for var in self.variables:
            if var not in variables_in_assignment:
                return False # not complete
        return True

    # Check if assignment is consistent and complete
    def is_goal(self, assignment):
        if (assignment == None):
            return False
        for var1 in assignment:
            color1 = assignment[var1]
            for var2 in assignment:
                color2 = assignment[var2]
                if var1 != var2:
                    if not self.constraint_consistent(var1, color1, var2, color2):
                        return False    # not consistent

        variables_in_assignment = []
        for var in list(assignment.keys()):
            variables_in_assignment.append(var)
        for var in self.variables:
            if var not in variables_in_assignment:
                return False # not complete
        return True

    def check_partial_assignment(self, assignment):
        for var1 in assignment:
            color1 = assignment[var1]
            for var2 in assignment:
                color2 = assignment[var2]
                if var1 != var2:
                    if not self.constraint_consistent(var1, color1, var2, color2):
                        return False    # not consistent
        return True


# AC-3 Arc-consistency algorithm to enforce binary constraints
def ac3(csp, arcs_queue=None, current_domains=None, assignment=None):
    if current_domains == None:
        current_domains = copy.deepcopy(csp.domains)
    else:
        current_domains = copy.deepcopy(current_domains)

    queue = arcs_queue
    if queue == None:
        queue = set()
    else:
        queue = set(queue)

        for key, values in csp.adjacency.items():
            for value in values:
                queue.add((key,value))
    while (len(queue) != 0):
        arc = queue.pop()
        var1 = arc[0]
        var2 = arc[1]
        if revise(current_domains, csp, var1, var2):
            if (len(current_domains[var1]) == 0):
                return False, current_domains
            for x in csp.adjacency[var1]:
                if(x != var2):
                    queue.add((x, var1))
    return True, current_domains
    
def revise(current_domains, csp, xi, xj):
    var1 = xi
    var2 = xj

    dom1 = current_domains[xi]
    dom2 = current_domains[xj]
    dom1_copy = copy.deepcopy(dom1)
    dom2_copy = copy.deepcopy(dom2)

    revision = False
    for color1 in dom1_copy:
        find_at_least_one = False
        for color2 in dom2_copy:
            if csp.constraint_consistent(var1, color1, var2, color2):
                find_at_least_one = True
                break
        if not find_at_least_one:
            dom1.remove(color1)
            current_domains[var1] = dom1
            revision = True

    return revision


# MRV: choose the variable with the fewest remaining legal values next
def select_unassigned_variable(csp, assignment, current_domains):
    not_assigned = []   # all variables not in assignment
    for var in csp.variables:
        if len(assignment) != 0:
            if var not in list(assignment.keys()):
                not_assigned.append(var)
        else: 
            not_assigned.append(var)
    
    # sort all variables in CSP from smallest to largest domain
    all_variables_MRV = sorted(
        list(current_domains.keys()), 
        key= lambda dictKey: len(current_domains[dictKey]), 
        reverse= False
    )
    
    # Return the first variable in all_variables_MRV which exists in not_assigned
    for var in all_variables_MRV:
        if var in not_assigned:
            return var
    return None


# Helper function for backtracking to check consistency of variable and value with assignment
def check_consistency(csp, var, value, assignment):
    for variable in list(assignment.keys()):
        if not csp.constraint_consistent(var, value, variable, assignment[variable]):
            return False
    return True

#-------------------------------- Backtracking algorithm --------------------------------
def backtracking(csp):
    return recursive_backtracking(csp)

def recursive_backtracking(csp, assignment={},current_domains=None):
    if current_domains == None:
        current_domains = copy.deepcopy(csp.domains)
    
    dom = copy.deepcopy(current_domains)
    if csp.is_complete(assignment):
        return assignment
    
    # select a variable using MRV
    var = select_unassigned_variable(csp, assignment, dom)
    
    queue = set()
    var_neighbors = csp.adjacency[var]
    unassigned_neighbors_of_var = []

    for neighbor in var_neighbors:
        if neighbor not in assignment:
            unassigned_neighbors_of_var.append(neighbor)

    for neighbor in unassigned_neighbors_of_var:
        queue.add((var,neighbor))
        queue.add((neighbor, var))
    
    for value in csp.domains[var]:
        if check_consistency(csp, var, value, assignment):
            assignment[var] = value
            dom[var] = [value]
            inferences = ac3(csp, arcs_queue=queue, current_domains=dom, assignment=assignment)
            if inferences[0]:
                result = recursive_backtracking(csp, assignment, inferences[1])
                if result != None:
                    return result
            assignment.pop(var)
    return None
    