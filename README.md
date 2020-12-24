### ka
```
$ ka 'x=5*3;y=1;pi+x-y'
17.141592653589793
$ ka 'x=5*3;y=1;pi+x-y' --show-tree
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

### TODO
* units.
* log & other mathematical functions. Functions to coerce to int, float, whatever.
* Fix CLI so it doesn't interpret leading negative unary operator as a flag: <https://docs.python.org/3/library/argparse.html#arguments-containing>
* nCk and n!, as well as lazy combinatorics resolution
* Handle runtime errors (e.g. incompatible units, division by 0, and the like).
* Documentation (features / interesting things; usage; the grammar, example files + ability to execute files)
* Put it on PyPI.
* An interpreter! Including special commands for showing the environment, clearing the environment, etc.
* Mayyyyybe some other application, like a Slack app.
* other number bases?
