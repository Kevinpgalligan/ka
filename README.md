# Ka(lculator) 🔢
Ka is a small calculator language for quick, day-to-day calculations.

<p align="center">
  <img src="https://github.com/user-attachments/assets/1e5cfb37-c8c9-4fa8-a280-c485970c4961" alt="The Ka GUI in action" />
</p>

Featuring...

* A **GUI** and **CLI**.
* **Fractions**: `(5/3) * 3` gives `5`.
* **Units** and unit conversion: `5 ft to m`.
* **Currencies** and exchange rates: `5€ to $`.
* **Probability** distributions and sampling, with a math-like syntax: `X = Bernoulli(0.3); P(X=1)`.
* **Plotting**: comes with an ergonomic interface to Python's matplotlib.
* **Arrays**, also with math-like syntax: `{3*x : x in 1..3}` gives `{3,6,9}`.
* **Lazy combinatorics**: `10000000!/9999999!` gives `10000000` rather than hanging like it would in other languages.
* **Dates and times**: `(#2024-12-25# - now()) to days` gives the number of days until Christmas.
* **Intervals** and interval arithmetic: `2*(1±0.1)` gives an interval from 1.8 to 2.2.
* Other boring stuff: Variable assignment. Common math functions and constants.

Ka aims to be convenient: you can start the GUI with a keyboard shortcut, fire off a quick calculation, and close the GUI with Ctrl-W -- no mouse needed! Or if you're pottering about in the terminal, you can do a one-off calculation with `ka '1+1'`.

More examples.

