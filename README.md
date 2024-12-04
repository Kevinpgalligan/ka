# Ka(lculator) 🔢
Ka is a small calculator language for quick, day-to-day calculations. It aims to be convenient: you can start the GUI, do your sums, and close the GUI with Ctrl-W -- no keyboard needed! Or if you're pottering about in the terminal, you can do a quick one-off calculation with `ka '1+1'`.

Featuring...

* A **GUI** and **CLI**.
* **Fractions**: `(5/3) * 3` gives `5`.
* **Units** and unit conversion: `5 ft to m`.
* **Probability** distributions and sampling: `X = Bernoulli(0.3); P(X=1)`.
* **Arrays** with math-like syntax: `{3*x : x in [1,3]}` gives `{3,6,9}`.
* **Lazy combinatorics**: `10000000!/9999999!` gives `10000000` rather than hanging.
* Other boring stuff: Variable assignment. Common math functions and constants.

More examples.

```
>>> 2 * (1/2)
1
>>> 1 metre + 1 foot to feet
4.28084
>>> p = 0.7; C(10,3) * p^3 * (1-p)^7
0.00900169
>>> p=.7; N=10; sum({C(N,k)*p^k*(1-p)^(N-k) : k in [0,4]})
0.047349
>>> sin(90 deg)
1 
>>> e^pi
23.1407
>>> X = Binomial(10, 0.3); P(3 <= X < 7)
0.6066
```

