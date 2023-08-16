from abc import ABC, abstractmethod
from pathlib import Path
import os
import json
import warnings


def _make_dir() -> tuple:
    name = "localfiles"
    _created = False
    current_directory = str(Path.cwd())
    path = Path("\\".join((current_directory, name)))

    if not path.exists():
        path.mkdir()
        _created = True

    else:
        if not path.is_dir():
            path.mkdir()
            _created = True

    return str(path), _created


class Updater(ABC):
    @abstractmethod
    def update(self, message: str):
        pass

    @abstractmethod
    def _create(self):
        pass

    @abstractmethod
    def clear(self) -> bool:
        pass

    @abstractmethod
    def delete(self) -> bool:
        pass


class TXTCreator(Updater):
    suffix = ".txt"

    def __init__(self, file_name: str):
        self.pathname, *args = _make_dir()
        self.file_path = "\\".join((self.pathname, file_name))

        if Path(self.file_path).suffix != self.suffix:
            self.file_path = self.file_path + self.suffix

        self._create()

    def _create(self) -> bool:
        if self._is_file(self.file_path):
            return False

        else:
            with open(self.file_path, "w", encoding='utf-8') as file:
                file.write("")

            return True

    def update(self, *, message: str) -> bool:
        if not isinstance(message, str):
            message = str(message)

        if self._is_file(self.file_path):
            with open(self.file_path, "a", encoding="utf-8") as file:
                file.write(message)
                file.write("\n")

            return True

        return False

    def clear(self) -> bool:
        if self._is_file(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as file:
                file.write("")

            return True

        return False

    def delete(self):
        if self._is_file(self.file_path):
            try:
                os.remove(self.file_path)

            except FileNotFoundError as error:
                warnings.warn("Error in basefather.TXTCreator.delete"
                              f"\n[Text] {error}")

    @staticmethod
    def _is_file(filepath: str):
        if Path(filepath).is_file():
            return True

        return False


class JSONCreator(TXTCreator):
    suffix = ".json"

    def __init__(self, file_name):
        super().__init__(file_name)

    def read_from_json(self) -> dict:
        if self._is_file(self.file_path):
            with open(self.file_path) as json_file:
                try:
                    data = json.load(json_file)
                    return data

                except json.decoder.JSONDecodeError as error:
                    warnings.warn("Cannot decode json-file because it's empty."
                                  f"[Text] {error}")
                    return dict()

    def write(self, *, dump: dict) -> bool:
        if not isinstance(dump, dict):
            return False

        if self._is_file(self.file_path):
            with open(self.file_path, "w") as json_file:
                json.dump(dump, json_file, ensure_ascii=False, indent=4)

            return True

        return False