```
>>> 2 * (1/2)
1
>>> 1 metre + 1 foot to feet
4.28084
>>> p = 0.7; C(10,3) * p^3 * (1-p)^7
0.00900169
>>> p=.7; N=10; sum({C(N,k)*p^k*(1-p)^(N-k) : k in 0..4})
0.047349
>>> sin(90 deg)
1 
>>> e^pi
23.1407
>>> X = Binomial(10, 0.3); P(3 <= X < 7)
0.6066
>>> line({0,1}, {0,1}, label: "hi", legend: true)
[...shows a line plot...]
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
  - [Currency](#currency)
  - [Probability and Randomness](#probability-and-randomness)
  - [Arrays](#arrays)
  - [Dates and times](#dates-and-times)
  - [Plotting](#plotting)
  - [Lazy Combinatorics](#lazy-combinatorics)
  - [Intervals](#intervals)
  - [Configuration](#configuration)
* [FAQ](#faq)
* [Development](#development)

## Installation
Ka is currently distributed through the [Python Package Index](https://pypi.org/project/ka-cli/). To install, run:

* `pip3 install ka-cli`

Requirements:

* Python 3.6+.
* (For the GUI) Qt 5 GUI framework. If your system uses the Aptitude package manager, try: `apt install qt5-default`.

#### Windows
On Windows, you'll need to run the installation command in an Administrator console. An executable called 'ka.exe' should be created under the `Scripts` subdirectory of your Python installation. You may need to add the path to this `Scripts` folder to the "PATH" environment variable (Advanced System Settings > Environment Variables). If using pyenv, you probably need to run `pyenv rehash` so that pyenv can create a shim for the new executable.

## Usage
There are various ways to interact with Ka: executing a single expression from the CLI; running an interpreter in the terminal; executing a script file; and a GUI.

To execute a single expression, pass it as an argument to the CLI. You may wish to surround the expression in single quotes so that it's not messed up by your terminal. 

```
$ ka '1+1'
2
```

The CLI offers introspection commands to show the available units, functions and whatnot (run `ka -h` for help with this).

Start the interpreter by executing `ka` from your CLI with no arguments. There are interpreter-specific commands, prefixed by '%', like `%help`. Run `%help` to see a list of these commands.

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

Execute a script file using the `--script` argument. Each statement must be separated by a semi-colon, and the value of the last statement will be printed to the console.

```
$ ka --script path/to/script.ka
```

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

An expression is a sequence of math operations that returns a value: addition, subtraction, function calls, and so on. If the value of an expression is a quantity (a number with a unit attached), then the unit can be converted to something else using the operator `to`. For example, this assigns `a` the magnitude of 3 metres when it's converted to feet: `a = 3m to ft`.

### Constants and Numbers
`pi` and `e` are the only mathematical constants provided. They're treated like variables and can be overwritten: `pi=3`, woops. `true` and `false` are also variables, with the values `1` and `0`, respectively.

Numbers can be integers (`123`), floats (`-1.23`), fractions (`1/3`), and they can be provided in scientific notation (`1.23e-7`).

The typical selection of number bases are supported: use the `0b` prefix for binary, `0o` for octal, and `0x` for hexadecimal. So `0x10` is 16 in base-10. Note that numbers with alternative bases can only be integers, and can't be mixed with scientific notation (otherwise, there's a parsing ambiguity in something like `0x1e-10`).

### Types
Ka is strongly typed, not statically typed. This means that when you pass a fractional number to a function that expects an integer, the type system will complain. But you don't have to declare the type of anything in advance.

The type system consists of (1) a hierarchy of numerical types, (2) quantities, and (3) some other types like arrays and random variables that don't mix with the other types so much.

The hierarchy of numerical types goes: `Number` > `Real` > `Rational` (Fraction) > `Integral` (Integer). There's also a `Combinatoric` type, used to lazily evaluate combinatoric operators/functions like `!` and `C`, and `Number` > `Combinatoric`.

'Real' numbers are represented as floating point numbers. If a fraction can be simplified to an integer, such as 2/2, then this will happen automatically. In the other direction, a type that is lower down the hierarchy, such as an integer, can be cast into a type that's further up the hierarchy in order to match a function signature.

`Bool` (stands for Boolean) is essentially an alias for the `Number` type. Non-zero values represent true. The variables `true` and `false` are provided for convenience, but they're just proxies for the values 1 and 0.

Quantities consist of two components: a magnitude and a unit (see: the section on units). Any quantities can be multiplied together or divided into each other, but only quantities of the same unit type can be added or subtracted. For example, you can add `1 metre` and `1 foot`, but not `1 metre` and `1 second`. This is enforced by the binary operators themselves (addition and subtraction).

Most arithmetic functions can be applied to both Numbers and Quantities.

`String`s, like `"hello world"`, are (so far) only used as configuration parameters for the plotting interface, and there's no way to manipulate or combine them.

Other types like `Instant`s, `Interval`s and `Array`s are discussed in later sections.

### Functions and operators
Ka has functions and 3 types of operators: binary operators, prefix operators, and postfix operators.

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

Functions accept positional arguments and keyword arguments. A function call can look something like the following: `f(x, y, keyword_arg: 1, another: "hi")`. Some functions, like `plot`, accept a variable number of the same argument type; `plot` happens to accept any number of `Plot`-type arguments.

Here's a selection of functions and operators in the language. To list all the functions, run `ka --functions`. To find out more about any particular function (including what types of arguments it accepts), run the CLI command `ka --function {name}`, or run the interpreter commands `%f {name}` or `%fun {name}`.

* +, -, *, /, %, ^, <, <=, ==, !=, >, >=, sin, cos, tan, sqrt, ln, log10, log2, abs, floor, ceil, round, int, float, log, C, !, quit

### Units
Here are most of the units supported by the language. To see a complete list (excluding currencies), run `ka --units` from the command-line.

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

As for how the unit system works, it's based on the [International System of Units (SI)](https://en.wikipedia.org/wiki/International_System_of_Units). All units are represented in terms of the 7 SI base units: second, metre, gram, ampere, kelvin, mole and candela. (Update -- see the next section for a newly-added base unit: cash). Feet are a multiple of the metre, and their "signature" in base units is `m^1`. Frequency, measured in hertz, is `s^-1`. Area is `m^2`. Velocity is `m s^-1`. Internally, the "unit signature" of a quantity is a 7-dimensional vector of integers, with each dimension corresponding to one of the SI base units. For example, 1 metre may have a unit signature of (1, 0, 0, 0, 0, 0, 0). 1 metre per second may have a unit signature of (1, -1, 0, 0, 0, 0, 0, 0). When you multiply two quantities together, their unit signatures are added together. When you divide, the unit signature of the divisor is subtracted.

Further reading for the interested:

* <https://en.wikipedia.org/wiki/Quantity>
* <https://en.wikipedia.org/wiki/International_System_of_Units>
* <https://en.wikipedia.org/wiki/Dimensional_analysis>
* <https://www.hillelwayne.com/post/frink/>
* <https://gmpreussner.com/research/dimensional-analysis-in-programming-languages>

### Currency
The unit system also incorporates currencies. They exist in an 8th dimension: the dimension of cold, hard cash. Currencies can be referenced using their [ISO-4217](https://en.wikipedia.org/wiki/ISO_4217#List_of_ISO_4217_currency_codes) code names (like eur and gbp). Special symbols are provided for some currencies: € for eur, $ for usd, $ for gbp, and ¥ for jpy. Currencies can also be referenced by longer names (e.g. "mexicanpeso"), but these are verbose and subject to change.

A pre-scraped database of currencies and exchange rates are shipped with Ka, which are current as of December 23rd, 2024. To re-scrape this data, run `ka --scrape-currency-to /path/to/file`, and then move the resulting file to `~/.config/ka/currency` - at least, that's the default path, but you can change it with the `currency-path` configuration parameter.

Another configuration parameter is `base-currency`, which is set to `eur` (the ISO-4217 code name of the Euro) by default. All cash amounts are represented in the base currency, so `1 usd` will automatically be converted to `0.961345 eur` (or whatever).

The introspection commands of the interpreter/CLI do not display currencies alongside the other units, since there are too many currencies. Instead, use `ka --currencies`, or, in the interpreter, `%cs` / `%currencies`. This will show you the exchange rates as well as the currency names and symbols.

The following examples show that: 1. if you worked 24/7 for 2000 years, earning $1000 per hour, you still wouldn't be the richest person in the world; 2. if you happened to find a USB stick containing 100 bitcoins, you'd be a multi-millionaire; and 3. if you dropped 1 million dollars in 1-dollar bills on your head, you'd be hit with a force of 9810 newtons. Another reason not to hoard wealth.

```
>>> 1000 dollars|hour * 2000 years to billion dollars
17.52
>>> 100 bitcoin to million euro
8.9007
>>> mass_per_dollar = 0.001 kg | dollar
>>> G = 9.81 m|s^2
>>> 1 million dollars * mass_per_dollar * G to newtons
9810
```

### Probability and Randomness
First, the usual utilities for randomness:

* `rand()` gives a random number in the range 0-1.
* `seed(n)` sets the (integer) seed for random number generation and sampling.

Additionally, a number of discrete and continuous probability distributions / random variables are provided. Various properties of these distributions can be calculated, and they can be sampled from. A full list of distributions is shown below. For now, let's say we've already entered `X = Binomial(10, .5)`. Then:

* `E(X)` or `mean(X)` gives the expectation, a.k.a. the mean.
* `P(X=3)` gives the probability of the value 3 (discrete random variables only).
* `P(X<3)`, `P(1 < X <= 3)`, `P(X > 5)` calculate the probability of a range.
* `sample(X)` returns a random value from the distribution.
* `sample(X, n)` returns `n` random values from the distribution.

These are the discrete probability distributions and their parameters:

* `Binomial(n, p)`: `n` trials and success probability `p`.
* `Poisson(lambda)`: rate `lambda` (an integer, representing the average).
* `Geometric(p)`: success probability `p`.
* `Bernoulli(p)`: success probability `p`.
* `UniformInt(lo, hi)`: uniform distribution over the integers `lo`, `lo+1`, ..., `hi-1`, `hi`.

And these are the continuous ones:

* `Exponential(lambda)`: rate `lambda` .
* `Uniform(lo, hi)`: uniform distribution over real numbers between `lo` and `hi`.
* `Gaussian(mu, stddev)`: normal distribution with mean `mu` and standard deviation `stddev`.

Here's an example (found at `examples/estimate-pi.ka`; run with `ka --script examples/estimate-pi.ka`) that samples from the `Uniform` distribution to estimate the value of `pi`. It makes use of the Array type, discussed in the next section.

```
N = 10000;
X = Uniform(0, 1);
xs = sample(X, N);
ys = sample(X, N);
distances = {sqrt(x^2+y^2) : x in xs, y in ys};
f = size({d : d in distances, d<=1})/N;
4*f
```

### Arrays
Arrays are written like so: `{1,2,3}`. They're basically a shim over Python lists.

The elements can be arbitrary expressions: `{1+1,2*x, 1 m}`.

The special synax `lo..hi` generates a range of integers `lo`, `lo+1`, ..., `hi`.

Based on the mathematical notation for sets, arrays can also be generated from a series of clauses / conditions. For example, to calculate the sum of the squares of all odd numbers between 1 and 10: `sum({x^2 : x in 1..10, (x%2)==1})`. 

Array-related functions, given an array `A`:

* `sum(A)` calculates the sum of the elements.
* `prod(A)` calculates the product of the elements.
* `mean(A)` calculates the mean.
* `median(A)` calculates the median.
* `size(A)` returns the number of elements in the array.
* `max(A)` returns the maximum element in the array.
* `min(A)` -- need I say more?
* `range(lo,hi)` returns an array of all integers between the integers `lo` and `hi` (bounds are inclusive). `lo..hi` is syntax sugar for calling this function.
* `range(lo,hi,step)` returns numbers between `lo` and `hi` in steps of size `step`.
* `x in A` returns whether `x` is in the Array `A`.

### Dates and times
The `Instant` type represents a particular moment in time. An instance of this type can be created using the syntax `#1984-01-25#`, where any [ISO-8601](https://en.wikipedia.org/wiki/ISO_8601)-formatted string can be substituted between the "#" delimiter.

