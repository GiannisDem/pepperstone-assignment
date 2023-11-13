from collections import Counter
import configparser
from itertools import permutations
import logging
from multiprocessing.managers import DictProxy
import os
from typing import Dict, List, Set

from utils.process_permutations import process_permutations

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "../../config.ini"))


# Control the size of generated permutations buffer
BUFFER_SIZE = int(config.get("settings", "buffer_size"))


def generate_permutations_with_buffer(
    input_string: str, target_list: List[str], shared_result_dict: Dict[int, int], lock
) -> Dict[int, int]:
    """Calculate the permutations of the input_string in batches using a buffer mechanism. Once the buffer is full or there are no more permutations to calculate we call the process_permutations module.
    Once the existance of permutations in the target strings is processed we return the results. Using the multiprocessing library we distribute the execution of this module in multiple processes.

    Args:
        input_string (str): String to calculate permutations for.
        target_list (List[str]): List of target strings as returned from the parse_input module.
        shared_result_dict (Dict[int, int]): Dictionary of the results shared between processes.
        lock (_type_): Lock that controls the access to the shared dictionary between processes.

    Returns:
        Dict[int, int]: Dictionary containing the number of permutations found for each target string.
    """
    logging.debug(
        f"Execution of '{generate_permutations_with_buffer.__name__}' started. Input: {input_string, target_list, shared_result_dict}"
    )
    # Initialize a dictionary to store the permutations that exists in each target string
    found_dict: Dict[int, Set[str]] = {i: set() for i, _ in enumerate(target_list)}

    # Initialize a dictionary to store the sum of all permutations that exists in each target string
    total_dict: Dict[int, int] = {i: 0 for i, _ in enumerate(target_list)}

    substring = input_string[1:-1]

    char_count = Counter(substring)

    perms_buffer: Set[str] = set()

    if not input_string:
        return total_dict

    # Skip generating permutations for substrings of same characters or words <=3 characters long i.e 'abbbc', 'abc'
    if len(char_count) <= 1:
        perms_buffer.add(input_string)
        process_permutations(perms_buffer, target_list, found_dict)
    else:
        for perm in permutations(substring):
            full_permutation = input_string[0] + "".join(perm) + input_string[-1]

            # Use a buffer to process permutations in batches
            perms_buffer.add(full_permutation)

            if len(perms_buffer) == BUFFER_SIZE:
                process_permutations(perms_buffer, target_list, found_dict)
                perms_buffer.clear()

        # Process any remaining permutations in the buffer
        if perms_buffer:
            process_permutations(perms_buffer, target_list, found_dict)

    for target_index, permutations_set in found_dict.items():
        total_dict[target_index] += len(permutations_set)

    with lock:
        # Add the total_dict to the dictionary shared between processes
        for key in total_dict.keys():
            shared_result_dict[key] += total_dict[key]

    logging.debug(
        f"Execution of '{generate_permutations_with_buffer.__name__}' ended. Output: {shared_result_dict}"
    )
    return shared_result_dict
