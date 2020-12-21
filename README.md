### ka
A toy calculator language.

```
x=5*3;y=1;pi+x-y
```

Parse tree:

```
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

Evaluation:

```
17.141592653589793
```

### TODO
* Tests.
* unary operator.
* log & other mathematical functions.
* type hierarchy / rational numbers & accompanying 'f' function to force float.
* other number bases?
* units.
* nCk and n!, as well as lazy combinatorics resolution
* Put it on PyPI.
* Mayyyyybe some other application, like a Slack app.
