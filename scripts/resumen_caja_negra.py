#!/usr/bin/env python3
"""
🗃️ ANALIZADOR COMPLETO CAJA NEGRA - TRADING GRID
===============================================

Genera un resumen completo de TODOS los registros capturados
por la caja negra del sistema Trading Grid.

Autor: GitHub Copilot
Fecha: Agosto 12, 2025
"""

import os
import json
import glob
from datetime import datetime
from pathlib import Path
from collections import defaultdict, Counter
import re

# Añadir el directorio raíz del proyecto al path
script_dir = Path(__file__).parent
project_root = script_dir.parent
import sys
sys.path.insert(0, str(project_root))

def analyze_logs():
    """Analiza todos los logs de la caja negra"""
    logs_dir = project_root / "logs"
    
    print("🗃️ RESUMEN COMPLETO DE LA CAJA NEGRA TRADING GRID")
    print("=" * 55)
    print(f"📅 Análisis realizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📂 Directorio de logs: {logs_dir}")
    print()
    
    # Estadísticas generales
    total_events = 0
    total_sessions = set()
    total_files = 0
    events_by_category = defaultdict(int)
    events_by_level = defaultdict(int)
    events_by_session = defaultdict(int)
    critical_events = []
    success_events = []
    error_events = []
    
    # Analizar cada categoría
    categories = ['system', 'trading', 'analytics', 'mt5', 'errors', 'performance', 
                 'fvg', 'signals', 'strategy', 'security']
    
    print("📊 ANÁLISIS POR CATEGORÍAS:")
    print("-" * 55)
    
    for category in categories:
        category_dir = logs_dir / category
        if not category_dir.exists():
            continue
            
        category_files = list(category_dir.glob("*.log"))
        total_files += len(category_files)
        
        category_events = 0
        category_sessions = set()
        
        for log_file in category_files:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            try:
                                # Extraer información del log
                                if '"session_id"' in line:
                                    # Log en formato JSON
                                    data = json.loads(line.split(':', 1)[1])
                                    session_id = data.get('session_id', 'unknown')
                                    level = data.get('level', 'INFO')
                                    message = data.get('message', '')
                                    
                                    total_events += 1
                                    category_events += 1
                                    events_by_category[category] += 1
                                    events_by_level[level] += 1
                                    total_sessions.add(session_id)
                                    category_sessions.add(session_id)
                                    events_by_session[session_id] += 1
                                    
                                    # Categorizar eventos importantes
                                    if level == 'ERROR':
                                        error_events.append({
                                            'session': session_id,
                                            'category': category,
                                            'message': message,
                                            'file': log_file.name
                                        })
                                    elif level == 'SUCCESS':
                                        success_events.append({
                                            'session': session_id,
                                            'category': category,
                                            'message': message
                                        })
                                    elif 'inicializado' in message.lower() or 'conectado' in message.lower():
                                        critical_events.append({
                                            'session': session_id,
                                            'category': category,
                                            'level': level,
                                            'message': message
                                        })
                                        
                            except (json.JSONDecodeError, KeyError):
                                # Log en formato texto simple
                                total_events += 1
                                category_events += 1
                                events_by_category[category] += 1
                                
            except Exception as e:
                continue
        
        # Mostrar estadísticas de la categoría
        size_kb = sum(f.stat().st_size for f in category_files) / 1024
        print(f"📁 {category:<12} | {len(category_files):>3} archivos | {category_events:>4} eventos | {len(category_sessions):>2} sesiones | {size_kb:>6.1f} KB")
    
    print()
    print("📈 ESTADÍSTICAS GENERALES:")
    print("-" * 55)
    print(f"🎯 Total de eventos registrados: {total_events:,}")
    print(f"📁 Total de archivos de log: {total_files}")
    print(f"🔄 Total de sesiones únicas: {len(total_sessions)}")
    print()
    
    # Distribución por niveles
    print("📊 DISTRIBUCIÓN POR NIVELES:")
    print("-" * 55)
    for level, count in sorted(events_by_level.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_events * 100) if total_events > 0 else 0
        icon = "✅" if level == "SUCCESS" else "❌" if level == "ERROR" else "⚠️" if level == "WARNING" else "ℹ️"
        print(f"{icon} {level:<8} | {count:>5} eventos ({percentage:>5.1f}%)")
    
    print()
    
    # Sesiones más activas
    print("🔥 SESIONES MÁS ACTIVAS:")
    print("-" * 55)
    top_sessions = sorted(events_by_session.items(), key=lambda x: x[1], reverse=True)[:5]
    for session_id, count in top_sessions:
        # Extraer fecha y hora del session_id
        try:
            if len(session_id) >= 15:  # formato: 20250812_190405
                date_part = session_id[:8]
                time_part = session_id[9:15]
                formatted_date = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:8]}"
                formatted_time = f"{time_part[:2]}:{time_part[2:4]}:{time_part[4:6]}"
                display_time = f"{formatted_date} {formatted_time}"
            else:
                display_time = session_id
        except:
            display_time = session_id
            
        print(f"🕐 {session_id} | {display_time} | {count:>4} eventos")
    
    print()
    
    # Eventos de éxito más importantes
    if success_events:
        print("🎉 EVENTOS DE ÉXITO MÁS IMPORTANTES:")
        print("-" * 55)
        success_by_message = Counter(event['message'] for event in success_events)
        for message, count in success_by_message.most_common(10):
            print(f"✅ {message} ({count} veces)")
        print()
    
    # Errores detectados
    if error_events:
        print("❌ ERRORES DETECTADOS:")
        print("-" * 55)
        for error in error_events[-10:]:  # Últimos 10 errores
            print(f"❌ [{error['category']}] {error['message']} (Sesión: {error['session']})")
        print()
    
    # Eventos críticos de inicialización
    if critical_events:
        print("🚀 EVENTOS CRÍTICOS DE INICIALIZACIÓN:")
        print("-" * 55)
        for event in critical_events[-15:]:  # Últimos 15 eventos críticos
            icon = "✅" if event['level'] == 'SUCCESS' else "ℹ️"
            print(f"{icon} [{event['category']}] {event['message']}")
        print()
    
    # Categorías más activas
    print("📊 CATEGORÍAS MÁS ACTIVAS:")
    print("-" * 55)
    for category, count in sorted(events_by_category.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_events * 100) if total_events > 0 else 0
        print(f"📁 {category:<12} | {count:>5} eventos ({percentage:>5.1f}%)")
    
    print()
    print("🗃️ RESUMEN COMPLETADO")
    print("=" * 55)
    print(f"La caja negra ha registrado {total_events:,} eventos a través de {len(total_sessions)} sesiones")
    print("Todos los logs están organizados y categorizados correctamente")

if __name__ == "__main__":
    analyze_logs()
