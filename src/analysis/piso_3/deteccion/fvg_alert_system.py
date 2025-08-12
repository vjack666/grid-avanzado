"""
🚨 SISTEMA DE ALERTAS FVG
Sistema de alertas inteligente en tiempo real

Fecha: Agosto 12, 2025
Oficina: Alertas - Piso 3
Estado: Sistema de Notificaciones
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class AlertPriority(Enum):
    """Prioridades de alertas"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AlertType(Enum):
    """Tipos de alertas"""
    NEW_FVG = "NEW_FVG"
    CONFLUENCE = "CONFLUENCE"
    LARGE_FVG = "LARGE_FVG"
    MARKET_BIAS = "MARKET_BIAS"
    SESSION_CONCENTRATION = "SESSION_CONCENTRATION"
    FVG_FILLED = "FVG_FILLED"
    SYSTEM_ERROR = "SYSTEM_ERROR"

@dataclass
class Alert:
    """Estructura de una alerta"""
    id: str
    type: AlertType
    priority: AlertPriority
    title: str
    message: str
    timestamp: datetime
    symbol: str
    timeframe: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    sent: bool = False
    acknowledged: bool = False
    
    def to_dict(self) -> Dict:
        """Convierte alerta a diccionario"""
        return {
            'id': self.id,
            'type': self.type.value,
            'priority': self.priority.value,
            'title': self.title,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'data': self.data,
            'sent': self.sent,
            'acknowledged': self.acknowledged
        }

class AlertChannel:
    """Canal base para envío de alertas"""
    
    def __init__(self, name: str, enabled: bool = True):
        self.name = name
        self.enabled = enabled
    
    async def send_alert(self, alert: Alert) -> bool:
        """Envía una alerta (implementar en subclases)"""
        raise NotImplementedError

class ConsoleAlertChannel(AlertChannel):
    """Canal de alertas por consola"""
    
    def __init__(self, colored: bool = True):
        super().__init__("Console", enabled=True)
        self.colored = colored
        self.priority_colors = {
            AlertPriority.LOW: '\033[92m',      # Verde
            AlertPriority.MEDIUM: '\033[93m',   # Amarillo
            AlertPriority.HIGH: '\033[91m',     # Rojo
            AlertPriority.CRITICAL: '\033[95m'  # Magenta
        }
        self.reset_color = '\033[0m'
    
    async def send_alert(self, alert: Alert) -> bool:
        """Envía alerta a consola"""
        try:
            if self.colored:
                color = self.priority_colors.get(alert.priority, '')
                reset = self.reset_color
            else:
                color = reset = ''
            
            # Icono por tipo
            icons = {
                AlertType.NEW_FVG: "🎯",
                AlertType.CONFLUENCE: "🔗",
                AlertType.LARGE_FVG: "📈",
                AlertType.MARKET_BIAS: "📊",
                AlertType.SESSION_CONCENTRATION: "🕒",
                AlertType.FVG_FILLED: "✅",
                AlertType.SYSTEM_ERROR: "❌"
            }
            
            icon = icons.get(alert.type, "🔔")
            timestamp = alert.timestamp.strftime('%H:%M:%S')
            
            print(f"{color}{icon} [{alert.priority.value}] {timestamp} - {alert.title}{reset}")
            print(f"{color}   {alert.message}{reset}")
            
            if alert.timeframe:
                print(f"   📊 {alert.symbol} {alert.timeframe}")
            
            if alert.data:
                key_data = []
                if 'gap_size_pips' in alert.data:
                    key_data.append(f"Gap: {alert.data['gap_size_pips']:.1f} pips")
                if 'confluence_strength' in alert.data:
                    key_data.append(f"Fuerza: {alert.data['confluence_strength']:.1f}")
                if key_data:
                    print(f"   📋 {' | '.join(key_data)}")
            
            print()  # Línea en blanco
            return True
            
        except Exception as e:
            logger.error(f"Error enviando alerta por consola: {e}")
            return False

