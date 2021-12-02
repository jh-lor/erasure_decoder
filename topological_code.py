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
                error_random = random_qubit/p_error_rate
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
            for qubit in stabilizers():
                adj_count = 0
                for y_d, x_d in [(1,0), (-1,0), (0,1), (0,-1)]:
                    if (qubit[0] + y_d, qubit[1] + x_d) in self.operations["X" if stab_type == "Z" else "Z"]:
                        adj_count += 1
                if adj_count%2:
                    self.syndromes[stab_type].add(qubit)


        return

    # def update_syndrome_qubit(self, qubit):
    #     if qubit in self.operations["Z"]:
    #         # Z error, caught by X stabilizers
    #         if qubit[0]%2:
    #             flipped_syndromes = [(qubit[0], qubit[1]-1), (qubit[0], qubit[1]+1)]
    #         else:
    #             if qubit[0]> 0 and qubit[0] < self.size - 1:
    #                 flipped_syndromes = [(qubit[0]-1, qubit[1]), (qubit[0] + 1, qubit[1])]
    #             elif qubit[0] == 0:
    #                 flipped_syndromes = [(qubit[0] + 1, qubit[1])]
    #             else:
    #                 flipped_syndromes = [(qubit[0] - 1, qubit[1])]
    #         self.syndromes["X"].symmetric_difference_update(flipped_syndromes)

    #     if qubit in self.operations["X"]:
    #         # X error, caught by Z stabilizers
    #         if qubit[0]%2:
    #             flipped_syndromes = [(qubit[0] - 1, qubit[1]), (qubit[0] + 1, qubit[1])]
    #         else:
    #             if qubit[0]> 0 and qubit[0] < self.size - 1:
    #                 flipped_syndromes = [(qubit[0]-1, qubit[1]), (qubit[0] + 1, qubit[1])]
    #             elif qubit[0] == 0:
    #                 flipped_syndromes = [(qubit[0] + 1, qubit[1])]
    #             else:
    #                 flipped_syndromes = [(qubit[0] - 1, qubit[1])]
    #         self.syndromes["Z"].symmetric_difference_update(flipped_syndromes)
    #     return

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


    def construct_erasure_tree(self):
        self.root_list = {"X": [],"Z": []}
        # loop this for X and Z
        for stab_type in ["X", "Z"]:
            # copy erasure set
            erasure_copy = self.erasure_set.copy()
            visited = set()
            # append root of erasure tree while deleting visited erasures
            while erasure_copy:
                curr_qubit = next(iter(erasure_copy))
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
                for stab in self.get_adjacent_stabilizers(qubit, stab_type):
                    if stab not in visited:
                        curr_node.children.append(self.erasure_tree_dfs(visited, qubit, erasure_copy, stab, stab_type))
        return curr_node

    def get_adjacent_stabilizers(self, qubit, stab_type):
        stab = []
        if stab_type == "X":
            if qubit[0] %2 == 0:
                if qubit[0] < self.size -1:
                    stab.append((qubit[0] + 1, qubit[1]))
                if qubit[0] > 0:
                    stab.append((qubit[0] - 1, qubit[1]))
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