The following functions and operations are also available for working with time:

* `now()` gives the current date & time in the local timezone.
* `today()` gives the current date in the local timezone, with the time set to 00:00:00 (midnight).
* `floor(instant)` returns a copy of the Instant with the time set to midnight at the *START* of the day.
* `ceil(instant)` returns a copy of the Instant with the time set to midnight at the *END* of the day.
* Time quantities (like `10 seconds`) can be added to an Instant to get a new Instant. Same for integers, in which case the integer represents a number of days. You can also subtract time quantities and integers from an Instant.
* Subtract two instants to get the time between them.
* `Instant`s can be compared using the usual operators: `==`, `!=`, `<`, `>=`, ...
* `year(I)`, `month(I)`, `day(I)`, `hour(I)`, `minute(I)`, `second(I)` extract the different components of an Instant.

The following examples show how to calculate: 1. the number of days until Christmas, 2. the number of hours until 9am tomorrow, and 3. the number of seconds until 16:21:10, March 8th, 2025.

```
>>> (#2024-12-25# - now()) to days
5
>>> (today() + 1 day + 9 hours) - now() to hours
10.8956
>>> #2025-03-08T16:21:10#-now()
6718341.204931 s
```

### Plotting
The following interface is basically a shim over Python's matplotlib plotting library. The drawing functions, like `line(...)` and `histogram(...)`, return a `Plot`, which can then be passed to the `plot(...)` function in order to render it. Alternatively, if a `Plot` is the last value in a script, or is returned at the REPL, it will be rendered implicitly. Wherever a `colour` parameter is expected (as a String) (yes, British English spelling, sorry), it should follow the format expected by the matplotlib API ("red", "#0f0f0f", ...). The same applies for other String-type arguments that get passed along to matplotlib. 