## Contents
* [Installation](#installation)
* [Usage](#usage)
* [Manual](#manual)
  - [Grammar](#grammar)
  - [Variables](#variables)
  - [Constants and Numbers](#constants-and-numbers)
  - [Types](#types)
  - [Functions and operators](#functions-and-operators)
  - [Units](#units)
  - [Probability](#probability)
  - [Arrays](#arrays)
  - [Lazy Combinatorics](#lazy-combinatorics)
  - [Configuration](#configuration)
* [FAQ](#faq)
* [Development](#development)

## Installation
Requirements:

* Qt 5 GUI framework (try: `apt install qt5-default`).
* Python 3.6+.

To install, run: `pip3 install ka-cli`. ka is currently distributed through the [Python Package Index](https://pypi.org/project/ka-cli/).

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
ka version 1.2
>>> 1+1
2
>>> %help
[...insert help text here...]
>>> quit()
$
```

There are also interpreter-specific commands, prefixed by '%', like `%help`. Run `%help` to see a list of these commands.

To start the GUI, run `ka --gui`.

## Manual
### Grammar
The basic unit of grammar is the statement. Multiple statements can be executed at once, separated by semi-colons:

```
>>> a = 3; b = 2; 2*a*b
12
```

An individual statement can be either an assignment (`a = 3`) or an expression (`1+1`).

An assignment consists of a variable name (such as `a`), followed by `=`, followed by an expression (such as `3` or `1+1` or `sin(90 deg)`). Assignments are not expressions, so you can't nest assignments like `a=(b=3)`. You can, however, assign the value of one variable to another: `a=3; b=a;`.

An expression is a sequence of math operations that returns a value. Addition, subtraction, function calls, and so on. If the value of an expression is a quantity (a number with a unit attached), then the unit can be converted to something else using the operator `to`. For example, this assigns `a` the magnitude of 3 metres when it's converted to feet: `a = 3m to ft`.

### Constants and Numbers
`pi` and `e` are the only constants provided. Currently, they're treated like variables and can be overwritten: `pi=3`, woops.

The typical selection of number bases are supported: use the `0b` prefix for binary, `0o` for octal, and `0x` for hexadecimal. So `0x10` is 16 in base-10. Note that alternative bases can only be integers, and can't be mixed with scientific notation (otherwise, there's a parsing ambiguity in something like `0x1e-10`).

### Types
ka is strongly typed, not statically typed. This means that when you pass a fractional number to a function that expects an integer, the type system will complain. But you don't have to declare the type of anything in advance.

The type system consists of (1) a hierarchy of numerical types, (2) quantities, and (3) some other types like arrays and random variables that don't mix with the other types so much.

The hierarchy of numerical types goes: Number > Real > Rational/Fraction > Integral/Integer. There's also a Combinatoric type, used to lazily evaluate combinatoric operators/functions like `!` and `C`, and Number > Combinatoric.

'Real' numbers are represented as floating point numbers. If a fraction can be simplified to an integer, such as 2/2, then this will happen automatically. In the other direction, a type that is lower down the hierarchy, such as an integer, can be cast into a type that's further up the hierarchy in order to match a function signature.

Quantities consist of two components: a magnitude and a unit (see: the section on units). Any quantities can be multiplied together or divided into each other, but only quantities of the same unit type can be added or subtracted. For example, you can add `1 metre` and `1 foot`, but not `1 metre` and `1 second`. This is enforced by the binary operators themselves (addition and subtraction).

Most functions can be applied to both Numbers and Quantities.

### Functions and operators
Here's a selection of functions and operators in the language. To list all the functions, run `ka --functions`. To find out more about any particular function (including what types of arguments it accepts), run the CLI command `ka --function {name}`, or run the interpreter commands `%f {name}` or `%fun {name}`.

* +, -, *, /, %, ^, <, <=, ==, !=, >, >=, sin, cos, tan, sqrt, ln, log10, log2, abs, floor, ceil, round, int, float, log, C, !, quit

ka has functions and 3 types of operators: binary operators, prefix operators, and postfix operators.

The binary operators, like addition (`+`), exponentiation (`^`) and division (`/`), take two arguments and come between those arguments, like `1+1`.

The prefix operators are `+` and `-`. They take a single argument and come before that argument: `+1` and `-1`.

The only postfix operator is `!` (factorial), which takes a single argument and comes after that argument: `9!`.

Operator precedence goes:

* `!`
* `^`
* `*`, `/`, `%`
* `+`, `-`
* `<`, `<=`, `>`, `>=`, `==`, `!=`

This means that `2^3!*5+1` gets parsed the same as `((2^(3!))*5)+1`.

### Units
Here are most of the units supported by the language. To see a complete list, run `ka --units` from the command-line. 

* second (s), metre (m), gram (g), ampere (A), kelvin (K), mole (mol), candela (cd), hertz (Hz), radian (rad), steradian (sr), newton (N), pascal (Pa), joule (J), watt (W), coulomb (C), volt (V), farad (F), ohm (ohm), siemens (S), weber (Wb), tesla (T), henry (H), degC (degC), lumen (lm), lux (lx), becquerel (Bq), gray (Gy), sievert (Sv), katal (kat), minute (min), hour (h), day (d), astronomicalunit (au), degree (deg), hectare (ha), acre (acre), litre (l), tonne (t), dalton (Da), electronvolt (eV), lightyear (lj), parsec (pc), inch (in), foot (ft), yard (yd), mile (mi), nauticalmile (sm), teaspoon (tsp), tablespoon (tbsp), fluidounce (floz), cup (cup), gill (gill), pint (pt), quart (qt), gallon (gal), grain (gr), dram (dr), ounce (oz), pound (lb), horsepower (hp), bar (bar), calorie (cal)

The following prefixes are also supported, mostly coming from the SI standard. For convenience, their shorthand names and multipliers are provided here.

* yotta (Y, 10^24), zetta (Z, 10^21), exa (E, 10^18), peta (P, 10^15), tera (T, 10^12), giga (G, 10^9), mega (M, 10^6), kilo (k/K, 10^3), hecto (h, 10^2), deca (da, 10^1), deci (d, 10^-1), centi (c, 10^-2), milli (m, 10^-3), micro (μ, 10^-6), nano (n, 10^-9), pico (p, 10^-12), femto (f, 10^-15), atto (a, 10^-18), zepto (z, 10^-21), yocto (y, 10^-24), kibi (Ki, 2^10), mebi (Mi, 2^20), gibi (Gi, 2^30), tebi (Ti, 2^40)

Notes on units:

* Division in the unit signature is represented by the symbol `|`, so 1 metre per second is written `1 m|s`. This avoids parsing ambiguities. A more complex unit signature is `1 kg | m s^2`, which is the same as `1 pascal`.
* To find out more about a specific unit, run `ka --unit {name}`, or execute `%u {name}` or `%unit {name}` in the interpreter.
* Units are case sensitive.
* You can convert from one unit to another using the `to` operator: `1m to feet`.
* Units are part of what makes up a quantity, together with a magnitude. It only makes sense to add or subtract quantities of the same unit type. You can add two areas, for example, but it doesn't make sense to add an area and a velocity. You can multiply and divide any quantities, however.
* A unit can be a multiple of base units (a pound is 0.45 kilograms), but it can also have an offset, as in the case of the degree Celcius, which is offset from the kelvin by -273.15. This makes degC tricky to work with and as a result you can't generally combine it with other units.
* UK / Imperial measures are used for the teaspoon and other ambiguous (mostly cooking-related) units, see: <https://en.wikipedia.org/wiki/Cooking_weights_and_measures>

As for how the unit system works, it's based on the [International System of Units (SI)](https://en.wikipedia.org/wiki/International_System_of_Units). All units are represented in terms of the 7 SI base units: second, metre, gram, ampere, kelvin, mole and candela. Feet are a multiple of the metre, and their "signature" in base units is `m^1`. Frequency, measured in hertz, is `s^-1`. Area is `m^2`. Velocity is `m s^-1`. Internally, the "unit signature" of a quantity is a 7-dimensional vector of integers, with each dimension corresponding to one of the SI base units. For example, 1 metre may have a unit signature of (1, 0, 0, 0, 0, 0, 0). 1 metre per second may have a unit signature of (1, -1, 0, 0, 0, 0, 0, 0). When you multiply two quantities together, their unit signatures are added together. When you divide, the unit signature of the divisor is subtracted.

Further reading for the interested:

* <https://en.wikipedia.org/wiki/Quantity>
* <https://en.wikipedia.org/wiki/International_System_of_Units>
* <https://en.wikipedia.org/wiki/Dimensional_analysis>
* <https://www.hillelwayne.com/post/frink/>
* <https://gmpreussner.com/research/dimensional-analysis-in-programming-languages>

### Probability
A number of discrete and continuous probability distributions / random variables are provided. Various properties of these distributions can be calculated, and they can be sampled from. A full list of distributions is shown below. For now, let's say we've already entered `X = Binomial(10, .5)`. Then:

* `E(X)` or `mean(X)` gives the expectation, a.k.a. the mean.
* `P(X=3)` gives the probability of the value 3 (discrete random variables only).
* `P(X<3)`, `P(1 < X <= 3)`, `P(X > 5)` calculate the probability of a range.
* `sample(X)` returns a random value from the distribution.
* `sample(X, n)` returns `n` random values from the distribution.

These are the discrete probability distributions and their parameters:

* `Binomial(n, p)`: `n` trials and success probability `p`.
* `Poisson(lambda)`: rate `lambda`.
* `Geometric(p)`: success probability `p`.
* `Bernoulli(p)`: success probability `p`.
* `UniformInt(lo, hi)`: uniform distribution over the integers `lo`, `lo+1`, ..., `hi-1`, `hi`.

And these are the continuous ones:

* `Exponential(lambda)`: rate `lambda` .
* `Uniform(lo, hi)`: uniform distribution over real numbers between `lo` and `hi`.
* `Gaussian(mu, stddev)`: normal distribution with mean `mu` and standard deviation `stddev`.

### Arrays
Arrays are written like so: `{1,2,3}`. They're basically a shim over Python lists.

The elements can be arbitrary expressions: `{1+1,2*x, 1 m}`.

The interval `[lo,hi]` generates a range of integers `lo`, `lo+1`, ..., `hi`.

Based on the mathematical notation for sets, arrays can also be generated from a series of clauses / conditions. For example, to calculate the sum of the squares of all odd numbers between 1 and 10: `sum({x^2 : x in [1,10], (x%2)==1})`. 

Array-related functions, given an array `A`:

* `sum(A)` calculates the sum of the elements.
* `prod(A)` calculates the product of the elements.
* `mean(A)` calculates the mean.
* `median(A)` calculates the median.
* `size(A)` returns the number of elements in the array.
* `max(A)` returns the maximum element in the array.
* `min(A)` -- need I say more?
* `range(lo,hi)` returns an array of all integers between the integers `lo` and `hi` (bounds are inclusive). `[lo,hi]` is syntax sugar for calling this function.
* `range(lo,hi,step)` returns numbers between `lo` and `hi` in steps of size `step`.

### Lazy Combinatorics
Some functions and operators, like the factorial (`5!`) and binomial coefficient function (`C(5,3)`), return a Combinatoric type instead of a number. This type can be used wherever the Number type can be used, but is evaluated lazily. For example, if `a=100!` is entered at the REPL, the factorial won't be evaluated at all, because its value hasn't been used anywhere. If `a/99!` is then entered, the Combinatoric will finally be evaluated, but not before the numerator and denominator mostly cancel out, leaving just `100`. Basically no multiplication is required to compute the final value.

### Configuration
ka can be configured through a config file at `${YOUR_HOME_DIR}/.config/ka/config`. All available properties are shown below with their default values. `precision` determines the floating point precision; the other properties determine various characteristics of the GUI like its dimensions and keyboard shortcuts.

```
precision=6
font-size=15
window-width=600
window-height=400
shortcut-up=Ctrl+Up
shortcut-down=Ctrl+Down
shortcut-functions=Ctrl+F
shortcut-units=Ctrl+Q
shortcut-prefixes=Ctrl+P
shortcut-close=Ctrl+W
```

## FAQ
#### How do you exit the interpreter?
Call the function `quit()`, use the interpreter command `%q` / `%quit`, or trigger an interrupt with CTRL+C.

#### Why is 1 metre per second written as `1m|s` instead of `1m/s`?
I would love to be able to write `1m/s`, but this would result in a parsing ambiguity: is it 1 metre divided by the variable called `s`, or 1 metre per second? So ka instead uses `|` to represent division in unit signatures.

#### Why does `5/4 m` give units in `m^-1`?
Units have higher precedence than division, so `5/4 m` is parsed the same as `5 / (4 m)`. The solution is to write `(5/4)m`.

#### How does this compare to other calculator languages?
Below is a selection of other calculator languages that I'm aware of. A few things that set ka apart: a relatively small codebase; math-like probability and array syntax; and lazy combinatorics.

* [Frink](https://frinklang.org/) - or more specifically, Hillel Wayne's [article](https://www.hillelwayne.com/post/frink/) about it - was my inspiration for making my own calculator language. Frink's syntax is very nice. Space-separated expressions are multiplied together, so `2 x` multiplies `2` by `x`, and units are all represented as variables. As a result, `1 m/s` is interpreted as "one times metres divided by seconds". Neat! Frink's unit catalogue is more extensive than ka's, and it has string-processing and control structures that ka doesn't, among other things. On the other hand, it's closed-source and has a slow start-up time, which makes it unsuitable for my purposes.
* [Qalculate!](https://qalculate.github.io/) is a feature-rich C++-based calculator. If I'd known of its existence before starting ka, then I mightn't have bothered, although there are advantages to the ka codebase being small and written in a dynamic language.
* [numbat](https://github.com/sharkdp/numbat) also looks cool.
* [F#](https://fsharpforfunandprofit.com/posts/units-of-measure/) is an example of a "real" programming language with unit features, but it's not suitable as a calculator.

## Development
To install ka locally, clone the repo and run `pip3 install .`. You may wish to test it within a virtual environment, however, if you have a copy of ka that you actually use and you don't want to break it.

[tox](https://tox.wiki/en/latest/) is used for unit testing, execute `tox` from the base directory to run all unit tests.

To run an individual script, such as `gui.py`, change to the `src/` directory and run `python3 -m ka.gui`. See [here](https://stackoverflow.com/questions/45446418/modulenotfounderror-no-module-named-main-xxxx-main-is-not-a-packag) for why.
