import argparse
import simulator
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
def main(args):
    df = simulator.simulate(args.size, args.lower_bound, args.upper_bound, args.n_points, args.n_samples, args.code)
    print(df)
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Simulating the pseudo-threshold and threshold for the Linear\
    Time Maximum Likelihood Decoding of the Surace Code over the Quantum Erasure Channel by Delfosse and Zemor (2017). ")
    parser.add_argument("size", type = int, help = "Simulating square lattice of qubits, size is number of qubits on one side")
    parser.add_argument("lower_bound", type = float, help = "lower bound of range of physical error")
    parser.add_argument("upper_bound", type = float, help = "upper bound of range of physical error")
    parser.add_argument("n_points", type = int, help = "number of physical error rates to simulate")
    parser.add_argument("n_samples", type = int, help = "number of samples to simulate within range")
    parser.add_argument("code", help = "Toric code or surface code", choices = ["toric", "surface"])

    # parser.add_argument("confidence", help = "Absolute percentage of error")
    args = parser.parse_args()
    main(args)