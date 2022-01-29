### ka(lculator)
A calculator language.

### TODO
* Multiple interfaces: interpreter, CLI, GUI. I think they can share code, it's just how the output is presented that changes. It should be possible to inspect the language (list units, list functions, list function help, list function signatures, etc)
* Documentation: description & features; lots of usage examples (incl. tree to show grammar); list of units; unit behaviour; types; documentation for functions; and a coherent kinda manual that can be printed in multiple formats (Markdown for GitHub readme, maybe HTML for website), should list the types, details of how unit arithmetic and whatnot works, FAQ. Use jinja (or whatever) to generate the documentation! `python3 generate-docs.py target`. This can be used to create an index, make tables, etc.

### Documenting behaviour
* Raising an integer to a really big power: tries to compute it and takes forever.
* Big float multiplication: becomes infinity.

I guess these things are okay.

### Development
To run tests: `tox`.

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