Here's an example. Executing this script (`ka --script examples/trigplot.ka`) will render a plot of sin(x) versus cos(x).

```
xs = {0.2*i : i in 0..100};
plot(
    options(
        integer_x_ticks: true,
        xlabel: "x",
        ylabel: "y",
        grid: true,
        legend: true),
    line(xs, {sin(x) : x in xs}, label: "sin(x)", colour: "blue"),
    line(xs, {cos(x) : x in xs}, label: "cos(x)", colour: "red"));
```

`plot(*ps)` accepts a variable number of `Plot`-type arguments and uses them to produce a plot, as seen above.

`options(...)` configures the appearance of the plot, and returns a `Plot` type. Its output should be passed to the `plot(...)` function to have any effect. The following keyword arguments are accepted:

* `xlabel` (String) Label for the x-axis.
* `ylabel` (String) Same, but for y-axis.
* `xlo` (Number) Lower bound for x-axis.
* `xhi` (Number) Upper bound for x-axis.
* `ylo` (Number) Same, but for y-axis.
* `yhi` (Number) Same, but for y-axis.
* `grid` (Bool) Whether to display a grid of lines over the plot.
* `title` (String) Plot title.
* `xlog` (Bool) Whether to use log10 scale in x dimension.
* `ylog` (Bool) Same, but for y dimension.
* `legend` (Bool) Whether to display a legend, showing plot labels.
* `xticks` (Array) Where to place ticks on the x-axis.
* `yticks` (Array) Same, but for y-axis.
* `integer_x_ticks` (Bool) Whether to use integer-rounded ticks for the x-axis.
* `integer_y_ticks` (Bool) Same, but for y-axis.

