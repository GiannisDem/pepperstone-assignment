# Scrambled-Strings

# Requirements

Before running the project, make sure you have the following requirements installed and up to date.

## Python

> [!NOTE]
> You may refer to https://realpython.com/installing-python/ for platform specific installation instructions.

Use the following command to check that you have a supported Python version installed:

```
python --version
```

Currently, the project is tested with Python 3.8+.

It is highly recommended to run the project inside a python virtual environment.

# Usage

Run the following command from your project root directory:
```
python src/scrambled_strings.py --dictionary <dictionary file path> --input <dictionary file path>
```

Running the command with the `--help` argument will output detailed information about the required arguments as shown below:

```
python src/scrambled_strings.py -h

usage: scrambled_strings.py [-h] --dictionary DICTIONARY --input INPUT

Take a set of words from a dictionary and find how many times they appear in a list of long string inputs in their original or scrambled form.

options:
  -h, --help            show this help message and exit
  --dictionary DICTIONARY
                        Path to the dictionary file.
  --input INPUT         Path to the input string file.
```

Example:
```
python src/scrambled_strings.py --dictionary data/dictionary.txt --input data/input_strings.txt
```

## Config.ini

Configure the size of the internal buffer as well as the size of the workers pool by adjusting the default values:

```
[settings]
parallel_workers=4
buffer_size=1000000

[dictionary_validations]
dictionary_size_limit=100
word_size_upper_limit=20
word_size_lower_limit=2

[input_validations]
target_string_size_limit=100
target_string_size_upper_limit=500
target_string_size_lower_limit=2
```

## Running with Docker

> [!IMPORTANT]
> Since we need to ensure the user can change the contents of both input files between each run, we are using `-v` to mount a volume between the host and the docker container.

### Limitations

Both command arguments are hardcoded to a specific directory and file names that exist inside the docker container:

```
--directory data/directory.txt
--input data/input_strings.txt
```

### Requirements

Create a folder `data` anywhere in your file system and add both `.txt` files inside, as shown below:

```
/data
|--> directory.txt
|--> input_strings.txt
```

We will use the absolute path of the above folder and pass it to the docker volume command.

### Build Image

Run the following command from your project root directory:
```
# Build Docker image containing the project
docker build --tag scrambled-string .
```

### Run

Run the following command from your project root directory:
```
# Run Docker container
docker run -v <data_folder_absolute_path>:/app/data scrambled-string

Example:
docker run -v $(pwd)/data:/app/data scrambled-string
```

### TL;DR

Even though we don't have access to each individual command argument, the user can change the contents of both `.txt` files on the fly.

# Testing

All tests can be found under the `/test` directory.

Pytest is used to implement all the test cases, so make sure to install it in your environment using `pip install pytest`.

To run the tests follow the commands below:

```
cd tests

# Windows
python -m pytest .

# Unix
pytest
```

# Design Concepts

At high level, here are the steps the project has implemented

1) Parse the dictionary and input strings files and apply validations.
2) Spawn a pool of workers responsible for running the `generate_permutations` module for each word in the dictionary file
    - Start calculating the permutations of the word
    - Utilize a buffer mechanism to store permutation in batches. Use this mechanism to limit the memory footprint.
    - When the buffer is full or there are no more permutations to generate, call the `process_permutations` module
    - The `process_permutations` module iterates the buffer and checks whether each permutation exists in the target strings and returns the results
    - If there are more permutations to generate, iterate through the above steps until all permutations are processed
    - Return the results of the process
3) When all spawn processes are finished print the aggregated result to the user

Based on the above mental model I separate each action in its own python module. That way each function is simple to understand and test.
The `main()` function inside the `scrambled_strings.py` file is responsible for importing the modules and spawning the pool of workers/threads.

A high-level view of the project structure:

```
/project
|--> data
|--> logs
|--> src # main() exist here
|    |--> utils # modules exists here
|--> tests
|--> Dockerfile
|--> README.md  
```

## Modules

> [!NOTE]
> Docstrings are added for each module/function.

### PARSE_DICTIONARY

**Description**
```
Parse a dictionary text file that includes words separated by newline, apply validations and returns a list of all words

    Args:
        file_path (str): Path of the text file as recorded from the command line arguments

    Raises:
        ValueError: Raise error when duplicate words are found in the file
        ValueError: Raise error when character length is out of specifications
        ValueError: Raise error when number of words exceeds limit
        ValueError: Raise error when file is not found

    Returns:
        List[str]: List containing all the words from the dictionary file
```

