import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.google.gchat import gchat          
from src.configs.configlogger import logger_config 
from src.executors.kp200_manager import kp200  
from src.executors.wiz_manager import wizlights       

logger = logger_config.main_production_logger


async def night_off():
    logger.info("Validando estado del KP200 antes del cierre...")
    status = await kp200.night_off()
    if status:
        gchat.send_advice(status)
    else:
        logger.info("KP200 ya estaba apagado; sin acción.")

async def turn_on_lights():
    light = await wizlights.discover_lights()

    if light:
        print("Turning bulb on...")
        await light.turn_on()
    else:
        logger.critical("No se encontraron bombillas")

async def clean():
    logger.info("Inicio de recordatorio de limpieza")
    try:
        gchat.send_advice("Recordatorio para limpiar el equipo Hollymatic Link: https://docs.google.com/document/d/1_35eAVieR_wksZyMpZfq1OVu411KRgn_dZRcfMIUlxA/edit?usp=sharing")
        self.logger.info("Recordatorio enviado")
    except:
        logger.critical("No se ha podido enviar el recordatorio de limpieza")
        


async def main():

    scheduler = AsyncIOScheduler(timezone="America/Los_Angeles")
    scheduler.add_job(night_off, trigger='cron',hour='22', minute='30')
    scheduler.add_job(turn_on_lights, trigger='cron',hour='16',minute='18')
    scheduler.add_job(clean, trigger='cron',hour='12',minute='30')

    scheduler.start()
    logger.log_startup("[START] AsyncIOScheduler iniciado.")

    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
