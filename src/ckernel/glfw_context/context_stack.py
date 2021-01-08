
class GLFWContextStack:
    # reserve None as first element
    __stack = []

    @classmethod
    def _get_current(cls):
        """
        return current context

        :return:
        """
        if cls.__stack:
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