In addition to the validations required from the project description we also handle `FileNotFoundError` exception.

I could have also checked whether the file is empty and raised an exception however I believe that's a valid scenario.

### PARSE_INPUT

**Description**
```
Parse text file that includes search strings separated by newline, apply validations and return a list

    Args:
        file_path (str): Path of the text file as recorded from the command line arguments

    Raises:
        ValueError: Raise error when file is empty
        ValueError: Raise error when character length is out of specifications
        ValueError: Raise error when number of strings exceeds limit
        ValueError: Raise error when file is not found

    Returns:
        List[str]: List containing all the target strings from the dictionary file
```

Similarly, with the `parse_dictionary` module we accept the file path, read the contents and apply validations.

### GENERATE_PERMUTATIONS

**Description**
```
Calculate the permutations of the input_string in batches using a buffer mechanism. Once the buffer is full or there are no more permutations to calculate we call the process_permutations module.
Once the existence of permutations in the target strings is processed we return the results. Using the multiprocessing library we distribute the execution of this module in multiple processes.

    Args:
        input_string (str): String to calculate permutations for.
        target_list (List[str]): List of target strings as returned from the parse_input module.
        shared_result_dict (Dict[int, int]): Dictionary of the results shared between processes.
        lock (_type_): Lock that controls the access to the shared dictionary between processes.

    Returns:
        Dict[int, int]: Dictionary containing the number of permutations found for each target string.
```

Here we accept as inputs a word from the dictionary file, the list of target strings and a list that holds the results between all spawned processes.

We strip the first and last character of the word and start generating the permutations of the substring. As an optimization step we skip generating the permutations if all the characters of the substring are the same.

At this point, depending on the length of the substring the number of permutations can be huge. Hence storing all of them in a data structure is likely to exceed the available memory of the host.

For this reason we are using a buffer mechanism where we store a configurable number of permutations (**buffer_size**). 

Once the buffer is full we send the permutations to the `process_permutations` module. When the processing of the buffer is finished we store the intermediary results and continue with the generation of the remaining permutations. We continue this process until all permutations are generated and processed.

> [!NOTE]
> Depending on the machine resources we can configure the amount of memory each process will consume by adjusting the buffer size through the config.ini file.


### PROCESS_PERMUTATIONS

**Description**
```
Iterate the permutation buffer and find whether the permutation exists in either of the target strings. 
If a match is found the permutation is added in a dictionary which is shared between all batches in order to correctly calculate the final results.

    Args:
        buffer (Set[str]): Set containing the permutations of the buffer in the calculate_permutations module.
        target_list (List[str]): List containing the target strings.
        found_dict (Dict[int, Set[str]]): Dictionary that includes the results from previous batches.

    Returns:
        Dict[int, Set[str]]: The update version of the found_dict containing any new matching permutations.
```

Here we accept as inputs the buffer from the `generate_permutations` module, the list of target strings and a dictionary that stores the results of previous batches.

We iterate the buffer list and check whether each permutation exists in any of the target strings using pythons `IN` operator. If we find a match we add the permutation to the shared dictionary Dict[Int, Set]. 

> [!NOTE]
> Using a shared dictionary between batches we make sure that, even if a duplicate permutation exists in a target string and is processed twice between different batches, we only counting it once.

Once we finish processing all permutations in the buffer we return the updated shared dictionary.

**Performance Optimization**

My first thought was to check whether there is an algorithm that is optimized for string searching in order to replace the built-in `IN` operator of Python. That got me to the following algorithm [KMP](https://en.wikipedia.org/wiki/Knuth%E2%80%93Morris%E2%80%93Pratt_algorithm) that provides a linear performance O(n).

However, after more research, I found out that the algorithm behind the `IN` operator has a sublinear performance.

Implementing the buffer mechanism and running the project on multiple processes/threads we manage to make it more performant. 

However our current performance bottleneck is generating the permutation for large dictionary strings which is a CPU-bound process.

# TODO

Rewrite the build-in permutation function in a way that it will use parallel processing for distributing the generation of permutations of a given string

# Parallel Processing Discussion

Parallel processing is all about distributing the work on different threads/workers.

I have already implement it by creating multiple processes each responsible for searching whether the permutations of a given string exists in another string.

```
with multiprocessing.Manager() as manager:
            # Create a shared dict to collect results
            shared_result_dict = manager.dict({i: 0 for i, _ in enumerate(target_strings)})
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
```