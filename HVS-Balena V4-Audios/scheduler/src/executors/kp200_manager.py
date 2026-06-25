import asyncio
from src.configs.settings import config
from src.tp_link.mikasa import SmartDeviceController 
from src.configs.configlogger import logger_config  

logger = logger_config.main_production_logger

controller = SmartDeviceController(
    ip_address=config.MIKASA_IP,
    username=config.MIKASA_USERNAME,
    password=config.MIKASA_PASSWORD,
)

class kp200:
    async def night_off():
        await controller.discover_device()
        if controller.device.is_on:
            status = ("⚠️ Cierre programado: hoy NO se presionó el botón de apagado manual. "
                "El equipo se apagará de forma automática.")
            await turn_off()
            return status
        
        else:
            logger.info("KP200 ya estaba apagado; sin acción.")
            return None