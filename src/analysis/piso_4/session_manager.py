"""
📅 SESSION MANAGER - PISO 4 OPERACIONES AVANZADAS
================================================

Gestor inteligente de sesiones de mercado para trading optimizado
Divide el día en ventanas estratégicas con objetivos específicos

SESIONES CONFIGURADAS:
- 🌅 ASIA: 01:00-03:00 GMT (1 trade, 0.7% risk, 1.0% target)
- 🇬🇧 LONDON: 08:00-10:00 GMT (2 trades, 1.0% risk, 1.5% target)  
- 🇺🇸 NEW_YORK: 13:30-15:30 GMT (1 trade, 0.8% risk, 0.8% target)

AUTOR: Trading Grid System - Piso 4
VERSIÓN: 1.0
FECHA: 2025-08-13
"""

import sys
from pathlib import Path
from datetime import datetime, time, timedelta
from typing import Dict, Optional, Any
from enum import Enum
import pytz

# Configurar imports del proyecto usando la central
import sys
from pathlib import Path
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent
sys.path.insert(0, str(project_root.absolute()))

# Usar central de imports
from src import LoggerManager

class TradingSession(Enum):
    """Sesiones de trading disponibles"""
    ASIA = "ASIA"
    LONDON = "LONDON" 
    NEW_YORK = "NEW_YORK"
    INACTIVE = "INACTIVE"

class SessionStatus(Enum):
    """Estados de una sesión"""
    PENDING = "PENDING"           # Esperando inicio
    ACTIVE = "ACTIVE"             # En progreso
    COMPLETED = "COMPLETED"       # Objetivos cumplidos
    FAILED = "FAILED"             # Riesgo máximo alcanzado
    EXPIRED = "EXPIRED"           # Tiempo agotado

