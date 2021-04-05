import threading


class ExecutionUndoneError(Exception):
    def __str__(self):
        return f'Command is still running'


class Modeler:
    """
    This class is inheritable.

    Modeler consists of command executor and model modifying commands themselves.
    Inheritor should fill in commands and use executor to inherit threading benefits.
    """

    def __init__(self):
        """
        :attr __elock: Lock, used to block execution

        :attr __exec_count_lock: Lock, used when updating execution counting
        :attr __exec_counter: int, number of execution being executed; same as number of active execution thread
        :attr __exec_results: dict, storage updated by execution threads, value will be popped once asked
        """
        self.__elock = threading.Lock()

        self.__exec_count_lock = threading.Lock()
        self.__exec_counter = 0
        self.__exec_results = {}

    @property
    def elock(self):
        return self.__elock

    @property
    def active_exec_count(self):
        """
        :return: number of threads being executed
        """
        return self.__exec_counter

    def get_returned(self, thread):
        """
        submit ticket to get back command's returned value

        ! If command hasn't returned value yet, error will be raise.
        Check thread.is_active() before calling this method or
        call the method with Exception handler.

        :param thread: Thread, use thread object returned by `execute`
        :return:
        """
        if thread not in self.__exec_results:
            raise ExecutionUndoneError()
        return self.__exec_results.pop(thread)

    def execute(self, command, model, args=(), kwargs={}, block_exec=True):
        """
        run command within separate thread

        It works like a cloakroom. Submit a job and get a ticket.
        Return it when you need the result.

        :param command: function to run
        :param model: model to modify
        :param args: tuple, args to feed into the command
        :param kwargs: dict, keyword args to feed into the command
        :param block_exec: bool, whether to block exection
                            ! commands submitted with True will be executed one at a time,
                            but commands submitted with False goes around this restriction.
        :return: Thread, this is a ticket for the returned value of the command
        """
        # include model and model lock
        kwargs['model'] = model

        # run single command if execution is locked
        t = threading.Thread(target=self.__executor(comm=command, block=block_exec), args=args, kwargs=kwargs)
        t.start()
        return t

    def __executor(self, comm, block):
        """
        create wrapper to add blocking and store returned

        :param comm: function to execute
        :param block: bool, whether to block or not
        :return: None
        """

        def wrapper(*args, **kwargs):
            # blocking
            do_release = False
            if block:
                self.__elock.acquire()
                do_release = True
            # update counter
            with self.__exec_count_lock:
                self.__exec_counter += 1

            # run and store result
            r = comm(*args, **kwargs)
            self.__exec_results[threading.currentThread()] = r

            # update counter
            with self.__exec_count_lock:
                self.__exec_counter -= 1
            if do_release:
                self.__elock.release()

        return wrapper
