import configparser
import logging
import os
from typing import List

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "../../config.ini"))

DICTIONARY_SIZE_LIMIT = int(
    config.get("dictionary_validations", "dictionary_size_limit")
)
WORD_SIZE_UPPER_LIMIT = int(
    config.get("dictionary_validations", "word_size_upper_limit")
)
WORD_SIZE_LOWER_LIMIT = int(
    config.get("dictionary_validations", "word_size_lower_limit")
)


def parse_dictionary(file_path: str) -> List[str]:
    """Parse a dictionary text file that includes words separated by newline, apply validations and returns a list of all words

    Args:
        file_path (str): Path of the text file as recorded from the command line arguments

    Raises:
        ValueError: Raise error when duplicate words are found in the file
        ValueError: Raise error when character length is out of specifications
        ValueError: Raise error when number of words exceeds limit
        ValueError: Raise error when file is not found

    Returns:
        List[str]: List containing all the words from the dictionary file
    """
    logging.debug(f"Execution of '{parse_dictionary.__name__}' started")

    word_list: List[str] = []

    try:
        with open(file_path, "r") as file:
            for line in file:
                # Remove leading and trailing whitespace (including the newline character)
                word = line.strip()

                # Check word length and duplicates
                if WORD_SIZE_LOWER_LIMIT <= len(word) <= WORD_SIZE_UPPER_LIMIT:
                    if word in word_list:
                        logging.error(
                            f"Parsing dictionary file: Duplicate word found: {word}"
                        )
                        raise ValueError(f"Duplicate word found: {word}")

                    word_list.append(word)
                else:
                    logging.error(
                        f"Parsing dictionary file: Word length not between {WORD_SIZE_LOWER_LIMIT} and {WORD_SIZE_UPPER_LIMIT} characters: {word}"
                    )
                    raise ValueError(
                        f"Word length not between {WORD_SIZE_LOWER_LIMIT} and {WORD_SIZE_UPPER_LIMIT} characters: {word}"
                    )

        if len(word_list) > DICTIONARY_SIZE_LIMIT:
            logging.error(
                f"Parsing dictionary file: File '{file_path}' contains more than {DICTIONARY_SIZE_LIMIT} words"
            )
            raise ValueError(f"File contains more than {DICTIONARY_SIZE_LIMIT} words")

        logging.debug(
            f"Execution of '{parse_dictionary.__name__}' ended. Output: {word_list}"
        )

        return word_list

    except FileNotFoundError:
        logging.error(f"Parsing dictionary file: File '{file_path}' does not exists")
        raise ValueError(f"The file does not exist: '{file_path}'")
