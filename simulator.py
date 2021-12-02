import numpy as np
from topological_code import surface_code, toric_code
import pandas as pd


def simulate(size_list, lower_bound, upper_bound, n_points, n_samples, code):
    """
    takes in size of code to simulate, the physical error rate to simulate
    """
    error_range = np.linspace(lower_bound, upper_bound, n_points)
    index = pd.MultiIndex.from_product([size_list,error_range], names = ["size", "physical_error_rate"])
    df = pd.DataFrame(columns = ["no_error", "undetected_error", "corrected_error", "uncorrected_error", "effective_error_rate"], index = index)
    for col in df.columns:
        df[col].values[:] = 0
    for size in size_list:
        for phys_error_rate in error_range:
            df.loc[(size,phys_error_rate), "effective_error_rate"] += 0.75*phys_error_rate
            for n in range(n_samples):
                if code == "toric":
                    encoding = toric_code(size)
                else:
                    encoding = surface_code(size)

                encoding.add_erasure_errors(phys_error_rate)
                encoding.measure_syndrome()
                if not encoding.error_detected():
                    if not encoding.has_logical_error():
                        df.loc[(size,phys_error_rate), "no_error"] += 1
                        continue
                    else:
                        df.loc[(size,phys_error_rate), "undetected_error"] += 1
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
                        df.loc[(size,phys_error_rate), "uncorrected_error"] += 1
                    else:
                        df.loc[(size,phys_error_rate), "corrected_error"] += 1

    return df

