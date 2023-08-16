from abc import abstractmethod, ABC
from typing import Sequence, Mapping, Any, Generator, Callable
from json import dump
import warnings
import os


def _write_types(object_to_update: Any, file_descriptor):
    ignore_types = (str, bytes, bytearray)
    if isinstance(object_to_update, Mapping):
        dump(object_to_update, file_descriptor)

    elif isinstance(object_to_update, Sequence) and not isinstance(object_to_update, ignore_types):
        strings = [str(i) for i in object_to_update]
        file_descriptor.writelines(strings)

    else:
        file_descriptor.write(str(object_to_update))


def catch_permission_error(function):
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)

        except PermissionError as error:
            warnings.warn(f"An error occurred in {function} "
                          f"{error}")
            return None

    return wrapper


class FileManager(ABC):
    default_extension: str
    local_directory = None

    def __init__(self):
        if self.local_directory is None:
            self.local_directory = self.__make_dir_for_temp_files()

    @staticmethod
    def is_file_valid(file_path) -> bool:
        if not file_path:
            return False

        if not os.path.isfile(file_path):
            return False
        return True

    @staticmethod
    @catch_permission_error
    def __make_dir_for_temp_files():
        name = "localfiles"
        current_path = os.getcwd()
        dir_path = os.path.join(current_path, name)

        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)

        return dir_path

    def _validate_file_path(self, file_path: str):
        path, extension = os.path.splitext(file_path)

        if not self.local_directory:
            return None

        if extension != self.default_extension:
            extension = self.default_extension

        path = "".join((path, extension))
        abs_path = os.path.abspath((os.path.join(self.local_directory, path)))
        return abs_path

    @abstractmethod
    def create(self):
        pass

    @abstractmethod
    def write(self, write_text):
        pass

    @abstractmethod
    def update(self, update_text):
        pass

    @abstractmethod
    def clear(self):
        pass


class HTMLFile(FileManager):
    default_extension = ".html"

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = self._validate_file_path(file_path)
        self.create()

    def create(self):
        if not self.is_file_valid(self.file_path):
            return False

        with open(self.file_path, "w", encoding="utf-8"):
            pass
        return True

    def write(self, write_text):
        pass




class TXTFile(FileManager):
    default_extension = ".txt"

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = self._validate_file_path(file_path)
        print(self.create())

    def __str__(self):
        return f"TXTFile(path='{self.file_path}', ext='{self.default_extension}')"

    @catch_permission_error
    def create(self) -> bool:
        if not self.is_file_valid(self.file_path):
            return False

        with open(self.file_path, "w", encoding="utf-8"):
            pass

        return True

    @catch_permission_error
    def clear(self) -> bool:
        if not self.is_file_valid(self.file_path):
            return False

        with open(self.file_path, "w", encoding="utf-8"):
            pass

        return True

    @catch_permission_error
    def write(self, object_to_write, newln=None):
        if not self.is_file_valid(self.file_path):
            return False

        with open(self.file_path, "w", encoding="utf-8") as file:
            if newln is True:
                file.write(os.linesep)

            _write_types(object_to_write, file)

        return True

    @catch_permission_error
    def update(self, object_to_update, newln=True) -> bool:
        if not self.file_path:
            return False

        if not os.path.isfile(self.file_path):
            return False

        with open(self.file_path, "a", encoding="utf-8") as file:
            if newln is True:
                file.write(os.linesep)

            _write_types(object_to_update, file)

        return True

    @catch_permission_error
    def readfile(self, discard: Callable = None) -> Generator[str, None, None]:
        if not self.is_file_valid(self.file_path):
            return

        with open(self.file_path, "r", encoding="utf-8") as file:
            if isinstance(discard, Callable):
                iterable = filter(discard, file)

            else:
                iterable = file

            for line in iterable:
                line = line.strip()
                if line and line != os.linesep:
                    yield line

    @catch_permission_error
    def read(self):
        if not self.is_file_valid(self.file_path):
            return

        with open(self.file_path, "r", encoding="utf-8") as file:
            string = file.readlines()

        return string


