### ka(lculator)
A CLI calculator.

Features:

* Minimal interface, type as little as possible to get results.

```
$ ka '3*(pi+1)'
```
* First-class support for rational numbers.
* First-class support for combinatorics functions, and lazy evaluation of combinatorics.

```
> 5!
120
> 1000!/999!
1000 # Python would overflow here
```
* Units.

```
> 5 feet to metres
> 5ft + 1m
```
* An interpreter.
* Common mathematical constants and functions (`pi`, `e`, `sin`, etc).
* Assignment.

```
$ ka 'x=5*3;y=1;pi+x-y'
17.141592653589793
```
* See the parse tree.

```
$ ka 'x=5*3;y=1;pi+x-y' --tree
├── x=
│   └── *
│       ├── 5
│       └── 3
├── y=
│   └── 1
└── +
    ├── pi
    └── -
        ├── x
        └── y
```
* Strongly typed, dispatch.

### TODO
* Units.
* Lazy combinatorics type.
* Fix CLI so it doesn't interpret leading negative unary operator as a flag: <https://docs.python.org/3/library/argparse.html#arguments-containing>
* Refactor ugly divide(), leverage dispatch.
* Handle runtime errors (e.g. incompatible units, division by 0, overflow, and the like; overflow can happen during parsing!).
* Accept more number input formats. 
* Documentation (features / interesting things; usage; the grammar, example files + ability to execute files; DISPATCH TABLE (functions))
* Put it on PyPI.
* An interpreter! Including special commands for showing the environment, clearing the environment, etc.
