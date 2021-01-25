class OpenglError(Exception):
    pass


class ShaderCompileError(OpenglError):
    pass


class PrgrmLinkError(OpenglError):
    pass


class EntityAbsenceError(OpenglError):
    def __str__(self):
        return f"Entity doesnt exist, probably not created"


class EntityPreexistError(OpenglError):
    def __str__(self):
        return "Entity for the context already exists"


class StructuredDtypeError(OpenglError):
    def __str__(self):
        return "given cant be comprehended as ndarray structured dtype"