class SessionManager:
    """
    📅 GESTOR DE SESIONES DE TRADING
    
    Funcionalidades:
    - Detección automática de sesión activa
    - Configuración específica por sesión
    - Tracking de objetivos y riesgo
    - Ventanas óptimas de trading
    - Estado del ciclo 24h
    """
    
    def __init__(self):
        self.logger = LoggerManager().get_logger('session_manager')
        
        # Configuración de sesiones
        self.session_config = {
            TradingSession.ASIA: {
                'name': 'Asia Pacific',
                'start_hour': 1,        # 01:00 GMT
                'start_minute': 0,
                'end_hour': 3,          # 03:00 GMT  
                'end_minute': 0,
                'max_trades': 1,
                'risk_percent': 0.7,    # % de cuenta máximo por sesión
                'target_return': 1.0,   # % objetivo de ganancia
                'min_quality_score': 7.5,
                'preferred_symbols': ['USDJPY', 'AUDUSD', 'EURJPY', 'NZDUSD'],
                'volatility_type': 'MODERATE',
                'characteristics': 'Tendencias claras, menos ruido'
            },
            TradingSession.LONDON: {
                'name': 'London Session',
                'start_hour': 8,        # 08:00 GMT
                'start_minute': 0,
                'end_hour': 10,         # 10:00 GMT
                'end_minute': 0,
                'max_trades': 2,        # Sesión principal
                'risk_percent': 1.0,
                'target_return': 1.5,
                'min_quality_score': 7.0,
                'preferred_symbols': ['EURUSD', 'GBPUSD', 'EURGBP', 'EURJPY'],
                'volatility_type': 'HIGH',
                'characteristics': 'Mayor volatilidad, FVGs de calidad'
            },
            TradingSession.NEW_YORK: {
                'name': 'New York Session',
                'start_hour': 13,       # 13:30 GMT
                'start_minute': 30,
                'end_hour': 15,         # 15:30 GMT
                'end_minute': 30,
                'max_trades': 1,
                'risk_percent': 0.8,
                'target_return': 0.8,
                'min_quality_score': 7.5,
                'preferred_symbols': ['EURUSD', 'GBPUSD', 'USDCAD', 'USDCHF'],
                'volatility_type': 'HIGH',
                'characteristics': 'Momentum fuerte, confirmaciones'
            }
        }
        
        # Estado actual del sistema
        self.current_session = TradingSession.INACTIVE
        self.session_status = SessionStatus.PENDING
        self.session_start_time = None
        self.daily_cycle_start = None
        
        # Tracking por sesión (reset cada 24h)
        self.session_stats = {
            TradingSession.ASIA: {
                'trades_executed': 0,
                'current_pnl': 0.0,
                'status': SessionStatus.PENDING,
                'start_time': None,
                'end_time': None,
                'trades': []
            },
            TradingSession.LONDON: {
                'trades_executed': 0,
                'current_pnl': 0.0,
                'status': SessionStatus.PENDING,
                'start_time': None,
                'end_time': None,
                'trades': []
            },
            TradingSession.NEW_YORK: {
                'trades_executed': 0,
                'current_pnl': 0.0,
                'status': SessionStatus.PENDING,
                'start_time': None,
                'end_time': None,
                'trades': []
            }
        }
        
        # Configurar timezone GMT
        self.gmt_tz = pytz.timezone('GMT')
        
        self.logger.info("📅 SessionManager inicializado - Configuradas 3 sesiones de trading")
    
    def get_current_session(self) -> TradingSession:
        """
        🕐 Detectar sesión de trading actual basada en hora GMT
        
        Returns:
            TradingSession: Sesión activa o INACTIVE
        """
        try:
            # Obtener hora actual en GMT
            now_utc = datetime.now(pytz.UTC)
            now_gmt = now_utc.astimezone(self.gmt_tz)
            current_time = now_gmt.time()
            
            # Verificar cada sesión
            for session, config in self.session_config.items():
                start_time = time(config['start_hour'], config['start_minute'])
                end_time = time(config['end_hour'], config['end_minute'])
                
                if start_time <= current_time <= end_time:
                    if self.current_session != session:
                        self._on_session_change(session)
                    return session
            
            # Si no está en ninguna sesión, marcar como INACTIVE
            if self.current_session != TradingSession.INACTIVE:
                self._on_session_change(TradingSession.INACTIVE)
            
            return TradingSession.INACTIVE
            
        except Exception as e:
            self.logger.error("❌ Error detectando sesión actual: %s", e)
            return TradingSession.INACTIVE
    
    def _on_session_change(self, new_session: TradingSession):
        """🔄 Manejar cambio de sesión"""
        try:
            old_session = self.current_session
            self.current_session = new_session
            
            if new_session != TradingSession.INACTIVE:
                # Iniciar nueva sesión
                self.session_start_time = datetime.now()
                self.session_stats[new_session]['start_time'] = self.session_start_time
                self.session_stats[new_session]['status'] = SessionStatus.ACTIVE
                
                self.logger.info("🌟 NUEVA SESIÓN INICIADA: %s (%s)", 
                               new_session.value, 
                               self.session_config[new_session]['name'])
                self.logger.info("   Trades permitidos: %d", 
                               self.session_config[new_session]['max_trades'])
                self.logger.info("   Riesgo máximo: %.1f%%", 
                               self.session_config[new_session]['risk_percent'])
                self.logger.info("   Objetivo: %.1f%%", 
                               self.session_config[new_session]['target_return'])
            else:
                # Finalizar sesión anterior
                if old_session != TradingSession.INACTIVE:
                    self._finalize_session(old_session)
                
                self.logger.info("⏸️ Fuera de horario de trading - Esperando próxima sesión")
        
        except Exception as e:
            self.logger.error("❌ Error en cambio de sesión: %s", e)
    
    def _finalize_session(self, session: TradingSession):
        """🏁 Finalizar sesión y calcular resultados"""
        try:
            session_data = self.session_stats[session]
            session_data['end_time'] = datetime.now()
            
            # Determinar estado final
            if session_data['status'] == SessionStatus.ACTIVE:
                if session_data['trades_executed'] > 0:
                    session_data['status'] = SessionStatus.COMPLETED
                else:
                    session_data['status'] = SessionStatus.EXPIRED
            
            self.logger.info("🏁 SESIÓN FINALIZADA: %s", session.value)
            self.logger.info("   Trades ejecutados: %d/%d", 
                           session_data['trades_executed'],
                           self.session_config[session]['max_trades'])
            self.logger.info("   P&L sesión: %.2f%%", session_data['current_pnl'])
            self.logger.info("   Estado: %s", session_data['status'].value)
            
        except Exception as e:
            self.logger.error("❌ Error finalizando sesión: %s", e)
    
    def can_trade_in_session(self, session: Optional[TradingSession] = None) -> Dict[str, Any]:
        """
        🎯 Verificar si se puede ejecutar trade en sesión actual
        
        Args:
            session: Sesión específica o None para actual
            
        Returns:
            dict: Estado de trading permitido
        """
        try:
            target_session = session or self.get_current_session()
            
            result = {
                'can_trade': False,
                'session': target_session.value,
                'reason': '',
                'trades_remaining': 0,
                'risk_remaining': 0.0,
                'session_config': {}
            }
            
            # Verificar si sesión está activa
            if target_session == TradingSession.INACTIVE:
                result['reason'] = 'Fuera de horario de trading'
                return result
            
            session_config = self.session_config[target_session]
            session_stats = self.session_stats[target_session]
            
            result['session_config'] = session_config.copy()
            
            # Verificar límite de trades
            trades_remaining = session_config['max_trades'] - session_stats['trades_executed']
            if trades_remaining <= 0:
                result['reason'] = f'Límite de trades alcanzado ({session_stats["trades_executed"]}/{session_config["max_trades"]})'
                return result
            
            result['trades_remaining'] = trades_remaining
            
            # Verificar riesgo acumulado
            risk_used = abs(min(0, session_stats['current_pnl']))  # Solo pérdidas
            risk_remaining = session_config['risk_percent'] - risk_used
            
            if risk_remaining <= 0.1:  # Margen de seguridad 0.1%
                result['reason'] = f'Riesgo máximo alcanzado ({risk_used:.1f}%/{session_config["risk_percent"]:.1f}%)'
                session_stats['status'] = SessionStatus.FAILED
                return result
            
            result['risk_remaining'] = risk_remaining
            
            # Verificar estado de sesión
            if session_stats['status'] not in [SessionStatus.ACTIVE, SessionStatus.PENDING]:
                result['reason'] = f'Sesión en estado: {session_stats["status"].value}'
                return result
            
            # Todo OK - se puede hacer trade
            result['can_trade'] = True
            result['reason'] = f'Sesión {target_session.value} activa - {trades_remaining} trades disponibles'
            
            return result
            
        except Exception as e:
            self.logger.error("❌ Error verificando trading en sesión: %s", e)
            return {
                'can_trade': False,
                'reason': f'Error: {e}',
                'session': 'ERROR'
            }
    
    def get_session_config(self, session: Optional[TradingSession] = None) -> Dict[str, Any]:
        """
        📋 Obtener configuración de sesión específica
        
        Args:
            session: Sesión específica o None para actual
            
        Returns:
            dict: Configuración de la sesión
        """
        target_session = session or self.get_current_session()
        
        if target_session == TradingSession.INACTIVE:
            return {}
        
        return self.session_config[target_session].copy()
    
    def record_trade(self, session: Optional[TradingSession], trade_data: Dict[str, Any]) -> bool:
        """
        📊 Registrar trade ejecutado en sesión
        
        Args:
            session: Sesión donde se ejecutó el trade
            trade_data: Datos del trade ejecutado
            
        Returns:
            bool: True si se registró correctamente
        """
        try:
            target_session = session or self.get_current_session()
            
            if target_session == TradingSession.INACTIVE:
                self.logger.warning("⚠️ Intento de registrar trade fuera de sesión")
                return False
            
            session_stats = self.session_stats[target_session]
            
            # Actualizar contadores
            session_stats['trades_executed'] += 1
            
            # Actualizar P&L
            trade_pnl = trade_data.get('pnl_percent', 0.0)
            session_stats['current_pnl'] += trade_pnl
            
            # Registrar trade
            trade_record = {
                'timestamp': datetime.now(),
                'symbol': trade_data.get('symbol', ''),
                'direction': trade_data.get('direction', ''),
                'lot_size': trade_data.get('lot_size', 0),
                'pnl_percent': trade_pnl,
                'quality_score': trade_data.get('quality_score', 0),
                'reason': trade_data.get('reason', '')
            }
            
            session_stats['trades'].append(trade_record)
            
            self.logger.info("📊 Trade registrado en %s: %.2f%% P&L", 
                           target_session.value, trade_pnl)
            
            # Verificar si se cumplió objetivo
            session_config = self.session_config[target_session]
            if session_stats['current_pnl'] >= session_config['target_return']:
                session_stats['status'] = SessionStatus.COMPLETED
                self.logger.info("🎯 OBJETIVO SESIÓN ALCANZADO: %s (%.2f%%)", 
                               target_session.value, session_stats['current_pnl'])
            
            return True
            
        except Exception as e:
            self.logger.error("❌ Error registrando trade: %s", e)
            return False
    
    def get_daily_summary(self) -> Dict[str, Any]:
        """
        📈 Obtener resumen completo del ciclo 24h
        
        Returns:
            dict: Estadísticas del día
        """
        try:
            summary = {
                'cycle_date': datetime.now().date(),
                'total_trades': 0,
                'total_pnl': 0.0,
                'sessions': {},
                'daily_objective': 3.0,  # 3% objetivo diario
                'daily_risk_limit': -2.0,  # -2% riesgo máximo
                'objective_achieved': False,
                'risk_exceeded': False
            }
            
            # Consolidar estadísticas por sesión
            for session, stats in self.session_stats.items():
                summary['sessions'][session.value] = {
                    'trades': stats['trades_executed'],
                    'pnl': stats['current_pnl'],
                    'status': stats['status'].value,
                    'config': self.session_config[session]
                }
                
                summary['total_trades'] += stats['trades_executed']
                summary['total_pnl'] += stats['current_pnl']
            
            # Verificar objetivos
            summary['objective_achieved'] = summary['total_pnl'] >= summary['daily_objective']
            summary['risk_exceeded'] = summary['total_pnl'] <= summary['daily_risk_limit']
            
            return summary
            
        except Exception as e:
            self.logger.error("❌ Error generando resumen diario: %s", e)
            return {}
    
    def reset_daily_cycle(self):
        """🔄 Reiniciar ciclo de 24 horas"""
        try:
            self.logger.info("🔄 Reiniciando ciclo diario de 24 horas")
            
            # Reset estadísticas de sesiones
            for session in self.session_stats.keys():
                self.session_stats[session] = {
                    'trades_executed': 0,
                    'current_pnl': 0.0,
                    'status': SessionStatus.PENDING,
                    'start_time': None,
                    'end_time': None,
                    'trades': []
                }
            
            self.daily_cycle_start = datetime.now()
            self.current_session = TradingSession.INACTIVE
            self.session_status = SessionStatus.PENDING
            
            self.logger.info("✅ Nuevo ciclo 24h iniciado")
            
        except Exception as e:
            self.logger.error("❌ Error reiniciando ciclo diario: %s", e)
    
    def get_next_session_info(self) -> Dict[str, Any]:
        """
        ⏰ Información sobre la próxima sesión de trading
        
        Returns:
            dict: Datos de la próxima sesión
        """
        try:
            now_utc = datetime.now(pytz.UTC)
            now_gmt = now_utc.astimezone(self.gmt_tz)
            current_time = now_gmt.time()
            
            # Lista de sesiones en orden cronológico
            sessions_order = [
                (TradingSession.ASIA, self.session_config[TradingSession.ASIA]),
                (TradingSession.LONDON, self.session_config[TradingSession.LONDON]),
                (TradingSession.NEW_YORK, self.session_config[TradingSession.NEW_YORK])
            ]
            
            # Buscar próxima sesión
            for session, config in sessions_order:
                session_start = time(config['start_hour'], config['start_minute'])
                
                if current_time < session_start:
                    # Calcular tiempo restante
                    today = now_gmt.date()
                    session_datetime = datetime.combine(today, session_start)
                    session_datetime = self.gmt_tz.localize(session_datetime)
                    
                    time_remaining = session_datetime - now_gmt
                    
                    return {
                        'next_session': session.value,
                        'session_name': config['name'],
                        'start_time_gmt': session_start.strftime('%H:%M'),
                        'time_remaining': str(time_remaining).split('.')[0],
                        'max_trades': config['max_trades'],
                        'target_return': config['target_return']
                    }
            
            # Si pasaron todas las sesiones de hoy, la próxima es Asia del día siguiente
            next_asia = TradingSession.ASIA
            next_config = self.session_config[next_asia]
            tomorrow = now_gmt.date() + timedelta(days=1)
            session_start = time(next_config['start_hour'], next_config['start_minute'])
            session_datetime = datetime.combine(tomorrow, session_start)
            session_datetime = self.gmt_tz.localize(session_datetime)
            
            time_remaining = session_datetime - now_gmt
            
            return {
                'next_session': next_asia.value,
                'session_name': next_config['name'],
                'start_time_gmt': session_start.strftime('%H:%M'),
                'time_remaining': str(time_remaining).split('.')[0],
                'max_trades': next_config['max_trades'],
                'target_return': next_config['target_return'],
                'next_day': True
            }
            
        except Exception as e:
            self.logger.error("❌ Error obteniendo próxima sesión: %s", e)
            return {}


