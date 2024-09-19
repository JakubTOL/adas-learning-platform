from .challenge_scenarios.failsafe import FailsafeScenario
from .challenge_scenarios.failsafe_crc import FailsafeCRCScenario
from .challenge_scenarios.uds_basics import UdsBasicsScenario
from .tutorial_scenarios.enable_disable_functionality import EnableDisableFunctionalityScenario
from .tutorial_scenarios.failsafe_introduction import FailsafeIntroductionScenario
from .tutorial_scenarios.specific_vehicle_data import SpecificVehicleDataScenario

"""
File containing list of Tutorial Scenario and Challenge Scenarios to be available in application.
"""


class ScenarioList(list):
    def get_scenario_by_name(self, name):
        return filter(lambda sc: sc.name == name, self).__next__()


tutorial_scenario_list = ScenarioList([
    FailsafeIntroductionScenario,
    EnableDisableFunctionalityScenario,
    SpecificVehicleDataScenario,
])

challenge_scenario_list = ScenarioList([
    UdsBasicsScenario,
    FailsafeScenario,
    FailsafeCRCScenario,
])
