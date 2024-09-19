from zalp.domain.canbus import DecodedMessage
from .message import Message, Messages
from .signal import Signal


# TODO: split TX and RX behavior
class SignalMapping:
    def __init__(self, can1):
        self.can1 = can1

        self.messages = Messages()
        self.messages.add_message(
            Message(
                mgr=can1,
                name='PP_Car_Signals',
                rx=False,
                signal_names=(
                    'PP_Car_Speed',
                    'PP_Car_Speed_CRC_Valid',
                    'PP_Car_Lines_Enabled',
                ))
        )
        self.messages.add_message(
            Message(
                mgr=can1,
                name='PP_ECUs_Status',
                rx=False,
                signal_names=(
                    'PP_BCM_Status',
                    'PP_ACC_Status',
                    'PP_ABS_Status',
                ))
        )
        self.messages.add_message(
            Message(
                mgr=can1,
                name='PP_Camera_Status',
                rx=True,
                signal_names=(
                    'PP_Vision_Status',
                    'PP_Calibration_Status',
                    'PP_Blockage_Status',
                ))
        )
        self.messages.add_message(
            Message(
                mgr=can1,
                name='PP_TSR_0',
                rx=True,
                signal_names=(
                    'PP_TSR_Sign_Name_0',
                    'PP_TSR_Sign_Status_0',
                    'PP_TSR_Sign_Name_1',
                    'PP_TSR_Sign_Status_1',
                ))
        )

        self.messages.add_message(
            Message(
                mgr=can1,
                name='PP_Line_Volt_Data',
                rx=True,
                signal_names=(
                    'PP_RightLineDistance',
                    'PP_LeftLineDistance',
                    'PP_BatteryVoltage',
                ))
        )

    @property
    def tsr_0(self) -> Message:
        return self.messages.PP_TSR_0

    @property
    def camera_status(self) -> Message:
        return self.messages.PP_Camera_Status

    @property
    def line_volt_data(self) -> Message:
        return self.messages.PP_Line_Volt_Data

    @property
    def car_speed(self) -> Signal:
        return self.messages.PP_Car_Signals.PP_Car_Speed

    @property
    def car_speed_valid(self) -> Signal:
        return self.messages.PP_Car_Signals.PP_Car_Speed_CRC_Valid

    @property
    def car_lines_enabled(self) -> Signal:
        return self.messages.PP_Car_Signals.PP_Car_Lines_Enabled

    @property
    def bcm_status(self) -> Signal:
        return self.messages.PP_ECUs_Status.PP_BCM_Status

    @property
    def acc_status(self) -> Signal:
        return self.messages.PP_ECUs_Status.PP_ACC_Status

    @property
    def abs_status(self) -> Signal:
        return self.messages.PP_ECUs_Status.PP_ABS_Status

    @property
    def tsr_sign_name_0(self) -> Signal:
        return self.messages.PP_TSR_0.PP_TSR_Sign_Name_0

    @property
    def tsr_sign_status_0(self) -> Signal:
        return self.messages.PP_TSR_0.PP_TSR_Sign_Status_0

    def on_message(self, msg: DecodedMessage):
        self.messages.on_message(msg)

    def set_initialization_values(self):
        self.car_speed.set(50)
        self.car_speed_valid.set(1)
        self.car_lines_enabled.set(10)

        self.bcm_status.set('OK')
        self.acc_status.set('OK')
        self.abs_status.set('OK')
