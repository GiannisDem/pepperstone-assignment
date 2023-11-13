import pytest
import sys
import os
from multiprocessing import Manager

# Add the path to your module's directory
module_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(module_dir, "../../src"))


from src.utils.generate_permutations import generate_permutations_with_buffer



@pytest.mark.parametrize(
    ("input_str", "target_strings", "expected"),
    (
        ("", ["abcdefg"], {0: 0}),
        ("aa", ["abcdefg"], {0: 0}),
        ("abc", ["abcdefg"], {0: 1}),
        ("abcd", ["abcdefgacbd"], {0: 2}),
        ("axpaj", ["a", "axpajasfe", "afasdfapxajikaaxpjke"], {0: 0, 1: 1, 2: 2}),
    ),
)
def test_generate_permutations_with_buffer(input_str, target_strings, expected):
    with Manager() as manager:
        result_dict = manager.dict({i: 0 for i, _ in enumerate(target_strings)})

        # Call the worker function in the current process for testing
        generate_permutations_with_buffer(
            input_str, target_strings, result_dict, manager.Lock()
        )

        # Check the result
        assert dict(result_dict) == expected


@pytest.mark.parametrize(
    ("input_str", "target_strings", "expected"),
    ((1, ["abcdefg"], {0: 0}),),
)
def test_generate_permutations_with_buffer_error(input_str, target_strings, expected):
    with Manager() as manager:
        result_dict = manager.dict({i: 0 for i, _ in enumerate(target_strings)})

        with pytest.raises(TypeError):
            generate_permutations_with_buffer(
                input_str, target_strings, result_dict, manager.Lock()
            )


if __name__ == "__main__":
    pytest.main()
