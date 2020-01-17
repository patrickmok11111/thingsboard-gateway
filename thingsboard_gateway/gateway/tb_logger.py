#     Copyright 2020. ThingsBoard
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

import logging
import logging.handlers
from time import time
# from thingsboard_gateway.gateway.tb_gateway_service import TBGatewayService


class TBLoggerHandler(logging.Handler):
    def __init__(self, gateway):
        self.__current_log_level = 'DEBUG'
        super().__init__(logging.getLevelName(self.__current_log_level))
        self.__gateway = gateway
        self.activated = False
        self.loggers = ['tb_gateway.service',
                        'tb_gateway.storage',
                        'tb_gateway.extension',
                        'tb_gateway.connector'
                        ]
        for logger in self.loggers:
            log = logging.getLogger(logger)
            log.setLevel(self.__current_log_level)
            log.addHandler(self.__gateway.main_handler)
            log.debug("Added remote handler to log %s", logger)
        logging.getLogger("tb_gateway.tb_connection").addHandler(self.__gateway.main_handler)
        logging.getLogger("tb_gateway.tb_connection").setLevel(logging.INFO)

    def activate(self, log_level=None):
        try:
            for logger in self.loggers:
                if log_level is not None and logging.getLevelName(log_level) is not None:
                    log = logging.getLogger(logger)
                    # log.addHandler(self)
                    self.__current_log_level = log_level
                    log.setLevel(logging.getLevelName(log_level))
        except Exception as e:
            log = logging.getLogger('tb_gateway.service')
            log.exception(e)
        self.activated = True

    def handle(self, record):
        if self.activated:
            record = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s').format(record)
            self.__gateway.send_to_storage(self.__gateway.name, {"deviceName": self.__gateway.name, "telemetry": [{'LOGS': record}]})

    def deactivate(self):
        self.activated = False
