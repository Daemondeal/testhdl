from abc import ABC, abstractmethod


class SimulatorBase(ABC):
    def validate(self):
        pass

    def setup(self):
        pass

    def clean(self):
        pass
