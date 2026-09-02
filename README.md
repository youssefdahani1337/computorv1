# ComputorV1

A simple Python program that reduces and solves polynomial equations of degree 2 or lower.

## Features

- Parses polynomial equations
- Prints the reduced form
- Detects the polynomial degree
- Solves equations of degree 0, 1, and 2
- Supports real and complex solutions
- Handles equations with a degree greater than 2
- Uses a custom square-root implementation

## Input format

Every polynomial term must follow this format:

```text
coefficient * X^exponent
```

Example:

```text
5 * X^0 + 4 * X^1 - 9.3 * X^2 = 1 * X^0
```

## Usage

Pass the equation as an argument:

```bash
python3 computor.py "5 * X^0 + 4 * X^1 - 9.3 * X^2 = 1 * X^0"
```

Or start the program without an argument and enter the equation through standard input:

```bash
python3 computor.py
```

## Tests

Run the unit tests with:

```bash
python3 -m unittest -v test_computor.py
```

## Requirements

- Python 3
- No external packages
