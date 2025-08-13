# Script de Descarga de Velas Históricas - MT5

Este script permite descargar velas históricas de MetaTrader 5 con opciones flexibles para especificar el rango de fechas desde la línea de comandos.

## Características

- ✅ Descarga desde abril hasta la fecha actual (por defecto)
- ✅ Especificar número de meses o días hacia atrás
- ✅ Definir fechas exactas de inicio y fin
- ✅ Cambiar el símbolo a descargar
- ✅ Múltiples timeframes (H4, H1, M15, M5)
- ✅ Nombres de archivo automáticos basados en el período

## Ejemplos de Uso

### 1. Descarga por defecto (desde abril hasta hoy)
```powershell
python scripts/descarga_velas.py
```

### 2. Descargar últimos 4 meses
```powershell
python scripts/descarga_velas.py --meses 4
```

### 3. Descargar últimos 120 días
```powershell
python scripts/descarga_velas.py --dias 120
```

### 4. Descargar desde una fecha específica hasta hoy
```powershell
python scripts/descarga_velas.py --desde 2025-04-01
```

### 5. Descargar un rango específico de fechas
```powershell
python scripts/descarga_velas.py --desde 2025-04-01 --hasta 2025-07-01
```

### 6. Cambiar el símbolo (ejemplo: GBPUSD)
```powershell
python scripts/descarga_velas.py --simbolo GBPUSD --meses 3
```

### 7. Descargar EURUSD desde abril con nombres cortos de parámetros
```powershell
python scripts/descarga_velas.py -f 2025-04-01 -s EURUSD
```

## Argumentos Disponibles

| Argumento | Forma Corta | Descripción | Ejemplo |
|-----------|-------------|-------------|---------|
| `--meses` | `-m` | Número de meses hacia atrás | `--meses 4` |
| `--dias` | `-d` | Número de días hacia atrás | `--dias 120` |
| `--desde` | `-f` | Fecha de inicio (YYYY-MM-DD) | `--desde 2025-04-01` |
| `--hasta` | `-t` | Fecha final (YYYY-MM-DD) | `--hasta 2025-08-13` |
| `--simbolo` | `-s` | Símbolo a descargar | `--simbolo GBPUSD` |

## Timeframes Descargados

- **H4**: Velas de 4 horas
- **H1**: Velas de 1 hora  
- **M15**: Velas de 15 minutos
- **M5**: Velas de 5 minutos

## Estructura de Archivos de Salida

Los archivos se guardan en la carpeta `data/YYYY-MM-DD/` con el formato:
```
velas_SIMBOLO_TIMEFRAME_PERIODO.csv
```

Ejemplos:
- `velas_EURUSD_H4_4meses.csv`
- `velas_EURUSD_H1_120dias.csv`
- `velas_GBPUSD_M15_3meses.csv`

## Contenido de los Archivos CSV

Cada archivo incluye las siguientes columnas:
- `datetime`: Fecha y hora de la vela
- `open`: Precio de apertura
- `high`: Precio máximo
- `low`: Precio mínimo
- `close`: Precio de cierre
- `volume`: Volumen de ticks
- `spread`: Spread
- `real_volume`: Volumen real
- `symbol`: Símbolo
- `timeframe`: Marco temporal
- `weekday`: Día de la semana
- `hour`: Hora del día

## Requisitos

- MetaTrader 5 debe estar abierto y conectado
- Cuenta MT5 activa
- Bibliotecas Python: `MetaTrader5`, `pandas`, `rich`

## Mensajes de Error Comunes

### Error de conexión a MT5
```
Error al inicializar MT5: Código: [ERROR_CODE]
```

**Soluciones:**
1. Asegúrate de que MetaTrader 5 esté abierto
2. Verifica que estés logueado en MT5
3. Comprueba que la cuenta esté activa
4. Reinicia MetaTrader 5 e intenta de nuevo

### Error de formato de fecha
```
Formato de fecha inválido. Use YYYY-MM-DD
```

**Solución:** Usa el formato correcto para las fechas (ejemplo: 2025-04-01)

## Notas Importantes

- Los argumentos `--meses`, `--dias` y `--desde` son mutuamente excluyentes
- Si no especificas ningún argumento, descargará desde abril del año actual
- El script puede tardar varios minutos dependiendo del rango de fechas y la conexión
- Los archivos se sobrescribirán si ya existen en la carpeta de destino
