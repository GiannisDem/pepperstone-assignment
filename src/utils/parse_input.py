import configparser
import logging
import os
from typing import List

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "../../config.ini"))

TARGET_STRING_SIZE_LIMIT = int(
    config.get("input_validations", "target_string_size_limit")
)
TARGET_STRING_SIZE_UPPER_LIMIT = int(
    config.get("input_validations", "target_string_size_upper_limit")
)
TARGET_STRING_SIZE_LOWER_LIMIT = int(
    config.get("input_validations", "target_string_size_lower_limit")
)


def parse_input(file_path: str) -> List[str]:
    """Parse text file that includes search strings separated by newline, apply validations and return a list

    Args:
        file_path (str): Path of the text file as recorded from the command line arguments

    Raises:
        ValueError: Raise error when file is empty
        ValueError: Raise error when character length is out of specifications
        ValueError: Raise error when number of strings exceeds limit
        ValueError: Raise error when file is not found

    Returns:
        List[str]: List containing all the target strings from the dictionary file
    """
    logging.debug(f"Execution of '{parse_input.__name__}' started")

    target_list: List[str] = []

    try:
        with open(file_path, "r") as file:
            if os.stat(file_path).st_size == 0:
                logging.error(f"Parsing input file: Input file '{file_path}' is empty")
                raise ValueError("Input file is empty")

            for line in file:
                # Remove leading and trailing whitespace (including the newline character)
                input_string = line.strip()

                # Check word length
                if (
                    TARGET_STRING_SIZE_LOWER_LIMIT
                    <= len(input_string)
                    <= TARGET_STRING_SIZE_UPPER_LIMIT
                ):
                    target_list.append(input_string)
                else:
                    logging.error(
                        f"Parsing input file: Input string length not between {TARGET_STRING_SIZE_LOWER_LIMIT} and {TARGET_STRING_SIZE_UPPER_LIMIT} characters: {input_string}"
                    )
                    raise ValueError(
                        f"Input string length not between {TARGET_STRING_SIZE_LOWER_LIMIT} and {TARGET_STRING_SIZE_UPPER_LIMIT} characters: {input_string}"
                    )

        if len(target_list) >= TARGET_STRING_SIZE_LIMIT:
            logging.error(
                f"Parsing input file: File '{file_path}' contains more than {TARGET_STRING_SIZE_LIMIT} lines"
            )
            raise ValueError("File contains more than 100 strings")

        logging.debug(
            f"Execution of '{parse_input.__name__}' ended. Output: {target_list}"
        )

        return target_list

    except FileNotFoundError:
        logging.error(f"Parsing input file: File '{file_path}' does not exists")
        raise ValueError(f"The file does not exist: '{file_path}'")
