import topological_code 
import numpy as np
from math import ceil

class UnitTester:
    def __init__(self, size, code_type, description, correct):
        self.code = topological_code.surface_code(size) if code_type == "surface" else topological_code.toric_code(size)
        self.description = description
        self.outcome = correct
        self.passed = -1
        self.code_type = code_type
        self.size = size

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
    def __init__(self, size, code_type, description, outcome, X_error_list, Z_error_list, erasure_list, verbose = False):
        super().__init__(size, code_type, description, outcome)
        self.X_errors = X_error_list
        self.Z_errors = Z_error_list
        self.erasures = erasure_list
        self.results_string = ""
        self.verbose = verbose

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
                if self.outcome == None:
                   self.results_string = f"PASSED: Syndrome Corrected"
                   self.passed = True
                   if self.verbose:
                       print(f"Test: {self.description}, {self.results_string}, Logical Error = {self.code.has_logical_error()}")
                elif self.code.has_logical_error() == self.outcome:
                    self.results_string = f"PASSED"
                    self.passed = True
                else:
                    self.results_string = f"FAILED: Correction failed {self.description}"

    def __str__(self):
        return self.results_string

class RandomErrorTester(UnitTester):
    def __init__(self, size, code_type, description, correct, p_error, repetitions) -> None:
        super().__init__(size, code_type, description, correct)
        self.p_error = p_error
        self.repetitions = repetitions
        self.statistics = {
            "containment": [False]*repetitions,
            "num_erasures": np.zeros(repetitions, dtype = np.int),
            "num_X": np.zeros(repetitions, dtype = np.int),
            "num_Z": np.zeros(repetitions, dtype = np.int)
        }

    def test(self):
        for rep in range(self.repetitions):
            self.code.add_erasure_errors(self.p_error)
            if not (self.code.operations["X"] in self.code.erasure_set and self.code.operations["Z"] in self.code.erasure_set):
                self.statistics["containment"][rep] = True
            self.statistics["num_erasures"][rep] = len(self.code.erasure_set)
            self.statistics["num_X"][rep] = len(self.code.operations["X"])
            self.statistics["num_Z"][rep] = len(self.code.operations["Z"])

            self.code = topological_code.surface_code(self.size) if self.code_type == "surface" else topological_code.toric_code(self.size)

        self.statistics_analysis()
        return 

    def statistics_analysis(self):
        if any(self.statistics["containment"]):
            self.results_string = "FAILED: Errors not contained within erasure set"
        mean_erasures = np.mean(self.statistics['num_erasures'])
        mean_X = np.mean(self.statistics["num_X"])
        mean_Z = np.mean(self.statistics["num_Z"])
        print(f"Expected vs Actual Average Erasures: {ceil(self.size**2/2)*self.p_error} = {mean_erasures}")
        print(f"Proportion of X and Z errors: {mean_X/mean_erasures}, {mean_Z/mean_erasures}")