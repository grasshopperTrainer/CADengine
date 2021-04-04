import threading
import weakref

from .vicinity_picker import VicinityPicker
from ..global_id_provider import GIDP
from gkernel.color import ClrRGBA
import mkernel.shapes as shp


class ExecutionUndoneError(Exception):
    def __str__(self):
        return f'Command is still running'


class Modeler:
    """
    This class is inheritable.

    Modeler consists of command executor and model modifying commands themselves.
    Inheritor should fill in commands and use executor to inherit threading benefits.
    """

    __mlocks = weakref.WeakKeyDictionary()

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
        mlock = self.__mlocks.setdefault(model, threading.Lock())
        kwargs['model'], kwargs['mlock'] = model, mlock

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


class AModeler(Modeler):
    """
    Default, engine-embedded modeler
    """

    def __init__(self):
        super().__init__()
        self.__vp = VicinityPicker(offset=500)
        self.__last_button_status = {0: 0, 1: 0, 2: 0}

        self.__selected = None
        self.__selection_color = 1, 1, 0, 1

    def listen(self, model, window, mouse, keyboard, camera, cursor, id_picker):
        """
        check condition and trigger commands

        :param window:
        :param model:
        :param spp:
        :return:
        """
        if mouse.get_button_status(0) and self.__last_button_status[0] != 1:
            self.execute(self.point_add_select, model, args=(window, camera, cursor, id_picker))
        elif keyboard.get_key_status('v'):
            self.execute(self.point_delete, model, args=(window, camera, cursor, id_picker))
        self.__last_button_status[0] = mouse.get_button_status(0)

    def point_add_select(self, window, camera, cursor, id_picker, model, mlock):
        """
        add new or select existing

        :param camera:
        :param cursor:
        :param id_picker: FramePixelPicker,
        :param model:
        :param mlock:
        :return:
        """
        # if selecting existing
        with window.context.gl:
            cid = id_picker.pick(cursor.pos_local, size=(1, 1))[0][0]
        clr = ClrRGBA(*cid).as_ubyte()[:3]
        shape = GIDP().get_registered(clr)

        if not shape:
            pos = self.__vp.pick(camera, cursor)[1]
            with mlock:
                model.add_geo(pos)
            if self.__selected:
                self.__remove_selected()
        else:
            if isinstance(shape, shp.Pnt):
                if self.__selected:
                    if self.__selected[0]() != shape:
                        self.__remove_selected()
                        self.__set_selected(shape)
                else:
                    self.__set_selected(shape)

    def point_delete(self, window, camera, cursor, id_picker, model, mlock):
        """

        :param window:
        :param camera:
        :param cursor:
        :param id_picker:
        :param model:
        :param mlock:
        :return:
        """
        if self.__selected:
            if self.__selected[0]() is not None:
                self.__selected[0]().delete()
        self.__selected = None

    def __remove_selected(self):
        """
        remove selected

        :return:
        """
        if self.__selected[0]() is not None:
            self.__selected[0]().clr = self.__selected[1]
        self.__selected = None

    def __set_selected(self, geo):
        """
        cache geometry as selected
        :return:
        """
        self.__selected = weakref.ref(geo), geo.clr.copy()
        geo.clr = (1, 1, 0, 1)