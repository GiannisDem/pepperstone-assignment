import argparse
import logging
import multiprocessing
import os
import pathlib
import configparser

from utils.parse_dictionary import parse_dictionary
from utils.parse_input import parse_input
from utils.generate_permutations import generate_permutations_with_buffer


def main():
    logging.basicConfig(
        level=logging.ERROR,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename="basic.log",
    )

    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), "../config.ini"))

    parser = argparse.ArgumentParser(
        description="Take a set of words from a dictionary and find how many times they appear in a list of long string inputs in their original or scrambled form."
    )
    parser.add_argument(
        "--dictionary",
        required=True,
        type=pathlib.Path,
        help="Path to the dictionary file.",
    )
    parser.add_argument(
        "--input",
        required=True,
        type=pathlib.Path,
        help="Path to the input string file.",
    )
    args = parser.parse_args()

    try:
        # Control the number of parallel processes to spawn
        WORKERS = int(config.get("settings", "parallel_workers"))

        dictionary_path = args.dictionary
        input_path = args.input

        words_list = parse_dictionary(dictionary_path)
        target_strings = parse_input(input_path)

        with multiprocessing.Manager() as manager:
            # Create a shared dict to collect results
            shared_result_dict = manager.dict(
                {i: 0 for i, _ in enumerate(target_strings)}
            )
            lock = manager.Lock()

            # Create a Pool of workers
            with multiprocessing.Pool(WORKERS) as pool:
                # Map the generate_permutations_with_buffer function to each string in the strings_list
                pool.starmap(
                    generate_permutations_with_buffer,
                    [
                        (s, target_strings, shared_result_dict, lock)
                        for s in words_list
                    ],
                )

            # Retrieve the final result from the shared dict
            for target_index, total in shared_result_dict.items():
                print(f"Case #{target_index + 1}: {total}")

    except ValueError as e:
        print("Error:", e)


if __name__ == "__main__":
    main()
