### Profiling slow start-up
There's noticeable delay in output, even for a simple calculation like 1+2.

```
$ time ka '1+2'
3

real	0m0.157s
user	0m0.147s
```

With the tokenising & parsing & execution disabled:

```
$ time ka '1+2'

real	0m0.156s
user	0m0.133s
```

So it seems that most of the time is taken up by Python start-up. Apparently, 15ms latency is noticeable in audio. ~70ms is noticeable in button taps. The actual execution is well within that budget, it's just Python's start-up that is taking forever.

Trying again with Python 3.7:

```
time ka '1+2'

real	0m0.127s
user	0m0.118s
sys	0m0.008s
```

Python 3.7 has a feature for profiling import times. It seems that at least 15ms of time is being used to import treelib. 28ms overall, which isn't bad. Where is the rest of the time going?

Okay, this is fugged up. If I call Python directly, the time drops in half. It seems to spend a lot of time figuring out how to call Python.

```
$ time python3 -X importtime profile.py '1+1'
real	0m0.052s
user	0m0.040s
sys	0m0.012s
```

Soooo, 2 suggested methods for reducing latency: 1) import treelib only when it's needed, and 2) call Python3 directly within the script.

Oh, the script imports pkg_resources or something. Which then has to load the script as a resource or somesuch?

Here's what is installed to bin/, this is probably slowing it down.

```
#!/home/kevingal/proyectos/ka/env/bin/python3
# EASY-INSTALL-SCRIPT: 'ka==1.0.0','ka'
__requires__ = 'ka==1.0.0'
__import__('pkg_resources').run_script('ka==1.0.0', 'ka')
```

It may also be the fact that it's running within a venv?

Hmmm, yes. That wrapper script is adding all the latency.

```
kevingal@dsk:~/proyectos/ka$ time python3 profile.py '1+1'
2
real	0m0.043s
user	0m0.026s
sys	0m0.017s
kevingal@dsk:~/proyectos/ka$ time ka '1+1'
2
real	0m0.189s
user	0m0.172s
sys	0m0.016s
```

Ugh. Yes. I see the same thing with bs and pseu. Except, pseu doesn't have that wrapper shit, for some reason. So it executes without delay. Did I install it differently?

```
kevingal@dsk:~/proyectos/ka$ pip3 show pseu
...
Location: /home/kevingal/.local/lib/python3.6/site-packages
kevingal@dsk:~/proyectos/ka$ pip3 show bs
...
Location: /usr/local/lib/python3.6/dist-packages/bs-1.0.0-py3.6.egg
```

Install location seems to be different.

YES. When I reinstalled bs, it appeared without all that extra shit. And it was much faster. It seems that installing through setup.py results in all the crap being added?

Yeah, `pip install .` doesn't add any crap. I was using an outdated way of installing the package.

This was useful, anyway: <https://pythondev.readthedocs.io/startup_time.html>
