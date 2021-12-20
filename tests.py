import simulator
import topological_code
import argparse

class UnitTester:
    def __init__(self, size, code_type, description, correct):
        self.code = topological_code.surface_code(size) if code_type == "surface" else topological_code.toric_code(size)
        self.description = description
        self.outcome = correct
        self.passed = -1

    def test(self):
        self.passed =  True

    def __bool__(self):
        if self.passed == -1:
            self.test()
        return self.passed

    def __str__(self):
        if self.passed == -1:
            return f"Test not run yet"
        elif not self.passed:
            return f"FAILED: {self.description}"
        else:
            return "PASSED"

class LogicalErrorTester(UnitTester):
    def __init__(self, size, code_type, description, outcome, X_error_list, Z_error_list):
        super().__init__(size, code_type, description, outcome)
        self.X_errors = X_error_list
        self.Z_errors = Z_error_list

    def test(self):
        self.code.operations["X"].update(self.X_errors)
        self.code.operations["Z"].update(self.Z_errors)
        if self.code.has_logical_error() == self.outcome:
            self.passed = True
        else:
            self.passed = False

class DecoderTester(UnitTester):
    def __init__(self, size, code_type, description, outcome, X_error_list, Z_error_list, erasure_list):
        super().__init__(size, code_type, description, outcome)
        self.X_errors = X_error_list
        self.Z_errors = Z_error_list
        self.erasures = erasure_list
        self.results_string = ""

    def test(self):
        self.code.operations["X"].update(self.X_errors)
        self.code.operations["Z"].update(self.Z_errors)
        self.code.erasure_set.update(self.erasures)
        self.code.measure_syndrome()
        self.passed = False
        if not self.code.error_detected():
            self.results_string = f"FAILED: Error not detected {self.description}"
        else:
            self.code.erasure_decoder()
            self.code.measure_syndrome()
            if self.code.error_detected():
                self.results_string = f"FAILED: Syndrome not corrected {self.description}"
            else:
                if self.code.has_logical_error() == self.outcome:
                    self.results_string = f"PASSED"
                    self.passed = True
                else:
                    self.results_string = f"FAILED: Correction failed {self.description}"

    def __str__(self):
        return self.results_string
 
def get_topological_code(type, size):
    if type == "toric":
        return topological_code.toric_code(size)
    elif type == "surface":
        return topological_code.surface_code(size)

def test_logical_errors(test_cases):
    failed_list = []
    for test in test_cases:
        tester = LogicalErrorTester(*test) 
        if not tester:
            failed_list.append(tester)
    return failed_list

def print_erasure_tree(code):
    for stab_type in ["X", "Z"]:
        for i, roots in enumerate(code.root_list[stab_type]):
            print(f"Stab Type {stab_type} {i}-th root:")
            print_root(roots)

def print_root(node):
    print(node.info())
    for child in node.children:
        print_root(child)

