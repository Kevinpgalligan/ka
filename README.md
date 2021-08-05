### ka(lculator)
A calculator language.

### TODO
* Unit shittiness: can't use symbol name of degrees Celcius (probably a unicode issue); unit name can't have spaces (see: astronomicalunit); can't add minute / second (plane & phase angle quantities) because of name conflict; logarithmic ratio quantities (neper, bel, decibel); make conversion multiples more precise, perhaps (fractions instead of floats).
* Fix CLI so it doesn't interpret leading negative unary operator as a flag: <https://docs.python.org/3/library/argparse.html#arguments-containing>
* Handle runtime errors (e.g. incompatible units, division by 0, overflow, and the like; overflow can happen during parsing!).
* Accept more number input formats. 
* Investigate precision when values are large.
* Documentation (features / interesting things; usage; the grammar, example files + ability to execute files; DISPATCH TABLE (functions))
* Put it on PyPI.
* An interpreter! Including special commands for showing the environment, clearing the environment, etc.
* Lazy combinatorics type.
* Set notation, and set functions: sum({C(n,k) : k in [0,4)}); prod([1,7]); and so on.
