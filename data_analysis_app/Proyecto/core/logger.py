class Logger:
    def __init__(self, log_file="", log_level="", timestamp=None, log_format=""):
        self.log_file = log_file
        self.log_level = log_level
        self.timestamp = timestamp
        self.format = log_format

    def debug(self):
        pass

    def info(self):
        pass

    def warning(self):
        pass

    def error(self):
        pass

    def _write_log(self):
        pass