class SimulatorError(Exception):
    message: str
    logs_file: bytes

    def __init__(self, message, stdout):
        super().__init__(self, message)
        self.message = message
        self.stdout = stdout

    def __str__(self):
        return self.message


class ValidationError(Exception):
    pass
