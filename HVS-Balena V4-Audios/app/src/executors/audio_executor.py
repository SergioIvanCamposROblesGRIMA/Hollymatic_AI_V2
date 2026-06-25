import os
import io
import json
import time

from src.configs.configlogger import logger_config
from src.configs.setting_audio import setting_audio

# El driver de audio y el silenciado del banner deben fijarse ANTES de
# importar pygame para que surtan efecto.
os.environ.setdefault("SDL_AUDIODRIVER", setting_audio.SDL_AUDIODRIVER)
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame
from pydub import AudioSegment


class audio_mixer:
    def __init__(self):
        """
        Inicializa el modulo de audio: logger, carpeta de audios y el mixer
        de pygame. Cualquier fallo al iniciar el mixer se registra pero no
        rompe el flujo principal.
        """
        self.logger = logger_config.main_production_logger
        self.audio_dir = setting_audio.AUDIO_DIR
        self.extensions = setting_audio.AUDIO_EXTENSIONS

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception as e:
            self.logger.error(f"No se pudo inicializar pygame.mixer: {e}")

        pass

    def _load_segment(self, path):
        """
        Carga un archivo de audio como AudioSegment indicando el formato segun
        la extension: asi los .wav usan el lector WAV nativo (sin ffmpeg) y los
        .mp3 usan ffmpeg.
        """
        fmt = os.path.splitext(path)[1].lower().lstrip(".")
        return AudioSegment.from_file(path, format=fmt)

    def catalog_durations(self):
        """
        Recorre AUDIO_DIR y calcula la duracion en segundos de cada archivo
        .wav/.mp3, guardando {nombre_archivo: segundos} (JSON) en
        setting_audio.AUDIO_DURATIONS. Devuelve el dict.
        """
        durations = {}
        if not os.path.isdir(self.audio_dir):
            self.logger.error(f"Carpeta de audios no encontrada: {self.audio_dir}")
        else:
            for filename in sorted(os.listdir(self.audio_dir)):
                if not filename.lower().endswith(self.extensions):
                    continue
                try:
                    seg = self._load_segment(os.path.join(self.audio_dir, filename))
                    durations[filename] = round(seg.duration_seconds, 3)
                except Exception as e:
                    self.logger.error(f"No se pudo leer duracion de {filename}: {e}")

        setting_audio.AUDIO_DURATIONS = durations
        self.logger.info(f"Duraciones de audio: {json.dumps(durations)}")
        return durations

    def _match_file(self, assembly_key):
        """
        Devuelve la ruta del archivo cuyo nombre (sin extension) coincide
        exactamente con assembly_key, o None si no existe.
        """
        for filename in os.listdir(self.audio_dir):
            base, ext = os.path.splitext(filename)
            if ext.lower() in self.extensions and base == assembly_key:
                return os.path.join(self.audio_dir, filename)
        return None

    def build_failed_assembly_audio(self, mandatory_assembly):
        """
        Construye en memoria (BytesIO, formato WAV) la suma/concatenacion de
        los audios correspondientes a los ensamblajes en False dentro de
        mandatory_assembly. Devuelve el BytesIO o None si no hay nada que mezclar.
        """
        failed = [k for k, v in mandatory_assembly.items() if not v]
        combined = AudioSegment.empty()
        used = []
        for key in failed:
            path = self._match_file(key)
            if not path:
                self.logger.error(f"Sin audio para ensamblaje: {key}")
                continue
            try:
                combined += self._load_segment(path)
                used.append(key)
            except Exception as e:
                self.logger.error(f"No se pudo agregar audio {key}: {e}")

        if not used:
            return None

        buf = io.BytesIO()
        combined.export(buf, format="wav")
        buf.seek(0)
        self.logger.info(
            f"Audio combinado para {used} ({combined.duration_seconds:.2f}s)"
        )
        return buf

    def play_failed_assembly(self, mandatory_assembly):
        """
        Construye el audio combinado de los ensamblajes en False y lo reproduce,
        bloqueando hasta que termine. Cualquier fallo se registra sin romper el
        flujo principal.
        """
        buf = self.build_failed_assembly_audio(mandatory_assembly)
        if buf is None:
            self.logger.info("No hay audios que reproducir para este armado")
            return

        try:
            pygame.mixer.music.load(buf)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.2)
        except Exception as e:
            self.logger.error(f"No se pudo reproducir el audio: {e}")
