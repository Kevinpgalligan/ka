# ka(lculator) 🔢
ka is a small calculator language. It supports various useful features for day-to-day calculations, such as:

* Common math functions (combinatoric, trigonometric, etc.) & constants.
* Fractions.
* Units and unit conversion.
* Variable assignment.

There are three ways to interface with it: direct CLI commands (`ka '1+1'`), a CLI interpreter (`ka`), and a GUI (`ka --gui`).

```
>>> sin(90 deg)
1 
>>> 2 * (1/2)
1
>>> 1m + 1ft
1.3048 m
>>> 5 metres > feet
16.404199475065617
>>> 5! + C(4,3)
124
>>> a = 3; b = 2; a*b
6
>>> e^pi
23.140692632779263
>>> quit()
$
```

## TODO
* Fix once-off commands starting with '-'.
* Simple GUI.
* Documentation for units (list of units, unit behaviour, unit arithmetic).
* Documentation for functions.
* Upload to PyPI, add link to README.

## Contents
* [Installation](#installation)
* [Usage](#usage)
* [FAQ](#faq)
* [Manual](#manual)
  - [Grammar](#grammar)
  - [Variables](#variables)
  - [Constants](#constants)
  - [Types](#types)
  - [Functions and operators](#functions-and-operators)
  - [Units](#units)
* [Contributing](#contributing)

## Installation
ka is currently distributed through PyPI (insert link here): `pip3 install ka-cli`.

If a kind person could help me to package it for the various Linux distributions, I would greatly appreciate it.

## Usage
To run a once-off command, surround the blah you want to execute in single quotes so that it's note interpreted as an argument to the CLI:

```
$ ka '1+1'
2
```

To start the interpreter, execute `ka` with no arguments:

```
$ ka
ka version 1.0
>>> 1+1
0
>>>
```

To start the GUI, run `ka --gui`.

Here's some of the stuff you can do.

## FAQ
#### How do you exit the interpreter?
Call the function `quit()`, use the interpreter command `%q` / `%quit`, or trigger an interrupt with CTRL+C.

#### Why does `5/4 m` give units in `m^-1`?
Units have higher precedence than division in the parsing, so `5/4 m` is parsed the same as `5 / (4 m)`. The solution is to write `(5/4)m`.

#### How does this compare to other calculator languages?
TODO

## Manual
### Grammar
The basic unit of grammar is the statement. You can execute multiple statements at once, separated by semi-colons:

```
>>> a = 3; b = 2; 2*a*b
12
```

An individual statement can be either an assignment (`a = 3`) or an expression (`1+1`).

An assignment consists of a variable name (such as `a`), followed by `=`, followed by an expression (such as `3` or `1+1` or `sin(90 deg)`). Assignments are not expressions, so you can't nest assignments like `a=(b=3)`. You can, however, assign the value of one variable to another: `a=3; b=a;`.

An expression is a sequence of math operations that returns a value. Addition, subtraction, function calls, and so on. If the value of an expression is a quantity, then the unit can be converted to something else using the symbol `>`. For example, this assigns `a` the magnitude of 3 metres when it's converted to feet: `a = 3m > ft`.

### Variables
ka has basic support for variables: `blah=9^3; blah`.

### Constants
`pi` and `e` are the only constants provided. Currently, they're treated like variables and can be overwritten.

### Types
ka is strongly typed, not statically typed. What this means is that when you pass a fractional number to a function that expects an integer, the type system will complain. But you don't have to declare the type of anything in advance.

The type system consists of (1) a hierarchy of numerical types, and (2) quantities.

The hierarchy of numerical types goes: Number > Real > Rational/Fraction > Integral/Integer. 'Real' numbers are represented as floating point numbers. If a fraction can be simplified to an integer, such as 2/2, then this will happen automatically. In the other direction, a type that is lower down the hierarchy, such as an integer, can be cast into a type that's further up the hierarchy in order to match a function signature.

Quantities consist of two components: a magnitude and a unit (see: the section on units). Any quantities can be multiplied together or divided into each other, but only quantities of the same unit type can be added or subtracted. For example, you can add a `1 metre` and `1 foot`, but not `1 metre` and `1 second`. This is enforced by the binary operators themselves (addition and subtraction) rather than any type-checking built into the language.

Most functions can be applied to both Numbers and Quantities.

### Functions and operators
ka has functions and 3 types of operators: binary operators, prefix operators, and postfix operators.

The binary operators, like addition (`+`), exponentiation (`^`) and division (`/`), take two arguments and slot in between those arguments, like `1+1`.

The prefix operators are `+` and `-`. They take a single argument and come before that argument: `+1` and `-1`.

The only postfix argument is `!` (factorial), which takes a single argument and comes after that argument: `9!`.

Operator precedence goes:

* `!`
* `^`
* `*`, `/`, `%`
* `+`, `-`

Here's a list of all the functions and operators. To find out more about any of them (including what types of arguments they accept), run the CLI command `ka --function {name}`, or run `%f {name}` or `%fun {name}` in the interpreter.

```
+, -, *, /, %, ^, sin, cos, tan, sqrt, ln, log10, log2, abs, floor, ceil, round, int, float, log, C, !, quit
```

### Units
TODO

## Contributing
Contributions are welcome, whether they be bug fixes or documentation or anything at all! Note that I don't intend to make any major additions to the core language, since for the purposes of a calculator it's reasonably complete. That means I don't plan to make it Turing-complete.

To install ka locally, clone the repo and run `pip install .`. You may wish to test it within a virtual environment, however, if you have a copy of ka that you actually use and you don't want to break it.

[tox](https://tox.wiki/en/latest/) is used for unit testing, execute `tox` from the base directory to run all unit tests.