class FileAlertChannel(AlertChannel):
    """Canal de alertas por archivo"""
    
    def __init__(self, file_path: str, max_file_size: int = 10_000_000):  # 10MB
        super().__init__("File", enabled=True)
        self.file_path = file_path
        self.max_file_size = max_file_size
    
    async def send_alert(self, alert: Alert) -> bool:
        """Envía alerta a archivo"""
        try:
            # Rotar archivo si es muy grande
            self._rotate_if_needed()
            
            alert_json = json.dumps(alert.to_dict(), indent=2)
            
            with open(self.file_path, 'a', encoding='utf-8') as f:
                f.write(f"{alert_json}\n")
                f.write("-" * 50 + "\n")
            
            return True
            
        except Exception as e:
            logger.error(f"Error enviando alerta a archivo: {e}")
            return False
    
    def _rotate_if_needed(self):
        """Rota el archivo si excede el tamaño máximo"""
        try:
            import os
            if os.path.exists(self.file_path) and os.path.getsize(self.file_path) > self.max_file_size:
                backup_path = f"{self.file_path}.backup"
                os.rename(self.file_path, backup_path)
        except Exception as e:
            logger.warning(f"Error rotando archivo de alertas: {e}")

class WebhookAlertChannel(AlertChannel):
    """Canal de alertas por webhook (Discord, Slack, etc.)"""
    
    def __init__(self, webhook_url: str, platform: str = "discord"):
        super().__init__(f"Webhook-{platform}", enabled=True)
        self.webhook_url = webhook_url
        self.platform = platform.lower()
    
    async def send_alert(self, alert: Alert) -> bool:
        """Envía alerta por webhook"""
        try:
            import aiohttp
            
            if self.platform == "discord":
                payload = self._format_discord_message(alert)
            elif self.platform == "slack":
                payload = self._format_slack_message(alert)
            else:
                payload = self._format_generic_message(alert)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    return response.status == 200
                    
        except Exception as e:
            logger.error(f"Error enviando webhook: {e}")
            return False
    
    def _format_discord_message(self, alert: Alert) -> Dict:
        """Formatea mensaje para Discord"""
        color_map = {
            AlertPriority.LOW: 0x00ff00,      # Verde
            AlertPriority.MEDIUM: 0xffff00,   # Amarillo
            AlertPriority.HIGH: 0xff0000,     # Rojo
            AlertPriority.CRITICAL: 0xff00ff  # Magenta
        }
        
        embed = {
            "embeds": [{
                "title": f"🚨 {alert.title}",
                "description": alert.message,
                "color": color_map.get(alert.priority, 0x808080),
                "timestamp": alert.timestamp.isoformat(),
                "fields": [
                    {"name": "Símbolo", "value": alert.symbol, "inline": True},
                    {"name": "Prioridad", "value": alert.priority.value, "inline": True}
                ]
            }]
        }
        
        if alert.timeframe:
            embed["embeds"][0]["fields"].append({
                "name": "Timeframe", "value": alert.timeframe, "inline": True
            })
        
        return embed

