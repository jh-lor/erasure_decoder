import argparse
import simulator
from datetime import datetime
import os
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
df_path = "./df"

def main(args):
    start = datetime.now().strftime("%m%d%Y_%H%M%S")
    if not os.path.exists(df_path):
        os.mkdir(df_path)

    size_list = []
    size = args.low_size
    while size <= args.high_size:
        size_list.append(size)
        size += args.interval

    df = simulator.simulate(size_list, args.lower_bound, args.upper_bound, args.n_points, args.n_samples, args.code)
    df["logical_error_rate"] = (df["uncorrected_error"] + df["undetected_error"])/args.n_samples
    df["better"] = df["effective_error_rate"] > df["logical_error_rate"]
    print(df)
    print(df[["logical_error_rate", "effective_error_rate", "better"]])
    df.to_pickle(f"{df_path}/{start}_{args.n_samples}.pkl")
    # _{args.low_size}_{args.high_size}_{args.lower_bound}_{args.upper_bound}_{args.n_points}_{args.n_samples}_{args.code}.csv")
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Simulating the pseudo-threshold and threshold for the Linear\
    Time Maximum Likelihood Decoding of the Surace Code over the Quantum Erasure Channel by Delfosse and Zemor (2017). ")
    parser.add_argument("low_size", type = int, help = "Simulating square lattice of qubits, size is number of qubits on one side")
    parser.add_argument("high_size", type = int, help = "Simulating square lattice of qubits, size is number of qubits on one side")
    parser.add_argument("interval", type = int, help = "Intervals between sizes")
    parser.add_argument("lower_bound", type = float, help = "lower bound of range of physical error")
    parser.add_argument("upper_bound", type = float, help = "upper bound of range of physical error")
    parser.add_argument("n_points", type = int, help = "number of physical error rates to simulate")
    parser.add_argument("n_samples", type = int, help = "number of samples to simulate within range")
    parser.add_argument("code", help = "Toric code or surface code", choices = ["toric", "surface"])

    # parser.add_argument("confidence", help = "Absolute percentage of error")
    args = parser.parse_args()
    main(args)