"""
TEST DE VALIDACIÓN FINAL - SISTEMA COMPLETO
Para ejecutar mañana Lunes 12 Agosto 2025

Este script valida el estado completo del sistema SÓTANO 1 + SÓTANO 2
y proporciona un reporte detallado del estado de cada componente.

COMANDO A EJECUTAR:
cd C:\\Users\\v_jac\\Desktop\\grid
python test_validacion_final.py
"""

import sys
import os
import time
import subprocess
from datetime import datetime
from typing import Dict, Any
import json

# Configurar paths
sys.path.insert(0, os.getcwd())

def run_pytest_with_details():
    """Ejecutar pytest y capturar resultados detallados"""
    print("🧪 EJECUTANDO SUITE COMPLETA DE TESTS...")
    print("=" * 60)
    
    # Ejecutar pytest con output detallado
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/sotano_2/", 
        "-v", 
        "--tb=short",
        "--no-header",
        "-q"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        print("📋 RESULTADO DE TESTS:")
        print("-" * 40)
        print(result.stdout)
        
        if result.stderr:
            print("\n⚠️ WARNINGS/ERRORS:")
            print("-" * 40)
            print(result.stderr)
        
        # Analizar resultados
        output = result.stdout
        
        # Extraer estadísticas
        if "passed" in output:
            lines = output.split('\n')
            summary_line = [line for line in lines if "passed" in line and ("failed" in line or "warning" in line)]
            if summary_line:
                print(f"\n📊 RESUMEN: {summary_line[-1]}")
        
        return result.returncode == 0, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        print("❌ TIMEOUT: Tests tomaron más de 5 minutos")
        return False, "", "Timeout"
    except Exception as e:
        print(f"❌ ERROR ejecutando tests: {e}")
        return False, "", str(e)

def analyze_warnings(stderr_output: str) -> Dict[str, Any]:
    """Analizar warnings y clasificarlos"""
    warnings_analysis = {
        'total_warnings': 0,
        'pytest_return_warnings': 0,
        'deprecation_warnings': 0,
        'other_warnings': 0,
        'affected_files': [],
        'recommendations': []
    }
    
    if not stderr_output:
        return warnings_analysis
    
    lines = stderr_output.split('\n')
    
    for line in lines:
        if "PytestReturnNotNoneWarning" in line:
            warnings_analysis['pytest_return_warnings'] += 1
        elif "PytestDeprecationWarning" in line:
            warnings_analysis['deprecation_warnings'] += 1
        elif "warning" in line.lower():
            warnings_analysis['other_warnings'] += 1
        
        # Extraer archivos afectados
        if "tests/" in line and "::" in line:
            file_part = line.split("::")[0]
            if file_part not in warnings_analysis['affected_files']:
                warnings_analysis['affected_files'].append(file_part)
    
    warnings_analysis['total_warnings'] = (
        warnings_analysis['pytest_return_warnings'] + 
        warnings_analysis['deprecation_warnings'] + 
        warnings_analysis['other_warnings']
    )
    
    # Generar recomendaciones
    if warnings_analysis['pytest_return_warnings'] > 0:
        warnings_analysis['recommendations'].append(
            "Cambiar 'return True/False' por 'assert True/False' en funciones de test"
        )
    
    if warnings_analysis['deprecation_warnings'] > 0:
        warnings_analysis['recommendations'].append(
            "Configurar asyncio_default_fixture_loop_scope en pytest"
        )
    
    return warnings_analysis

def analyze_failed_tests(stdout_output: str) -> Dict[str, Any]:
    """Analizar tests fallidos y proporcionar detalles"""
    failed_analysis = {
        'failed_tests': [],
        'failure_types': {},
        'recommendations': []
    }
    
    lines = stdout_output.split('\n')
    in_failures = False
    current_failure = None
    
    for line in lines:
        if "FAILURES" in line:
            in_failures = True
            continue
        elif "short test summary info" in line:
            in_failures = False
            continue
        
        if in_failures and "::" in line and "FAILED" in line:
            # Extraer nombre del test fallido
            test_name = line.split(" ")[0] if " " in line else line
            failed_analysis['failed_tests'].append(test_name)
            current_failure = test_name
        
        # Analizar tipo de error
        if current_failure and "AssertionError" in line:
            failed_analysis['failure_types'][current_failure] = "AssertionError"
        elif current_failure and "ImportError" in line:
            failed_analysis['failure_types'][current_failure] = "ImportError"
    
    # Generar recomendaciones específicas
    for test, error_type in failed_analysis['failure_types'].items():
        if "advanced_analyzer" in test and "AssertionError" in error_type:
            failed_analysis['recommendations'].append(
                f"Test {test}: Revisar método get_analyzer_status() para incluir campo 'error' en excepción"
            )
    
    return failed_analysis

