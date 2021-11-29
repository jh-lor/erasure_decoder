import simulator
import topological_code
import argparse

def test_get_data_qubits():

    return

 






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

def test_add_random_errors():
    return


def main(args):
    logical_error_failed = test_surface_code_logical_errors()
    if logical_error_failed:
        print(f"Logical Error Test Failed: ".join(logical_error_failed))
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Test Suite")
    parser.add_argument("type", choices = ["toric", "surface"], help = "Enter toric or surface")
    args = parser.parse_args()
    main(args)