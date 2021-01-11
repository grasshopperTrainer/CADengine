class OpenglError(Exception):
    pass


class ShaderCompileError(OpenglError):
    pass

class PrgrmLinkError(OpenglError):
    pass