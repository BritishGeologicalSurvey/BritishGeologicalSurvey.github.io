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

    print(f"Number of running threads: {len(enumerate())}")
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
