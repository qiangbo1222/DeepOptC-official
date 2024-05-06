import json
import os

from dacite import from_dict

from running_modes.configurations import ScaffoldDecoratingConfiguration, ConfigurationEnvelope
from running_modes.enums import GenerativeModelRegimeEnum, RunningModeEnum
from running_modes.scaffold_decorating.logging.scaffold_decorating_logger import ScaffoldDecoratingLogger
from running_modes.scaffold_decorating.scaffold_decoration import ScaffoldDecorator



class Manager:

    def __init__(self, configuration):
        self._configuration = from_dict(data_class=ConfigurationEnvelope, data=configuration)
        self._model_regime = GenerativeModelRegimeEnum()
        self._load_environmental_variables()

    def _scaffold_decorating(self):
        config = from_dict(data_class=ScaffoldDecoratingConfiguration, data=self._configuration.parameters)
        logger = ScaffoldDecoratingLogger(config.logging_path)
        scaffold_decorator = ScaffoldDecorator(config, logger)
        scaffold_decorator.run()

    def run(self):
        """determines from the configuration object which type of run it is expected to start"""
        running_mode = RunningModeEnum()
        switcher = {
            running_mode.SCAFFOLD_DECORATING: self._scaffold_decorating,
        }
        job = switcher.get(self._configuration.run_type, lambda: TypeError)
        job()

    def _load_environmental_variables(self):
        try:
            project_root = os.path.dirname(__file__)
            with open(os.path.join(project_root, '../configurations/config.json'), 'r') as f:
                config = json.load(f)
            environmental_variables = config["ENVIRONMENTAL_VARIABLES"]
            for key, value in environmental_variables.items():
                os.environ[key] = value

        except KeyError as ex:
            raise ex
