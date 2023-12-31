import time
import logging


logger = logging.getLogger(__name__)


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            logger.info('%r  %2.2f secs' % (method.__name__, (te - ts)))
        return result
    return timed


def time_category_iteration(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            # assumes that the first argument to the method is 'category'
            category = args[1] if len(args) > 1 else 'no category provided'
            logger.info('%r (%r)  %2.2f secs' % (method.__name__, category, (te - ts)))
        return result
    return timed
