#------------ Start Here ----------------------------
import threading
import os
import differentialModule as nw

def task1():
    print("Task 1 assigned to thread: {}".format(threading.current_thread().name))
    print("ID of process running task 1: {}".format(os.getpid()))
    # ----- load screen saver
    nw.dScreen()

def task2():
    print("Task 2 assigned to thread: {}".format(threading.current_thread().name))
    print("ID of process running task 2: {}".format(os.getpid()))
    nw.watchDog()

if __name__ == "__main__":

    print("\nID of process running main program: {}".format(os.getpid()))
    print("Main thread name: {}\n".format(threading.current_thread().name))

    t1 = threading.Thread(target=task1, name='t1')
    t2 = threading.Thread(target=task2, name='t2')

    t1.start()
    t2.start()

    t1.join()
    t2.join()