import os


class setting_audio:
    # Carpeta de audios, resuelta relativa a este archivo (app/src/configs ->
    # subiendo 3 niveles: configs -> src -> app) para que funcione igual en
    # local y dentro del contenedor (/app/audios).
    AUDIO_DIR = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "audios",
    )

    # Extensiones de audio soportadas para el catalogo y la mezcla.
    AUDIO_EXTENSIONS = (".wav", ".mp3")

    # Driver de audio de SDL para pygame en contenedor headless (ALSA).
    SDL_AUDIODRIVER = "alsa"

    # JSON {nombre_archivo: duracion_segundos}; se llena en el arranque
    # mediante audio_mixer.catalog_durations().
    AUDIO_DURATIONS = {}
