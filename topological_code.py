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
            [(2*y + (self.size + 1)%2, self.size - 1) for y in range((self.size+1)//2)]  
    
    def get_Z_boundary(self):
        return [(0,2*x) for x in range((self.size+1)//2)], \
            [(self.size - 1, 2*x + (self.size + 1)%2) for x in range((self.size+1)//2)]  

    def add_erasure_errors(self, p_error_rate, seed = 42):
        """
        For each qubit, with equal probability apply I, X, Y, Z
        We only apply erasure errors on data qubits?
        """
        np.random.seed(seed)
        random = np.random.rand(self.size, self.size)
        for qubit in self.get_data_qubits():
            if random[qubit[0]][qubit[1]]< p_error_rate:
                # print("applying errors")
                self.erasure_set.add(qubit)
                error_random = np.random.rand()
                if error_random < 1/4:
                    self.operations["X"].symmetric_difference_update(qubit)
                elif error_random < 1/2:
                    self.operations["X"].symmetric_difference_update(qubit)
                    self.operations["Z"].symmetric_difference_update(qubit)
                elif error_random <3/4:
                    self.operations["Z"].symmetric_difference_update(qubit)
        return

    def has_logical_error(self):
        """
        DFS to check if boundaries are connected 
        """
        # error = {"X": False, "Z": False}
        for error_type in ["X", "Z"]:
            visited = set()
            for qubit in self.boundary[error_type][0]:
                if qubit in self.operations[error_type]:
                    if self.logical_error_DFS(visited, error_type, qubit):
                        return True
        return False

    
    def logical_error_DFS(self, visited, error_type, qubit):
        if qubit not in visited:
            # only visit new nodes
            visited.add(qubit)
            if qubit in self.boundary[error_type][1]:
                return True
            for y,x in self.adjacency[error_type]:
                # for each adjacent qubit
                next_qubit = (qubit[0] + y, qubit[1] + x)
                if next_qubit in self.operations[error_type]:
                    if self.logical_error_DFS(visited, error_type, next_qubit):
                        return True
        return False    


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

class surface_code(topological_code):
    def __init__(self, size):
        super().__init__(size)
        self.root_list = {
            "X": [],
            "Z": []
        }

    def measure_syndrome(self):
        for qubit in self.erasure_set:
            self.update_syndrome_qubit(qubit)
        return

    def update_syndrome_qubit(self, qubit):
        if qubit in self.operations["Z"]:
            # Z error, caught by X stabilizers
            if qubit[0]%2:
                flipped_syndromes = [(qubit[0], qubit[1]-1), (qubit[0], qubit[1]+1)]
            else:
                if qubit[0]> 0 and qubit[0] < self.size - 1:
                    flipped_syndromes = [(qubit[0]-1, qubit[1]), (qubit[0] + 1, qubit[1])]
                elif qubit[0] == 0:
                    flipped_syndromes = [(qubit[0] + 1, qubit[1])]
                else:
                    flipped_syndromes = [(qubit[0] - 1, qubit[1])]
            self.syndromes["X"].symmetric_difference_update(flipped_syndromes)

        if qubit in self.operations["X"]:
            # X error, caught by Z stabilizers
            if qubit[0]%2:
                flipped_syndromes = [(qubit[0] - 1, qubit[1], qubit[0] + 1, qubit[1])]
            else:
                if qubit[0]> 0 and qubit[0] < self.size - 1:
                    flipped_syndromes = [(qubit[0]-1, qubit[1]), (qubit[0] + 1, qubit[1])]
                elif qubit[0] == 0:
                    flipped_syndromes = [(qubit[0] + 1, qubit[1])]
                else:
                    flipped_syndromes = [(qubit[0] - 1, qubit[1])]
            self.syndromes["Z"].symmetric_difference_update(flipped_syndromes)
        return

    def erasure_decoder(self):
        """
        Construct tree, peel the tree
        """
        self.construct_erasure_tree()
        for stab_type in ["X", "Z"]:
            while self.root_list[stab_type]:
                chosen_qubits = set()
                self.peel_tree_dfs(chosen_qubits, self.root_list[stab_type].pop())
                self.operations["X" if stab_type == "Z" else "Z"].symmetric_difference_update(chosen_qubits)
        self.root_list = {"X": [],"Z": []}
        return

    def peel_tree_dfs(self, qubits_set, node):
        node.subtree_syndrome_sum += node.syndrome
        for child in node.children:
            self.peel_tree_dfs(qubits_set, child)
            node.subtree_syndrome_sum += child.subtree_syndrome_sum
        if node.subtree_syndrome_sum%2:
            qubits_set.add(node.parent_qubit)


    def construct_erasure_tree(self):

        # loop this for X and Z
        for stab_type in ["X", "Z"]:
            # copy erasure set
            erasure_copy = self.erasure_set.copy()
            visited = set()
            # append root of erasure tree while deleting visited erasures
            while erasure_copy:
                curr_qubit = next(iter(erasure_copy))
                curr_stab = self.get_adjacent_stabilizers(curr_qubit, stab_type)[0]
                self.root_list[stab_type].append(self.erasure_tree_dfs(visited, None, erasure_copy, curr_stab, stab_type))
        return

    def erasure_tree_dfs(self, visited, parent_qubit, erasure_copy, curr, stab_type):
        visited.add(curr)
        curr_node = TreeNode()
        curr_node.coordinate = curr
        curr_node.parent_qubit = parent_qubit
        curr_node.syndrome = curr_node.coordinate in self.syndromes[stab_type]
        for qubit in self.get_adjacent_data_qubits(self,curr_node.coordinate):
            if qubit in erasure_copy:
                erasure_copy.remove(qubit)
                for stab in self.get_adjacent_stabilizers(self,qubit, stab_type):
                    if stab not in visited:
                        curr_node.children.append(self.erasure_tree_dfs(visited, qubit, erasure_copy, stab, stab_type))
        return curr_node

    def get_adjacent_stabilizers(self, qubit, stab_type):
        stab = []
        if stab_type == "X":
            if qubit[0] %2 == 0:
                if qubit[0] < self.size -1:
                    stab.append((qubit[0] - 1, qubit[1]))
                if qubit[0] > 0:
                    stab.append((qubit[0] + 1, qubit[1]))
            else:
                stab.extend([(qubit[0], qubit[1]-1), (qubit[0], qubit[1] + 1)])
        else:
            if qubit[1]%2 == 0:
                if qubit[1] < self.size - 1:
                    stab.append((qubit[0], qubit[1] + 1))
                if qubit[1] > 0:
                    stab.append((qubit[0], qubit[1] - 1))
            else:
                stab.extend([(qubit[0]-1, qubit[1]), (qubit[0] + 1, qubit[1])])
        return stab

    def get_adjacent_data_qubits(self, stab):
        return [(stab[0]+y, stab[1]+x) for y, x in [(1,0), (-1,0), (0,1), (0,-1)]]

class toric_code(topological_code):
    def __init__(self):
        super().__init__()

    def erasure_decoder(self):
        return