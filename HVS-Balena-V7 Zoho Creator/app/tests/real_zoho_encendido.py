"""
Prueba REAL (end-to-end) del flujo de encendido a Zoho Creator.

A DIFERENCIA de test_zoho_encendido.py, aqui NO se mockea la red: se golpean
Grima y Zoho Creator de verdad y se CREA UN REGISTRO REAL con sus imagenes.

Camino de produccion replicado 1:1:
  1. assembly_composite.prepare_temporal_images() limpia ./temporal/images
  2. save_view_frame() deja los frames reales en ./temporal/images/<dia>/<view>.jpeg
  3. ZohoEncendidoProxy().send_encendido() hace:
        login Grima -> getTicket -> crear registro Pendiente -> subir 3 imagenes

Uso:
    cd app
    python3 tests/real_zoho_encendido.py                 # sube las 3 vistas
    python3 tests/real_zoho_encendido.py frontal         # sube solo 'frontal'
"""
import os
import sys

APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if APP_ROOT not in sys.path:
    sys.path.insert(0, APP_ROOT)

from src.zoho.zoho_proxy import ZohoEncendidoProxy
from src.configs.configzoho import config_zoho
from src.executors.assembly_composite import assembly_composite

IMAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")


def _place_frames(views):
    assembly_composite.prepare_temporal_images()
    for view in views:
        src = os.path.join(IMAGES_DIR, f"{view}.jpeg")
        dest = assembly_composite.save_view_frame(src, view)
        if not dest or not os.path.exists(dest):
            raise RuntimeError(f"No se pudo colocar el frame real de la vista '{view}'")
        print(f"  frame '{view}' -> {dest}")


def main():
    views = sys.argv[1:] or ["frontal", "zenithal", "backward"]

    print("=" * 72)
    print("PRUEBA REAL - Flujo de encendido Zoho Creator (Grima 2 pasos)")
    print(f"  Endpoint Grima : {config_zoho.GRIMA_AUTH_URL}")
    print(f"  Zoho base      : {config_zoho.ZOHO_CREATOR_BASE}")
    print(f"  App / Form     : {config_zoho.ZOHO_APP} / {config_zoho.ZOHO_FORM}")
    print(f"  Vistas a subir : {views}")
    print("  *** CREA UN REGISTRO REAL EN ZOHO CREATOR ***")
    print("=" * 72)

    print("\n[1/2] Colocando frames reales...")
    _place_frames(views)

    print("\n[2/2] Ejecutando send_encendido() contra la red REAL...")
    record_id = ZohoEncendidoProxy().send_encendido()

    print("\n" + "=" * 72)
    if record_id:
        print(f"RESULTADO: OK. Registro creado en Zoho Creator -> ID={record_id}")
        print("Revisa el formulario en Zoho para confirmar estado 'Pendiente' e imagenes.")
    else:
        print("RESULTADO: FALLO. send_encendido() devolvio None. Revisa el log de arriba.")
        sys.exit(1)


if __name__ == "__main__":
    main()
