"""
🔮 SÓTANO 3 - STRATEGIC AI
=========================

El nivel superior del sistema Trading Grid que implementa tu visión del
"enlace estrategia-bases", conectando los fundamentos sólidos del SÓTANO 1
con inteligencia estratégica avanzada.

✨ VISIÓN: "Enlace Estrategia-Bases"
🎯 PROPÓSITO: Inteligencia Estratégica y Decisional
🧠 CAPACIDADES: IA, Machine Learning, Decisiones Estratégicas

Componentes principales:
- FoundationBridge: Tu "enlace estrategia-bases"
- StrategyCoordinator: Coordinación estratégica
- DecisionEngine: Motor de decisiones inteligente
- MachineLearningCore: Aprendizaje continuo

Estado: IMPLEMENTATION IN PROGRESS
Fecha: Agosto 12, 2025
"""

# Componentes implementados
from .foundation_bridge import FoundationBridge, StrategicContext, FoundationData
from .strategic_config import (
    StrategicConfiguration, 
    StrategicThresholds, 
    AnalysisWeights, 
    OperationalSettings,
    get_strategic_config,
    reload_strategic_config
)

# Componentes por implementar
# from .strategy_coordinator import StrategyCoordinator  
# from .decision_engine import DecisionEngine
# from .machine_learning_core import MachineLearningCore

__version__ = "3.0.0"
__status__ = "IMPLEMENTATION_IN_PROGRESS"

# Metadatos del SÓTANO 3
SOTANO_3_INFO = {
    'name': 'Strategic AI',
    'version': '3.0.0',
    'vision': 'Enlace Estrategia-Bases',
    'description': 'Inteligencia estratégica que conecta fundamentos con decisiones',
    'components': ['foundationbridge', 'strategycoordinator', 'decisionengine', 'machinelearningcore'],
    'status': 'IMPLEMENTATION_IN_PROGRESS',
    'integration_level': 'SOTANO_1_2_3',
    'author': 'Trading Grid System',
    'date': '2025-08-12',
    'integration_ready': True,
    'sotano_1_compatible': True,
    'sotano_2_compatible': True,
    'no_hardcoding': True,
    'centralized_config': True
}

__all__ = [
    'SOTANO_3_INFO',
    'FoundationBridge',
    'StrategicContext', 
    'FoundationData',
    'StrategicConfiguration',
    'StrategicThresholds',
    'AnalysisWeights',
    'OperationalSettings',
    'get_strategic_config',
    'reload_strategic_config'
]
