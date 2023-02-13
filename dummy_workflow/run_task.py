import random
import time

from task_client import register_wrappers

@register_wrappers.register_function
def sleep_geometric_mean(input_1, input_2, input_3):
    """
    This task is meant to be a fake task that runs for [runtime] miliseconds.
    The runtime is random but depends on the input parameters. 
    """
    start = time.time()
    runtime_ms = 10*(1+0.1*random.random())*(abs(input_1*input_2*input_3))**(1/3)
    time.sleep(runtime_ms/1000)
    return int(1000*(time.time()-start))

if __name__ == '__main__':

    for x in range(0,11,2):
        for y in range(0,11,2):
            for z in range(0,11,2):
                runtime = sleep_geometric_mean(x, y, z)
                print('Runtime [ms]', runtime)


