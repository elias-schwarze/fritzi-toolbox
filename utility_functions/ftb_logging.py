import bpy
import time


from enum import Enum, unique

ENDC = "\033[0m"  # ends text formatting and resets to default


@unique
class Severity(Enum):
    NONE = ""                   # no severity code printed + no color
    INFO = "\033[94m"           # blue
    WARNING = "\033[93m"        # yellow
    ERROR = "\033[91m"          # red


def console(self, severity: Severity, message: str, end: str = "\n") -> None:
    """
    Prints the specified message with specific color-coded severity to the console using current time
    and bl_idname as identifier.
    :param severity: The severity of the message. (NONE, INFO, WARNING, ERROR)
    :type severity:'Severity'
    :param message: The message being printed to the console
    :type message:'str'
    """
    _time_str = time.strftime("%H:%M:%S", time.localtime())
    _severity_str = (f"[{severity.name}]", "")[severity == Severity.NONE]
    _identifier = self.__class__.__name__
    if isinstance(self, bpy.types.Operator):
        _identifier = self.bl_idname
    print(f"[{_time_str}]{severity.value}{_severity_str}{ENDC} {_identifier}: {message}", end=end)


def report(self, severity: Severity, message: str) -> None:
    """
    This should only be called from inside an operator class. Prints a message with specific color-coded
    severity to the console and also performs a report in blender using the message and severity specified.
    :param severity: The severity of the message. (NONE, INFO, WARNING, ERROR)
    :type severity:'Severity'
    :param message: The message being printed to the console and in the report
    :type message:'str'
    """
    console(self, severity, message)
    if not issubclass(self.__class__, bpy.types.Operator):
        _class_name = __name__.split('.')[-1]
        _error_msg = (f"The {_class_name}.report() method should only be called from inside an operator "
                      f"class. The current class calling is of type: \"{self.__class__.__base__}\". "
                      f"Use the {_class_name}.console() method instead")
        console(self, Severity.ERROR, _error_msg)
        return

    if severity != Severity.NONE:
        self.report({severity.name}, message)
