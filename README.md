### ka(lculator)
ka is a small calculator language. It supports various useful features for day-to-day calculations, including common math functions, fractions, units, and unit conversion.

There are three ways to interface with it: direct CLI commands (`ka '1+1'`), a CLI interpreter (run with `ka`), and a GUI.

### TODO
* Write manual for GitHub:
    - Description & features
    - Installation
    - Usage examples
    - Units (list of units, unit behaviour, unit arithmetic)
    - Functions & operators
    - FAQ
* Simple GUI.

### Development
To run tests: `tox`.

### Types
ka is strongly typed, not statically typed. What this means is that when you pass a fractional number to a function that expects an integer, the type system will complain. But you don't have to declare the type of anything in advance.

The type system consists of (1) a hierarchy of numerical types, and (2) quantities.

The hierarchy of numerical types goes: Number > Real > Rational/Fraction > Integral/Integer. 'Real' numbers are represented as floating point numbers. If a fraction can be simplified to an integer, such as 2/2, then this will happen automatically. In the other direction, a type that is lower down the hierarchy, such as an integer, can be cast into a type that's further up the hierarchy in order to match a function signature.

Quantities consist of two components: a magnitude and a unit (see below). Any quantities can be multiplied together or divided into each other, but only quantities of the same type can be added or subtracted. This is enforced by the binary operators themselves (addition and subtraction) rather than any type-checking built into the language.

Most functions can be applied to both Numbers and Quantities.

### Functions
4 types of functions: regular, binary operators, prefix operators, postfix operators.

| Name | Signatures |
| --- | --- |
| ! | (Integral) |
| % | (Number, Number) |
| * | (Number, Number)<br/>(Quantity, Quantity)<br/>(Number, Quantity)<br/>(Quantity, Number) |
| + | (Number, Number)<br/>(Number)<br/>(Quantity)<br/>(Quantity, Quantity)<br/>(Number, Quantity)<br/>(Quantity, Number) |
| - | (Number, Number)<br/>(Number)<br/>(Quantity)<br/>(Quantity, Quantity)<br/>(Number, Quantity)<br/>(Quantity, Number) |
| / | (Number, Number)<br/>(Integral, Integral)<br/>(Quantity, Quantity)<br/>(Number, Quantity)<br/>(Quantity, Number) |
| C | (Integral, Integral) |
| ^ | (Number, Number) |
| abs | (Number)<br/>(Quantity) |
| ceil | (Number)<br/>(Quantity) |
| cos | (Number)<br/>(Quantity) |
| float | (Number)<br/>(Quantity) |
| floor | (Number)<br/>(Quantity) |
| int | (Number)<br/>(Quantity) |
| ln | (Number)<br/>(Quantity) |
| log | (Number, Number) |
| log10 | (Number)<br/>(Quantity) |
| log2 | (Number)<br/>(Quantity) |
| round | (Number)<br/>(Quantity) |
| sin | (Number)<br/>(Quantity) |
| sqrt | (Number)<br/>(Quantity) |
| tan | (Number)<br/>(Quantity) |

### FAQ
##### How do you exit the interpreter?
Call the function `quit()`, use the interpreter command `%q` / `%quit`, or trigger an interrupt with CTRL+C.

##### Why does `5/4 m` give units in `m^-1`?
Units have higher precedence than division in the parsing, so `5/4 m` is parsed the same as `5 / (4 m)`. The solution is to write `(5/4)m`.
