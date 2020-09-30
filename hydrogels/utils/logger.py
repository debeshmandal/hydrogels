import logging
import sys
import os

class NewLineFormatter(logging.Formatter):
    def __init__(self):
        """
        Init given the log line format and date format
        """
        logging.Formatter.__init__(self, '%(levelname)s: [%(name)s] %(message)s')


    def format(self, record):
        """
        Override format function
        """
        msg = logging.Formatter.format(self, record)

        if record.message != "":
            parts = msg.split(record.message)
            msg = msg.replace('\n', '\n' + parts[0])

        return msg

class Logger:
    def __init__(self, name):
        if name == '__main__':
            name = 'root'
        self.logger = logging.getLogger(name)
        self.logger.setLevel(
            int(os.environ.get('DEBUG_LEVEL', logging.INFO))
        )
        ch = logging.StreamHandler()
        ch.setFormatter(NewLineFormatter())
        self.logger.addHandler(ch)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def kill(self, message=''):
        self.logger.critical(message)
        sys.exit()

    