def test_tree_construction(type):
    print("Tree Constructor Test 1:")
    new_code = topological_code.surface_code(5)
    new_code.erasure_set.update([(2,0), (2,4)])
    new_code.operations["X"].update([(2,0),(2,4)])
    new_code.measure_syndrome()
    new_code.construct_erasure_tree()
    for stab_type in ["X", "Z"]:
        for i, roots in enumerate(new_code.root_list[stab_type]):
            print(f"Stab Type {stab_type} {i}-th root:")
            print_root(roots)

    print("Tree Constructor Test 2:")
    new_code = topological_code.surface_code(5)
    new_code.erasure_set.update([(2,0), (2,4)])
    new_code.operations["Z"].update([(2,0),(2,4)])
    new_code.measure_syndrome()
    new_code.construct_erasure_tree()
    for stab_type in ["X", "Z"]:
        for i, roots in enumerate(new_code.root_list[stab_type]):
            print(f"Stab Type {stab_type} {i}-th root:")
            print_root(roots)

    print("Tree Constructor Test 3:")
    new_code = topological_code.surface_code(5)
    new_code.erasure_set.update([(2,0), (2,2)])
    new_code.operations["Z"].update([(2,0),(2,2)])
    new_code.measure_syndrome()
    new_code.construct_erasure_tree()
    for stab_type in ["X", "Z"]:
        for i, roots in enumerate(new_code.root_list[stab_type]):
            print(f"Stab Type {stab_type} {i}-th root:")
            print_root(roots)

    print("Tree Constructor Test 4:")
    new_code = topological_code.surface_code(5)
    new_code.erasure_set.update([(0,2),(4,2)])
    new_code.operations["Z"].update([(0,2),(4,2)])
    new_code.measure_syndrome()
    new_code.construct_erasure_tree()
    print_erasure_tree(new_code)

    print("Tree Constructor Test 5:")
    new_code = topological_code.surface_code(5)
    new_code.erasure_set.update([(0,0),(1,1)])
    new_code.operations["Z"].update([(0,0),(1,1)])
    new_code.measure_syndrome()
    new_code.construct_erasure_tree()
    print_erasure_tree(new_code)

    print("Tree Constructor Test 6:")
    new_code = topological_code.surface_code(5)
    new_code.erasure_set.update([(0,2),(1,3)])
    new_code.operations["Z"].update([(0,2),(1,3)])
    new_code.measure_syndrome()
    new_code.construct_erasure_tree()
    print_erasure_tree(new_code)

    print("Tree Constructor Test 7:")
    new_code = topological_code.surface_code(5)
    new_code.erasure_set.update([(3,3),(4,4)])
    new_code.operations["Z"].update([(3,3),(4,4)])
    new_code.measure_syndrome()
    new_code.construct_erasure_tree()
    print_erasure_tree(new_code)

    print("Tree Constructor Test 8:")
    new_code = topological_code.surface_code(5)
    new_code.erasure_set.update([(0,0),(0,2),(0,4)])
    new_code.operations["X"].update([(0,0),(0,2),(0,4)])
    new_code.measure_syndrome()
    new_code.construct_erasure_tree()
    print_erasure_tree(new_code)

    print("Tree Constructor Test 9:")
    new_code = topological_code.surface_code(5)
    new_code.erasure_set.update([(3, 1), (2, 0)])
    new_code.operations["X"].update([(3, 1), (2, 0)])
    new_code.measure_syndrome()
    new_code.construct_erasure_tree()
    print_erasure_tree(new_code)

    print("Tree Constructor Test 10:")
    new_code = topological_code.surface_code(5)
    new_code.erasure_set.update([(3, 1), (2, 0), (4,0)])
    new_code.operations["X"].update([(3, 1), (2, 0), (4,0)])
    new_code.measure_syndrome()
    new_code.construct_erasure_tree()
    print_erasure_tree(new_code)


def test_decoder(test_cases):
    failed_list = []
    for test in test_cases:
        tester = DecoderTester(*test) 
        if not tester:
            failed_list.append(tester)
    return failed_list

    # print("Decoder Test 10:")
    # new_code = topological_code.surface_code(5)
    # new_code.erasure_set.update([(0,0), (1,1)])
    # new_code.operations["Z"].update([(0,0), (1,1)])
    # # new_code.operations["Z"].update([(1,1), (3,3)])
    # new_code.measure_syndrome()
    # print(new_code.syndromes)
    # new_code.erasure_decoder()
    # new_code.measure_syndrome()
    # print(f"Operations: {new_code.operations}")
    # print(f"X stabilizers: {new_code.syndromes['X']}")
    # print(f"Z stabilizers: {new_code.syndromes['Z']}")
    # print(f"Corner Case \nLogical error: {new_code.has_logical_error()}")

    # print("Decoder Test 11:")
    # new_code = topological_code.surface_code(5)
    # new_code.erasure_set.update([(3,3),(4,4)])
    # new_code.operations["Z"].update([(3,3),(4,4)])
    # new_code.measure_syndrome()
    # print(new_code.syndromes)
    # new_code.erasure_decoder()
    # new_code.measure_syndrome()
    # print(f"Operations: {new_code.operations}")
    # print(f"X stabilizers: {new_code.syndromes['X']}")
    # print(f"Z stabilizers: {new_code.syndromes['Z']}")
    # print(f"Corner Case \nLogical error: {new_code.has_logical_error()}")

    # print("Decoder Test 12:")
    # new_code = topological_code.surface_code(5)
    # new_code.erasure_set.update([(3,1),(2,0)])
    # new_code.operations["X"].update([(3,1),(2,0)])
    # new_code.measure_syndrome()
    # print(new_code.syndromes)
    # new_code.erasure_decoder()
    # new_code.measure_syndrome()
    # print(f"Operations: {new_code.operations}")
    # print(f"X stabilizers: {new_code.syndromes['X']}")
    # print(f"Z stabilizers: {new_code.syndromes['Z']}")
    # print(f"Corner Case \nLogical error: {new_code.has_logical_error()}")


