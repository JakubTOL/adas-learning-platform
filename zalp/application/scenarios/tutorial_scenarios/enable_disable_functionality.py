from zalp.application.scenarios import Step, Scenario
from zalp.application.scenarios.common_steps import CameraInitializationStep


class Wprowadzenie(Step):
    name = 'Wprowadzenie'
    description = """W nowoczesnych samochodach producenci dostarczają wiele asystentów. Pomagają one kierowcy w prowadzeniu pojazdu i mogą zapobiegać sytuacjom potencjalnie niebezpiecznym.
    Wiele z tych systemów może być konfigurowanych za pomocą menu dostępnego dla kierowcy. Przykładem takiej funkcjonalności może być asystent pasa ruchu."""


class NormalnaPracaKamery(Step):
    name = 'Normalna praca kamery'
    description = """Kamera jest w stanie aktywnym. Zweryfikuj, że wykrywanie linii jest włączone z poziomu UI - zakładka "Tx" pola "Stan samochodu", checkbox "Wykrywanie linii włączone".
    Dane z tego widżetu są wysyłane do kamery w ramce CAN PP_Car_Signals (ID: 0x200), którą znaleźc można w zakładce "CAN traffic analyzer".
    
    W widżecie "Wykryte linie" można zaobserwować pracę kamery - dystans do wykrytych na drodze linii jest wysyłany do innych ECU w samochodzie.
    Dane te przekazywane są w ramce CAN PP_Line_Volt_Data (ID: 0x100), którą znaleźc można w zakładce "CAN traffic analyzer"."""


class WylaczenieAsystenta(Step):
    name = 'Wyłączenie asystenta pasa ruchu'
    description = """W zakładce "Tx" w polach "Stan samochodu" wyłącz funkcję wykrywania linii za pomocą checkbox'a "Wykrywanie linii włączone"."""
    waitable = False

    def is_done(self) -> bool:
        return self.app.can_manager.signal_mapping.car_lines_enabled.get() == 0


class AsystentWylaczony(Step):
    name = 'Asystent pasa ruchu wyłączony'
    description = """W ramce CAN PP_Line_Volt_Data (ID: 0x100) wartości odległości do prawej i lewej linii wynoszą 40.00 (dec). Jest to wartość specjalna informujące inne ECU w pojeździe, że kierowca wyłączył asystenta i pozostałe systemy związane z tą funkcjonalnością mają się nie uruchamiać.
    Dodatkowo ikona sygnalizująca stan asystenta w zakładce "Rx" w widżecie "Wykryte linie" zmienia kolor na pomarańczowy."""


class EnableDisableFunctionalityScenario(Scenario):
    name = 'Włączanie/wyłączanie funkcjonalności'
    description = 'Prezentacja włączania oraz wyłączania funkcjonalności przez kierowcę na przykładzie asystenta pasa ruchu'
    steps = (
        Wprowadzenie,
        CameraInitializationStep,
        NormalnaPracaKamery,
        WylaczenieAsystenta,
        AsystentWylaczony
    )