class FVGAlertSystem:
    """
    🚨 SISTEMA DE ALERTAS FVG COMPLETO
    
    Características:
    - Múltiples canales de notificación
    - Filtrado inteligente de alertas
    - Throttling para evitar spam
    - Historial de alertas
    - Configuración flexible
    """
    
    def __init__(self, config: Dict = None):
        """
        Inicializa el sistema de alertas
        
        Args:
            config: Configuración del sistema
        """
        default_config = {
            'max_alerts_per_minute': 10,
            'duplicate_suppression_minutes': 5,
            'min_priority': AlertPriority.LOW,
            'enabled_types': [t.value for t in AlertType],
            'throttling_enabled': True,
            'history_max_size': 1000
        }
        
        self.config = {**default_config, **(config or {})}
        
        # Canales de alerta
        self.channels: List[AlertChannel] = []
        
        # Historial y throttling
        self.alert_history = deque(maxlen=self.config['history_max_size'])
        self.sent_alerts = deque(maxlen=100)  # Para throttling
        self.last_alerts = {}  # Para supresión de duplicados
        
        # Métricas
        self.metrics = {
            'total_alerts': 0,
            'sent_alerts': 0,
            'suppressed_alerts': 0,
            'failed_sends': 0,
            'alerts_by_type': {t.value: 0 for t in AlertType},
            'alerts_by_priority': {p.value: 0 for p in AlertPriority}
        }
        
        # Configurar canales por defecto
        self._setup_default_channels()
        
        logger.info("Sistema de alertas FVG inicializado")
    
    def _setup_default_channels(self):
        """Configura canales por defecto"""
        # Canal de consola siempre activo
        console_channel = ConsoleAlertChannel(colored=True)
        self.add_channel(console_channel)
        
        # Canal de archivo
        from pathlib import Path
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        file_channel = FileAlertChannel(str(log_dir / "fvg_alerts.log"))
        self.add_channel(file_channel)
    
    def add_channel(self, channel: AlertChannel):
        """Agrega un canal de alertas"""
        self.channels.append(channel)
        logger.info(f"Canal agregado: {channel.name}")
    
    def remove_channel(self, channel_name: str):
        """Remueve un canal por nombre"""
        self.channels = [c for c in self.channels if c.name != channel_name]
        logger.info(f"Canal removido: {channel_name}")
    
    async def send_alert(self, 
                        alert_type: AlertType,
                        title: str,
                        message: str,
                        symbol: str,
                        priority: AlertPriority = AlertPriority.MEDIUM,
                        timeframe: Optional[str] = None,
                        data: Dict[str, Any] = None) -> str:
        """
        Envía una alerta
        
        Args:
            alert_type: Tipo de alerta
            title: Título de la alerta
            message: Mensaje descriptivo
            symbol: Símbolo relacionado
            priority: Prioridad de la alerta
            timeframe: Timeframe opcional
            data: Datos adicionales
            
        Returns:
            ID de la alerta enviada
        """
        # Crear alerta
        alert_id = self._generate_alert_id()
        alert = Alert(
            id=alert_id,
            type=alert_type,
            priority=priority,
            title=title,
            message=message,
            timestamp=datetime.now(),
            symbol=symbol,
            timeframe=timeframe,
            data=data or {}
        )
        
        # Actualizar métricas
        self.metrics['total_alerts'] += 1
        self.metrics['alerts_by_type'][alert_type.value] += 1
        self.metrics['alerts_by_priority'][priority.value] += 1
        
        # Verificar filtros
        if not self._should_send_alert(alert):
            self.metrics['suppressed_alerts'] += 1
            logger.debug(f"Alerta suprimida: {alert_id}")
            return alert_id
        
        # Enviar por todos los canales
        send_results = []
        for channel in self.channels:
            if channel.enabled:
                try:
                    success = await channel.send_alert(alert)
                    send_results.append(success)
                    if success:
                        alert.sent = True
                except Exception as e:
                    logger.error(f"Error enviando alerta por {channel.name}: {e}")
                    send_results.append(False)
        
        # Actualizar métricas
        if any(send_results):
            self.metrics['sent_alerts'] += 1
            self.sent_alerts.append(alert.timestamp)
        else:
            self.metrics['failed_sends'] += 1
        
        # Agregar al historial
        self.alert_history.append(alert)
        
        # Actualizar last_alerts para supresión de duplicados
        alert_key = f"{alert_type.value}_{symbol}_{timeframe or 'ALL'}"
        self.last_alerts[alert_key] = alert.timestamp
        
        return alert_id
    
    def _should_send_alert(self, alert: Alert) -> bool:
        """Verifica si se debe enviar la alerta"""
        # Verificar prioridad mínima
        priority_levels = {
            AlertPriority.LOW: 1,
            AlertPriority.MEDIUM: 2,
            AlertPriority.HIGH: 3,
            AlertPriority.CRITICAL: 4
        }
        
        min_level = priority_levels[self.config['min_priority']]
        alert_level = priority_levels[alert.priority]
        
        if alert_level < min_level:
            return False
        
        # Verificar tipo habilitado
        if alert.type.value not in self.config['enabled_types']:
            return False
        
        # Verificar throttling
        if self.config['throttling_enabled']:
            if not self._check_throttling():
                return False
        
        # Verificar supresión de duplicados
        if self._is_duplicate_alert(alert):
            return False
        
        return True
    
    def _check_throttling(self) -> bool:
        """Verifica límites de throttling"""
        now = datetime.now()
        one_minute_ago = now - timedelta(minutes=1)
        
        # Contar alertas en el último minuto
        recent_alerts = [t for t in self.sent_alerts if t > one_minute_ago]
        
        return len(recent_alerts) < self.config['max_alerts_per_minute']
    
    def _is_duplicate_alert(self, alert: Alert) -> bool:
        """Verifica si es una alerta duplicada"""
        alert_key = f"{alert.type.value}_{alert.symbol}_{alert.timeframe or 'ALL'}"
        
        if alert_key in self.last_alerts:
            last_time = self.last_alerts[alert_key]
            time_diff = (alert.timestamp - last_time).total_seconds() / 60
            
            return time_diff < self.config['duplicate_suppression_minutes']
        
        return False
    
    def _generate_alert_id(self) -> str:
        """Genera ID único para alerta"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        import random
        rand_suffix = random.randint(1000, 9999)
        return f"ALERT_{timestamp}_{rand_suffix}"
    
    async def send_fvg_alert(self, fvg_data: Dict, symbol: str, timeframe: str):
        """Alerta específica para nuevo FVG"""
        gap_pips = fvg_data.get('gap_size', 0) * 10000
        fvg_type = fvg_data.get('type', 'UNKNOWN')
        
        # Determinar prioridad por tamaño
        if gap_pips >= 10:
            priority = AlertPriority.HIGH
        elif gap_pips >= 5:
            priority = AlertPriority.MEDIUM
        else:
            priority = AlertPriority.LOW
        
        await self.send_alert(
            alert_type=AlertType.NEW_FVG,
            title=f"Nuevo FVG {fvg_type}",
            message=f"FVG {fvg_type.lower()} detectado: {gap_pips:.1f} pips",
            symbol=symbol,
            priority=priority,
            timeframe=timeframe,
            data={'gap_size_pips': gap_pips, 'fvg_type': fvg_type}
        )
    
    async def send_confluence_alert(self, confluence_data: Dict, symbol: str):
        """Alerta específica para confluencia"""
        strength = confluence_data.get('confluence_strength', 0)
        timeframes = confluence_data.get('timeframes', [])
        
        priority = AlertPriority.HIGH if strength >= 8 else AlertPriority.MEDIUM
        
        await self.send_alert(
            alert_type=AlertType.CONFLUENCE,
            title="Confluencia FVG Detectada",
            message=f"Confluencia entre {'-'.join(timeframes)}: fuerza {strength:.1f}",
            symbol=symbol,
            priority=priority,
            data={'confluence_strength': strength, 'timeframes': timeframes}
        )
    
    def get_alert_history(self, limit: int = 50) -> List[Dict]:
        """Retorna historial de alertas"""
        recent_alerts = list(self.alert_history)[-limit:]
        return [alert.to_dict() for alert in reversed(recent_alerts)]
    
    def get_metrics(self) -> Dict:
        """Retorna métricas del sistema"""
        return {
            **self.metrics,
            'active_channels': len([c for c in self.channels if c.enabled]),
            'total_channels': len(self.channels),
            'history_size': len(self.alert_history)
        }
    
    def configure(self, **kwargs):
        """Configura parámetros del sistema"""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
                logger.info(f"Configuración actualizada: {key} = {value}")

# Función de utilidad para testing
async def test_alert_system():
    """🧪 Test del sistema de alertas"""
    print("🚨 Testing Alert System...")
    
    # Crear sistema
    alert_system = FVGAlertSystem()
    
    # Enviar alertas de prueba
    await alert_system.send_alert(
        AlertType.NEW_FVG,
        "Test FVG Alert",
        "Esto es una alerta de prueba",
        "EURUSD",
        AlertPriority.HIGH,
        "M5",
        {'gap_size_pips': 5.5}
    )
    
    await alert_system.send_confluence_alert(
        {'confluence_strength': 8.5, 'timeframes': ['M15', 'H1']},
        "EURUSD"
    )
    
    # Mostrar métricas
    metrics = alert_system.get_metrics()
    print(f"✅ Alertas enviadas: {metrics['sent_alerts']}")
    print(f"📊 Total alertas: {metrics['total_alerts']}")

if __name__ == "__main__":
    asyncio.run(test_alert_system())