def test_individual_components():
    """Probar componentes individuales rápidamente"""
    print("\n🔧 VALIDACIÓN RÁPIDA DE COMPONENTES:")
    print("=" * 60)
    
    components_to_test = [
        ("ConfigManager", "src.config_manager", "ConfigManager"),
        ("LoggerManager", "src.logger_manager", "LoggerManager"),
        ("ErrorManager", "src.error_manager", "ErrorManager"),
        ("AnalyticsManager", "src.core.analytics_manager", "AnalyticsManager"),
        ("FundedNextMT5Manager", "src.core.fundednext_mt5_manager", "FundedNextMT5Manager"),
    ]
    
    results = {}
    
    for name, module_path, class_name in components_to_test:
        try:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            _ = cls()  # Crear instancia para validar
            results[name] = "✅ OK"
            print(f"✅ {name}: Importación y creación exitosa")
        except Exception as e:
            results[name] = f"❌ ERROR: {str(e)[:50]}..."
            print(f"❌ {name}: {str(e)[:50]}...")
    
    return results

def generate_final_report(test_success: bool, stdout: str, stderr: str, 
                         warnings_analysis: Dict, failed_analysis: Dict, 
                         component_results: Dict):
    """Generar reporte final con recomendaciones"""
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'overall_success': test_success,
        'test_summary': {
            'passed': test_success,
            'stdout_lines': len(stdout.split('\n')),
            'stderr_lines': len(stderr.split('\n'))
        },
        'warnings_analysis': warnings_analysis,
        'failed_analysis': failed_analysis,
        'component_results': component_results,
        'action_plan': []
    }
    
    # Generar plan de acción
    if not test_success:
        report['action_plan'].append("🚨 PRIORIDAD ALTA: Corregir tests fallidos")
    
    if warnings_analysis['total_warnings'] > 0:
        report['action_plan'].append(f"⚠️ PRIORIDAD MEDIA: Resolver {warnings_analysis['total_warnings']} warnings")
    
    if warnings_analysis['pytest_return_warnings'] > 0:
        report['action_plan'].extend(warnings_analysis['recommendations'])
    
    if failed_analysis['failed_tests']:
        report['action_plan'].extend(failed_analysis['recommendations'])
    
    # Imprimir reporte
    print("\n" + "="*80)
    print("📊 REPORTE FINAL DE VALIDACIÓN")
    print("="*80)
    
    print(f"🕒 Timestamp: {report['timestamp']}")
    print(f"🎯 Estado General: {'✅ EXITOSO' if test_success else '❌ REQUIERE CORRECCIONES'}")
    
    print("\n📋 RESUMEN DE COMPONENTES:")
    for name, status in component_results.items():
        print(f"   {status} {name}")
    
    print(f"\n⚠️ WARNINGS DETECTADOS: {warnings_analysis['total_warnings']}")
    if warnings_analysis['total_warnings'] > 0:
        print(f"   - PytestReturnNotNone: {warnings_analysis['pytest_return_warnings']}")
        print(f"   - Deprecation: {warnings_analysis['deprecation_warnings']}")
        print(f"   - Otros: {warnings_analysis['other_warnings']}")
        print(f"   - Archivos afectados: {len(warnings_analysis['affected_files'])}")
    
    print(f"\n❌ TESTS FALLIDOS: {len(failed_analysis['failed_tests'])}")
    if failed_analysis['failed_tests']:
        for test in failed_analysis['failed_tests']:
            error_type = failed_analysis['failure_types'].get(test, "Unknown")
            print(f"   - {test}: {error_type}")
    
    print(f"\n📋 PLAN DE ACCIÓN PARA MAÑANA:")
    for i, action in enumerate(report['action_plan'], 1):
        print(f"   {i}. {action}")
    
    if not report['action_plan']:
        print("   🎉 ¡NO SE REQUIEREN ACCIONES! Sistema al 100%")
    
    # Guardar reporte en archivo
    try:
        with open('validation_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n💾 Reporte guardado en: validation_report.json")
    except Exception as e:
        print(f"\n⚠️ No se pudo guardar reporte: {e}")
    
    return report

def main():
    """Función principal de validación"""
    print("🚀 INICIANDO VALIDACIÓN FINAL DEL SISTEMA")
    print("📅 Preparación para trabajo del Lunes 12 Agosto 2025")
    print("="*80)
    
    start_time = time.time()
    
    # 1. Ejecutar suite completa de tests
    test_success, stdout, stderr = run_pytest_with_details()
    
    # 2. Analizar warnings
    warnings_analysis = analyze_warnings(stderr)
    
    # 3. Analizar tests fallidos
    failed_analysis = analyze_failed_tests(stdout)
    
    # 4. Probar componentes individuales
    component_results = test_individual_components()
    
    # 5. Generar reporte final
    report = generate_final_report(
        test_success, stdout, stderr, 
        warnings_analysis, failed_analysis, 
        component_results
    )
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n⏰ Validación completada en {duration:.1f} segundos")
    print("="*80)
    
    # Mensaje final para mañana
    if test_success and warnings_analysis['total_warnings'] == 0:
        print("🎉 ¡PERFECTO! Sistema listo para SÓTANO 3")
    elif test_success:
        print("✅ Tests OK, pero revisar warnings para código limpio")
    else:
        print("🔧 Requiere correcciones - seguir plan de acción")
    
    return report

if __name__ == "__main__":
    try:
        report = main()
        # Exit code basado en resultados
        exit_code = 0 if report['overall_success'] and report['warnings_analysis']['total_warnings'] == 0 else 1
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️ Validación cancelada por usuario")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        sys.exit(1)
