from zalp.application.scenarios import Step, Scenario
from zalp.application.scenarios.common_steps import CameraInitializationStep


class Wprowadzenie(Step):
    name = 'Wprowadzenie'
    description = """Failsafe – mechanizmy zabezpieczające użytkownika pojazdu przed nieprawidłowym działaniem Kamery ADAS spowodowanym np. przez błędy pochodzące z innych ECU. W tym scenariuszu zademonstrowane zostanie uszkodzenie CRC zabezpieczającego informację o prędkości pojazdu.
Gdy suma kontrolna jest niepoprawna, Kamera ADAS nie może polegać na otrzymywanych danych i uruchamia mechanizmy informujące pojazd o wykrytym problemie i degradacji pewnych funkcji. W naszym przykładzie obserwować będziemy ramkę CAN niosącą informacje o dystansie do prawej i lewej linii. 
Oto przykładowe wymaganie opisujące to zachowanie:
Jeżeli suma kontrolna CRC skojarzona z prędkością pojazdu jest niepoprawna odległość do lewej i prawej linii wysyłana przez Kamerę ADAS powinna wynosić 0xBB8 (3000 dec)."""


class NormalnaPracaKamery(Step):
    name = 'Normalna praca kamery'
    description = """W zakładce "Rx" w polach "Wykryte linie" można zaobsersować pracę kamery - dystans do wykrytych na drodze linii jest wysyłany do innych ECU znajdujących się w samochodzie.
    Dane te przekazywane są w ramce CAN PP_Line_Volt_Data (ID: 0x100), którą obserwować można w zakładce "CAN traffic analyzer"."""


class WprowadzenieBledu(Step):
    name = 'Wprowadzenie błędu do systemu'
    description = """W zakładce "Tx" w polach "Stan samochodu", odznaczając checkbox "CRC prędkości poprawne", ustaw niepoprawną CRC (sumę kontrolną) prędkości samochodu.
    Dane z tego widżetu zostaną wysyłane do kamery w ramce CAN PP_Car_Signals (ID: 0x200), która można obserwować w zakładce "CAN traffic analyzer"."""
    waitable = False

    def is_done(self) -> bool:
        return self.app.can_manager.signal_mapping.car_speed_valid.get() == 0


class PrezentacjaMechanizmuFailsafe(Step):
    name = 'Prezentacja mechanizmu Failsafe'
    description = """W reakcji na niepoprawną sumę kontrolą prędkości samochodu, Kamera ADAS wyłącza funkcjonalność wykrywania linii.
    Zauważ, że w ramce CAN PP_Line_Volt_Data (ID: 0x100), którą znajdziesz w zakładce "CAN traffic analyzer", dystans do linii wynosi 0xBB8 (3000 dec).
    W ten sposób Kamera ADAS informuje wszystkie ECU na tej samej magistrali CAN, że otrzymuje niepoprawne dane i pewne funkcjonalności pojazdu zostały wyłączone. W tym przykładzie niepoprawna prędkość mogłaby spowodować błędną detekcję dystansu do linii na drodze i podczas autonomicznej jazdy doprowadzić do sytuacji kryzysowej."""


class FailsafeIntroductionScenario(Scenario):
    name = 'Podstawy Failsafe'
    description = 'Wprowadzenie do Failsafe - mechanizmy wykrywania i reakcji na błędy systemu'
    steps = (
        Wprowadzenie,
        CameraInitializationStep,
        NormalnaPracaKamery,
        WprowadzenieBledu,
        PrezentacjaMechanizmuFailsafe
    )
