---
title:  "Fork vs Spawn in Python Multiprocessing"
author: Dr John A Stevenson
categories:
  - science
tags:
  - Python
  - multiprocessing
  - parallel
  - Matplotlib
---

I recently got stuck trying to plot multiple figures in parallel with Matplotlib.
It took 5 hours to find a 2-line fix to make it work again.
Afterwards I spent even more hours learning about multiprocessing to understand
what had gone wrong and how the fix worked.
This post is an attempt to capture what I learned.


### The problem

The British Geological Survey's [Ash Model Plotting](https://github.com/BritishGeologicalSurvey/ash-model-plotting) tool makes maps of simulated of volcanic ash clouds.
Properties are calculated on a grid of locations for many different times and elevations, resulting in hundreds of maps.
Creating the maps is [CPU-bound](https://realpython.com/python-concurrency/#how-to-speed-up-a-cpu-bound-program) and each map is independent, so plotting with multiple processes is a logical way to speed it up.

Python's [multiprocessing pool](https://docs.python.org/3/library/multiprocessing.html) makes this easy to set up.
Using `pool.map(plot_function, args)` (or `pool.starmap(plot_function, tuples_of_args)` as I needed) will use multiple processes to call `plot_function` on the different `args` in parallel.

It didn't take long to configure the code to use the pool for a simple script.
Unfortunately, however, calling the function within the test suite caused _pytest_ to hang/freeze.
Quitting with _\<ctrl-c\>_ said that it was stuck at `waiter.aquire()`.
Thus began a long search through Stack Overflow, bug reports and blog posts for
a way to make it run.


### The fix

I eventually found the answer in a blog post called [Why your multiprocessing Pool is stuck (it's full of sharks!)](https://pythonspeed.com/articles/python-multiprocessing/).
It suggested modifying the code to "spawn" new processes in the multiprocessing pool, instead of using the default "fork" method.
This is as simple as changing:

```python
import multiprocessing

with multiprocessing.Pool() as pool:
    pool.map(plot_function, args)
```

to

```python
import multiprocessing

with multiprocessing.get_context('spawn').Pool() as pool:
    pool.map(plot_function, args)
```

I made the change, pytest ran to completion and all the tests turned green.
I was very happy.
I was now also very curious about `fork` and `spawn`.


### Fork vs spawn

See the link above for *why* this works.

### Why the code was hanging


As explained in the linked blog post, the problem is that resources that have been locked by threads in the parent process remain locked when you _fork_ the process.
However, the thread that holds the lock (and would eventually release the
resource) is not transferred.
Anything else that needs the resource is stuck waiting and the process hangs.
Using to _spawn_ results in creation of fresh instances of the resources so
none of them are in a locked state.


To understand the difference between "fork" and "spawn", I wrote the script
below.
Fork starts each child process with the variables in the exact state that they were
in the parent process.
Spawn re-imports the module into the child process and thus recreates all the
variables.
Thus the locked state of resources is not transferred when you use "spawn".

The practical differences are summarised in this table.

| Action | fork | spawn |
| ---- | ---- | ---- |
| Create new PID for processes | yes | yes |
| Module-level variables and functions present | yes | yes |
| Reuse processes for multiple pool args | yes | yes |
| Track variable state within processes | yes | yes |
| Update parent process from child variable state | no | no |
| Variables have same id as in parent process | yes | no |
| Import module in each process | no | yes |
| Include variables defined in name equals main block | yes | no |
| Include changes made in name equals main block | yes | no |


```python
# fork_vs_spawn.py

import datetime as dt
import logging
from multiprocessing import get_context
import os
import time

print(f"Importing 'multi_demo.py' at {dt.datetime.now()}")
logger = logging.getLogger("multi_demo")

# Define some module-level variables
CONSTANT = 3.14
MUTABLE = {"mutated": False}


def run_multi(context):
    """
    Run multiprocessing job with given context type
    """
    with get_context(context).Pool(2, initializer=init) as pool:
        pool.map(run_task, (1, 2, 3, 4))


def init():
    """This function is called when new processes start."""
    print(f'Initializing process {os.getpid()}')


def run_task(index):
    """Print 'index' and state of different variables."""
    time.sleep(2)
    logger.info("Hello from run_task(%s) with root logger id %s",
                index, id(logging.getLogger()))
    print(f"Index: {index}")
    print(f"PID: {os.getpid()}")

    public_globals = [g for g in globals().keys() if not g.startswith('__')]
    print(f"Global vars: {', '.join(public_globals)}")
    print(f"CONSTANT: {CONSTANT} (with id {id(CONSTANT)})")

    MUTABLE[index] = os.getpid()
    print(f"MUTABLE: {MUTABLE}")
    print()


if __name__ == '__main__':
    # Configure root logger with handler to print messages from multi_demo
    # logger to std_err
    logging.basicConfig(level=logging.INFO)
    logger.info("Original PID: %s", os.getpid())
    logger.info("root logger id: %s", id(logging.getLogger()))

    # modify mutable global var
    MUTABLE['mutated'] = True
    logger.info("MUTABLE before tasks: %s", MUTABLE)

    # Run pool processes with different contexts
    for context in ('fork', 'spawn'):
        print('\n\n')
        logger.info("Running as '%s' pool at %s", context, dt.datetime.now())
        logger.info("_" * 20 + " pool process begin " + "_" * 20)

        run_multi(context)

        logger.info("_" * 20 + " pool process end " + "_" * 20)

    # Log final MUTABLE value
    print('\n')
    logger.info("MUTABLE after tasks: %s", MUTABLE)
```

Output:

```
Importing 'multi_demo.py' at 2020-11-11 22:33:52.142051
INFO:multi_demo:Original PID: 412551
INFO:multi_demo:root logger id: 140515181750688
INFO:multi_demo:MUTABLE before tasks: {'mutated': True}


INFO:multi_demo:Running as 'fork' pool at 2020-11-11 22:33:52.142621
INFO:multi_demo:____________________ pool process begin ____________________
Initializing process 412552
Initializing process 412553
INFO:multi_demo:Hello from run_task(2) with root logger id 140515181750688
Index: 2
PID: 412553
Global vars: dt, logging, get_context, os, time, logger, CONSTANT, MUTABLE, run_multi, init, run_task, context
CONSTANT: 3.14 (with id 140515182892272)
MUTABLE: {'mutated': True, 2: 412553}

INFO:multi_demo:Hello from run_task(1) with root logger id 140515181750688
Index: 1
PID: 412552
Global vars: dt, logging, get_context, os, time, logger, CONSTANT, MUTABLE, run_multi, init, run_task, context
CONSTANT: 3.14 (with id 140515182892272)
MUTABLE: {'mutated': True, 1: 412552}

INFO:multi_demo:Hello from run_task(3) with root logger id 140515181750688
Index: 3
PID: 412553
Global vars: dt, logging, get_context, os, time, logger, CONSTANT, MUTABLE, run_multi, init, run_task, context
CONSTANT: 3.14 (with id 140515182892272)
MUTABLE: {'mutated': True, 2: 412553, 3: 412553}
INFO:multi_demo:Hello from run_task(4) with root logger id 140515181750688
Index: 4

PID: 412552
Global vars: dt, logging, get_context, os, time, logger, CONSTANT, MUTABLE, run_multi, init, run_task, context
CONSTANT: 3.14 (with id 140515182892272)
MUTABLE: {'mutated': True, 1: 412552, 4: 412552}

INFO:multi_demo:____________________ pool process end ____________________


INFO:multi_demo:Running as 'spawn' pool at 2020-11-11 22:33:56.188244
INFO:multi_demo:____________________ pool process begin ____________________
Importing 'multi_demo.py' at 2020-11-11 22:33:56.377781
Importing 'multi_demo.py' at 2020-11-11 22:33:56.380271
Initializing process 412559
Initializing process 412560
Index: 1
PID: 412559
Global vars: dt, logging, get_context, os, time, logger, CONSTANT, MUTABLE, run_multi, init, run_task
CONSTANT: 3.14 (with id 140223920441616)
MUTABLE: {'mutated': False, 1: 412559}

Index: 2
PID: 412560
Global vars: dt, logging, get_context, os, time, logger, CONSTANT, MUTABLE, run_multi, init, run_task
CONSTANT: 3.14 (with id 139817631729936)
MUTABLE: {'mutated': False, 2: 412560}

Index: 3
PID: 412559
Global vars: dt, logging, get_context, os, time, logger, CONSTANT, MUTABLE, run_multi, init, run_task
CONSTANT: 3.14 (with id 140223920441616)
MUTABLE: {'mutated': False, 1: 412559, 3: 412559}

Index: 4
PID: 412560
Global vars: dt, logging, get_context, os, time, logger, CONSTANT, MUTABLE, run_multi, init, run_task
CONSTANT: 3.14 (with id 139817631729936)
MUTABLE: {'mutated': False, 2: 412560, 4: 412560}

INFO:multi_demo:____________________ pool process end ____________________


INFO:multi_demo:MUTABLE after tasks: {'mutated': True}
```


## Further reading

+ Bug report on Python.org that suggests making "spawn" the default.
  [multiprocessing's default start method of fork()-without-exec() is
broken](https://bugs.python.org/issue40379).
+ Stack Overflow search with many results for ["matplotlib
  multiprocessing"](https://stackoverflow.com/search?q=matplotlib+multiprocessing)

Stack Overflow posts
+ [Matplotlib with multiprocessing freeze
  computer](https://stackoverflow.com/questions/31341127/matplotlib-with-multiprocessing-freeze-computer)

