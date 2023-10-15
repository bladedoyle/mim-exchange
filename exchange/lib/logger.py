#!/usr/bin/env python3

import logging
import logging.handlers


class Logger:
    __instance = None

    def __new__(cls, log_level="ERROR", log_dir=None):
        if cls.__instance is None:
            cls.__instance = super(Logger, cls).__new__(cls)
            log_formatter = logging.Formatter("%(asctime)s [%(process)d:%(filename)s:%(lineno)d] [%(levelname)-5.5s]  %(message)s")
            l = logging.getLogger()
            l.root.setLevel(log_level)

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(log_formatter)
            console_handler.setLevel(log_level)
            l.addHandler(console_handler)

            if log_dir is not None:
                logfilename = "{0}/messages.log".format(log_dir)
                file_handler = logging.FileHandler(logfilename)
                file_handler.setFormatter(log_formatter)
                file_handler.setLevel(log_level)
                l.addHandler(file_handler)

                rotationHandler = logging.handlers.RotatingFileHandler(
                    filename=logfilename,
                    mode="a",
                    maxBytes=100000000,
                    backupCount=0,
                )
                l.addHandler(rotationHandler)

            cls.__instance.logger = l
        return cls.__instance.logger

    @classmethod
    def clear(cls):
        if cls.__instance is not None:
            cls.__instance.logger.handlers.clear()
            cls.__instance = None
