### Description
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
* Features: logs; rational numbers & accompanying float to force decimal; other number bases?; units.
* Plan what to do with it (maybe just dump it somewhere, maybe write about it, maybe tune it to my twisted needs).
