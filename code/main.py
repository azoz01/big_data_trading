from argparse import ArgumentParser, Namespace

from processing.processes.process_registry import process_registry


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--process", choices=sorted(process_registry.processess_mapping.keys()))
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    process = process_registry.processess_mapping[args.process]()
    process.execute()