def test_add_random_errors(type):
    size = 5
    new_code = get_topological_code(type, size)
    new_code.add_erasure_errors(1)
    new_code.measure_syndrome()
    
    print(f"Generated Erasure errors for size {size}")
    # print(new_code.erasure_set)
    if len(new_code.erasure_set) != (size**2+1)//2:
        print(f"Incorrect number of erasure errors: Expected {(size**2+1)//2} but got {len(new_code.erasure_set)}")
    print(f"Erasure Set {new_code.erasure_set}")
    print(f"X errors: {new_code.operations['X']}")
    print(f"Z stabilizers: {new_code.syndromes['Z']}")
    print(f"Z errors: {new_code.operations['Z']}")
    print(f"X stabilizers: {new_code.syndromes['X']}")
    return

def test_measurement():
    print("Measurement Test 1:")
    new_code = topological_code.surface_code(5)
    new_code.operations["X"].update([(2,2)])
    # new_code.operations["Z"].update([(2,2)])
    new_code.measure_syndrome()
    if new_code.syndromes == {
        "X": set(),
        "Z": set([(2,1),(2,3)])
    }:
        print(f"PASSED: low weight X error")
    else:
        print(f"FAILED {new_code.syndromes}")

    print("Measurement Test 2:")
    new_code = topological_code.surface_code(5)
    # new_code.operations["X"].update([(2,2)])
    new_code.operations["Z"].update([(2,2)])
    new_code.measure_syndrome()
    if new_code.syndromes == {
        "X": set([(1,2),(3,2)]),
        "Z": set()
    }:
        print(f"PASSED: low weight Z error")
    else:
        print(f"FAILED {new_code.syndromes}")

    print("Measurement Test 3:")
    new_code = topological_code.surface_code(5)
    new_code.operations["X"].update([(0,0)])
    new_code.operations["Z"].update([(0,0)])
    new_code.measure_syndrome()
    if new_code.syndromes == {
        "X": set([(1,0)]),
        "Z": set([(0,1)])
    }:
        print(f"PASSED: Corner Y error")
    else:
        print(f"FAILED {new_code.syndromes}")

    print("Measurement Test 4:")
    new_code = topological_code.surface_code(5)
    new_code.operations["X"].update([(2,0)])
    new_code.operations["Z"].update([(2,0)])
    new_code.measure_syndrome()
    if new_code.syndromes == {
        "X": set([(1,0), (3,0)]),
        "Z": set([(2,1)])
    }:
        print(f"PASSED: Boundary Y error")
    else:
        print(f"FAILED {new_code.syndromes}")

    print("Measurement Test 5:")
    new_code = topological_code.surface_code(5)
    new_code.operations["X"].update([(2,0), (2,2), (2,4)])
    # new_code.operations["Z"].update([(2,0)])
    new_code.measure_syndrome()
    if new_code.syndromes == {
        "X": set(),
        "Z": set()
    }:
        print(f"PASSED: Logical X error")
    else:
        print(f"FAILED {new_code.syndromes}")

    print("Measurement Test 6:")
    new_code = topological_code.surface_code(5)
    new_code.operations["Z"].update([(0,2), (2,2), (4,2)])
    # new_code.operations["Z"].update([(2,0)])
    new_code.measure_syndrome()
    if new_code.syndromes == {
        "X": set(),
        "Z": set()
    }:
        print(f"PASSED: Logical Z error")
    else:
        print(f"FAILED {new_code.syndromes}")

