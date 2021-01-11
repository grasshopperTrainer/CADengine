from .none_context import OpenglNoneContext


# dont know context binding is a common thing so placing class for opengl
class OpenglContextStack:
    # reserve None context as first element
    __stack = [OpenglNoneContext()]

    @classmethod
    def get_current(cls):
        """
        return current context

        :return:
        """
        return cls.__stack[-1]

    @classmethod
    def put_current(cls, context):
        """
        add current to the stack

        :param context:
        :return:
        """
        cls.__stack.append(context)

    @classmethod
    def pop_current(cls):
        """
        remove top context

        To return context to idle, None context is never removed
        :return:
        """
        if 1 < len(cls.__stack):
            cls.__stack.pop()


class OpenglUnboundError(Exception):
    """
    exception for no bound opengl context

    Raised when current opengl context is None.
    """
    pass