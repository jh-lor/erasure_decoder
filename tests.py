from random import Random
import topological_code
import argparse
from UnitTester import LogicalErrorTester, DecoderTester, RandomErrorTester

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

def test_decoder(test_cases, verbose = False):
    failed_list = []
    for test in test_cases:
        tester = DecoderTester(*test, verbose) 
        if not tester:
            failed_list.append(tester)
    return failed_list

def test_random_errors(test_cases):
    test_list = []
    for test in test_cases:
        tester = RandomErrorTester(*test)
        tester.test()
        test_list.append(tester)
    return test_list

def indepth_test():
    print("Specific Test")
    code = topological_code.surface_code(5)
    code.operations["X"].update([(2,0),(2,4)])
    code.erasure_set.update([(2,0), (2,2), (2,4)])
    code.measure_syndrome()
    print(code.operations)
    print(code.syndromes)
    code.construct_erasure_tree()
    print_erasure_tree(code)
    code.erasure_decoder()
    code.measure_syndrome()
    print(code.operations)
    print(code.syndromes)
    return code

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
        (5, args.type, "Sparse errors on 5x5 surface", False, [(1,1),(3,3)],[(1,1),(3,3)])
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
        (5, "surface", "Z error = (0,2), (4,2)", False, [], [(0,2),(4,2)], [(0,2),(4,2)]),
        (5, "surface", "X error = (0,2) Er = (0,2), (4,2)", False, [(0,2)], [], [(0,2),(4,2)]),
        (5, "surface", "Z error = (0,2) Er = (0,2), (2,2),(4,2)", None, [], [(0,2)], [(0,2),(2,2), (4,2)]),
        (5, "surface", "X error = (1,1),(3,3), Z error = (1,1), (3,3) Er = (1,1), (3,3)", False, [(1,1), (3,3)], [(1,1), (3,3)], [(1,1), (3,3)]),
        (5, "surface", "X error = (2,0),(2,4), Er = (2,0),(2,2), (2,4)", None, [(2,0), (2,4)], [], [(2,0),(2,2), (2,4)]),
        (5, "surface", "X error = (2,2), Er = (2,0),(2,2), (2,4)", None, [(2,2)], [], [(2,0),(2,2), (2,4)]),
        (5, "surface", "Z error = (0,2),(4,2), Er = (0,2),(2,2), (4,2)", None, [(0,2), (4,2)], [], [(0,2),(2,2), (4,2)]),
        (5, "surface", "X error = (2,2), Z = (0,2), (2,2), (4,2), Er = (2,0),(2,2), (2,4)", None, [(2,2)], [(2,0), (2,2), (4,2)], [(2,0),(2,2), (4,2)]),
        (5, "surface", "X error = [(2,2), (1,1)], Z = [(0,2), (2,2), (4,2), (1,1),(3,3)], Er = [(0,2),(2,2), (4,2), (1,1), (3,3)])", None, [(2,2), (1,1)], [(0,2), (2,2), (4,2), (1,1),(3,3)], [(0,2),(2,2), (4,2), (1,1), (3,3)]),
        (5, "surface", "[(1,1),(3,3),(3,1),(1,3)], [], [(1,1),(3,3),(3,1),(1,3)]", False, [(1,1),(3,3),(3,1),(1,3)], [], [(1,1),(3,3),(3,1),(1,3)]),
        (5, "surface", "Side Error", False, [(0,0),(2,0),(4,0),(0,4),(2,4),(4,4)],[],[(0,0),(2,0),(4,0),(0,4),(2,4),(4,4)]),
        (5, "surface", "Side Error", False, [],[(0,0),(0,2),(0,4),(4,4),(4,2),(4,0)],[(0,0),(0,2),(0,4),(4,4),(4,2),(4,0)])
    ]
    decoder_failed_list = test_decoder(decoder_cases, True)
    if decoder_failed_list:
        print("Failed Decoder Error Checks")
        for test in decoder_failed_list:
            print(test)
            print(test.code.has_logical_error())
    else: 
        print("Passed Decoder Checks")

    random_error_cases = [
        (5, "surface", "Size = 5, p_error = 0.25", True, 0.25, 10000),
        (5, "surface", "Size = 5, p_error = 0.5", True, 0.5, 10000),
        (9, "surface", "Size = 9, p_error = 0.25", True, 0.25, 10000),
        (9, "surface", "Size = 9, p_error = 0.5", True, 0.5, 10000),
        (13, "surface", "Size = 13, p_error = 0.25", True, 0.25, 10000),
        (13, "surface", "Size = 13, p_error = 0.5", True, 0.5, 10000),
    ]
    test_random_errors(random_error_cases)

    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Test Suite")
    parser.add_argument("type", choices = ["toric", "surface"], help = "Enter toric or surface")
    args = parser.parse_args()
    main(args)