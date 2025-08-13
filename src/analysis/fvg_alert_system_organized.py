"""
🚨 SISTEMA UNIFICADO DE NOTIFICACIONES FVG - PISO 3
Sistema de notificaciones especializado para Fair Value Gaps
Integrado con AlertEngine del SÓTANO 2 y Enhanced Order Executor

Autor: Trading Grid System
Fecha: Agosto 13, 2025
Oficina: Piso 3 - Advanced Analytics
Estado: SISTEMA OPERATIVO DE PRODUCCIÓN
Versión: v2.0.0-PRODUCTION

PROPÓSITO REAL:
- Sistema especializado de notificaciones para eventos FVG
- Bridge entre FVGDetector y Enhanced Order Executor
- Gestión de alertas críticas de trading automático
- Integración con canales externos (Discord, Telegram, Email)
- Monitoreo en tiempo real de oportunidades FVG
"""

# =============================================================================
# IMPORTS ESPECIALIZADOS PARA PRODUCCIÓN
# =============================================================================
import asyncio
import json
import logging
import os
import smtplib
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import aiohttp

# Importaciones del sistema Trading Grid
from src.core.config_manager import ConfigManager
from src.core.logger_manager import LoggerManager

# =============================================================================
# CONFIGURACIÓN DEL SISTEMA REAL
# =============================================================================
logger = logging.getLogger(__name__)

# Sistema de configuración integrado
config_manager = ConfigManager()
logger_manager = LoggerManager()

# =============================================================================
# ENUMS Y DATACLASSES
# =============================================================================
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

# =============================================================================
# CLASES BASE DE CANALES
# =============================================================================
class AlertChannel:
    """Canal base para envío de alertas"""
    
    def __init__(self, name: str, enabled: bool = True):
        self.name = name
        self.enabled = enabled

    async def send_alert(self, alert: Alert) -> bool:
        """Envía una alerta (implementar en subclases)"""
        raise NotImplementedError

# =============================================================================
# CANALES DE ALERTA ESPECÍFICOS
# =============================================================================
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
        # Formateador personalizado usando Callable
        self.custom_formatter: Optional[Callable[[Alert], Dict]] = None

    async def send_alert(self, alert: Alert) -> bool:
        """Envía alerta por webhook"""
        try:
            # Usar formateador personalizado si existe
            if self.custom_formatter:
                payload = self.custom_formatter(alert)
            elif self.platform == "discord":
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

    def _format_slack_message(self, alert: Alert) -> Dict:
        """Formatea mensaje para Slack"""
        color_map = {
            AlertPriority.LOW: "good",      # Verde
            AlertPriority.MEDIUM: "warning", # Amarillo
            AlertPriority.HIGH: "danger",   # Rojo
            AlertPriority.CRITICAL: "#ff00ff"  # Magenta
        }

        # Icono por tipo
        icons = {
            AlertType.NEW_FVG: ":dart:",
            AlertType.CONFLUENCE: ":link:",
            AlertType.LARGE_FVG: ":chart_with_upwards_trend:",
            AlertType.MARKET_BIAS: ":bar_chart:",
            AlertType.SESSION_CONCENTRATION: ":clock8:",
            AlertType.FVG_FILLED: ":white_check_mark:",
            AlertType.SYSTEM_ERROR: ":x:"
        }
        icon = icons.get(alert.type, ":bell:")

        fields = [
            {"title": "Símbolo", "value": alert.symbol, "short": True},
            {"title": "Prioridad", "value": alert.priority.value, "short": True}
        ]

        if alert.timeframe:
            fields.append({
                "title": "Timeframe",
                "value": alert.timeframe,
                "short": True
            })

        if alert.data and 'gap_size_pips' in alert.data:
            fields.append({
                "title": "Gap Size",
                "value": f"{alert.data['gap_size_pips']:.1f} pips",
                "short": True
            })

        return {
            "attachments": [{
                "color": color_map.get(alert.priority, "#808080"),
                "title": f"{icon} {alert.title}",
                "text": alert.message,
                "fields": fields,
                "ts": alert.timestamp.timestamp()
            }]
        }

    def _format_generic_message(self, alert: Alert) -> Dict:
        """Formatea mensaje genérico para webhook"""
        return {
            "text": f"🚨 {alert.title}",
            "content": {
                "alert_id": alert.id,
                "type": alert.type.value,
                "priority": alert.priority.value,
                "title": alert.title,
                "message": alert.message,
                "symbol": alert.symbol,
                "timeframe": alert.timeframe,
                "timestamp": alert.timestamp.isoformat(),
                "data": alert.data
            }
        }


