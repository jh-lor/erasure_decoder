import numpy as np

class topological_code:
    def __init__(self, size):
        self.size = size
        self.erasure_set = set()
        self.syndromes = {
            "X": set(),
            "Z": set()
        }
        self.operations = {
            "X": set(),
            "Z": set()
        }

        self.adjacency = {
            "X": [(0,2),(-1,1), (1, 1),(0,-2), (-1,-1), (-1,1)],
            "Z": [(2,0),(1,-1), (1, 1),(-2,0), (-1,-1), (-1,1)]
        }
        self.boundary = {
            "X":self.get_X_boundary(),
            "Z": self.get_Z_boundary()
            }

        self.open_qubits = {
            "X": self.get_X_open(),
            "Z": self.get_Z_open()
        }

    def get_data_qubits(self):
        if self.size%2== 1:
            return [(y, 2*k + y%2) for y in range(self.size) for k in range(self.size//2 + (y+1)%2)]
        else:
            return [(y, 2*k + y%2) for y in range(self.size) for k in range(self.size//2)]

    def get_X_stabilizers(self):
        return [(1+2*y, 2*x) for y in range(self.size//2) for x in range((self.size +1)//2)]
    
    def get_Z_stabilizers(self):
        return [(2*y, 1+ 2*x) for y in range((self.size+1)//2) for x in range(self.size//2)]

    def get_X_boundary(self):
        return [(2*y,0) for y in range((self.size+1)//2)], \
            [(2*y + (self.size + 1)%2, self.size-1) for y in range((self.size+1)//2)]  
    
    def get_Z_boundary(self):
        return [(0,2*x) for x in range((self.size+1)//2)], \
            [(self.size-1, 2*x + (self.size + 1)%2) for x in range((self.size+1)//2)]  

    def get_X_open(self):
        return [(2*y,-1) for y in range((self.size+1)//2)], \
            [(2*y + (self.size + 1)%2, self.size) for y in range((self.size+1)//2)]   

    def get_Z_open(self):
        return [(-1,2*x) for x in range((self.size+1)//2)], \
            [(self.size, 2*x + (self.size + 1)%2) for x in range((self.size+1)//2)]  

    def set_random_seed(seed = 42):
        np.random.seed(seed)

    def add_erasure_errors(self, p_error_rate):
        """
        For each qubit, with equal probability apply I, X, Y, Z
        We only apply erasure errors on data qubits?
        """
        random = np.random.rand(self.size, self.size)
        for qubit in self.get_data_qubits():
            random_qubit = random[qubit[0]][qubit[1]]
            if random_qubit < p_error_rate:
                # print("applying errors")
                self.erasure_set.add(qubit)
                # print(random_qubit)
                error_random = random_qubit/p_error_rate
                # print(error_random)
                if error_random < 1/4:
                    self.operations["X"].symmetric_difference_update([qubit])
                elif error_random < 1/2:
                    self.operations["X"].symmetric_difference_update([qubit])
                    self.operations["Z"].symmetric_difference_update([qubit])
                elif error_random <3/4:
                    self.operations["Z"].symmetric_difference_update([qubit])
        return

    def has_logical_error(self):
        """
        DFS to check if boundaries are connected 
        """
        # error = {"X": False, "Z": False}
        for error_type in ["X", "Z"]:
            visited = set()
            # we check the first boundary if there is an error of the appropriate type
            # print(self.boundary[error_type])
            for qubit in self.boundary[error_type][0]:
                if qubit in self.operations[error_type]:
                    if self.logical_error_DFS(visited, error_type, qubit):
                        return True
        return False
    
    def logical_error_DFS(self, visited, error_type, qubit):
        if qubit not in visited:
            # only visit new nodes
            visited.add(qubit)
            # print(f"Visiting {qubit}")
            if qubit in self.boundary[error_type][1]:
                if qubit in self.operations[error_type]:
                    # print(f"Connected to second boundary:{qubit}")
                    return True
            for y,x in self.adjacency[error_type]:
                # for each adjacent qubit
                next_qubit = (qubit[0] + y, qubit[1] + x)
                if next_qubit in self.operations[error_type]:
                    if self.logical_error_DFS(visited, error_type, next_qubit):
                        return True
        return False    

    def reset_syndrome(self):
        self.syndromes = {
            "X": set(),
            "Z": set()
        }

    def error_detected(self):
        """
        Check if there are any stabilizer measurements?
        """
        return len(self.syndromes["X"]) or len(self.syndromes["Z"])

class TreeNode():
    def __init__(self):
        self.parent_qubit = None
        self.children = []
        self.syndrome = False
        self.coordinate = None
        self.subtree_syndrome_sum = 0

    def __str__(self) -> str:
        return str(self.coordinate)

    def __repr__(self) -> str:
        return str(self.coordinate)

    def info(self):
        return f"Qubit = {self.coordinate}, Syn = {self.syndrome}, Children = {self.children}, Parent_qbit = {self.parent_qubit}"


class surface_code(topological_code):
    def __init__(self, size):
        super().__init__(size)
        self.root_list = None

    def measure_syndrome(self):
        self.reset_syndrome()
        for stabilizers, stab_type in [(self.get_Z_stabilizers, "Z"), (self.get_X_stabilizers, "X")]:
            operation = "X" if stab_type == "Z" else "Z"
            for stab in stabilizers():
                adj_count = 0
                for y_d, x_d in [(1,0), (-1,0), (0,1), (0,-1)]:
                    if (stab[0] + y_d, stab[1] + x_d) in self.operations[operation]:
                        adj_count += 1
                if adj_count%2:
                    self.syndromes[stab_type].add(stab)
        return


    def erasure_decoder(self):
        """
        Construct tree, peel the tree
        """
        self.construct_erasure_tree()
        # print(self.root_list)
        for stab_type in ["X", "Z"]:
            while self.root_list[stab_type]:
                chosen_qubits = set()
                curr_root = self.root_list[stab_type].pop()
                self.peel_tree_dfs(chosen_qubits, curr_root)
                # print(f"Chosen qubits {chosen_qubits} for {curr_root} for Stab Type {stab_type}")
                self.operations["X" if stab_type == "Z" else "Z"].symmetric_difference_update(chosen_qubits)
        
        return

    def peel_tree_dfs(self, qubits_set, node):
        node.subtree_syndrome_sum += node.syndrome
        for child in node.children:
            self.peel_tree_dfs(qubits_set, child)
            node.subtree_syndrome_sum += child.subtree_syndrome_sum
        if node.subtree_syndrome_sum%2:
            # print(f"Trying to add the parent of: {node.info()}")
            qubits_set.add(node.parent_qubit)

#
    def construct_erasure_tree(self):
        self.root_list = {"X": [],"Z": []}

        # loop this for X and Z
        for stab_type in ["X", "Z"]:
            open_boundaries = self.open_qubits[stab_type]
            combined_boundaries = open_boundaries[0] + open_boundaries[1]
            # copy erasure set
            erasure_copy = self.erasure_set.copy()
            visited = set()

            # we search for all trees that are touching the boundary
            for open_qubit in combined_boundaries:
                if not open_qubit in visited:
                    boundary_tree = self.erasure_tree_dfs(visited, None, erasure_copy,open_qubit, stab_type)
                    if not boundary_tree.children:
                        # check if there is an erased edge leading from boundary tree
                        self.root_list[stab_type].append(boundary_tree)
            # append root of erasure tree while deleting visited erasures
            # we search for all the erasures not touching boundary
            while erasure_copy:
                # print(erasure_copy)
                curr_qubit = next(iter(erasure_copy))
                # print(curr_qubit)
                curr_stab = self.get_adjacent_stabilizers(curr_qubit, stab_type)[0]
                self.root_list[stab_type].append(self.erasure_tree_dfs(visited, curr_qubit, erasure_copy, curr_stab, stab_type))
        return

    def erasure_tree_dfs(self, visited, parent_qubit, erasure_copy, curr, stab_type):
        visited.add(curr)
        curr_node = TreeNode()
        curr_node.coordinate = curr
        curr_node.parent_qubit = parent_qubit
        curr_node.syndrome = curr_node.coordinate in self.syndromes[stab_type]
        for qubit in self.get_adjacent_data_qubits(curr_node.coordinate):
            if qubit in erasure_copy:
                erasure_copy.remove(qubit)
                # print(qubit)
                for stab in self.get_adjacent_stabilizers(qubit, stab_type):
                    if stab not in visited:
                        curr_node.children.append(self.erasure_tree_dfs(visited, qubit, erasure_copy, stab, stab_type))
        return curr_node

    def get_adjacent_stabilizers(self, qubit, stab_type):
        # we make this return the open stabs
        if stab_type == "X":
            if qubit[0] %2 == 0:
                return [(qubit[0] + 1, qubit[1]),(qubit[0] - 1, qubit[1])]
            else:
                return [(qubit[0], qubit[1]-1), (qubit[0], qubit[1] + 1)]
        else:
            if qubit[1]%2 == 0:
                return [(qubit[0], qubit[1] + 1), (qubit[0], qubit[1] - 1)]
            else:
                return [(qubit[0]-1, qubit[1]), (qubit[0] + 1, qubit[1])]
    

    def get_adjacent_data_qubits(self, stab):
        return [(stab[0]+y, stab[1]+x) for y, x in [(1,0), (-1,0), (0,1), (0,-1)]]

class toric_code(topological_code):
    def __init__(self):
        super().__init__()

    def erasure_decoder(self):
        return