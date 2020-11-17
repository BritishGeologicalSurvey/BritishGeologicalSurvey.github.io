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

When a process is `forked` the child process inherits  all the same
variables in the same state as they were in the parent.
Each child process then continues independently from the forking point.
The pool divides the args between the children and they work though them
sequentially.

On the other hand, when a process is `spawned`, it begins by starting a new Python interpreter.
The current module is reimported and new versions of all the variables are
created.
The `plot_function` is then called on each of the the `args` allocated to that
child process.
As with forking, the child processes are independent of each other and the
parent.

Neither method copies running threads into the child processes.

Similarities and differences between the two start methods are:

| Action | fork | spawn |
| ---- | ---- | ---- |
| Create new PID for processes | yes | yes |
| Module-level variables and functions present | yes | yes |
| Each child process calls plot_function on multiple pool args | yes | yes |
| Child processes independently track variable state | yes | yes |
| Import module at start of each child process | no | yes |
| Variables have same id as in parent process | yes | no |
| Child process gets variables defined in name == main block | yes | no |
| Parent process variables are updated from child process state | no | no |
| Threads from parent process run in child processes | no | no |
| Threads from parent process modify child variables | no | no |

See the appendix for a script that illustrates these differences.

### Why my code was hanging

The problem with my test suite was caused by
[threading](https://realpython.com/intro-to-python-threading/), either within
Matplotlib or Pytest.
Threads are not transferred to child processes (see [Why your multiprocessing Pool
is stuck](https://pythonspeed.com/articles/python-multiprocessing/) for more
details).
Resources that have been locked by threads in the parent process remain locked when you _fork_ the process.
However, the thread that holds the lock (and would eventually release the
resource) is not transferred.
Anything else that needs the resource is stuck waiting and the process hangs at
`waiter.acquire()`.
Using _spawn_ creates of fresh instances of each resource so none are in a locked state.


### Other multiprocessing tricks

Multiprocessing processes are independent and state is not shared between.

Sometimes, however, it is necessary to update a dictionary with information from each process.
In this case, state can be shared between processes using a [Manager()](https://docs.python.org/3/library/multiprocessing.html#sharing-state-between-processes) object.

Furthermore, things such as logging configuration that are normally defined in the `__name__ == '__main__'` block of a script are not passed to the spawned processes.
Configuring loggers or other global varaibles in the child prcesses can be done by defining an [initializer](https://docs.python.org/3/library/multiprocessing.html#module-multiprocessing.pool) function that is called at the
beginning of each process.

See the Ash Model Plotting code for examples of each: [ash_model_plotting/plotting.py](https://github.com/BritishGeologicalSurvey/ash-model-plotting/blob/6b2607ed17c07f88c5d5598ef717d72550e9abcf/ash_model_plotting/plotting.py#L121)


### Learn more

Hopefully these notes have given you (or [future me](https://xkcd.com/1421/)) some insight into multiprocessing and a possible fix for processes that freeze.
There is a bug report on Python.org that suggests making "spawn" the default start method ([multiprocessing's default start method of fork()-without-exec() is broken](https://bugs.python.org/issue40379)).
It may be worth checking back there to see if things change in future.

Below is a script to demonstrate some differences between `fork` and `spawn`.
There is also a copy of the output that it produces.
Experimenting with it may help deepen your understanding of multiprocessing.

Happy parallel computing!


--------------------------

## Appendix

### Variables and processes with fork and spawn

The script below uses a `multiprocessing.Pool()` with both `fork` and `spawn`
start methods to repeatedly call a function that prints information about
current processes and variables.
Comparing the two start methods gives insight into how the child
processes are created in each context.

Notice especially what happens to the LOCK in each case.
In the `fork` version, the lock is released after the child processes have
begun so their version of it remains locked.
In the `spawn` version, the thread that acquires the lock is never started as
it is not called when the module is imported.


```python
# multi_demo.py
import datetime as dt
import logging
from multiprocessing import get_context
import os
import time
from threading import Lock, Thread, enumerate

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
    logger.info("*** Lock acquired in thread process ***")
    time.sleep(hold_time)
    lock.release()
    logger.info("*** Lock released in thread process ***")


def run_task(index):
    """Print 'index' and state of different variables."""
    time.sleep(4)
    logger.info("Hello from run_task(%s) with root logger id %s",
                index, id(logging.getLogger()))
    print(f"Index: {index}")
    print(f"process ID: {os.getpid()}")

    public_globals = [g for g in globals().keys() if not g.startswith('__')]
    print(f"Global vars: {', '.join(public_globals)}")
    print(f"CONSTANT: {CONSTANT} (with id {id(CONSTANT)})")

    MUTABLE[index] = os.getpid()
    print(f"MUTABLE: {MUTABLE}")

    print(f"Number of running threads: {len(enumerate())}")
    print(f"LOCK is locked? {LOCK.locked()}")
    # Uncomment the following to make "fork" process hang at waiter.acquire()
    # LOCK.acquire()

    print()


if __name__ == '__main__':
    # Configure root logger with handler to print messages from multi_demo
    # logger to std_err
    logging.basicConfig(level=logging.INFO)
    logger.info("Original process ID: %s", os.getpid())
    logger.info("root logger id: %s", id(logging.getLogger()))

    # modify mutable global var
    MUTABLE['mutated'] = True
    logger.info("MUTABLE before tasks: %s", MUTABLE)

    # Start a thread to hold the lock.  This will unlock after the pool has
    # started but while the process is still sleeping.
    lock_holder_thread = Thread(target=hold_lock, args=(LOCK, 1))
    lock_holder_thread.start()
    logger.info("Number of running threads: %s", len(enumerate()))

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
Importing 'multi_demo.py' at 2020-11-16 17:19:32.825109
INFO:multi_demo:Original process ID: 439383
INFO:multi_demo:root logger id: 140472182712832
INFO:multi_demo:MUTABLE before tasks: {'mutated': True}
INFO:multi_demo:*** Lock acquired in thread process ***
INFO:multi_demo:Number of running threads: 2



INFO:multi_demo:Running as 'fork' pool at 2020-11-16 17:19:32.826051
INFO:multi_demo:____________________ pool process begin ____________________
Initializing process 439385
Initializing process 439386
INFO:multi_demo:*** Lock released in thread process ***
INFO:multi_demo:Hello from run_task(1) with root logger id 140472182712832
Index: 1
process ID: 439385
Global vars: dt, logging, get_context, os, time, Lock, Thread, enumerate, logger, CONSTANT, MUTABLE, LOCK, run_multi, init, hold_lock, run_task, lock_holder_thread, context
CONSTANT: 3.14 (with id 140472183846128)
MUTABLE: {'mutated': True, 1: 439385}
Number of running threads: 1
LOCK is locked? True

INFO:multi_demo:Hello from run_task(2) with root logger id 140472182712832
Index: 2
process ID: 439386
Global vars: dt, logging, get_context, os, time, Lock, Thread, enumerate, logger, CONSTANT, MUTABLE, LOCK, run_multi, init, hold_lock, run_task, lock_holder_thread, context
CONSTANT: 3.14 (with id 140472183846128)
MUTABLE: {'mutated': True, 2: 439386}
Number of running threads: 1
LOCK is locked? True

INFO:multi_demo:Hello from run_task(3) with root logger id 140472182712832
Index: 3
process ID: 439385
INFO:multi_demo:Hello from run_task(4) with root logger id 140472182712832
Index: 4
process ID: 439386
Global vars: dt, logging, get_context, os, time, Lock, Thread, enumerate, logger, CONSTANT, MUTABLE, LOCK, run_multi, init, hold_lock, run_task, lock_holder_thread, context
CONSTANT: 3.14 (with id 140472183846128)
MUTABLE: {'mutated': True, 2: 439386, 4: 439386}
Number of running threads: 1
LOCK is locked? True

Global vars: dt, logging, get_context, os, time, Lock, Thread, enumerate, logger, CONSTANT, MUTABLE, LOCK, run_multi, init, hold_lock, run_task, lock_holder_thread, context
CONSTANT: 3.14 (with id 140472183846128)
MUTABLE: {'mutated': True, 1: 439385, 3: 439385}
Number of running threads: 1
LOCK is locked? True

INFO:multi_demo:____________________ pool process end ____________________



INFO:multi_demo:Running as 'spawn' pool at 2020-11-16 17:19:40.908982
INFO:multi_demo:____________________ pool process begin ____________________
Importing 'multi_demo.py' at 2020-11-16 17:19:41.097592
Importing 'multi_demo.py' at 2020-11-16 17:19:41.098022
Initializing process 439393
Initializing process 439394
Index: 1
process ID: 439393
Global vars: dt, logging, get_context, os, time, Lock, Thread, enumerate, logger, CONSTANT, MUTABLE, LOCK, run_multi, init, hold_lock, run_task
CONSTANT: 3.14 (with id 140312126736656)
MUTABLE: {'mutated': False, 1: 439393}
Number of running threads: 1
LOCK is locked? False

Index: 2
process ID: 439394
Global vars: dt, logging, get_context, os, time, Lock, Thread, enumerate, logger, CONSTANT, MUTABLE, LOCK, run_multi, init, hold_lock, run_task
CONSTANT: 3.14 (with id 140298227288336)
MUTABLE: {'mutated': False, 2: 439394}
Number of running threads: 1
LOCK is locked? False

Index: 3
process ID: 439393
Global vars: dt, logging, get_context, os, time, Lock, Thread, enumerate, logger, CONSTANT, MUTABLE, LOCK, run_multi, init, hold_lock, run_task
CONSTANT: 3.14 (with id 140312126736656)
MUTABLE: {'mutated': False, 1: 439393, 3: 439393}
Number of running threads: 1
LOCK is locked? False

Index: 4
process ID: 439394
Global vars: dt, logging, get_context, os, time, Lock, Thread, enumerate, logger, CONSTANT, MUTABLE, LOCK, run_multi, init, hold_lock, run_task
CONSTANT: 3.14 (with id 140298227288336)
MUTABLE: {'mutated': False, 2: 439394, 4: 439394}
Number of running threads: 1
LOCK is locked? False

INFO:multi_demo:____________________ pool process end ____________________


INFO:multi_demo:MUTABLE after tasks: {'mutated': True}
```
