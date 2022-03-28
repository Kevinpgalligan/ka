# ka(lculator) 🔢
ka is a small calculator language. It supports various useful features for day-to-day calculations, such as:

* Common math functions and constants.
* Fractions.
* Units and unit conversion.
* Variable assignment.

There are 3 ways to interact with it: executing individual expressions through the CLI (`ka '1+1'`), a CLI interpreter (`ka`), and a GUI (`ka --gui`).

```
>>> 2 * (1/2)
1
>>> 1 metre + 1 foot > feet
4.2808398950131235
>>> p = 0.7; C(10,3) * p^3 * (1-p)^7
0.009001692000000007
>>> sin(90 deg)
1 
>>> e^pi
23.140692632779263
```

## Contents
* [Installation](#installation)
* [Usage](#usage)
* [Manual](#manual)
  - [Grammar](#grammar)
  - [Variables](#variables)
  - [Constants](#constants)
  - [Types](#types)
  - [Functions and operators](#functions-and-operators)
  - [Units](#units)
* [FAQ](#faq)
* [Contributing](#contributing)

## Installation
Requirements:

* Qt 5 GUI framework (try: `apt install qt5-default`).
* Python 3.6+.

To install, run: `pip3 install ka-cli`. ka is currently distributed through the [Python Package Index](https://pypi.org/project/ka-cli/1.0.0/).

I would appreciate it if a kind person could help me to package it for Linux package managers.

## Usage
To execute a single expression, pass it as an argument to the CLI. You may wish to surround the expression in single quotes so that it's not messed up by your terminal. 

```
$ ka '1+1'
2
```

The CLI offers introspection commands to show the available units, functions and whatnot (run `ka -h` for help with this).

Start the interpreter by executing `ka` from your CLI with no arguments.

```
$ ka
ka version 1.0
>>> 1+1
2
>>> %help
[...insert help text here...]
>>> quit()
$
```

There are also interpreter-specific commands, prefixed by '%'. Run `%help` to see a list of these commands.

To start the GUI, run `ka --gui`.

For more information on the language and the features it offers, see the manual below.

## Manual
### Grammar
The basic unit of grammar is the statement. You can execute multiple statements at once, separated by semi-colons:

```
>>> a = 3; b = 2; 2*a*b
12
```

An individual statement can be either an assignment (`a = 3`) or an expression (`1+1`).

An assignment consists of a variable name (such as `a`), followed by `=`, followed by an expression (such as `3` or `1+1` or `sin(90 deg)`). Assignments are not expressions, so you can't nest assignments like `a=(b=3)`. You can, however, assign the value of one variable to another: `a=3; b=a;`.

An expression is a sequence of math operations that returns a value. Addition, subtraction, function calls, and so on. If the value of an expression is a quantity (a number with a unit attached), then the unit can be converted to something else using the symbol `>`. For example, this assigns `a` the magnitude of 3 metres when it's converted to feet: `a = 3m > ft`.

### Variables
ka has basic support for variables: `blah=9^3; blah`.

### Constants
`pi` and `e` are the only constants provided. Currently, they're treated like variables and can be overwritten.

### Types
ka is strongly typed, not statically typed. What this means is that when you pass a fractional number to a function that expects an integer, the type system will complain. But you don't have to declare the type of anything in advance.

The type system consists of (1) a hierarchy of numerical types, and (2) quantities.

The hierarchy of numerical types goes: Number > Real > Rational/Fraction > Integral/Integer. 'Real' numbers are represented as floating point numbers. If a fraction can be simplified to an integer, such as 2/2, then this will happen automatically. In the other direction, a type that is lower down the hierarchy, such as an integer, can be cast into a type that's further up the hierarchy in order to match a function signature.

Quantities consist of two components: a magnitude and a unit (see: the section on units). Any quantities can be multiplied together or divided into each other, but only quantities of the same unit type can be added or subtracted. For example, you can add `1 metre` and `1 foot`, but not `1 metre` and `1 second`. This is enforced by the binary operators themselves (addition and subtraction)..

Most functions can be applied to both Numbers and Quantities.

### Functions and operators
Here's a list of all the functions and operators in the language. To find out more about any of them (including what types of arguments they accept), run the CLI command `ka --function {name}`, or run the interpreter commands `%f {name}` or `%fun {name}`.

* +, -, *, /, %, ^, sin, cos, tan, sqrt, ln, log10, log2, abs, floor, ceil, round, int, float, log, C, !, quit

ka has functions and 3 types of operators: binary operators, prefix operators, and postfix operators.

The binary operators, like addition (`+`), exponentiation (`^`) and division (`/`), take two arguments and come between those arguments, like `1+1`.

The prefix operators are `+` and `-`. They take a single argument and come before that argument: `+1` and `-1`.

The only postfix operator is `!` (factorial), which takes a single argument and comes after that argument: `9!`.

Operator precedence goes:

* `!`
* `^`
* `*`, `/`, `%`
* `+`, `-`

This means that `2^3!*5+1` gets parsed the same as `((2^(3!))*5)+1`.

### Units
Here's a list of all the units supported by the language:

* second (s), metre (m), gram (g), ampere (A), kelvin (K), mole (mol), candela (cd), hertz (Hz), radian (rad), steradian (sr), newton (N), pascal (Pa), joule (J), watt (W), coulomb (C), volt (V), farad (F), ohm (ohm), siemens (S), weber (Wb), tesla (T), henry (H), degC (degC), lumen (lm), lux (lx), becquerel (Bq), gray (Gy), sievert (Sv), katal (kat), minute (min), hour (h), day (d), astronomicalunit (au), degree (deg), hectare (ha), acre (acre), litre (l), tonne (t), dalton (Da), electronvolt (eV), lightyear (lj), parsec (pc), inch (in), foot (ft), yard (yd), mile (mi), nauticalmile (sm), teaspoon (tsp), tablespoon (tbsp), fluidounce (floz), cup (cup), gill (gill), pint (pt), quart (qt), gallon (gal), grain (gr), dram (dr), ounce (oz), pound (lb), horsepower (hp), bar (bar), calorie (cal)

Notes on units:

* Division in the unit signature is represented by the symbol `|`, so 1 metre per second is written `1 m|s`. This avoids parsing ambiguities. A more complex unit signature is `1 kg | m s^2`, which is the same as `1 pascal`.
* To find out more about a specific unit, run `ka --unit {name}`, or execute `%u {name}` or `%unit {name}` in the interpreter.
* Units are case sensitive.
* You can convert from one unit to another using the `>` symbol: `1m > feet`.
* Units are part of what makes up a quantity, together with a magnitude. It only makes sense to add or subtract quantities with the same unit type. You can add two areas, for example, but it doesn't make sense to add an area and a velocity. You can multiply and divide any quantities, however.
* A unit can be a multiple of base units (a pound is 0.45 kilograms), but it can also have an offset, as in the case of the degree Celcius, which is offset from the kelvin by -273.15. This makes degC tricky to work with and as a result you can't generally combine it with other units.
* UK / Imperial measures are used for the teaspoon and other ambiguous (mostly cooking-related) units, see: <https://en.wikipedia.org/wiki/Cooking_weights_and_measures>

As for how the unit system works, it's based on the [International System of Units (SI)](https://en.wikipedia.org/wiki/International_System_of_Units). All units are represented in terms of the 7 SI base units: second, metre, gram, ampere, kelvin, mole and candela. Pounds are a multiple of the metre, and their "signature" in base units is `m^1`. Frequency, measured in hertz, is `s^-1`. Area is `m^2`. Velocity is `m s^-1`. Internally, the "unit signature" of a quantity is a 7-dimensional vector of integers, with each dimension corresponding to one of the SI base units. For example, 1 metre may have a unit signature of (1, 0, 0, 0, 0, 0, 0). 1 metre per second may have a unit signature of (1, -1, 0, 0, 0, 0, 0, 0). When you multiply two quantities together, their unit signatures are added together. When you divide, the unit signature of the divisor is subtracted.

Further reading for the interested:

* <https://en.wikipedia.org/wiki/Quantity>
* <https://en.wikipedia.org/wiki/International_System_of_Units>
* <https://en.wikipedia.org/wiki/Dimensional_analysis>
* <https://www.hillelwayne.com/post/frink/>
* <https://gmpreussner.com/research/dimensional-analysis-in-programming-languages>

## FAQ
#### How do you exit the interpreter?
Call the function `quit()`, use the interpreter command `%q` / `%quit`, or trigger an interrupt with CTRL+C.

### Why is 1 metre per second written as `1m|s` instead of `1m/s`?
I would love to be able to write `1m/s`, but this would result in a parsing ambiguity: is it 1 metre divided by the variable called `s`, or 1 metre per second? So ka instead uses `|` to represent division in unit signatures.

#### Why does `5/4 m` give units in `m^-1`?
Units have higher precedence than division, so `5/4 m` is parsed the same as `5 / (4 m)`. The solution is to write `(5/4)m`.

#### How does this compare to other calculator languages?
[Frink](https://frinklang.org/) is Turing-complete, has configurable units, has many more features than ka, and has a cool grammar. On the other hand, it's closed-source, it has expanded way beyond the scope of a simple calculator, and it has a slow start-up time, which makes it unsuitable for my purposes.

It's worth commenting a bit more on the grammar. Frink basically represents all units as variables. This means that the variable namespace is full of unit names, and it's possible for units to be overwritten accidentally. The good thing is that, coupled with the Frink grammar's support for implicit multiplication, you can write nice things like `1 m/s` and it's interpreted as you would expect (the number 1, multiplied by metres, divided by seconds; this gives 1 metre per second). But if you write `4m / 2m` you get `2m^2`. There are design trade-offs when incorporating units into the grammar of a computer language and I don't think there's a perfect solution.

[Qalculate!](https://qalculate.github.io/) seems awesome and has bucketfuls of features! On the other hand, it's a massive project written in C++, while ka consists of 1000 lines of Python code. Units in Qalculate! behave similarly to variables, except you can't overwrite them because it doesn't support variable assignment. It sensibly handles both `1m/s` and `4m / 2m`, somehow.

[F#](https://fsharpforfunandprofit.com/posts/units-of-measure/) is an example of a "real" programming language with cool unit features, but it's not suitable as a calculator.

## Contributing
Contributions are welcome, whether they be bug fixes or documentation or anything at all! I don't intend to make any major additions to the core language, since for the purposes of a calculator it's reasonably complete. That means I don't plan to make it Turing-complete.

To install ka locally, clone the repo and run `pip install .`. You may wish to test it within a virtual environment, however, if you have a copy of ka that you actually use and you don't want to break it.

[tox](https://tox.wiki/en/latest/) is used for unit testing, execute `tox` from the base directory to run all unit tests.
