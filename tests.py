import simulator
import topological_code
import argparse

def test_get_data_qubits():

    return

 
def get_topological_code(type, size):
    if type == "toric":
        return topological_code.toric_code(size)
    elif type == "surface":
        return topological_code.surface_code(size)

def test_surface_code_logical_errors():
    failed_list = []
    print("Logical Error Test 1:")
    errors = []
    failed = False
    for i in range(10):
        if topological_code.surface_code(i).has_logical_error():
            errors.append(i)
            failed = True
    if failed:
        print(f"FAILED: Error detected where no error is expected on sizes {errors}")
        failed_list.append(1)
    else:
        print("PASSED")
    
    print("Logical Error Test 2:")
    code = topological_code.surface_code(1)
    code.operations["X"].add((0,0))
    if code.has_logical_error():
        print("PASSED")
    else: 
        print(f"FAILED: Failed to detect X error on a single qubit")

    print("Logical Error Test 3:")
    code = topological_code.surface_code(1)
    code.operations["Z"].add((0,0))
    if code.has_logical_error():
        print("PASSED")
    else: 
        print(f"FAILED: Failed to detect Z error on a single qubit")


    print("Logical Error Test 4:")
    code = topological_code.surface_code(5)
    code.operations["X"].update([(2,0), (2,2), (2,4)])
    if code.has_logical_error():
        print("PASSED")
    else: 
        print(f"FAILED: Failed to detect X logical error on a 5x5 surface code")

    print("Logical Error Test 5:")
    code = topological_code.surface_code(5)
    code.operations["Z"].update([(0,2), (2,2), (4,2)])
    if code.has_logical_error():
        print("PASSED")
    else: 
        print(f"FAILED: Failed to detect Z error on a 5x5 surface code")

    print("Logical Error Test 6:")
    code = topological_code.surface_code(5)
    code.operations["X"].update([(2,0), (2,4)])
    if not code.has_logical_error():
        print("PASSED")
    else: 
        print(f"FAILED: Detected non-existent X logical error on a 5x5 surface code")

    print("Logical Error Test 7:")
    code = topological_code.surface_code(5)
    code.operations["Z"].update([(0,2), (4,2)])
    if not code.has_logical_error():
        print("PASSED")
    else: 
        print(f"FAILED: Detected non-existent Z error on a 5x5 surface code")

    print("Logical Error Test 8:")
    code = topological_code.surface_code(5)
    code.operations["Z"].update([(0,2), (4,2)])
    code.operations["X"].update([(2,0),(2,2)])
    if not code.has_logical_error():
        print("PASSED")
    else: 
        print(f"FAILED: Detected non-existent error on a 5x5 surface code")

    print("Logical Error Test 9:")
    code = topological_code.surface_code(5)
    code.operations["Z"].update([(0,2), (2,2), (4,2)])
    code.operations["X"].update([(0,2), (2,2), (4,2)])
    if code.has_logical_error():
        print("PASSED")
    else: 
        print(f"FAILED: Failed to detect Z error on a 5x5 surface code")

    print("Logical Error Test 10:")
    code = topological_code.surface_code(5)
    code.operations["X"].update([(0,0), (0,2), (0,4)])
    if code.has_logical_error():
        print("PASSED")
    else: 
        print(f"FAILED: Failed to detect X error on side of a 5x5 surface code")

    print("Logical Error Test 11:")
    code = topological_code.surface_code(5)
    code.operations["Z"].update([(0,0), (2,0), (4,0)])
    if code.has_logical_error():
        print("PASSED")
    else: 
        print(f"FAILED: Failed to detect Z error on side of a 5x5 surface code")
    return failed_list

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


