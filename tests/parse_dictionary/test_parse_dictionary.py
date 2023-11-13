import os
import pytest

from src.utils.parse_dictionary import parse_dictionary

script_dir = os.path.dirname(__file__)


def test_parse_dictionary_nonexistent_file():
    with pytest.raises(ValueError, match="The file does not exist:"):
        parse_dictionary("nonexistent.txt")


def test_parse_dictionary_exceed_characters_file():
    input_file_path = os.path.join(script_dir, "over_character_limit_dictionary.txt")
    with pytest.raises(ValueError, match="Word length not between 2 and 20 characters"):
        parse_dictionary(input_file_path)


def test_parse_dictionary_duplicates_file():
    input_file_path = os.path.join(script_dir, "duplicate_dictionary.txt")
    with pytest.raises(ValueError, match="Duplicate word found"):
        parse_dictionary(input_file_path)
