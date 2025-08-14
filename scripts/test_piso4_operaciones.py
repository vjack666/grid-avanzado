"""
🎯 TEST PISO 4 - OPERACIONES AVANZADAS
====================================

Prueba del sistema de gestión de ciclos de 24 horas
Simulación completa del SessionManager y DailyCycleManager

AUTOR: Trading Grid System - Piso 4
FECHA: 2025-08-13
"""

from datetime import datetime, time
from typing import Dict, Any

class SimplePiso4Test:
    """
    🎯 Test simplificado del sistema Piso 4
    """
    
    def __init__(self):
        # Configuración de sesiones (GMT)
        self.session_config = {
            'ASIA': {
                'name': 'Asia Pacific',
                'start': '01:00',
                'end': '03:00',
                'max_trades': 1,
                'risk_percent': 0.7,
                'target_percent': 1.0,
                'symbols': ['USDJPY', 'AUDUSD']
            },
            'LONDON': {
                'name': 'London Session', 
                'start': '08:00',
                'end': '10:00',
                'max_trades': 2,
                'risk_percent': 1.0,
                'target_percent': 1.5,
                'symbols': ['EURUSD', 'GBPUSD']
            },
            'NEW_YORK': {
                'name': 'New York Session',
                'start': '13:30',
                'end': '15:30', 
                'max_trades': 1,
                'risk_percent': 0.8,
                'target_percent': 0.8,
                'symbols': ['EURUSD', 'USDCAD']
            }
        }
        
        # Objetivos del ciclo 24h
        self.cycle_objectives = {
            'daily_target': 3.0,      # +3% objetivo
            'daily_risk_limit': -2.0, # -2% riesgo máximo
            'max_trades': 3            # 3 trades total
        }
        
        # Estado del ciclo actual
        self.cycle_stats = {
            'total_trades': 0,
            'total_pnl_percent': 0.0,
            'trades_by_session': {
                'ASIA': [],
                'LONDON': [],
                'NEW_YORK': []
            },
            'balance': 10000.0
        }
        
        print("🎯 Sistema Piso 4 - Operaciones Avanzadas inicializado")
        print("="*60)
    
    def get_current_session_info(self) -> Dict[str, Any]:
        """🕐 Simular detección de sesión actual"""
        # Para demo, simular que estamos en London Session
        current_time = datetime.now().strftime("%H:%M")
        
        # Simular que estamos en horario de London
        london_session = self.session_config['LONDON']
        
        return {
            'current_session': 'LONDON',
            'session_name': london_session['name'],
            'current_time_gmt': current_time,
            'session_window': f"{london_session['start']} - {london_session['end']} GMT",
            'max_trades_session': london_session['max_trades'],
            'risk_allocation': london_session['risk_percent'],
            'target_allocation': london_session['target_percent']
        }
    
    def can_execute_trade(self, session: str) -> Dict[str, Any]:
        """🎯 Verificar si se puede ejecutar trade"""
        session_config = self.session_config.get(session, {})
        session_trades = len(self.cycle_stats['trades_by_session'].get(session, []))
        
        # Verificaciones
        checks = {
            'daily_trades_ok': self.cycle_stats['total_trades'] < self.cycle_objectives['max_trades'],
            'session_trades_ok': session_trades < session_config.get('max_trades', 0),
            'risk_limit_ok': self.cycle_stats['total_pnl_percent'] > self.cycle_objectives['daily_risk_limit'],
            'target_not_reached': self.cycle_stats['total_pnl_percent'] < self.cycle_objectives['daily_target']
        }
        
        can_trade = all(checks.values())
        
        return {
            'can_execute': can_trade,
            'checks': checks,
            'trades_remaining_daily': self.cycle_objectives['max_trades'] - self.cycle_stats['total_trades'],
            'trades_remaining_session': session_config.get('max_trades', 0) - session_trades,
            'risk_budget_remaining': abs(self.cycle_objectives['daily_risk_limit']) - abs(min(0, self.cycle_stats['total_pnl_percent'])),
            'target_remaining': self.cycle_objectives['daily_target'] - self.cycle_stats['total_pnl_percent']
        }
    
    def simulate_trade(self, session: str, symbol: str, pnl_percent: float) -> bool:
        """💹 Simular ejecución de trade"""
        try:
            # Registrar trade
            trade_data = {
                'timestamp': datetime.now().strftime("%H:%M:%S"),
                'session': session,
                'symbol': symbol,
                'pnl_percent': pnl_percent,
                'balance_before': self.cycle_stats['balance'],
                'balance_after': self.cycle_stats['balance'] + (pnl_percent/100 * self.cycle_stats['balance'])
            }
            
            # Actualizar estadísticas
            self.cycle_stats['trades_by_session'][session].append(trade_data)
            self.cycle_stats['total_trades'] += 1
            self.cycle_stats['total_pnl_percent'] += pnl_percent
            self.cycle_stats['balance'] = trade_data['balance_after']
            
            return True
            
        except Exception as e:
            print(f"❌ Error simulando trade: {e}")
            return False
    
    def get_cycle_summary(self) -> Dict[str, Any]:
        """📈 Resumen del ciclo actual"""
        return {
            'total_trades': self.cycle_stats['total_trades'],
            'total_pnl_percent': self.cycle_stats['total_pnl_percent'],
            'current_balance': self.cycle_stats['balance'],
            'daily_target': self.cycle_objectives['daily_target'],
            'daily_risk_limit': self.cycle_objectives['daily_risk_limit'],
            'objective_achieved': self.cycle_stats['total_pnl_percent'] >= self.cycle_objectives['daily_target'],
            'risk_breached': self.cycle_stats['total_pnl_percent'] <= self.cycle_objectives['daily_risk_limit'],
            'trades_by_session': {
                session: len(trades) for session, trades in self.cycle_stats['trades_by_session'].items()
            }
        }
    
    def run_demo_cycle(self):
        """🎯 Ejecutar demo completo del ciclo 24h"""
        print("\n🌟 DEMO CICLO 24 HORAS - PISO 4")
        print("="*50)
        
        # 1. Mostrar configuración inicial
        print("\n📋 CONFIGURACIÓN INICIAL:")
        print(f"   🎯 Objetivo diario: +{self.cycle_objectives['daily_target']:.1f}%")
        print(f"   🛡️ Riesgo máximo: {self.cycle_objectives['daily_risk_limit']:.1f}%")
        print(f"   📊 Trades máximos: {self.cycle_objectives['max_trades']}")
        print(f"   💰 Balance inicial: ${self.cycle_stats['balance']:,.2f}")
        
        # 2. Mostrar sesiones configuradas
        print("\n🕐 SESIONES CONFIGURADAS:")
        for session, config in self.session_config.items():
            print(f"   {session}: {config['start']}-{config['end']} GMT | "
                  f"Max: {config['max_trades']} trades | "
                  f"Risk: {config['risk_percent']:.1f}% | "
                  f"Target: {config['target_percent']:.1f}%")
        
        # 3. Sesión actual
        current_session = self.get_current_session_info()
        print(f"\n🕐 SESIÓN ACTUAL: {current_session['session_name']}")
        print(f"   Ventana: {current_session['session_window']}")
        print(f"   Trades permitidos: {current_session['max_trades_session']}")
        
        # 4. Simular trades por sesión
        print(f"\n💹 SIMULACIÓN DE TRADES:")
        
        # Trade 1 - Asia (ganador)
        print(f"\n🌅 TRADE ASIA:")
        asia_check = self.can_execute_trade('ASIA')
        print(f"   ✅ Permitido: {asia_check['can_execute']}")
        
        if asia_check['can_execute']:
            self.simulate_trade('ASIA', 'USDJPY', 1.1)
            print(f"   📊 USDJPY BUY: +1.1%")
        
        # Trade 2 - London (perdedor)
        print(f"\n🇬🇧 TRADE LONDON:")
        london_check = self.can_execute_trade('LONDON')
        print(f"   ✅ Permitido: {london_check['can_execute']}")
        
        if london_check['can_execute']:
            self.simulate_trade('LONDON', 'EURUSD', -0.7)
            print(f"   📊 EURUSD SELL: -0.7%")
        
        # Trade 3 - New York (ganador grande)
        print(f"\n🇺🇸 TRADE NEW YORK:")
        ny_check = self.can_execute_trade('NEW_YORK')
        print(f"   ✅ Permitido: {ny_check['can_execute']}")
        
        if ny_check['can_execute']:
            self.simulate_trade('NEW_YORK', 'GBPUSD', 2.3)
            print(f"   📊 GBPUSD BUY: +2.3%")
        
        # 5. Resumen final
        summary = self.get_cycle_summary()
        
        print(f"\n📈 RESUMEN DEL CICLO:")
        print("="*40)
        print(f"💰 Balance inicial: ${10000:,.2f}")
        print(f"💰 Balance final: ${summary['current_balance']:,.2f}")
        print(f"📊 P&L total: {summary['total_pnl_percent']:+.2f}%")
        print(f"🎯 Objetivo: {summary['daily_target']:.1f}% | ✅ Alcanzado: {summary['objective_achieved']}")
        print(f"🛡️ Límite: {summary['daily_risk_limit']:.1f}% | ⚠️ Violado: {summary['risk_breached']}")
        print(f"📊 Trades ejecutados: {summary['total_trades']}/{self.cycle_objectives['max_trades']}")
        
        print(f"\n📋 TRADES POR SESIÓN:")
        for session, count in summary['trades_by_session'].items():
            max_trades = self.session_config[session]['max_trades']
            print(f"   {session}: {count}/{max_trades} trades")
        
        # 6. Evaluación del sistema
        print(f"\n🏆 EVALUACIÓN DEL SISTEMA:")
        if summary['objective_achieved']:
            profit_usd = summary['current_balance'] - 10000
            print(f"   ✅ ÉXITO: Objetivo alcanzado (+{summary['total_pnl_percent']:.2f}% = ${profit_usd:,.2f})")
            print(f"   🎯 Distribución inteligente por sesiones funcionó")
            print(f"   🛡️ Riesgo controlado dentro de límites")
        else:
            print(f"   📊 Parcial: {summary['total_pnl_percent']:.2f}% de {summary['daily_target']:.1f}%")
        
        if not summary['risk_breached']:
            print(f"   ✅ Risk Management: Riesgo bajo control")
        else:
            print(f"   ⚠️ Risk Management: Límite excedido")
        
        print(f"\n🚀 PRÓXIMO PASO: Integración con FVG Piso 3")
        print(f"   📅 Sistema listo para gestión automática 24h")
        print("="*60)


def main():
    """Función principal de prueba"""
    # Crear y ejecutar test del sistema
    piso4_test = SimplePiso4Test()
    piso4_test.run_demo_cycle()


if __name__ == "__main__":
    main()
