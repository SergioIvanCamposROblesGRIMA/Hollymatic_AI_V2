import os
from dotenv import load_dotenv

class config:
    load_dotenv()

    #===================== GOOGLE CONFIGURATIONS ========================#
    SERVICE_ACCOUNT_PATH = os.getenv("SERVICE_ACCOUNT_PATH")
    SPACE_ID = os.getenv("SPACE_ID")
    # Carpeta destino en Drive para el PDF comparativo (recomendado: una
    # Unidad Compartida a la que el service-account tenga acceso de escritura).
    DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")

    #===================== MIKASA CONFIGURATIONS ========================#
    MIKASA_IP = os.getenv("MIKASA_IP")
    MIKASA_USERNAME = os.getenv("MIKASA_USERNAME")
    MIKASA_PASSWORD = os.getenv("MIKASA_PASSWORD")

    #==================== APP LOGGER CONFIGURATIONS ======================#
    GOOGLE_CHAT_WEBHOOK_URL = os.getenv('GOOGLE_CHAT_WEBHOOK_URL')
    ROOT_PROYECT_NAME = os.getenv('ROOT_PROYECT_NAME')
    MAIN_LOG_FILE = os.getenv('MAIN_LOG_FILE')
    CORE_NAME_MAIN = os.getenv('CORE_NAME_MAIN')

    