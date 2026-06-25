"""
Tests de audio_mixer (src/executors/audio_executor.py) usando los .wav REALES de
./app/audios.

Por cada caso:
  1. catalog_durations(): cataloga la duracion (seg) de cada .wav/.mp3 y la guarda
     en setting_audio.AUDIO_DURATIONS.
  2. Correspondencia clave de MANDATORY_ASSEMBLY -> archivo (mismo nombre antes de
     la extension).
  3. build_failed_assembly_audio(): concatena en memoria las partes de los
     ensamblajes en False y la duracion del combinado ~= suma de esas partes;
     con todo en True devuelve None.

Ademas deja el WAV combinado en ./tests/output/audio/ para escucharlo y validarlo
manualmente.

Uso (validacion manual):
    python3 tests/test_audio_mixer.py
    # luego escuchar ./tests/output/audio/combined_failed.wav
    # (opcional) AUDIO_PLAY_DEMO=1 python3 tests/test_audio_mixer.py  -> reproduce

Tambien es compatible con pytest:
    pytest tests/test_audio_mixer.py -s

Requiere pydub (ffmpeg solo hace falta para .mp3; los .wav no lo necesitan). Si
falta alguna dependencia, los tests se SALTAN con un mensaje claro.
"""
import os
import sys
import unittest

# Permite ejecutar el archivo directamente (python3 tests/...) y que `src` sea importable.
APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if APP_ROOT not in sys.path:
    sys.path.insert(0, APP_ROOT)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "audio")

# Mismas claves/valores que config_models.MANDATORY_ASSEMBLY por defecto
# (3 en False: RAM, KOCUP, ECCENTRIC).
DEFAULT_ASSEMBLY = {
    "RAM_ASSEMBLY_AND_DRIVE_BAR": False,
    "LOCK_SHAFT_ASSAMBLY": True,
    "KOCUP_KOARM_AND_MOLDPLATE": False,
    "ECCENTRIC_LEVER": False,
    "TUMBLER": True,
}

# Import de la clase bajo prueba. Si faltan dependencias (pydub/pygame), se SALTA.
audio_mixer = None
setting_audio = None
IMPORT_ERROR = None
try:
    from src.configs.setting_audio import setting_audio
    from src.executors.audio_executor import audio_mixer
except Exception as e:  # pydub/pygame ausentes, mixer sin dispositivo, etc.
    IMPORT_ERROR = e


def _require_audio():
    if audio_mixer is None or setting_audio is None:
        raise unittest.SkipTest(f"Dependencias de audio no disponibles: {IMPORT_ERROR}")


def _mixer():
    _require_audio()
    return audio_mixer()


# --------------------------------------------------------------------------- #
#  Tests (compatibles con pytest; no retornan valor)
# --------------------------------------------------------------------------- #
def test_catalog_durations():
    """catalog_durations cataloga los audios reales con duracion > 0 y los
    guarda en setting_audio.AUDIO_DURATIONS."""
    mixer = _mixer()
    durations = mixer.catalog_durations()
    assert isinstance(durations, dict) and durations, "No se catalogo ningun audio"
    assert durations == setting_audio.AUDIO_DURATIONS, \
        "catalog_durations no se reflejo en setting_audio.AUDIO_DURATIONS"
    for name, secs in durations.items():
        assert name.lower().endswith(setting_audio.AUDIO_EXTENSIONS), \
            f"Archivo con extension no soportada: {name}"
        assert isinstance(secs, (int, float)) and secs > 0, \
            f"Duracion invalida para {name}: {secs}"


def test_every_key_has_audio():
    """Cada clave de MANDATORY_ASSEMBLY resuelve a un archivo por nombre sin extension."""
    mixer = _mixer()
    for key in DEFAULT_ASSEMBLY:
        assert mixer._match_file(key) is not None, f"Sin audio para ensamblaje: {key}"


def test_build_failed_assembly_audio_concatenates():
    """El WAV combinado de las partes en False dura ~ la suma de esas partes, y se
    deja en tests/output/audio/ para escucharlo."""
    mixer = _mixer()
    durations = mixer.catalog_durations()

    buf = mixer.build_failed_assembly_audio(DEFAULT_ASSEMBLY)
    assert buf is not None, "Deberia generar audio (hay ensamblajes en False)"

    failed = [k for k, v in DEFAULT_ASSEMBLY.items() if not v]
    expected = sum(durations[os.path.basename(mixer._match_file(k))] for k in failed)

    from pydub import AudioSegment
    buf.seek(0)
    combined = AudioSegment.from_file(buf, format="wav")
    assert abs(combined.duration_seconds - expected) < 0.5, \
        (f"Duracion combinada {combined.duration_seconds:.2f}s != suma esperada "
         f"{expected:.2f}s")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, "combined_failed.wav")
    buf.seek(0)
    with open(out_path, "wb") as f:
        f.write(buf.read())
    print(f"[i] WAV combinado ({combined.duration_seconds:.2f}s) escrito en: {out_path}")


def test_all_correct_returns_none():
    """Sin ensamblajes en False no se genera audio (retorna None)."""
    mixer = _mixer()
    all_true = {k: True for k in DEFAULT_ASSEMBLY}
    assert mixer.build_failed_assembly_audio(all_true) is None


# --------------------------------------------------------------------------- #
#  Demo opcional de reproduccion (no es test_*: no corre en pytest)
# --------------------------------------------------------------------------- #
def play_demo():
    """Reproduce el audio combinado del armado por defecto (requiere dispositivo
    de sonido). Solo se invoca con AUDIO_PLAY_DEMO=1 en el runner manual."""
    mixer = _mixer()
    print("[i] Reproduciendo audio combinado del armado por defecto...")
    mixer.play_failed_assembly(DEFAULT_ASSEMBLY)
    print("[i] Reproduccion finalizada")


# --------------------------------------------------------------------------- #
#  Runner manual
# --------------------------------------------------------------------------- #
def main():
    print("=" * 70)
    print("TESTS - audio_mixer (audios reales de ./app/audios)")
    print(f"Salida para escucha manual: {OUTPUT_DIR}")
    print("=" * 70)

    tests = [
        ("catalog_durations", test_catalog_durations),
        ("cada clave tiene audio", test_every_key_has_audio),
        ("build concatena (suma de partes)", test_build_failed_assembly_audio_concatenates),
        ("todo correcto -> None", test_all_correct_returns_none),
    ]
    failures = skipped = 0
    for title, fn in tests:
        try:
            fn()
            print(f"[OK]    {title}")
        except unittest.SkipTest as e:
            skipped += 1
            print(f"[SKIP]  {title}: {e}")
        except AssertionError as e:
            failures += 1
            print(f"[FALLA] {title}: {e}")

    if os.environ.get("AUDIO_PLAY_DEMO") and not skipped:
        try:
            play_demo()
        except Exception as e:
            print(f"[SKIP]  demo de reproduccion: {e}")

    print("=" * 70)
    if failures:
        print(f"RESULTADO: {failures} test(s) con fallas.")
        sys.exit(1)
    if skipped:
        print(f"RESULTADO: {skipped} test(s) SALTADOS por dependencias; el resto OK.")
    else:
        print("RESULTADO: todos OK. Escucha tests/output/audio/combined_failed.wav")


if __name__ == "__main__":
    main()
