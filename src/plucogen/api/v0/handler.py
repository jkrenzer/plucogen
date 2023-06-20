from abc import ABC
from .base import Interface as BaseInterface


class Interface(BaseInterface, ABC):
   
    from .consumer import Interface as ConsumerInterface
    InputData = ConsumerInterface.OutputData
    OutputData = ConsumerInterface.OutputData


