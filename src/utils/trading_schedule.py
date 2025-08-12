from datetime import datetime, time
import json
import os
from typing import List

# Configuración centralizada - directa desde los valores definidos
user_dir = os.path.expanduser("~")
safe_data_dir = os.path.join(user_dir, "Documents", "GRID SCALP")
parametros_path = os.path.join(safe_data_dir, "parametros_usuario.json")

SESIONES_TRADING = {
    'SIDNEY': {'inicio': time(17, 0), 'fin': time(2, 0), 'dias': [0, 1, 2, 3, 4, 6]},
    'TOKIO': {'inicio': time(19, 0), 'fin': time(4, 0), 'dias': [0, 1, 2, 3, 4, 6]},
    'LONDRES': {'inicio': time(2, 0), 'fin': time(11, 0), 'dias': [0, 1, 2, 3, 4]},
    'NUEVA_YORK': {'inicio': time(7, 0), 'fin': time(16, 0), 'dias': [0, 1, 2, 3, 4]},
    'LONDRES_NY': {'inicio': time(7, 0), 'fin': time(11, 0), 'dias': [0, 1, 2, 3, 4]}
}

def esta_en_horario_operacion(sesiones_seleccionadas: List[str]) -> bool:
    ahora = datetime.now().replace(tzinfo=None)
    hora_actual = ahora.time()
    dia_actual = ahora.weekday()

    for sesion in sesiones_seleccionadas:
        if sesion not in SESIONES_TRADING:
            continue
        config = SESIONES_TRADING[sesion]
        inicio = config['inicio']
        fin = config['fin']

        if fin < inicio:
            if (hora_actual >= inicio or hora_actual <= fin) and dia_actual in config['dias']:
                return True
            if hora_actual <= fin and (dia_actual - 1) % 7 in config['dias']:
                return True
        else:
            if inicio <= hora_actual <= fin and dia_actual in config['dias']:
                return True

    return False

def mostrar_horario_operacion(sesiones_seleccionadas: List[str]) -> str:
    return f"Sesiones activas: {', '.join(sesiones_seleccionadas) if sesiones_seleccionadas else 'NINGUNA'}"

def solicitar_horario_operacion() -> List[str]:
    sesiones_previas = []
    if os.path.exists(parametros_path):
        try:
            with open(parametros_path, "r", encoding="utf-8") as f:
                datos = json.load(f)
                sesiones_previas = datos.get("sesiones_operacion", [])
        except Exception:
            sesiones_previas = []

    print("\n⏰ Configura las sesiones de trading (Horario Ecuador, UTC-5)")
    print("   1 → Sídney (17:00 - 02:00)")
    print("   2 → Tokio (19:00 - 04:00)")
    print("   3 → Londres (02:00 - 11:00)")
    print("   4 → Nueva York (07:00 - 16:00)")
    print("   5 → Solapamiento Londres-NY (07:00 - 11:00)")
    print("   6 → TODAS las sesiones")
    if sesiones_previas:
        print(f"[Enter] para usar las sesiones previas: {', '.join(sesiones_previas)}")

    opcion = input("👉 Ingresa los números de las sesiones deseadas (separados por comas, ej. 3,5): ").strip()

    if opcion == "" and sesiones_previas:
        sesiones_seleccionadas = sesiones_previas
    else:
        mapa = {
            '1': 'SIDNEY',
            '2': 'TOKIO',
            '3': 'LONDRES',
            '4': 'NUEVA_YORK',
            '5': 'LONDRES_NY',
            '6': ['SIDNEY', 'TOKIO', 'LONDRES', 'NUEVA_YORK', 'LONDRES_NY']
        }
        opciones = [opt.strip() for opt in opcion.split(',')]
        sesiones_seleccionadas = []
        for opt in opciones:
            if opt in mapa:
                if opt == '6':
                    sesiones_seleccionadas = mapa['6']
                    break
                elif mapa[opt] not in sesiones_seleccionadas:
                    sesiones_seleccionadas.append(mapa[opt])
        if not sesiones_seleccionadas:
            sesiones_seleccionadas = sesiones_previas or ['LONDRES_NY']

    try:
        if os.path.exists(parametros_path):
            with open(parametros_path, "r", encoding="utf-8") as f:
                datos = json.load(f)
        else:
            datos = {}
        datos["sesiones_operacion"] = sesiones_seleccionadas
        os.makedirs(os.path.dirname(parametros_path), exist_ok=True)
        with open(parametros_path, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Error al guardar sesiones: {e}")

    print(f"✅ Sesiones de operación configuradas: {', '.join(sesiones_seleccionadas)}\n")
    return sesiones_seleccionadas
