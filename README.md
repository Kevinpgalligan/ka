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
* Parser / evaluator tests.
* Fix CLI so it doesn't interpret leading negative unary operator as a flag: <https://docs.python.org/3/library/argparse.html#arguments-containing>
* log & other mathematical functions.
* type hierarchy / rational numbers & accompanying 'f' function to force float.
* units.
* nCk and n!, as well as lazy combinatorics resolution
* Documentation (features / interesting things; usage; the grammar, example files + ability to execute files)
* Put it on PyPI.
* An interpreter! Including special commands for showing the environment, clearing the environment, etc.
* Mayyyyybe some other application, like a Slack app.
* other number bases?