def main(args):
    test_cases = [
        (1, args.type, "X error on single qubit", True, [(0,0)], []),
        (1, args.type, "Z error on single qubit", True, [], [(0,0)]),
        (5, args.type, "X logical error on 5x5 surface", True, [(2,0), (2,2), (2,4)], []),
        (5, args.type, "Z logical error on 5x5 surface", True, [], [(0,2), (2,2), (4,2)]),
        (5, args.type, "Correctable X error on 5x5 surface", False, [(2,0), (2,4)], []),
        (5, args.type, "Correctable Z error on 5x5 surface", False, [], [(0,2), (4,2)]),
        (5, args.type, "Vertical X error on 5x5 surface", False, [(0,0), (2,0), (4,0)], []),
        (5, args.type, "Horizontal Z error on 5x5 surface", False, [], [(0,0), (0,2), (0,4)]),
        (5, args.type, "Snake X error on 5x5 surface", True, [(0,0), (2,0), (4,0), (0,2), (2,2), (4,2), (0,4), (2,4), (4,4)], []),
        (5, args.type, "Snake Z error on 5x5 surface", True, [], [(0,0), (2,0), (4,0), (0,2), (2,2), (4,2), (0,4), (2,4), (4,4)]),
        (5, args.type, "Diagonal X error on 5x5 surface", True, [(0,0), (1,1), (2,2), (3,3), (4,4)], []),
        (5, args.type, "Diagonal Z error on 5x5 surface", True, [],  [(0,0), (1,1), (2,2), (3,3), (4,4)]),
    ]
    logical_error_failed = test_logical_errors(test_cases)
    if logical_error_failed:
        print("Failed Logical Error Checks")
        for test in logical_error_failed:
            print(test)
            print(test.code.has_logical_error())
    else: 
        print("Passed Logical Error Checks")
    # test_add_random_errors(args.type)
    # test_tree_construction(args.type)
    # test_measurement()
    decoder_cases = [
        (5, "surface", "X error = (2,0), (2,4)", False, [(2,0),(2,4)], [], [(2,0),(2,4)]),
        (5, "surface", "Z error = (0,2),(4,2)", False, [], [(0,2),(4,2)], [(0,2),(4,2)]),
        (5, "surface", "X error = (0,2) Er = (0,2), (4,2)", False, [(0,2)], [], [(0,2),(4,2)]),
        (5, "surface", "Z error = (0,2) Er = (0,2), (2,2),(4,2)", False, [], [(0,2)], [(0,2),(2,2), (4,2)]),
        (5, "surface", "X error = (1,1),(3,3), Z error = (1,1), (3,3) Er = (1,1), (3,3)", False, [(1,1), (3,3)], [(1,1), (3,3)], [(1,1), (3,3)]),
        (5, "surface", "X error = (2,0),(2,4), Er = (2,0),(2,2), (2,4)", True, [(2,0), (2,4)], [], [(2,0),(2,2), (2,4)]),
        (5, "surface", "X error = (2,2), Er = (2,0),(2,2), (2,4)", False, [(2,2)], [], [(2,0),(2,2), (2,4)]),
        (5, "surface", "Z error = (0,2),(4,2), Er = (0,2),(2,2), (4,2)", True, [(0,2), (4,2)], [], [(0,2),(2,2), (4,2)]),
        (5, "surface", "X error = (2,2), Z = (0,2), (2,2), (4,2), Er = (2,0),(2,2), (2,4)", True, [(2,2)], [(2,0), (2,2), (4,2)], [(2,0),(2,2), (4,2)]),
        (5, "surface", "X error = [(2,2), (1,1)], Z = [(0,2), (2,2), (4,2), (1,1),(3,3)], Er = [(0,2),(2,2), (4,2), (1,1), (3,3)])", True, [(2,2), (1,1)], [(0,2), (2,2), (4,2), (1,1),(3,3)], [(0,2),(2,2), (4,2), (1,1), (3,3)]),
    ]
    decoder_failed_list = test_decoder(decoder_cases)
    if decoder_failed_list:
        print("Failed Decoder Error Checks")
        for test in decoder_failed_list:
            print(test)
    else: 
        print("Decoder Checks")

    print("Specific Test")
    code = topological_code.surface_code(5)
    code.operations["Z"].update([(0,2)])
    code.erasure_set.update([(0,2), (2,2), (4,2)])
    code.measure_syndrome()
    print(code.operations)
    print(code.syndromes)
    code.construct_erasure_tree()
    print_erasure_tree(code)

    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Test Suite")
    parser.add_argument("type", choices = ["toric", "surface"], help = "Enter toric or surface")
    args = parser.parse_args()
    main(args)