`line(xs, ys, ...)` does a line plot with the given x & y values (passed as Arrays). It returns a `Plot`, which, if it's the last value in a script or is returned at the REPL, will be rendered as a matplotlib plot. It accepts all the keywords that can be passed to `options`, as well as:

* `label` (String) Label for the line.
* `colour` (String) The colour of the line itself.
* `marker` (String) Determines the appearance of the marker. See the matplotlib API for which values are acceptable, but e.g. `"o"` gives a circle, `"s"` gives a square, and `"."` gives a small dot.
* `markercolour` (String) The colour of the marker.

`histogram(xs, ...)` returns a `Plot` that can be used to render a histogram based on the values in `xs`. The range spanned by the values is divided up into bins; the number of values falling into each bin is counted; and then a bar is plotted for each bin showing the number of values it contains. Like `line`, it accepts all the same keyword arguments as `options`, as well as:

* `label` (String) Label for the histogram.
* `cumulative` (Bool) Whether the count should accumulate across the bins. If `true`, the bars will always increase in height. 
* `normalise` (Bool) If `true`, the height of each bar will be divided by the total number of values. This can be combined with `cumulative` to plot a cumulative distribution function (CDF).
* `colour` (String) Colour of the bars.
* `num_bins` (Number) How many bins.
* `bin_width` (Number) The width of the bins.
* `start` (Number) Where the bins should start on the x-axis. If not given, this is based on the minimum of the values.
* `align` (String) How the bars should be aligned with the center of the bin. Acceptable values are `"left"`, `"mid"` (default), and `"right"`.
* `border_colour` (String) The border colour of the histogram bars.

Here's an example that uses `histogram(...)` to plot the CDF of a Poisson distribution (see `examples/cdf.ka`).

```
X = Poisson(7);
xs = sample(X, 1000);
histogram(xs,
          grid: true,
          title: "Sample CDF for Poisson distribution with rate=7",
          xlabel: "x",
          ylabel: "cumulative probability",
          normalise: true,
          cumulative: true,
          integer_x_ticks: true,
          yticks: range(0,1,0.2),
          border_colour: "black")
```

`scatter(xs, ys, ...)` produces a scatter plot using the given x & y coordinates, and accepts the following keyword arguments in addition to the common ones:

* `label` (String) Need I say more?
* `marker` (String) See above.
* `size` (Number) Size of the marker.
* `colour` (String) Colour of the marker.

An example, found in `examples/scatterplot.ka`:

```
G = Gaussian(0, 10);
N = 100;
scatter(
    sample(G, N),
    sample(G, N),
    marker: ".",
    colour: "green",
    xlabel: "x",
    ylabel: "y",
    title: "2d Gaussian",
    grid: true)
```

`vline(x, colour: String, weight: Number, style: String)` draws a vertical line at the given x coordinate. The keyword argument `weight` determines the line thickness, and `style` determines the line style (e.g. use `"--"` for a dotted line; consult the matplotlib API for other line styles).

`hline(y, ...)` is like `vline` but horizontal.

`text(x, y, s, colour: String, size: String)` displays the String `s` at the given `x` & `y` coordinates. The keyword argument `size` sets the font size.

### Lazy Combinatorics
Some functions and operators, like the factorial (`5!`) and binomial coefficient function (`C(5,3)`), return a Combinatoric type instead of a number. This type can be used wherever the Number type can be used, but is evaluated lazily. For example, if `a=100!` is entered at the REPL, the factorial won't be evaluated at all, because its value hasn't been used anywhere. If `a/99!` is then entered, the Combinatoric will finally be evaluated, but not before the numerator and denominator mostly cancel out, leaving just `100`. No multiplication is required to compute the final value.

The value won't always be resolved automatically, e.g. currently you'll get an error if you pass a Combinatoric type in an Array to the plotting interface. This can be resolved by explicitly resolving the value with `int(c)` or `float(c)`.

### Intervals
Interval arithmetic is supported by the language via the `Interval` type. `[-5,10]` is an interval containing all real numbers between -5 and 10, hence why `3.123123 in [-5,10]` returns `1` (meaning "true"). Intervals can be used to perform calculations with uncertainty.

