import argparse
from .pipeline import run
from .utils_logging import setup_logging

def main():
    parser = argparse.ArgumentParser(description="mainpipe data pipeline")
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to YAML config file (e.g. configs/local.yaml)",
    )
    args = parser.parse_args()
    logger = setup_logging()
    logger.info("Starting mainpipe pipeline with config: %s", args.config)
    run(args.config)

if __name__ == "__main__":
    main()
