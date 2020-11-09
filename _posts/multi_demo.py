import datetime as dt
import logging
import multiprocessing
import os
import time

print(f"Importing 'multi_demo.py' at {dt.datetime.now()}")
logger = logging.getLogger("multi_demo")

CONSTANT = 3.14
MUTABLE = {}


def run_multi(context):
    """
    Run multiprocessing job with given context type
    """
    logger.info("Running as '%s' pool at %s", context, dt.datetime.now())
    with multiprocessing.get_context(context).Pool(initializer=init) as pool:
        pool.map(run_task, (1, 2, 3))


def init():
    print(f'Initializing process {os.getpid()}')


def run_task(index):
    """Print some info about the task."""
    time.sleep(0.5)
    public_globals = [g for g in globals().keys() if not g.startswith('__')]
    MUTABLE[index] = os.getpid()
    logger.info("Hello from run_task(%s) with root logger id %s",
                index, id(logging.getLogger()))
    print(f"Index: {index}")
    print(f"PID: {os.getpid()}")
    print(f"Global vars: {', '.join(public_globals)}")
    print(f"CONSTANT: {CONSTANT} (with id {id(CONSTANT)})")
    print(f"MUTABLE: {MUTABLE}")
    print()


if __name__ == '__main__':
    # Configure root logger with handler to print messages from multi_demo
    # logger to std_err
    logging.basicConfig(level=logging.INFO)

    runtime_var = 'hello'  # new variable
    MUTABLE['runtime_var'] = runtime_var  # modify global var

    logger.info("Original PID: %s", os.getpid())
    logger.info("root logger id: %s", id(logging.getLogger()))

    print()

    run_multi('fork')
    logger.info("MUTABLE after tasks: %s", MUTABLE)

    print(f"\n{40 * '-'}\n")

    run_multi('spawn')
    logger.info("MUTABLE after tasks: %s", MUTABLE)
