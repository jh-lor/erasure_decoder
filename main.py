import argparse
import simulator
import matplotlib.pyplot as plt
"""
Simulating the pseudo-threshold and threshold for the Lienar Time Maximum Likelihood Decoding of the Surace Code over the Quantum Erasure Channel by Delfosse and Zemor (2017). 

Will accept two arguments:
size of code
physical error rate
certainty

returns:
the logical error rate for given parameters

The idea is to be able to parallelize this

Structure of program:
1. initialize code state. Takes in size of code and physical error rate and generates the syndrome and erasure qubits
2. Algorithm. takes in the code state and outputs maximumlikelihoood decoding
3. Iterator. Check whether error is corrected
"""

# def pseudo_threshold_plot(data, time, mode):
    
#     expected_logical_dict = {
#         "code_capacity": 1,
#         "initialization_error": 2/3,
#         "measurement_error": 2/3
#     }

#     physical_error_rates, no_errors, undetected_errors, uncorrected_errors, corrected_errors = data
#     total_repetitions = no_errors + undetected_errors + uncorrected_errors + corrected_errors
#     fig, ax = plt.subplots()

#     simulation_logical_error_rate = (undetected_errors + uncorrected_errors)/total_repetitions
    
#     proportions = [simulation_logical_error_rate*100]
#     labels = ["Simulation Logical Error Rate"]
#     ax.stackplot(physical_error_rates*100, proportions,
#                 labels = labels)
    
#     expected_logical_error_rate = physical_error_rates*expected_logical_dict[mode]
#     ax.plot(physical_error_rates*100, physical_error_rates*expected_logical_dict[mode]*100, label = f"Logical Error Rate for one qubit: y = {expected_logical_dict[mode]:0.2f}x")
    
#     ax.legend(loc = 'upper left')
#     ax.set_title(f'Logical Error Rate {mode}')
#     # plt.xticks(np.arange(100*min(physical_error_rate), 100*max(physical_error_rate)+1, 5))
#     ax.set_xlabel('Physical Error Rate')
#     ax.set_ylabel('Logical Error Rate')
#     fig.savefig(f'{plots_path}Logical Error Rate Plot {mode}_{time}.png')

#     diff_list = simulation_logical_error_rate - expected_logical_error_rate
#     for i in range(len(diff_list)-2):
#         if diff_list[i]*diff_list[i+1] < 0:
#             return (physical_error_rates[i]+physical_error_rates[i+1])/2

def main(args):
    size = args.low_size
    while size <= args.high_size:
        print(f"For size {size}:")
        df = simulator.simulate(size, args.lower_bound, args.upper_bound, args.n_points, args.n_samples, args.code)
        df["logical_error_rate"] = (df["uncorrected_error"] + df["undetected_error"])/args.n_samples
        print(df)
        print(df["logical_error_rate"])
        size += 2
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Simulating the pseudo-threshold and threshold for the Linear\
    Time Maximum Likelihood Decoding of the Surace Code over the Quantum Erasure Channel by Delfosse and Zemor (2017). ")
    parser.add_argument("low_size", type = int, help = "Simulating square lattice of qubits, size is number of qubits on one side")
    parser.add_argument("high_size", type = int, help = "Simulating square lattice of qubits, size is number of qubits on one side")
    parser.add_argument("lower_bound", type = float, help = "lower bound of range of physical error")
    parser.add_argument("upper_bound", type = float, help = "upper bound of range of physical error")
    parser.add_argument("n_points", type = int, help = "number of physical error rates to simulate")
    parser.add_argument("n_samples", type = int, help = "number of samples to simulate within range")
    parser.add_argument("code", help = "Toric code or surface code", choices = ["toric", "surface"])

    # parser.add_argument("confidence", help = "Absolute percentage of error")
    args = parser.parse_args()
    main(args)