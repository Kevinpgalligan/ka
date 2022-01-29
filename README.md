### ka(lculator)
A calculator language.

### TODO
* Naughty behaviour: sin(4x+3) treats x as a unit, 4 m/s treats s as a variable. The Frink solution may actually be best, even though it fills up the namespace and can lead to accidentally shadowing units / variables. Could use a different assignment syntax to force shadowing 'x := 7'? Brainstorm other solutions.
* Handle runtime errors (e.g. incompatible units, division by 0, overflow, and the like; overflow can happen during parsing!), add tests.
* Accept more number input formats (1e2, different bases?, ...). 
* Investigate precision when values are large; handle overflow / underflow / whatever.
* Multiple interfaces: interpreter, CLI, GUI. I think they can share code, it's just how the output is presented that changes. It should be possible to inspect the language (list units, list functions, list function help, list function signatures, etc)
* Documentation: description & features; lots of usage examples (incl. tree to show grammar); list of units; documentation for functions; and a coherent kinda manual that can be printed in multiple formats (Markdown for GitHub readme, maybe HTML for website), should list the types, details of how unit arithmetic and whatnot works, FAQ.
* Fuzzing to make sure that all inputs & errors are handled gracefully (this may require refactoring grammar to be a data structure so that valid inputs can be generated).
* Lazy combinatorics type.
* Set notation, and set functions: sum({C(n,k) : k in [0,4)}); prod([1,7]); and so on.
* Oooh, random variable type would be cool! X ~ binom(n, p), P(X <= 3), E(X).
* Why NOT support syntax sugar like the degree sign & real pi (maybe I already support real pi). The GUI could have a keyboard display for this.

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

