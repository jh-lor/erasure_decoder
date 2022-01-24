import topological_code 

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
                if self.outcome == None:
                   self.results_string = f"PASSED: Syndrome Corrected"
                   self.passed = True
                elif self.code.has_logical_error() == self.outcome:
                    self.results_string = f"PASSED"
                    self.passed = True
                else:
                    self.results_string = f"FAILED: Correction failed {self.description}"

    def __str__(self):
        return self.results_string