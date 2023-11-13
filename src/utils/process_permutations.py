import logging
from typing import Dict, List, Set


def process_permutations(
    buffer: Set[str], target_list: List[str], found_dict: Dict[int, Set[str]]
) -> Dict[int, Set[str]]:
    """Iterate the permutation buffer and find whether the permutation exists in either of the target strings. 
    If a match is found the permutation is added in a dictionary which is shared between all batches in order to correctly calculate the final results.

    Args:
        buffer (Set[str]): Set containing the permutations of the buffer in the calculate_permutations module.
        target_list (List[str]): List containing the target strings.
        found_dict (Dict[int, Set[str]]): Dictionary that includes the results from previous batches.

    Returns:
        Dict[int, Set[str]]: The update version of the found_dict containing any new matching permutations.
    """
    logging.debug(
        f"Execution of '{process_permutations.__name__}' started. Input: {buffer, target_list}"
    )

    for perm in buffer:
        for target_index, target_string in enumerate(target_list):
            if perm in target_string:
                found_dict[target_index].add(perm)

    logging.debug(
        f"Execution of '{process_permutations.__name__}' ended. Output: {found_dict}"
    )

    return found_dict
