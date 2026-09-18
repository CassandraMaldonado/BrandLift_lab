import argparse
import json
from .analysis import analyze

def main():
    parser = argparse.ArgumentParser(description="Produce a causal brand-lift decision brief")
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--budget", type=float, default=1_000_000)
    args = parser.parse_args()
    print(json.dumps(analyze(args.seed, args.budget), indent=2))

if __name__ == "__main__":
    main()