Most numeric operations can be performed with, or on, intervals. Some examples...

```
1 ± 0.1            --> [0.9, 1.1]
tol(1, 0.1)        --> [0.9, 1.1]
   (same as ±)
[0,1] + 1          --> [1, 2]
2 * [5,10]         --> [10, 20]
5 in [0,10]        --> 1
5 in [6,10]        --> 0
3 < [2,10]         --> 0    
   (only true if true for all elements in interval)
3 < [5, 10]        --> 1
[0,3] < [5, 10]    --> 1   
   (true if true for all pairwise combinations of elements)
[-1, 1]^2          --> [0, 1]
log2([4, 16])      --> [2, 4]
sqrt([-1,1])       --> (Error, square root of negative numbers)
abs([-10, 1])      --> [0, 1]
min([-5, 5], 0)    --> [-5, 0]
   (it's like taking the minmum of 0 and each element)
lower([0,1])       --> 0
upper([0,1])       --> 1
size([-1,.5])      --> 1.5
```

### Configuration
Ka can be configured through a config file at `${YOUR_HOME_DIR}/.config/ka/config`. All available properties are shown below with their default values.

* `precision` determines the floating point precision.
* Various properties determine characteristics of the GUI like its appearance and keyboard shortcuts.
* `save-history` determines whether to save a history of commands to the history file, and can be `true` or `false`; `history-path` determines where this file is located. (Note: loading and saving the history fails softly, since it's non-essential).
* `prompt` defines the interpreter prompt.
* `base-currency` is the currency in which all cash amounts will be represented; `currency-path` will be used to look for a file containing a table of currencies and their exchange rates.

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
save-history=true
history-path=[home directory]/.config/ka/history
prompt=>>>
base-currency=eur
currency-path=[home directory]/.config/ka/currency
```

## FAQ
#### How do you exit the interpreter?
Call the function `quit()`, use the interpreter command `%q` / `%quit`, or trigger an interrupt with CTRL+C.

#### Why is 1 metre per second written as `1m|s` instead of `1m/s`?
I would love to be able to write `1m/s`, but this would result in a parsing ambiguity: is it 1 metre divided by the variable called `s`, or 1 metre per second? So Ka instead uses `|` to represent division in unit signatures.

#### Why does `5/4 m` give units in `m^-1`?
Units have higher precedence than division, so `5/4 m` is parsed the same as `5 / (4 m)`. The solution is to write `(5/4)m`.

#### How does this compare to other calculator languages?
Below is a selection of other calculator languages that I'm aware of. A few things that set Ka apart: a relatively small codebase; math-like probability and array syntax; lazy combinatorics; and a plotting interface.

* [Frink](https://frinklang.org/) - or more specifically, Hillel Wayne's [article](https://www.hillelwayne.com/post/frink/) about it - was my inspiration for making my own calculator language. Frink's syntax is very nice. Space-separated expressions are multiplied together, so `2 x` multiplies `2` by `x`, and units are all represented as variables. As a result, `1 m/s` is interpreted as "one times metres divided by seconds". Neat! Frink's unit catalogue is more extensive than Ka's, and it has string-processing and control structures that Ka doesn't, among other things. On the other hand, it's closed-source and has a slow start-up time, which makes it unsuitable for my purposes.
* [Qalculate!](https://qalculate.github.io/) is a feature-rich C++-based calculator. If I'd known of its existence before starting Ka, then I mightn't have bothered, although there are advantages to the Ka codebase being small and written in a dynamic language.
* [numbat](https://github.com/sharkdp/numbat) also looks cool.
* [F#](https://fsharpforfunandprofit.com/posts/units-of-measure/) is an example of a "real" programming language with unit features, but it's not suitable as a calculator.

## Development
To install Ka locally, clone the repo and run `pip3 install .`. You may wish to test it within a virtual environment, however, if you have a copy of Ka that you actually use and you don't want to break it.

[tox](https://tox.wiki/en/latest/) is used for unit testing, execute `tox` from the base directory to run all unit tests.

To run an individual script, such as `gui.py`, change to the `src/` directory and run `python3 -m ka.gui`. See [here](https://stackoverflow.com/questions/45446418/modulenotfounderror-no-module-named-main-xxxx-main-is-not-a-packag) for why.
