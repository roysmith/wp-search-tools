from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL
from time import time

class ProgressMonitor:
    """Log a subset of messages, based on various criteria.

    count: log every n-th message.

    delay: number of seconds which must elapse between logged messages.

    If more than one criteria is specified, they must all be met to
    log a message.  This is probably not a very useful thing to do.

    """
    def __init__(self, logger, count=1, delay=0.0):
        if (not (isinstance(count, int) and count > 0)):
            raise ValueError(f'count ({count}) must be a positive integer')
        if (delay < 0):
            raise ValueError(f'delay ({delay}) must be >= 0')
        self.logger = logger
        self.count = count
        self.delay = delay
        self.n = 0
        self.next_log_time = time() + delay

    def debug(self, msg, *args, **kwargs):
        return self.log(DEBUG, msg, *args, **kwargs)


    def info(self, msg, *args, **kwargs):
        return self.log(INFO, msg, *args, **kwargs)


    def warning(self, msg, *args, **kwargs):
        return self.log(WARNING, msg, *args, **kwargs)


    def error(self, msg, *args, **kwargs):
        return self.log(ERROR, msg, *args, **kwargs)


    def critical(self, msg, *args, **kwargs):
        return self.log(CRITICAL, msg, *args, **kwargs)


    def log(self, level, msg, *args, **kwargs):
        self.n += 1
        if self.n % self.count != 0:
            return
        time_now = time()
        if time_now >= self.next_log_time:
            self.next_log_time = time_now + self.delay
            return self.logger.log(level, msg, *args, **kwargs)
