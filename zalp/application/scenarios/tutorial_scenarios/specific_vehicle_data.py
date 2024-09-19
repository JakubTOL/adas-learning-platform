from zalp.application.scenarios import Step, Scenario
from zalp.application.scenarios.common_steps import CameraInitializationStep


# TODO: this scenario can be extended to actually change the coded camera region to USA, then showing that
#       it will ignore EU signs and show USA signs
#       Maybe via CAN msg or diagnostic?

class Wprowadzenie(Step):
    name = 'Wprowadzenie'
    description = """Podczas finalnej instalacji kamer w fabrykach produkujących auta kamery są kodowane.
    Producent za pomocą UDS wgrywa do nieulotnej pamięci kamery pewne dane, które później pomagają algorytmom detekcji w rozpoznawaniu obiektów na drodze."""


class OgraniczeniePredkosciEuropa(Step):
    name = 'Ograniczenie prędkosci Europa'
    description = """Wyświetlony został film ze znakiem ograniczenia prędkości występującym w Europie.
    
    W zakładce "Rx" w polach "Wykryte znaki drogowe" (reprezentującym dane z ramki CAN PP_TSR_0) można zaobserwować poprawne wykrycie przy zbliżaniu się do znaku."""

    minimum_time = 6  # s

    def pre(self):
        self.app.video_player.load_video('Signs\\SpeedLimit30.mp4')


class OgraniczeniePredkosciUsa(Step):
    name = 'Ograniczenie prędkosci USA'
    description = """Wyświetlony został film ze znakiem ograniczenia prędkości występującym w USA.
    
    Dane wgrane do kamery na tym stanowisku podczas jej kodowania wskazują na lokalizację Europa. Dlatego też kamera ignoruje znaki pochodzące z USA. W ten sposób ograniczamy ilość możliwych do wystąpienia kombinacji i redukujemy możliwość pomyłki podczas detekcji."""

    minimum_time = 6  # s

    def pre(self):
        self.app.video_player.load_video('Signs\\SpeedLimit30_USA.mp4')


class SpecificVehicleDataScenario(Scenario):
    name = 'Dane specyficzne dla pojazdu'
    description = 'Wprowadzenie mechanizmu kodowania ECU na podstawie regionu przeznaczenia'
    steps = (
        Wprowadzenie,
        CameraInitializationStep,
        OgraniczeniePredkosciEuropa,
        OgraniczeniePredkosciUsa
    )
