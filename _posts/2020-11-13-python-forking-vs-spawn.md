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
It took five hours to find a two-line fix to make it work.
Afterwards I spent even more hours learning about multiprocessing in order to understand
what had gone wrong and how the fix worked.
This post is an attempt to capture what I learned.


### The problem

The British Geological Survey's [Ash Model Plotting](https://github.com/BritishGeologicalSurvey/ash-model-plotting) tool makes maps of simulated of volcanic ash clouds.
Properties are calculated on a grid of locations for many different times and elevations, resulting in hundreds of maps.
Creating the maps is [CPU-bound](https://realpython.com/python-concurrency/#how-to-speed-up-a-cpu-bound-program) and each map is independent, so plotting with multiple processes is a logical way to speed it up.

Python's [multiprocessing pool](https://docs.python.org/3/library/multiprocessing.html) makes this easy.
Using `pool.map(plot_function, args)` sets up multiple processes to call `plot_function` on the different `args` in parallel.

It didn't take long to configure a pool for a simple script.
Unfortunately, however, calling the plot function within the test suite caused _pytest_ to hang/freeze.
Quitting with _\<ctrl-c\>_ reported that the code was stuck at `waiter.aquire()`.
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
I was also curious about how `fork` and `spawn` work.


### What happens when you start a new process?

Forking and spawning are two different [start
methods](https://docs.python.org/3/library/multiprocessing.html#contexts-and-start-methods)
for new processes.
_Fork_ is the default on Linux (it isn't available on Windows), while Windows
and MacOS use _spawn_ by default.

When a process is `forked` the new process is created with all the same
variables in the same state as they were in the parent.
Each process continues from the forking point and the pool loops over the `args`, allocating
them to the different child processes.
The processes carry on down their own independent paths from the fork point.

When a process is `spawned`, it starts a new Python interpreter.
The current module is reimported, creating new versions of all the variables, before
the `plot_function` is called on the `args`.
As with forking, the child processes are independent of each other and the
parent.


The full output is below and can be summarised as follows:

| Action | fork | spawn |
| ---- | ---- | ---- |
| Create new PID for processes | yes | yes |
| Module-level variables and functions present | yes | yes |
| Reuse processes for multiple pool args | yes | yes |
| Track variable state within processes | yes | yes |
| Import module at start of each process | no | yes |
| Variables have same id as in parent process | yes | no |
| Include variables defined in name equals main block | yes | no |
| Include changes made in name equals main block | yes | no |
| Update parent process from child variable state | no | no |


### Why my code was hanging

The problem with my test suite was due to threads in the parent process.
These are not transferred to the children (see [Why your multiprocessing Pool
is stuck](https://pythonspeed.com/articles/python-multiprocessing/) for more
details).
Resources that have been locked by threads in the parent process remain locked when you _fork_ the process.
However, the thread that holds the lock (and would eventually release the
resource) is not transferred.
Anything else that needs the resource is stuck waiting and the process hangs.
Using _spawn_ creates of fresh instances of each resource so none are in a locked state.


### Other multiprocessing tricks

The experiments here show that processes are independent and state is not
shared between.
In the Ash Model Plotting [plotting.py code](https://github.com/BritishGeologicalSurvey/ash-model-plotting/blob/6b2607ed17c07f88c5d5598ef717d72550e9abcf/ash_model_plotting/plotting.py#L121), however, it was necessary to update a dictionary with results of each process.
State can be shared between processes using a [Manager()](https://docs.python.org/3/library/multiprocessing.html#sharing-state-between-processes) object.

Also, things such as logging configuration that are normally defined in the `__name__ == '__main__'` block of a script are not passed to the spawned processes.
You can handle this be defining an [initializer](https://docs.python.org/3/library/multiprocessing.html#module-multiprocessing.pool) function that is called at the
beginning of each process.


### Learn more

Hopefully these notes have given you (or [future me](https://xkcd.com/1421/)) some insight into multiprocessing and a possible fix for processes that freeze.
There is a bug report on Python.org that suggests making "spawn" the default start method.  [multiprocessing's default start method of fork()-without-exec() is broken](https://bugs.python.org/issue40379).
It may be worth checking that to see if things change in future.

Below is a script to demonstrate some differences between `fork` and `spawn`
and a copy of the output that it produces.
Experimenting with it may help with understanding how they work.

Happy parallel processing!


--------------------------

### Variables and processes with fork and spawn

The script below uses a `multiprocessing.Pool()` with both `fork` and `spawn`
start methods to repeatedly call a function that prints information about
current processes and variables.
It demonstrates how these change and so gives insight into how the child
processes work in each context.
Running it for yourself and modifying outputs may help understanding of how
things work.

```python
# multi_demo.py
import datetime as dt
import logging
from multiprocessing import get_context
import os
import time
from threading import Lock, Thread

print(f"Importing 'multi_demo.py' at {dt.datetime.now()}")
logger = logging.getLogger("multi_demo")

# Define some module-level variables
CONSTANT = 3.14
MUTABLE = {"mutated": False}
LOCK = Lock()


def run_multi(context):
    """
    Run multiprocessing job with given context type
    """
    with get_context(context).Pool(2, initializer=init) as pool:
        pool.map(run_task, (1, 2, 3, 4))


def init():
    """This function is called when new processes start."""
    print(f'Initializing process {os.getpid()}')
    # Uncomment the following to see pool process log messages with spawn
    # logging.basicConfig(level=logging.INFO)


def hold_lock(lock, hold_time=1):
    """Hold a lock item for "hold_time" seconds"""
    lock.acquire()
    logging.info("*** Lock acquired in thread process ***")
    time.sleep(hold_time)
    lock.release()
    logging.info("*** Lock released in thread process ***")


def run_task(index):
    """Print 'index' and state of different variables."""
    time.sleep(4)
    logger.info("Hello from run_task(%s) with root logger id %s",
                index, id(logging.getLogger()))
    print(f"Index: {index}")
    print(f"PID: {os.getpid()}")

    public_globals = [g for g in globals().keys() if not g.startswith('__')]
    print(f"Global vars: {', '.join(public_globals)}")
    print(f"CONSTANT: {CONSTANT} (with id {id(CONSTANT)})")

    MUTABLE[index] = os.getpid()
    print(f"MUTABLE: {MUTABLE}")

    print(f"LOCK is locked? {LOCK.locked()}")
    # Uncomment the following to make "fork" process hang at waiter.acquire()
    # LOCK.acquire()

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

    # Start a thread to hold the lock.  This will unlock after the pool has
    # started but while the process is still sleeping.
    lock_holder_thread = Thread(target=hold_lock, args=(LOCK, 1))
    lock_holder_thread.start()

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

#### Script output


```
Importing 'multi_demo.py' at 2020-11-16 16:17:13.352398
INFO:multi_demo:Original PID: 437989
INFO:multi_demo:root logger id: 140659214875136
INFO:multi_demo:MUTABLE before tasks: {'mutated': True}



INFO:root:*** Lock acquired in thread process ***
INFO:multi_demo:Running as 'fork' pool at 2020-11-16 16:17:13.353169
INFO:multi_demo:____________________ pool process begin ____________________
Initializing process 437992
Initializing process 437991
INFO:root:*** Lock released in thread process ***
INFO:multi_demo:Hello from run_task(1) with root logger id 140659214875136
Index: 1
PID: 437992
Global vars: dt, logging, get_context, os, time, Lock, Thread, logger, CONSTANT, MUTABLE, LOCK, run_multi, init, hold_lock, run_task, lock_holder_thread, context
CONSTANT: 3.14 (with id 140659216016624)
MUTABLE: {'mutated': True, 1: 437992}
LOCK is locked? True

INFO:multi_demo:Hello from run_task(2) with root logger id 140659214875136
Index: 2
PID: 437991
Global vars: dt, logging, get_context, os, time, Lock, Thread, logger, CONSTANT, MUTABLE, LOCK, run_multi, init, hold_lock, run_task, lock_holder_thread, context
CONSTANT: 3.14 (with id 140659216016624)
MUTABLE: {'mutated': True, 2: 437991}
LOCK is locked? True

INFO:multi_demo:Hello from run_task(3) with root logger id 140659214875136
Index: 3
PID: 437992
Global vars: dt, logging, get_context, os, time, Lock, Thread, logger, CONSTANT, MUTABLE, LOCK, run_multi, init, hold_lock, run_task, lock_holder_thread, context
CONSTANT: 3.14 (with id 140659216016624)
MUTABLE: {'mutated': True, 1: 437992, 3: 437992}
LOCK is locked? True

INFO:multi_demo:Hello from run_task(4) with root logger id 140659214875136
Index: 4
PID: 437991
Global vars: dt, logging, get_context, os, time, Lock, Thread, logger, CONSTANT, MUTABLE, LOCK, run_multi, init, hold_lock, run_task, lock_holder_thread, context
CONSTANT: 3.14 (with id 140659216016624)
MUTABLE: {'mutated': True, 2: 437991, 4: 437991}
LOCK is locked? True

INFO:multi_demo:____________________ pool process end ____________________



INFO:multi_demo:Running as 'spawn' pool at 2020-11-16 16:17:21.401243
INFO:multi_demo:____________________ pool process begin ____________________
Importing 'multi_demo.py' at 2020-11-16 16:17:21.606964
Importing 'multi_demo.py' at 2020-11-16 16:17:21.616654
Initializing process 437998
Initializing process 437999
Index: 1
PID: 437998
Global vars: dt, logging, get_context, os, time, Lock, Thread, logger, CONSTANT, MUTABLE, LOCK, run_multi, init, hold_lock, run_task
CONSTANT: 3.14 (with id 139779703290128)
MUTABLE: {'mutated': False, 1: 437998}
LOCK is locked? False

Index: 2
PID: 437999
Global vars: dt, logging, get_context, os, time, Lock, Thread, logger, CONSTANT, MUTABLE, LOCK, run_multi, init, hold_lock, run_task
CONSTANT: 3.14 (with id 140350905727248)
MUTABLE: {'mutated': False, 2: 437999}
LOCK is locked? False

Index: 3
PID: 437998
Global vars: dt, logging, get_context, os, time, Lock, Thread, logger, CONSTANT, MUTABLE, LOCK, run_multi, init, hold_lock, run_task
CONSTANT: 3.14 (with id 139779703290128)
MUTABLE: {'mutated': False, 1: 437998, 3: 437998}
LOCK is locked? False

Index: 4
PID: 437999
Global vars: dt, logging, get_context, os, time, Lock, Thread, logger, CONSTANT, MUTABLE, LOCK, run_multi, init, hold_lock, run_task
CONSTANT: 3.14 (with id 140350905727248)
MUTABLE: {'mutated': False, 2: 437999, 4: 437999}
LOCK is locked? False

INFO:multi_demo:____________________ pool process end ____________________


INFO:multi_demo:MUTABLE after tasks: {'mutated': True}
```