def test_decoder(type):
    print("Decoder Test 1:")
    new_code = topological_code.surface_code(5)
    new_code.erasure_set.update([(2,0),(2,4)])
    new_code.operations["X"].update([(2,0),(2,4)])
    new_code.measure_syndrome()
    if not new_code.error_detected():
        print(f"FAILED: Error Not Detected")
    else:
        new_code.erasure_decoder()
        new_code.measure_syndrome()
        if new_code.error_detected():
            print(f"FAILED: Error not corrected")
            print(new_code.operations)
            print(f"X stabilizers: {new_code.syndromes['X']}")
            print(f"Z stabilizers: {new_code.syndromes['Z']}")
        else:
            print(f"PASSED: High weight X error \nLogical error: {new_code.has_logical_error()}")
    

    print("Decoder Test 2:")
    new_code = topological_code.surface_code(5)
    new_code.erasure_set.update([(0,2),(4,2)])
    new_code.operations["Z"].update([(0,2),(4,2)])
    new_code.measure_syndrome()
    if not new_code.error_detected():
        print(f"FAILED: Error Not Detected")
    else:
        new_code.erasure_decoder()
        new_code.measure_syndrome()
        
        if new_code.error_detected():
            print(f"FAILED: Error not corrected")
            print(new_code.operations)
            print(f"X stabilizers: {new_code.syndromes['X']}")
            print(f"Z stabilizers: {new_code.syndromes['Z']}")
        else:
            print(f"PASSED: High weight Z error \nLogical error:{new_code.has_logical_error()}")

    print("Decoder Test 3:")
    new_code = topological_code.surface_code(5)
    new_code.erasure_set.update([(0,2)])
    new_code.operations["Z"].update([(0,2)])
    new_code.measure_syndrome()
    if not new_code.error_detected():
        print(f"FAILED: Error Not Detected")
    else:
        new_code.erasure_decoder()
        new_code.measure_syndrome()
        if new_code.error_detected():
            print(f"FAILED: Error not corrected")
            print(new_code.operations)
            print(f"X stabilizers: {new_code.syndromes['X']}")
            print(f"Z stabilizers: {new_code.syndromes['Z']}")
        else:
            print(f"PASSED: Low weight Z error \nLogical error: {new_code.has_logical_error()}")

    print("Decoder Test 4:")
    new_code = topological_code.surface_code(5)
    new_code.erasure_set.update([(2,0)])
    new_code.operations["X"].update([(2,0)])
    new_code.measure_syndrome()
    if not new_code.error_detected():
        print(f"FAILED: Error Not Detected")
    else:
        new_code.erasure_decoder()
        new_code.measure_syndrome()
        if new_code.error_detected():
            print(f"FAILED: Error not corrected")
            print(new_code.operations)
            print(f"X stabilizers: {new_code.syndromes['X']}")
            print(f"Z stabilizers: {new_code.syndromes['Z']}")
        else:
            print(f"PASSED: Low weight X error \nLogical error: {new_code.has_logical_error()}")

    print("Decoder Test 5:")
    new_code = topological_code.surface_code(5)
    new_code.erasure_set.update([(1,1), (3,3)])
    new_code.operations["X"].update([(1,1), (3,3)])
    new_code.operations["Z"].update([(1,1), (3,3)])
    new_code.measure_syndrome()
    if not new_code.error_detected():
        print(f"FAILED: Error Not Detected")
    else:
        new_code.erasure_decoder()
        new_code.measure_syndrome()
        if new_code.error_detected():
            print(f"FAILED: Error not corrected")
            print(f"Operations: {new_code.operations}")
            print(f"X stabilizers: {new_code.syndromes['X']}")
            print(f"Z stabilizers: {new_code.syndromes['Z']}")
        else:
            print(f"PASSED: Low weight Y error \nLogical error: {new_code.has_logical_error()}")

    print("Decoder Test 6:")
    new_code = topological_code.surface_code(5)
    new_code.erasure_set.update([(0,2), (4,2)])
    new_code.operations["X"].update([(0,2), (4,2)])
    # new_code.operations["Z"].update([(1,1), (3,3)])
    new_code.measure_syndrome()
    if not new_code.error_detected():
        print(f"FAILED: Error Not Detected")
    else:
        new_code.erasure_decoder()
        new_code.measure_syndrome()
        if new_code.error_detected():
            print(f"FAILED: Error not corrected")
            print(f"Operations: {new_code.operations}")
            print(f"X stabilizers: {new_code.syndromes['X']}")
            print(f"Z stabilizers: {new_code.syndromes['Z']}")
        else:
            print(f"PASSED: High weight X error \nLogical error: {new_code.has_logical_error()}")

    print("Decoder Test 7:")
    new_code = topological_code.surface_code(5)
    new_code.erasure_set.update([(0,2),(2,2), (4,2)])
    new_code.operations["Z"].update([(0,2), (2,2), (4,2)])
    # new_code.operations["Z"].update([(1,1), (3,3)])
    new_code.measure_syndrome()
    new_code.erasure_decoder()
    new_code.measure_syndrome()
    print(f"Operations: {new_code.operations}")
    print(f"X stabilizers: {new_code.syndromes['X']}")
    print(f"Z stabilizers: {new_code.syndromes['Z']}")
    print(f"PASSED: Logical Z error \nLogical error: {new_code.has_logical_error()}")

    print("Decoder Test 8:")
    new_code = topological_code.surface_code(5)
    new_code.erasure_set.update([(0,2),(2,2), (4,2)])
    new_code.operations["Z"].update([(0,2), (2,2), (4,2)])
    new_code.operations["X"].update([(2,2)])
    # new_code.operations["Z"].update([(1,1), (3,3)])
    new_code.measure_syndrome()
    new_code.erasure_decoder()
    new_code.measure_syndrome()
    print(f"Operations: {new_code.operations}")
    print(f"X stabilizers: {new_code.syndromes['X']}")
    print(f"Z stabilizers: {new_code.syndromes['Z']}")
    print(f"PASSED: Logical Z error with X error \nLogical error: {new_code.has_logical_error()}")
    
    print("Decoder Test 9:")
    new_code = topological_code.surface_code(5)
    new_code.erasure_set.update([(0,2),(2,2), (4,2), (1,1), (3,3)])
    new_code.operations["Z"].update([(0,2), (2,2), (4,2), (1,1),(3,3)])
    new_code.operations["X"].update([(2,2), (1,1)])
    # new_code.operations["Z"].update([(1,1), (3,3)])
    new_code.measure_syndrome()
    new_code.erasure_decoder()
    new_code.measure_syndrome()
    print(f"Operations: {new_code.operations}")
    print(f"X stabilizers: {new_code.syndromes['X']}")
    print(f"Z stabilizers: {new_code.syndromes['Z']}")
    print(f"PASSED: Logical Z error with X and Z error \nLogical error: {new_code.has_logical_error()}")

    print("Decoder Test 10:")
    new_code = topological_code.surface_code(5)
    new_code.erasure_set.update([(0,0), (1,1)])
    new_code.operations["Z"].update([(0,0), (1,1)])
    # new_code.operations["Z"].update([(1,1), (3,3)])
    new_code.measure_syndrome()
    print(new_code.syndromes)
    new_code.erasure_decoder()
    new_code.measure_syndrome()
    print(f"Operations: {new_code.operations}")
    print(f"X stabilizers: {new_code.syndromes['X']}")
    print(f"Z stabilizers: {new_code.syndromes['Z']}")
    print(f"Corner Case \nLogical error: {new_code.has_logical_error()}")

    print("Decoder Test 11:")
    new_code = topological_code.surface_code(5)
    new_code.erasure_set.update([(3,3),(4,4)])
    new_code.operations["Z"].update([(3,3),(4,4)])
    new_code.measure_syndrome()
    print(new_code.syndromes)
    new_code.erasure_decoder()
    new_code.measure_syndrome()
    print(f"Operations: {new_code.operations}")
    print(f"X stabilizers: {new_code.syndromes['X']}")
    print(f"Z stabilizers: {new_code.syndromes['Z']}")
    print(f"Corner Case \nLogical error: {new_code.has_logical_error()}")

    print("Decoder Test 12:")
    new_code = topological_code.surface_code(5)
    new_code.erasure_set.update([(3,1),(2,0)])
    new_code.operations["X"].update([(3,1),(2,0)])
    new_code.measure_syndrome()
    print(new_code.syndromes)
    new_code.erasure_decoder()
    new_code.measure_syndrome()
    print(f"Operations: {new_code.operations}")
    print(f"X stabilizers: {new_code.syndromes['X']}")
    print(f"Z stabilizers: {new_code.syndromes['Z']}")
    print(f"Corner Case \nLogical error: {new_code.has_logical_error()}")


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
    logical_error_failed = test_surface_code_logical_errors()
    if logical_error_failed:
        print(f"Logical Error Test Failed: ".join(logical_error_failed))
    else: 
        print("Passed Logical Error Checks")
    test_add_random_errors(args.type)
    test_tree_construction(args.type)
    test_measurement()
    test_decoder(args.type)
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Test Suite")
    parser.add_argument("type", choices = ["toric", "surface"], help = "Enter toric or surface")
    args = parser.parse_args()
    main(args)