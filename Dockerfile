FROM python:3.11-slim

WORKDIR /app

COPY . /app

# CMD to run the Python script with arguments
CMD ["python", "src/scrambled_strings.py", "--dictionary=data/dictionary.txt", "--input=data/input_strings.txt"]