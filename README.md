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
* Review associativity rules.
* unary operator.
* Tests.
* log & other mathematical functions.
* type hierarchy / rational numbers & accompanying 'f' function to force float.
* units.
* nCk and n!, as well as lazy combinatorics resolution
* Documentation (features / interesting things; usage; the grammar, example files + ability to execute files)
* Put it on PyPI.
* Mayyyyybe some other application, like a Slack app.
* other number bases?
