### ka(lculator)
A calculator language.

### TODO
* '5/4 m' is parsed as '5/(4 m)', which was surprising to me. I think factors should be bound together more tightly than units & factors. But then what would the parsing be like for '5m/3m'?
* Change notation for unit conversion ('~', maybe?)
* Improve interpreter:
    - handle interrupts smoothly (while a command is running, while a command is not running)
    - introspection commands
    - quit command(s)
    - readline history
    - a way to reference previous values
    - investigate error-handling behaviour
* Write manual for GitHub:
    - Description & features
    - Installation
    - Usage examples
    - Units (list of units, unit behaviour, unit arithmetic)
    - Types
    - Functions & operators
    - FAQ.
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

