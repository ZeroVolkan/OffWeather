from abc import abstractmethod, ABC


class Command(ABC):
    @abstractmethod
    def __init__(self) -> None:
        self.name: str = self.__class__.__name__

    @abstractmethod
    def execute(self):
        pass
