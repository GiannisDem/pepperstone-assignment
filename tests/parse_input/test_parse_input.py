import os
import pytest

from src.utils.parse_input import parse_input

script_dir = os.path.dirname(__file__)


def test_parse_input_nonexistent_file():
    with pytest.raises(ValueError, match="The file does not exist"):
        parse_input('nonexistent.txt')


def test_parse_input_empty_file():
    input_file_path = os.path.join(script_dir, "empty_input.txt")
    with pytest.raises(ValueError, match="Input file is empty"):
        parse_input(input_file_path)


def test_parse_input_exceed_limit_file():
    input_file_path = os.path.join(script_dir, "exceed_limit_input.txt")
    with pytest.raises(ValueError, match="File contains more than 100 strings"):
        parse_input(input_file_path)


def test_parse_input_exceed_characters_file():
    input_file_path = os.path.join(script_dir, "over_character_limit_input.txt")
    with pytest.raises(
        ValueError, match="Input string length not between 2 and 500 characters"
    ):
        parse_input(input_file_path)
