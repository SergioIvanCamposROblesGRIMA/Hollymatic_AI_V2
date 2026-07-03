import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.google.gchat import gchat
from src.configs.configlogger import logger_config
from src.executors.kp200_manager import kp200
from src.executors.kpi_manager import kpi_manager

logger = logger_config.main_production_logger


async def night_off():
    logger.info("Validando estado del KP200 antes del cierre...")
    status = await kp200.night_off()
    if status:
        gchat.send_advice(status)
    else:
        logger.info("KP200 ya estaba apagado; sin acción.")

async def clean():
    logger.info("Inicio de recordatorio de limpieza")
    try:
        gchat.send_advice("Recordatorio para limpiar el equipo Hollymatic Link: https://docs.google.com/document/d/1_35eAVieR_wksZyMpZfq1OVu411KRgn_dZRcfMIUlxA/edit?usp=sharing")
        logger.info("Recordatorio enviado")
    except:
        logger.critical("No se ha podido enviar el recordatorio de limpieza")


async def kpi_report():
    """Reporte mensual de KPIs (día 1): lee la base de datos, arma el PDF,
    lo sube a Drive y manda el link por Google Chat."""
    logger.info("Generando reporte mensual de KPIs...")
    try:
        out = kpi_manager.generate_monthly_report()
        logger.info(f"Reporte de KPIs generado: {out}")
    except Exception as e:
        logger.critical(f"No se pudo generar el reporte mensual de KPIs debido a: {e}")



async def main():

    scheduler = AsyncIOScheduler(timezone="America/Los_Angeles")
    scheduler.add_job(night_off, trigger='cron',hour='22', minute='30')
    scheduler.add_job(clean, trigger='cron',hour='12',minute='3')
    # Reporte mensual de KPIs: el día 1 de cada mes a las 06:00 (hora local).
    scheduler.add_job(kpi_report, trigger='cron', day='1', hour='6', minute='0')

    scheduler.start()
    logger.log_startup("[START] AsyncIOScheduler iniciado.")

    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
