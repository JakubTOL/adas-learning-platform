from zalp.application.canbus.diagnostic import READ_ALL_DTCS_SUBFUNCTION
from zalp.application.scenarios import Step, Scenario
from zalp.application.scenarios.common_steps import CameraInitializationStep


class Wprowadzenie(Step):
    name = "Wprowadzenie"
    description = """Failsafe – mechanizmy zabezpieczające użytkownika pojazdu przed nieprawidłowym działaniem Kamery ADAS spowodowanym np. przez błędy pochodzące z innych ECU lub usterki innych komponentów pojazdu. W tym scenariuszu użytkownik stanie się na chwilę diagnostą pracującym w serwisie samochodowym. """

    def pre(self):
        self.app.psu_service.set_voltage(18)


# Use CameraInitializationStep, just changing the name and description
class OpisProblemuOrazInicjalizacja(CameraInitializationStep):
    name = "Opis problemu i inicjalizacja kamery"
    description = """Do serwisu dostarczony został pojazd, który zgłasza niepoprawne działanie kamery ADAS, dodatkowo funkcja detekcji linii nie działa.  
    
    Kamera została zasilona i jest w trakcie inicjalizacji. Może to zajęć do 15 sekund.
    Status kamery można obserwować w zakładce "Rx" w polach "Status kamery".
    """

    def is_done(self) -> bool:
        return self.has_elapsed_time(15)


class Diagnostyka(Step):
    name = "Diagnostyka"
    description = """Jak widać żadna funkcja systemu ADAS nie jest dostępna, gdy kamera zgłasza błąd.
    
    Za pomocą konsoli diagnostycznej odczytaj błędy zapisane w pamięci kamery i zinterpretuj je z pomocą dostarczonej instrukcji serwisowej kamery.

    [b]Wpisz "ID" błędu powodującego niepoprawne działanie ECU w formacie HEX np.: 60AA12.[/b] 
    """

    ask_user_input = True

    def is_user_input_correct(self, user_input):
        return str(user_input).upper() == 'FF0001'  # 01 overvoltage, 02 undervoltage?


class Naprawa(Step):
    name = "Naprawa"
    description = """Problem spowodowany jest zbyt wysokim napięciem zasilania kamery. W samochodzie taka usterka może być spowodowana niepoprawnym działaniem regulatora napięcia umieszczonym w alternatorze.
    
    Usterka zostaje usunięta poprzez przywrócenie zasilania do nominalnej wartości, w tym wypadku 13.7 V, co odpowiada typowemu napięciu zasilania urządzeń w pojazdach osobowych.
    """

    def post(self):
        self.app.psu_service.set_voltage(13.7)


class DTC(Step):
    name = "Usunięcie błędów z pamięci"
    description = """Przyczyna problemu została usunięta, ale system ADAS wciąż nie działa poprawnie. W pamięci istnieją błędy historyczne, których usunięcie jest niezbędne do przywrócenia funkcjonalności systemu.
    [b] Wyczyść błędy z poziomu konsoli diagnostycznej. [/b]
    [b] Odczytaj błędy z poziomu konsoli diagnostycznej, aby upewnić się, że wszystkie problemy zostały rozwiązane, a pamięć błędów jest pusta. [/b]
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response_ok = False

    def pre(self):
        self.app.can_manager.can1.add_diagnostic_rx_callback(self.callback)

    def callback(self, response):
        if self.response_ok:
            return
        if response.subfunction is READ_ALL_DTCS_SUBFUNCTION and \
                response.positive and \
                not response.service_data.dtcs:
            self.response_ok = True
            # self.force_next_iteration()

    def is_done(self) -> bool:
        return self.response_ok

    def post(self):
        self.app.can_manager.can1.remove_diagnostic_rx_callback(self.callback)


class Koniec(Step):
    name = 'Poprawne działanie kamery'
    description = """Błędy historyczne zostały usunięte i system ADAS ponownie działa poprawnie."""


class FailsafeScenario(Scenario):
    name = 'Mechanizm Failsafe'
    description = 'Wprowadzenie do mechanizmu failsafe - diagnostyka i naprawa błędów systemu ADAS'
    steps = (
        Wprowadzenie,
        OpisProblemuOrazInicjalizacja,
        Diagnostyka,
        Naprawa,
        DTC,
        Koniec
    )
