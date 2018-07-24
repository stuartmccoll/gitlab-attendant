import collections
import json
import logging
import traceback


class loggingJsonFormatter(logging.Formatter):
    def format(self, record):
        exc = (
            traceback.format_exception(*record.exc_info)
            if record.exc_info
            else None
        )

        log_entry = collections.OrderedDict(
            [
                ("timestamp", self.formatTime(record)),
                ("level", record.levelname),
                ("message", record.msg),
                ("exception", exc),
            ]
        )

        return json.dumps(log_entry)


jsonFormatter = loggingJsonFormatter()

logger = logging.getLogger(__name__)

_logger = logging.StreamHandler()
_logger.setFormatter(jsonFormatter)

logger.addHandler(_logger)
logger.setLevel(logging.DEBUG)

logger.debug("Logging initialised...")
