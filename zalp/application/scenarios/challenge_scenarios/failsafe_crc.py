from zalp.application.scenarios import Step, Scenario
from zalp.application.scenarios.common_steps import CameraInitializationStep


class Wprowadzenie(Step):
    name = "Wprowadzenie"
    description = """W kamerze obecne są mechanizmy zabezpieczające pojazd przed nieprawidłowym działaniem Kamery ADAS spowodowanym np. przez błędy pochodzące z innych ECU lub usterki innych komponentów pojazdu. 
    W tym scenariuszu użytkownik stanie się na chwilę diagnostą pracującym w serwisie samochodowym. """

    def pre(self):
        self.app.can_manager.signal_mapping.car_speed_valid.set(0)


# Use CameraInitializationStep, just changing the name and description
class OpisProblemuOrazInicjalizacja(CameraInitializationStep):
    name = "Opis problemu i inicjalizacja kamery"
    description = """Do serwisu dostarczony został pojazd, w którym funkcja detekcji linii nie działa.
    Twoim zadaniem jest zdiagnozowanie problemu jaki wystąpił w systemie oraz jego naprawa.
    
    Kamera została zasilona i jest w trakcie inicjalizacji. Może to zajęć do 15 sekund.
    Status kamery można obserwować w zakładce "Rx" w polach "Status kamery".
    """


class JazdaTestowa(Step):
    name = "Jazda testowa"
    description = """Jak widać w zakładce "Rx" w polach "Wykryte linie", funkcja detekcji linii nie działa poprawnie.
    Dane te wysłane z kamery w ramce CAN PP_Line_Volt_Data (0x100), którą obserwować można w zakładce "CAN traffic analyzer".
    Zwróć uwagę, że sygnały PP_LeftLineDistance oraz PP_LeftLineDistance oraz PP_RightLineDistance przyjmują wartość 0xBB8 (3000 dec)."""


class Diagnostyka(Step):
    name = "Diagnostyka problemy"
    description = """Za pomocą konsoli diagnostycznej (zakładka "Diagnostyka UDS") odczytaj błędy zapisane w pamięci kamery i zinterpretuj je za pomocą dostarczonej instrukcji serwisowej kamery.
    
    [b] Wpisz ID błędu powodującego niepoprawne działanie ECU - 6 znaków w formacie heksadecymalnym. np.: 60AA12.[/b]
    """

    ask_user_input = True

    def is_user_input_correct(self, user_input):
        return str(user_input).upper() == '650378'


class Naprawa(Step):
    name = "Naprawa problemu"
    description = """Interpretacja błędu za pomocą instrukcji serwisowej sugeruje niepoprawne działanie komputera wysyłającego do kamery ADAS aktualną prędkość samochodu.
    Suma kontrolna zabezpieczająca wartość prędkości nie jest poprawna.
    
    Zasymuluj naprawienie usterki, zaznaczając "CRC prędkości poprawne" w widżecie "Stan samochodu" w zakładce "Tx"."""

    def is_done(self) -> bool:
        return self.app.can_manager.signal_mapping.car_speed_valid.get() == 1


class Weryfikacja(Step):
    name = "Weryfikacja poprawności naprawy"
    description = """Przyczyna problemu została usunięta i funkcja wykrywania linii została uruchomiona ponownie."""


class FailsafeCRCScenario(Scenario):
    name = 'Mechanizm Failsafe - CRC'
    description = 'Podstawowa diagnostyka niedziałającej funkcji systemu ADAS oraz jej przywrócenie'
    steps = (
        Wprowadzenie,
        OpisProblemuOrazInicjalizacja,
        JazdaTestowa,
        Diagnostyka,
        Naprawa,
        Weryfikacja
    )
