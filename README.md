### ka(lculator)
A calculator language.

### TODO
* Documentation: description & features; lots of usage examples (incl. tree to show grammar); list of units; documentation for functions; and a coherent kinda manual that can be printed in multiple formats (Markdown for GitHub readme, maybe HTML for website), should list the types, details of how unit arithmetic and whatnot works, FAQ.
* Usability: print decimal even if fraction.
* Handle runtime errors (e.g. incompatible units, division by 0, overflow, and the like; overflow can happen during parsing!), add tests.
* Accept more number input formats. 
* Investigate precision when values are large.
* Plan interfaces (interpreter, CLI for running scripts & one-off commands, GUI)
* Lazy combinatorics type.
* Set notation, and set functions: sum({C(n,k) : k in [0,4)}); prod([1,7]); and so on.

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

