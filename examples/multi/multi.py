import time
import logging
import multiprocessing


import pipa
logger=logging.getLogger('pipa')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - (%(funcName)20s.%(lineno)s) - %(levelname)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

def pipe_launcher(pipe, queue, pipe_kwargs={}):
    iterable = queue.get()
    if iterable != None:
        for result in pipe.execute(iterable, **pipe_kwargs):
            print result


def print_string(iterable, **kwargs):
    for s in iterable:
        print "leggo: %s" %s
        if s == 'stop':
            raise StopIteration

proc_pipe = pipa.Pipeline()
proc_pipe.append(print_string)


queue = multiprocessing.Queue()
p = multiprocessing.Process(target=pipe_launcher, args=(proc_pipe, queue,))
p.start()
time.sleep(1)

queue.put("ciccio")
queue.put("pinco")
queue.put("pallo")
queue.put("stop")
queue.close()
queue.join_thread()
p.join()

