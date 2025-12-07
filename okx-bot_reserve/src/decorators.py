import functools
import logging
import time

def retry(max_attempts: int = 3, delay: float = 1.0):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__module__)
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    wait_time = delay * (2 ** attempt)
                    logger.warning(f'{func.__name__} failed, retry in {wait_time}s')
                    time.sleep(wait_time)
        return wrapper
    return decorator

def logcall(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        start = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start
            logger.debug(f'{func.__name__} completed in {duration:.3f}s')
            return result
        except Exception as e:
            duration = time.time() - start
            logger.error(f'{func.__name__} failed after {duration:.3f}s: {e}')
            raise
    return wrapper
