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

    print("Logical Error Test 8:")
    code = topological_code.surface_code(5)
    code.operations["Z"].update([(0,2), (2,2), (4,2)])
    code.operations["X"].update([(0,2), (2,2), (4,2)])
    if code.has_logical_error():
        print("PASSED")
    else: 
        print(f"FAILED: Failed to detect Z error on a 5x5 surface code")
    return failed_list

def test_add_random_errors(type):
    for size in range(1, 10):
        new_code = get_topological_code(type, size)
        new_code.add_erasure_errors(1)
        new_code.measure_syndrome()
        
        print(f"Generated Erasure errors for size {size}")
        # print(new_code.erasure_set)
        if len(new_code.erasure_set) != (size**2+1)//2:
            print(f"Incorrect number of erasure errors: Expected {(size**2+1)//2} but got {len(new_code.erasure_set)}")
        print(f"X errors: {new_code.operations['X']}")
        print(f"Z stabilizers: {new_code.syndromes['Z']}")
        print(f"Z errors: {new_code.operations['Z']}")
        print(f"X stabilizers: {new_code.syndromes['X']}")
    return

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
            print(f"PASSED")

def main(args):
    logical_error_failed = test_surface_code_logical_errors()
    if logical_error_failed:
        print(f"Logical Error Test Failed: ".join(logical_error_failed))
    else: 
        print("Passed Logical Error Checks")

    test_add_random_errors(args.type)
    test_decoder(args.type)
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Test Suite")
    parser.add_argument("type", choices = ["toric", "surface"], help = "Enter toric or surface")
    args = parser.parse_args()
    main(args)