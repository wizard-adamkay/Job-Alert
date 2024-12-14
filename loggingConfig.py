import logging
import logging.handlers
import multiprocessing

def configure_logging(queue):
    handler = logging.handlers.QueueHandler(queue)
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)

def listener_process(queue, logFile):
    listener_logger = logging.getLogger()
    listener_logger.setLevel(logging.INFO)
    handler = logging.FileHandler(logFile)
    formatter = logging.Formatter('%(asctime)s - %(processName)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    listener_logger.addHandler(handler)

    while True:
        record = queue.get()
        if record is None:
            break
        listener_logger.handle(record)
