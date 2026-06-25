import time
import asyncio
from gpiozero import Button
from src.configs.configmodels import config_models
from src.configs import configmessages
from src.configs.configlogger import logger_config
from src.configs.configRPI import config_rpi
from src.executors.visionsistem import HollyVisionSystem
from src.executors.assembly_messages import hollymatic_messages
from src.executors.assembly_composite import assembly_composite
from src.utils.camerautils import cameraUtils
from src.google.gchat import gchat
from src.google.gdrive import gdrive
from src.Rclone.rclone_GDrive import rclone_upload



if __name__ == "__main__":
    logger = logger_config.main_production_logger
    config_models.set_to_default()
    system = HollyVisionSystem()
    camerautils = cameraUtils()
    hvs_messages = hollymatic_messages()


    turn_on_button = Button(config_rpi.TURN_ON_PIN, hold_time=1.5)
    shut_down_button = Button(config_rpi.SHUT_DOWN_PIN, hold_time=1.5)
    calibrate_button = Button(config_rpi.CALIBRATE_PIN, hold_time=1.5)
    


    logger.log_startup("Se ha inicializado el main")
    execute = True
    loop = asyncio.get_event_loop()
    loop.run_until_complete(system.discover_kp200())

    while execute == True:
            
        if turn_on_button.is_held:
            
            correct_assamblies = 0
            config_models.set_to_default()
            # Requisito A: limpiar ./temporal/images al inicio de cada corrida
            # (una corrida = cada vez que se presiona turn_on_button).
            assembly_composite.prepare_temporal_images()

            gchat.send_advice(configmessages.HOLLYMATIC_MESSAGE_START)
            # 1. Verificar cámaras
            logger.info("\nVerificando cámaras...")
            cameras = camerautils.check_cameras()
            logger.info("Camaras checadas")
            for path, info in cameras.items():
                status = "Conectada" if info['exists'] else "No conectada"
                logger.info(f"{path}: {status}")

            # 2. Procesar con la primera cámara disponible
            available_cams = [path for path, info in cameras.items() if info['exists']]
            if not available_cams:
                logger.critical("\nError: No hay cámaras disponibles")
            else:
                for camera_holly in available_cams:
                    logger.info(f"\nProcesando con cámara: {camera_holly}")
                    system.full_processing(camera_holly)
                    mandatory_assamblies = len(config_models.MANDATORY_ASSEMBLY.values())

                if config_models.RESULTS:
                    results = config_models.RESULTS
                    system.correct_assambly(results)
                    logger.info(f"Resultados de validacion de armado: {config_models.MANDATORY_ASSEMBLY}")
                    for assembly in config_models.MANDATORY_ASSEMBLY.values():
                        if assembly == True:
                            correct_assamblies = correct_assamblies + 1
                logger.info(f"Se han detectado {correct_assamblies} de {mandatory_assamblies}")
                rclone_upload.copy_now()
                
                if correct_assamblies == mandatory_assamblies:
                    loop.run_until_complete(system.hollymatic_turn_on())
                    gchat.send_advice(configmessages.HOLLYMATIC_MESSAGE_CORRECT_ASSEMBLY)
                    pass
                else:
                    # Mal armado: generar el PDF comparativo, subirlo a Drive y
                    # enviar su link unico en el mensaje. Si algo falla, el mensaje
                    # sale igual (solo texto) sin bloquear.
                    composite_link = None
                    try:
                        failed = [k for k, v in config_models.MANDATORY_ASSEMBLY.items() if not v]
                        pdf_path = assembly_composite.build_comparison_pdf(failed)
                        if pdf_path:
                            composite_link = gdrive.upload_and_get_link(pdf_path)
                    except Exception as e:
                        logger.critical(f"No se pudo generar/subir el PDF comparativo debido a: {e}")

                    bad_assembly_message = hvs_messages.bad_assembly_message(
                        config_models.MANDATORY_ASSEMBLY, composite_link=composite_link)
                    gchat.send_advice(bad_assembly_message)

        if shut_down_button.is_held:
            gchat.send_advice(configmessages.HOLLYMATIC_MESSAGE_SHUT_DOWN)
            loop.run_until_complete(system.hollymatic_shut_down())
            logger.info("Apagado")
        if calibrate_button.is_held:
            logger.info("Inicia calibración")
            gchat.send_advice(configmessages.HOLLYMATIC_MESSAGE_CALIBRATE_START)
            loop.run_until_complete(system.hollymatic_calibrate())
            gchat.send_advice(configmessages.HOLLYMATIC_MESSAGE_CALIBRATE_END)
            logger.info("Fin de calibración")
            


                        
                    
                    

