from abc import abstractmethod


class BaseJob:
    """
    this is an abstract class for manage some job
    """

    def __init__(self):
        """
        initialize the class
        """

        pass

    @abstractmethod
    def start(self):
        """
        start the job
        """

        pass
