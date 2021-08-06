### ka(lculator)
A calculator language.

### TODO
* Documentation (features / interesting things; usage; the grammar, example files + ability to execute files; list of units)
* Handle runtime errors (e.g. incompatible units, division by 0, overflow, and the like; overflow can happen during parsing!).
* Accept more number input formats. 
* Investigate precision when values are large.
* Put it on PyPI.
* An interpreter! Including special commands for showing the environment, clearing the environment, etc.
* Lazy combinatorics type.
* Set notation, and set functions: sum({C(n,k) : k in [0,4)}); prod([1,7]); and so on.
* Fix CLI so it doesn't interpret leading negative unary operator as a flag: <https://docs.python.org/3/library/argparse.html#arguments-containing>

### Supported functions

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
| f | (Number)<br/>(Quantity) |
| floor | (Number)<br/>(Quantity) |
| i | (Number)<br/>(Quantity) |
| ln | (Number)<br/>(Quantity) |
| log | (Number, Number) |
| log10 | (Number)<br/>(Quantity) |
| log2 | (Number)<br/>(Quantity) |
| round | (Number)<br/>(Quantity) |
| sin | (Number)<br/>(Quantity) |
| sqrt | (Number)<br/>(Quantity) |
| tan | (Number)<br/>(Quantity) |

