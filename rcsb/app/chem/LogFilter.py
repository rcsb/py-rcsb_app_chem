##
# File: LogFilter.py
# Date: 29-Jun-2020 jdw
#
# Pre-filter for Gunicorn health check requests - NOT CURRENTLY USED
##
import logging

from gunicorn import glogging


class HealthCheckFilter(logging.Filter):
    def filter(self, record):
        return record.getMessage().find("/hc") == -1


class LogFilter(glogging.Logger):
    def setup(self, cfg):
        super().setup(cfg)
        # Add filters to Gunicorn logger
        logger = logging.getLogger("gunicorn.error")
        logger.addFilter(HealthCheckFilter())


class LogFilterQ(glogging.Logger):
    def access(self, resp, req, environ, request_time):
        # disable healthcheck logging
        if req.path in ["/hc"]:
            return
        super().access(resp, req, environ, request_time)
