### ka(lculator)
A calculator language.

### TODO
* Change notation for unit conversion ('~', maybe?)
* Function documentation.
* Make interpreter handle interrupts smoothly (while a command is running, while a command is not running), and add simple functionality (introspection commands, quit command(s), mayyyybe a way to reference previous values; definitely a way to scroll back through previous commands; see how it handles errors)
* Define layout of manual (description & features; installation; usage examples; units (list of units, unit behaviour, unit arithmetic); types; functions & operators; FAQ.
* Write manual template (jinja), allow rendering to Markdown and HTML. `python3 generate-docs.py target`.
* Simple GUI.

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
| float | (Number)<br/>(Quantity) |
| floor | (Number)<br/>(Quantity) |
| int | (Number)<br/>(Quantity) |
| ln | (Number)<br/>(Quantity) |
| log | (Number, Number) |
| log10 | (Number)<br/>(Quantity) |
| log2 | (Number)<br/>(Quantity) |
| round | (Number)<br/>(Quantity) |
| sin | (Number)<br/>(Quantity) |
| sqrt | (Number)<br/>(Quantity) |
| tan | (Number)<br/>(Quantity) |

