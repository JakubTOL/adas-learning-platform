from zalp.application.canbus.diagnostic import READ_SOFTWARE_VERSION_SUBFUNCTION
from zalp.application.scenarios import Step, Scenario
from zalp.application.scenarios.common_steps import CameraInitializationStep


class Wprowadzenie(Step):
    name = 'Wprowadzenie'
    description = """Unified Diagnostic Services – ustandaryzowany sposób komunikacji z diagnostycznej elektroniką pojazdową.
Nowoczesne pojazdy posiadające różnego rodzaju ECU umożliwiają weryfikację ich stanu, odczytanie błędów lub parametrów pracy w samochodzie. W tym celu producenci implementują w oprogramowaniu odpowiednie mechanizmy umożliwiające komunikację z nimi i ich diagnostykę za pomocą dostępnych magistrali komunikacyjnych np. CAN, Ethernet. Komunikacja taka odbywa się na zasadzie odpytywania ECU za pomocą predefiniowanych serwisów diagnostycznych."""


class SerwisyDiagnostyczne(Step):
    name = 'Serwisy diagnostyczne'
    description = """Każdemu serwisowi przyporządkowano numer ID (pierwszy bajt). Kolejne bajty niosą informacje specyficzne dla danego serwisu. Czasem są to predefiniowane identyfikatory, ale mogą to również być dane (np. podczas procesu aktualizacji oprogramowania ECU).
    
    Przykładowe serwisy diagnostyczne:
    [b]- Serwis 0x10 – zmiana sesji diagnostycznej[/b]
        - 0x10 0x01 – sesja „Default” – standardowa praca ECU
        - 0x10 0x03 – sesja „Extended” – rozszerzona o dodatkową diagnostykę
        
    [b]- Serwis 0x22 – odczytaj dane bazując na ID[/b]
        - 0x22 0xF0 0x10 - odczytaj wersję oprogramowania ECU
        
    [b]- Serwis 0x14 – wyczyść błędy w ECU[/b]
        - 0x14 0xFF 0xFF 0xFF - wyczyść wszystkie błędy"""


class UzycieKonsoliDiagnostycznej(Step):
    name = 'Użycie konsoli diagnostycznej'
    description = """W ćwiczeniu skorzystamy z odczytania danych z ECU.
    Korzystając z zakładki "Diagnostyka UDS", wyślij komendę „ReadDataByIdentifier - ReadSoftwareVersion (0x22 0xF0 0x10)”."""
    waitable = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response_ok = False

    def pre(self):
        self.app.can_manager.can1.add_diagnostic_rx_callback(self.callback)

    def callback(self, response):
        if self.response_ok:
            return
        if response.subfunction is READ_SOFTWARE_VERSION_SUBFUNCTION and response.positive:
            self.response_ok = True
            # self.force_next_iteration()

    def is_done(self) -> bool:
        return self.response_ok

    def post(self):
        self.app.can_manager.can1.remove_diagnostic_rx_callback(self.callback)


class InterpretacjaOtrzymanychDanych(Step):
    name = 'Interpretacja otrzymanych danych'
    description = """Kamera odpowiedziała na komendę wysłaną z konsoli diagnostycznej. Jest ona wyświetlona zarówno w postaci heksadecymalnej, jak i zdekodowanej (znaki ASCII).
    
    Zgodnie z instrukcją serwisową, podaj "Identyfikator ECU" (ZZZZ) ze zdekodowanej odpowiedzi.
    Format odpowiedzi: [b]XXXXYYYYYYZZZZ[/b], 14 znaków, gdzie:
    - XXXX - wersja oprogramowania (4 znaki)
    - YYYYYY - wersja hardware (6 znaków)
    - ZZZZ - identyfikator ECU (4 znaki)
    """
    ask_user_input = True

    def is_user_input_correct(self, user_input):
        return str(user_input).upper() == '39AF'


class UdsBasicsScenario(Scenario):
    name = 'Podstawy UDS'
    description = 'Wprowadzenie do podstaw diagnostyki elektroniki pojazdowej - Unified Diagnostic Services'
    steps = (
        Wprowadzenie,
        CameraInitializationStep,
        SerwisyDiagnostyczne,
        UzycieKonsoliDiagnostycznej,
        InterpretacjaOtrzymanychDanych
    )
