import numpy as np
from topological_code import surface_code, toric_code
import pandas as pd


def simulate(size, lower_bound, upper_bound, n_points, n_samples, code):
    """
    takes in size of code to simulate, the physical error rate to simulate
    """
    error_range = np.linspace(lower_bound, upper_bound, n_points)
    df = pd.DataFrame(
        {
            "physical_error_rate": error_range, 
            "no_error":np.zeros(n_points),
            "undetected_error":np.zeros(n_points), 
            "corrected_error":np.zeros(n_points), 
            "uncorrected_error":np.zeros(n_points),
            "syndrome_error":np.zeros(n_points)
            }
            )
    df = df.set_index("physical_error_rate")

    for phys_error_rate in error_range:
        for n in range(n_samples):
            if code == "toric":
                encoding = toric_code(size)
            else:
                encoding = surface_code(size)

            encoding.add_erasure_errors(phys_error_rate)
            encoding.measure_syndrome()
            if not encoding.error_detected():
                if not encoding.has_logical_error():
                    df.loc[phys_error_rate, "no_error"] += 1
                    continue
                else:
                    df.loc[phys_error_rate, "undetected_error"] += 1
                continue # exit to next sample
            else:
            # we use the decoding algorithm if there is any error
                encoding.erasure_decoder()
                encoding.measure_syndrome()
                if encoding.error_detected():
                    print(f"For Size {size}")
                    print(f"Symdromes: {encoding.syndromes}")
                    print(f"Operations: {encoding.operations}")
                    print(f"Erasure Set: {encoding.erasure_set}")
                    break
                if encoding.has_logical_error():
                    df.loc[phys_error_rate, "uncorrected_error"] += 1
                else:
                    df.loc[phys_error_rate, "corrected_error"] += 1

    return df