def main():
    """Función de prueba del SessionManager"""
    print("📅 Testing SessionManager - Piso 4")
    print("=" * 50)
    
    # Crear manager
    session_manager = SessionManager()
    
    # Obtener sesión actual
    current_session = session_manager.get_current_session()
    print(f"🕐 Sesión actual: {current_session.value}")
    
    # Verificar si se puede hacer trading
    trade_check = session_manager.can_trade_in_session()
    print(f"💹 ¿Puede hacer trading?: {trade_check['can_trade']}")
    print(f"📝 Razón: {trade_check['reason']}")
    
    if trade_check['can_trade']:
        print(f"📊 Trades restantes: {trade_check['trades_remaining']}")
        print(f"🛡️ Riesgo restante: {trade_check['risk_remaining']:.1f}%")
    
    # Información de próxima sesión
    next_session = session_manager.get_next_session_info()
    if next_session:
        print(f"\n⏰ Próxima sesión: {next_session['next_session']}")
        print(f"🕐 Inicio: {next_session['start_time_gmt']} GMT")
        print(f"⏱️ Tiempo restante: {next_session['time_remaining']}")
    
    # Resumen diario
    daily_summary = session_manager.get_daily_summary()
    print(f"\n📈 Resumen del día:")
    print(f"💰 P&L total: {daily_summary['total_pnl']:.2f}%")
    print(f"📊 Trades totales: {daily_summary['total_trades']}")
    print(f"🎯 Objetivo diario: {daily_summary['daily_objective']:.1f}%")


if __name__ == "__main__":
    main()
