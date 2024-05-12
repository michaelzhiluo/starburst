import collections
import logging
import os


class LogManager(object):
    """
    LogManager is a class that manages logging to a log file.
    """

    def __init__(self, log_name: str, log_file_path: str):
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(logging.DEBUG)
        # Remove the default stdout handler from the logger
        self.logger.handlers = []
        log_file_path = os.path.abspath(log_file_path)
        self.file_handler = logging.FileHandler(log_file_path)
        self.file_handler.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter("%(message)s")
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)
        # Prevent the logger from propagating to the root logger.
        self.logger.propagate = False

        if not os.path.exists(log_file_path):
            os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
            with open(log_file_path, 'w') as f:
                pass

    def append(self, message):
        self.logger.debug(message)

    def close(self):
        for handler in self.logger.handlers:
            handler.close()
            self.logger.removeHandler(handler)


class SimpleEventLogger(object):

    def __init__(self, max_len=1000):
        """
        Constructor.
        """
        self.events = collections.deque(maxlen=max_len)
        super(SimpleEventLogger, self).__init__()

    def log_event(self, event):
        """
        Do nothing, just store event in memory and flush the list if exceeds
        size.
        """
        self.events.append(event)