class EmailAlertChannel(AlertChannel):
    """Canal de alertas por email"""
    
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str, 
                 from_email: str, to_emails: List[str], use_tls: bool = True):
        super().__init__("Email", enabled=True)
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.to_emails = to_emails
        self.use_tls = use_tls

    async def send_alert(self, alert: Alert) -> bool:
        """Envía alerta por email"""
        try:
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            msg['Subject'] = f"🚨 FVG Alert: {alert.title}"

            # Formatear contenido HTML
            html_content = self._format_html_content(alert)
            msg.attach(MIMEText(html_content, 'html'))

            # Enviar email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            if self.use_tls:
                server.starttls()
            server.login(self.username, self.password)
            text = msg.as_string()
            server.sendmail(self.from_email, self.to_emails, text)
            server.quit()

            return True
            
        except Exception as e:
            logger.error(f"Error enviando email: {e}")
            return False

    def _format_html_content(self, alert: Alert) -> str:
        """Formatea contenido HTML para email"""
        priority_colors = {
            AlertPriority.LOW: "#28a745",
            AlertPriority.MEDIUM: "#ffc107", 
            AlertPriority.HIGH: "#dc3545",
            AlertPriority.CRITICAL: "#6f42c1"
        }
        
        color = priority_colors.get(alert.priority, "#6c757d")
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 20px;">
            <div style="border-left: 4px solid {color}; padding-left: 20px;">
                <h2 style="color: {color};">🚨 {alert.title}</h2>
                <p><strong>Mensaje:</strong> {alert.message}</p>
                <p><strong>Símbolo:</strong> {alert.symbol}</p>
                <p><strong>Prioridad:</strong> <span style="color: {color};">{alert.priority.value}</span></p>
                <p><strong>Tipo:</strong> {alert.type.value}</p>
                <p><strong>Timestamp:</strong> {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
        """
        
        if alert.timeframe:
            html += f"<p><strong>Timeframe:</strong> {alert.timeframe}</p>"
            
        if alert.data:
            html += "<h3>Datos Adicionales:</h3><ul>"
            for key, value in alert.data.items():
                html += f"<li><strong>{key}:</strong> {value}</li>"
            html += "</ul>"
            
        html += """
            </div>
            <hr>
            <p style="color: #6c757d; font-size: 12px;">
                Este es un mensaje automático del Sistema de Alertas FVG Trading Grid.
            </p>
        </body>
        </html>
        """
        
        return html

# =============================================================================
# CLASE PRINCIPAL DEL SISTEMA DE ALERTAS
# =============================================================================
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
        
        # Filtro personalizado usando Callable
        self.custom_filter: Optional[Callable[[Alert], bool]] = None
        
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
        # Verificar filtro personalizado primero
        if self.custom_filter and not self.custom_filter(alert):
            return False
            
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
        import uuid
        rand_suffix = str(uuid.uuid4())[:8]
        return f"FVG_ALERT_{timestamp}_{rand_suffix}"

    # =========================================================================
    # MÉTODOS ESPECÍFICOS DE ALERTAS
    # =========================================================================
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

    async def send_large_fvg_alert(self, fvg_data: Dict, symbol: str, timeframe: str):
        """Alerta para FVGs especialmente grandes"""
        gap_pips = fvg_data.get('gap_size', 0) * 10000

        await self.send_alert(
            alert_type=AlertType.LARGE_FVG,
            title="FVG Excepcional",
            message=f"FVG de {gap_pips:.1f} pips detectado - Mayor al promedio",
            symbol=symbol,
            priority=AlertPriority.CRITICAL,
            timeframe=timeframe,
            data={'gap_size_pips': gap_pips, 'exceptional': True}
        )

    async def send_fvg_filled_alert(self, fvg_data: Dict, symbol: str, timeframe: str):
        """Alerta cuando un FVG es llenado/completado"""
        fill_percentage = fvg_data.get('fill_percentage', 0)

        await self.send_alert(
            alert_type=AlertType.FVG_FILLED,
            title="FVG Completado",
            message=f"FVG llenado {fill_percentage:.1f}% en {symbol} {timeframe}",
            symbol=symbol,
            priority=AlertPriority.MEDIUM,
            timeframe=timeframe,
            data={'fill_percentage': fill_percentage, 'fvg_id': fvg_data.get('id')}
        )

    async def send_market_session_alert(self, session: str, session_data: Dict):
        """Alerta específica para concentración de sesión"""
        fvg_count = session_data.get('fvg_count', 0)
        avg_strength = session_data.get('avg_strength', 0)
        
        priority = AlertPriority.HIGH if fvg_count >= 5 else AlertPriority.MEDIUM

        await self.send_alert(
            alert_type=AlertType.SESSION_CONCENTRATION,
            title=f"Concentración Sesión {session}",
            message=f"Sesión {session}: {fvg_count} FVGs, fuerza promedio {avg_strength:.1f}",
            symbol="MULTI",
            priority=priority,
            data={'session': session, 'fvg_count': fvg_count, 'avg_strength': avg_strength}
        )

    async def send_system_status_alert(self, status: str, details: Dict = None):
        """Envía alerta de estado del sistema"""
        priority = AlertPriority.HIGH if status in ['ERROR', 'WARNING'] else AlertPriority.LOW

        await self.send_alert(
            alert_type=AlertType.SYSTEM_ERROR if status == 'ERROR' else AlertType.MARKET_BIAS,
            title=f"Sistema Status: {status}",
            message=f"Estado del sistema FVG: {status}",
            symbol="SYSTEM",
            priority=priority,
            data=details or {}
        )

    # =========================================================================
    # MÉTODOS DE GESTIÓN
    # =========================================================================
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

    def enable_channel(self, channel_name: str):
        """Habilita un canal específico"""
        for channel in self.channels:
            if channel.name == channel_name:
                channel.enabled = True
                logger.info(f"Canal habilitado: {channel_name}")
                return True
        return False

    def disable_channel(self, channel_name: str):
        """Deshabilita un canal específico"""
        for channel in self.channels:
            if channel.name == channel_name:
                channel.enabled = False
                logger.info(f"Canal deshabilitado: {channel_name}")
                return True
        return False

    def get_channel_status(self) -> Dict[str, bool]:
        """Retorna estado de todos los canales"""
        return {channel.name: channel.enabled for channel in self.channels}

    def clear_history(self):
        """Limpia el historial de alertas"""
        self.alert_history.clear()
        logger.info("Historial de alertas limpiado")

    def export_metrics_to_dict(self) -> Dict:
        """Exporta métricas detalladas"""
        return {
            'timestamp': datetime.now().isoformat(),
            'metrics': self.get_metrics(),
            'config': self.config,
            'channels': self.get_channel_status(),
            'recent_alerts': len(self.alert_history)
        }

    async def health_check(self) -> Dict:
        """Verifica la salud del sistema de alertas"""
        health_status = {
            'status': 'healthy',
            'channels_active': 0,
            'channels_total': len(self.channels),
            'last_alert': None,
            'issues': []
        }

        # Verificar canales activos
        for channel in self.channels:
            if channel.enabled:
                health_status['channels_active'] += 1

        # Verificar última alerta
        if self.alert_history:
            last_alert = self.alert_history[-1]
            health_status['last_alert'] = last_alert.timestamp.isoformat()

        # Verificar problemas
        if health_status['channels_active'] == 0:
            health_status['issues'].append("No hay canales activos")
            health_status['status'] = 'warning'

        if self.metrics['failed_sends'] > self.metrics['sent_alerts'] * 0.1:
            health_status['issues'].append("Alto ratio de fallos en envío")
            health_status['status'] = 'warning'

        return health_status

# =============================================================================
# FUNCIONES DE UTILIDAD Y FACTORY
# =============================================================================
def create_production_alert_system(webhook_url: str = None, email_config: Dict = None) -> FVGAlertSystem:
    """
    🏭 Crea un sistema de alertas configurado para producción
    Args:
        webhook_url: URL del webhook para Discord/Slack
        email_config: Configuración de email {server, port, username, password, from_email, to_emails}
    Returns:
        Sistema de alertas configurado
    """
    # Configuración optimizada para producción
    prod_config = {
        'max_alerts_per_minute': 15,
        'duplicate_suppression_minutes': 3,
        'min_priority': AlertPriority.MEDIUM,
        'enabled_types': [
            AlertType.NEW_FVG.value,
            AlertType.CONFLUENCE.value,
            AlertType.LARGE_FVG.value,
            AlertType.SYSTEM_ERROR.value
        ],
        'throttling_enabled': True,
        'history_max_size': 500
    }

    alert_system = FVGAlertSystem(prod_config)

    # Agregar webhook si se proporciona
    if webhook_url:
        webhook_channel = WebhookAlertChannel(webhook_url, "discord")
        alert_system.add_channel(webhook_channel)
        logger.info("Canal webhook agregado para producción")

    # Agregar email si se proporciona
    if email_config:
        try:
            email_channel = EmailAlertChannel(
                smtp_server=email_config['server'],
                smtp_port=email_config['port'],
                username=email_config['username'],
                password=email_config['password'],
                from_email=email_config['from_email'],
                to_emails=email_config['to_emails']
            )
            alert_system.add_channel(email_channel)
            logger.info("Canal email agregado para producción")
        except KeyError as e:
            logger.error(f"Configuración de email incompleta: {e}")

    return alert_system


def create_development_alert_system() -> FVGAlertSystem:
    """
    🛠️ Crea un sistema de alertas configurado para desarrollo
    Returns:
        Sistema de alertas para desarrollo (solo consola y archivo)
    """
    dev_config = {
        'max_alerts_per_minute': 30,
        'duplicate_suppression_minutes': 1,
        'min_priority': AlertPriority.LOW,
        'enabled_types': [t.value for t in AlertType],
        'throttling_enabled': False,
        'history_max_size': 100
    }
    
    return FVGAlertSystem(dev_config)

# =============================================================================
# FUNCIONES DE INTEGRACIÓN REAL CON EL SISTEMA
# =============================================================================
class FVGNotificationBridge:
    """
    🌉 PUENTE DE NOTIFICACIONES FVG
    Integra el sistema de alertas FVG con el sistema principal
    """
    
    def __init__(self, alert_system: FVGAlertSystem, enhanced_order_executor=None):
        self.alert_system = alert_system
        self.enhanced_order_executor = enhanced_order_executor
        self.logger = logging.getLogger("FVGNotificationBridge")
        
    async def on_fvg_detected(self, fvg_data, symbol: str, timeframe: str):
        """
        Callback real para cuando se detecta un FVG
        Integrado con el FVGDetector del sistema principal
        """
        try:
            # Convertir FVGData a dict si es necesario
            if hasattr(fvg_data, '__dict__'):
                fvg_dict = {
                    'gap_size': fvg_data.gap_size,
                    'type': fvg_data.type,
                    'gap_low': fvg_data.gap_low,
                    'gap_high': fvg_data.gap_high,
                    'formation_time': fvg_data.formation_time.isoformat() if hasattr(fvg_data.formation_time, 'isoformat') else str(fvg_data.formation_time)
                }
            else:
                fvg_dict = fvg_data
                
            # Enviar alerta especializada
            await self.alert_system.send_fvg_alert(fvg_dict, symbol, timeframe)
            
            # Notificar a Enhanced Order Executor si está disponible
            if self.enhanced_order_executor:
                await self._notify_enhanced_executor(fvg_dict, symbol, timeframe)
                
            # Log del evento
            self.logger.info(f"📡 FVG Notification Bridge: {symbol} {timeframe} - Gap: {fvg_dict.get('gap_size', 0)*10000:.1f} pips")
            
        except Exception as e:
            self.logger.error(f"❌ Error en FVG notification bridge: {e}")

    async def on_confluence_detected(self, confluence_data: Dict, symbol: str):
        """
        Callback real para cuando se detecta confluencia
        """
        try:
            await self.alert_system.send_confluence_alert(confluence_data, symbol)
            self.logger.info(f"🔗 Confluencia detectada para {symbol}: fuerza {confluence_data.get('confluence_strength', 0)}")
        except Exception as e:
            self.logger.error(f"❌ Error en confluence notification: {e}")
            
    async def _notify_enhanced_executor(self, fvg_data: Dict, symbol: str, timeframe: str):
        """Notifica al Enhanced Order Executor sobre nuevo FVG"""
        try:
            if hasattr(self.enhanced_order_executor, 'on_fvg_opportunity'):
                await self.enhanced_order_executor.on_fvg_opportunity(fvg_data, symbol, timeframe)
        except Exception as e:
            self.logger.error(f"❌ Error notificando a Enhanced Order Executor: {e}")


def setup_fvg_notifications_system() -> tuple[FVGAlertSystem, FVGNotificationBridge]:
    """
    🔧 CONFIGURACIÓN DEL SISTEMA REAL DE NOTIFICACIONES FVG
    
    Returns:
        Tuple con (alert_system, notification_bridge) configurados para producción
    """
    # Configuración de producción para notificaciones FVG
    production_config = {
        'max_alerts_per_minute': 20,  # Más alertas para trading activo
        'duplicate_suppression_minutes': 2,  # Reducido para FVG rápidos
        'min_priority': AlertPriority.MEDIUM,  # Solo alertas importantes
        'enabled_types': [
            AlertType.NEW_FVG.value,
            AlertType.CONFLUENCE.value,
            AlertType.LARGE_FVG.value,
            AlertType.FVG_FILLED.value
        ],
        'throttling_enabled': True,
        'history_max_size': 200  # Historial más pequeño para performance
    }
    
    # Crear sistema especializado
    fvg_alert_system = FVGAlertSystem(production_config)
    
    # Configurar canales según configuración del sistema
    try:
        # Canal Discord/Webhook si está configurado
        # Nota: Por ahora usar configuración por defecto
        # TODO: Implementar cuando ConfigManager tenga soporte completo para notifications
        
        # Ejemplo de configuración manual (reemplazar con config real)
        webhook_url = None  # config_manager.get_webhook_url() cuando esté disponible
        if webhook_url:
            webhook_channel = WebhookAlertChannel(webhook_url, "discord")
            fvg_alert_system.add_channel(webhook_channel)
            logger.info("✅ Canal webhook FVG configurado")
            
        # Canal email (configurar manualmente por ahora)
        email_enabled = False  # Cambiar a True y configurar para producción
        if email_enabled:
            # Configuración manual de email para producción
            email_channel = EmailAlertChannel(
                smtp_server='smtp.gmail.com',  # Configurar según necesidades
                smtp_port=587,
                username='',  # Configurar email
                password='',  # Configurar password
                from_email='',  # Configurar email origen
                to_emails=[]  # Configurar emails destino
            )
            fvg_alert_system.add_channel(email_channel)
            logger.info("✅ Canal email FVG configurado")
            
    except Exception as e:
        logger.warning(f"⚠️ Error configurando canales externos: {e}")
    
    # Crear bridge de integración
    notification_bridge = FVGNotificationBridge(fvg_alert_system)
    
    logger.info("🚨 Sistema de notificaciones FVG inicializado para PRODUCCIÓN")
    
    return fvg_alert_system, notification_bridge


def integrate_with_fvg_detector(notification_bridge: FVGNotificationBridge, fvg_detector):
    """
    🔗 Integra el sistema de notificaciones con el detector FVG real
    Args:
        notification_bridge: Bridge de notificaciones configurado
        fvg_detector: RealTimeFVGDetector del sistema principal
    """
    try:
        # Registrar callbacks reales en el detector
        if hasattr(fvg_detector, 'set_callbacks'):
            fvg_detector.set_callbacks(
                on_fvg_detected=notification_bridge.on_fvg_detected,
                on_fvg_filled=None  # Por ahora solo nuevos FVGs
            )
            logger.info("✅ Callbacks FVG registrados en detector real")
        else:
            logger.warning("⚠️ FVG Detector no tiene método set_callbacks")
            
    except Exception as e:
        logger.error(f"❌ Error integrando con FVG detector: {e}")


# =============================================================================
# FUNCIONES DE FACTORY PARA DIFERENTES ENTORNOS
# =============================================================================


def create_alert_filter(strategy: str) -> Callable[[Alert], bool]:
    """
    🎯 Crea filtros de alertas según estrategia de trading
    Args:
        strategy: Tipo de estrategia ('scalping', 'swing', 'daily')
    Returns:
        Función filtro que evalúa si una alerta debe enviarse
    """
    # Helper para comparar prioridades
    def _priority_level(priority: AlertPriority) -> int:
        levels = {
            AlertPriority.LOW: 1,
            AlertPriority.MEDIUM: 2,
            AlertPriority.HIGH: 3,
            AlertPriority.CRITICAL: 4
        }
        return levels.get(priority, 0)
    
    def scalping_filter(alert: Alert) -> bool:
        """Filtro para estrategia de scalping"""
        if alert.type == AlertType.NEW_FVG:
            gap_pips = alert.data.get('gap_size_pips', 0)
            return gap_pips <= 5 and alert.timeframe in ['M1', 'M5', 'M15']
        return _priority_level(alert.priority) >= _priority_level(AlertPriority.MEDIUM)
    
    def swing_filter(alert: Alert) -> bool:
        """Filtro para estrategia de swing trading"""
        if alert.type == AlertType.NEW_FVG:
            gap_pips = alert.data.get('gap_size_pips', 0)
            return gap_pips >= 8 and alert.timeframe in ['H1', 'H4']
        return _priority_level(alert.priority) >= _priority_level(AlertPriority.HIGH)
    
    def daily_filter(alert: Alert) -> bool:
        """Filtro para estrategia de trading diario"""
        if alert.type == AlertType.NEW_FVG:
            return alert.timeframe in ['H4', 'D1']
        return alert.priority == AlertPriority.CRITICAL
    
    filters = {
        'scalping': scalping_filter,
        'swing': swing_filter,
        'daily': daily_filter
    }
    
    return filters.get(strategy, lambda alert: True)


def create_custom_formatter(platform: str) -> Callable[[Alert], Dict]:
    """
    🎨 Crea formateadores personalizados para diferentes plataformas
    Args:
        platform: Plataforma de destino ('discord', 'slack', 'telegram')
    Returns:
        Función que formatea una alerta para la plataforma específica
    """
    def discord_trading_format(alert: Alert) -> Dict:
        """Formato especializado para Discord trading"""
        priority_emojis = {
            AlertPriority.LOW: "🟢",
            AlertPriority.MEDIUM: "🟡", 
            AlertPriority.HIGH: "🔴",
            AlertPriority.CRITICAL: "🚨"
        }
        
        emoji = priority_emojis.get(alert.priority, "⚪")
        
        embed = {
            "embeds": [{
                "title": f"{emoji} {alert.title}",
                "description": f"**{alert.symbol}** | {alert.timeframe or 'ALL'}",
                "color": 0x00ff41 if alert.type == AlertType.NEW_FVG else 0xff6b00,
                "fields": [
                    {"name": "💬 Mensaje", "value": alert.message, "inline": False},
                    {"name": "⏰ Hora", "value": alert.timestamp.strftime('%H:%M:%S'), "inline": True},
                    {"name": "📈 Prioridad", "value": alert.priority.value, "inline": True}
                ],
                "footer": {"text": f"ID: {alert.id}"}
            }]
        }
        
        # Agregar datos específicos de FVG
        if alert.data and 'gap_size_pips' in alert.data:
            embed["embeds"][0]["fields"].append({
                "name": "📏 Gap", 
                "value": f"{alert.data['gap_size_pips']:.1f} pips", 
                "inline": True
            })
        
        return embed
    
    def telegram_format(alert: Alert) -> Dict:
        """Formato para Telegram"""
        priority_emojis = {
            AlertPriority.LOW: "🟢",
            AlertPriority.MEDIUM: "🟡", 
            AlertPriority.HIGH: "🔴",
            AlertPriority.CRITICAL: "🚨"
        }
        
        emoji = priority_emojis.get(alert.priority, "⚪")
        gap_info = ""
        
        if alert.data and 'gap_size_pips' in alert.data:
            gap_info = f"\n📏 Gap: {alert.data['gap_size_pips']:.1f} pips"
        
        text = f"""
{emoji} **{alert.title}**

💬 {alert.message}
📊 {alert.symbol} | {alert.timeframe or 'ALL'}
⏰ {alert.timestamp.strftime('%H:%M:%S')}
📈 {alert.priority.value}{gap_info}

🆔 `{alert.id}`
        """.strip()
        
        return {"text": text, "parse_mode": "Markdown"}
    
    formatters = {
        'discord': discord_trading_format,
        'telegram': telegram_format,
        'slack': lambda alert: {"text": f"🚨 {alert.title}: {alert.message}"}
    }
    
    return formatters.get(platform, lambda alert: {"text": str(alert.to_dict())})


# Ejemplo de uso de Callable en el sistema
def setup_trading_strategy(alert_system: FVGAlertSystem, strategy: str = "scalping"):
    """
    ⚙️ Configura el sistema de alertas para una estrategia específica
    Args:
        alert_system: Sistema de alertas a configurar
        strategy: Estrategia de trading ('scalping', 'swing', 'daily')
    """
    # Crear filtro específico para la estrategia
    custom_filter: Callable[[Alert], bool] = create_alert_filter(strategy)
    
    # Aplicar filtro personalizado
    alert_system.custom_filter = custom_filter
    
    # Configurar formatters personalizados para canales webhook
    for channel in alert_system.channels:
        if isinstance(channel, WebhookAlertChannel):
            if "discord" in channel.name.lower():
                formatter: Callable[[Alert], Dict] = create_custom_formatter("discord")
                channel.custom_formatter = formatter
    
    logger.info(f"Sistema configurado para estrategia: {strategy}")

# =============================================================================
# MAIN - SOLO PARA TESTING EN DESARROLLO
# =============================================================================
if __name__ == "__main__":
    # Este archivo es importado por el sistema principal
    # No se ejecuta directamente en producción
    print("🚨 FVG Notification System - Módulo de Producción")
    print("✅ Sistema listo para integración con Trading Grid")
