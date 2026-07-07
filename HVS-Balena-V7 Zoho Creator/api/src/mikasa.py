"""Controlador del enchufe Kasa (KP200), copia minima de app/src/mikasa/mikasa.py.

Solo depende de python-kasa: habla con el dispositivo por la LAN (TCP 9999).
No arrastra torch/opencv ni el resto del stack del servicio de vision.
"""
import logging

from kasa import Discover, SmartDeviceException

from src.config import config

logger = logging.getLogger(__name__)


class SmartDeviceController:
    def __init__(self, ip_address, username, password):
        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.device = None

    async def discover_device(self):
        try:
            self.device = await Discover.discover_single(
                host=self.ip_address, port=9999,
                username=self.username, password=self.password,
            )
            await self.device.update()
        except SmartDeviceException as e:
            logger.error(f"Connection issue with the device: {e}")
            raise

    async def update_plugs(self, armado_correcto):
        try:
            # Asegurar que el dispositivo esta inicializado.
            if self.device is None:
                await self.discover_device()

            if armado_correcto:
                await self.device.turn_on()
            else:
                await self.device.turn_off()

            # Actualizar y verificar estado.
            await self.device.update()
            plug_states = [self.device.get_plug_by_index(i).is_on for i in range(2)]
            logger.info(f"Plug states: {plug_states}")
            if armado_correcto and not all(plug_states):
                logger.warning("One or both plugs did not turn on as expected")
        except SmartDeviceException as e:
            logger.error(f"Error updating plug states: {e}")
            raise  # Propagar la excepcion para manejo externo.


# Singleton a nivel modulo (mismo patron que app/src/configs/configmikasa.py::CONTROLLER).
# El constructor no hace I/O de red; la primera llamada a update_plugs descubre el dispositivo.
CONTROLLER = SmartDeviceController(
    config.MIKASA_IP, config.MIKASA_USERNAME, config.MIKASA_PASSWORD,
)
