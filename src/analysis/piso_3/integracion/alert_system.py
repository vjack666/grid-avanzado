"""
🔔 SISTEMA DE ALERTAS AVANZADO FVG
Sistema inteligente de notificaciones para el Piso 3
"""

import json
import smtplib
import requests
import logging
from datetime import datetime, timedelta
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from typing import Dict, List, Optional, Callable
from pathlib import Path

class AlertSystem:
    """
    🔔 SISTEMA DE ALERTAS AVANZADO
    
    Funcionalidades:
    - Múltiples canales de notificación (Email, Discord, Telegram, etc.)
    - Filtros inteligentes de alertas
    - Agrupación y priorización
    - Rate limiting y anti-spam
    - Plantillas personalizables
    """
    
    def __init__(self, config=None):
        """
        Inicializa el sistema de alertas
        
        Args:
            config: Configuración del sistema de alertas
        """
        self.config = config or self._get_default_config()
        self.alert_history = []
        self.alert_stats = {
            'total_sent': 0,
            'by_priority': {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0},
            'by_channel': {},
            'last_alert': None,
            'errors': 0
        }
        
        self.filters = []
        self.channels = {}
        self.templates = {}
        
        self.logger = logging.getLogger(__name__)
        
        # Inicializar canales y plantillas
        self._initialize_channels()
        self._initialize_templates()
        
        print("🔔 AlertSystem inicializado")
    
    def _get_default_config(self):
        """Configuración por defecto del sistema"""
        return {
            "rate_limits": {
                "HIGH": 10,     # 10 alertas HIGH por hora
                "MEDIUM": 5,    # 5 alertas MEDIUM por hora  
                "LOW": 3        # 3 alertas LOW por hora
            },
            "channels": {
                "email": {
                    "enabled": False,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "username": "",
                    "password": "",
                    "recipients": []
                },
                "discord": {
                    "enabled": False,
                    "webhook_url": "",
                    "mention_roles": []
                },
                "telegram": {
                    "enabled": False,
                    "bot_token": "",
                    "chat_ids": []
                },
                "console": {
                    "enabled": True,
                    "show_details": True
                }
            },
            "filters": {
                "min_quality_score": 6.0,
                "blocked_symbols": [],
                "quiet_hours": {
                    "enabled": False,
                    "start": "22:00",
                    "end": "06:00"
                }
            },
            "grouping": {
                "enabled": True,
                "window_minutes": 5,
                "max_group_size": 3
            }
        }
    
    def send_alert(self, alert_data):
        """
        Envía una alerta a través de los canales configurados
        
        Args:
            alert_data: Datos de la alerta
            
        Returns:
            bool: True si se envió exitosamente
        """
        try:
            # Procesar y validar alerta
            processed_alert = self._process_alert(alert_data)
            
            if not processed_alert:
                return False
            
            # Aplicar filtros
            if not self._should_send_alert(processed_alert):
                return False
            
            # Verificar rate limits
            if not self._check_rate_limits(processed_alert):
                return False
            
            # Verificar agrupación
            if self.config['grouping']['enabled']:
                grouped_alert = self._check_grouping(processed_alert)
                if grouped_alert != processed_alert:
                    processed_alert = grouped_alert
            
            # Enviar por todos los canales habilitados
            success = self._send_to_channels(processed_alert)
            
            if success:
                self._update_stats(processed_alert)
                self.alert_history.append(processed_alert)
                
                # Mantener historial limitado
                if len(self.alert_history) > 1000:
                    self.alert_history = self.alert_history[-1000:]
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error enviando alerta: {e}")
            self.alert_stats['errors'] += 1
            return False
    
    def send_fvg_alert(self, fvg_data, context=None):
        """
        Envía alerta específica para FVG detectado
        
        Args:
            fvg_data: Datos del FVG
            context: Contexto adicional
        """
        alert = {
            'type': 'FVG_DETECTED',
            'priority': self._calculate_fvg_priority(fvg_data),
            'title': f"🎯 FVG {fvg_data.get('type', 'UNKNOWN')} Detectado",
            'message': f"Nuevo FVG {fvg_data.get('type', '')} en {fvg_data.get('symbol', 'UNKNOWN')}",
            'fvg': fvg_data,
            'context': context or {},
            'timestamp': datetime.now(),
            'source': 'FVG_DETECTOR'
        }
        
        return self.send_alert(alert)
    
    def send_system_alert(self, alert_type, message, priority='MEDIUM'):
        """
        Envía alerta del sistema
        
        Args:
            alert_type: Tipo de alerta del sistema
            message: Mensaje de la alerta
            priority: Prioridad (HIGH, MEDIUM, LOW)
        """
        alert = {
            'type': alert_type,
            'priority': priority,
            'title': f"🖥️ Sistema: {alert_type}",
            'message': message,
            'timestamp': datetime.now(),
            'source': 'SYSTEM'
        }
        
        return self.send_alert(alert)
    
    def add_filter(self, filter_func: Callable[[Dict], bool], name: str = None):
        """
        Añade filtro personalizado para alertas
        
        Args:
            filter_func: Función que retorna True si debe enviarse la alerta
            name: Nombre del filtro
        """
        filter_info = {
            'func': filter_func,
            'name': name or f"filter_{len(self.filters)}",
            'added': datetime.now()
        }
        
        self.filters.append(filter_info)
        print(f"✅ Filtro '{filter_info['name']}' añadido")
    
    def get_alert_stats(self):
        """Obtiene estadísticas de alertas"""
        
        recent_alerts = [a for a in self.alert_history if 
                        (datetime.now() - a['timestamp']).total_seconds() < 3600]  # Última hora
        
        return {
            'total_alerts': self.alert_stats['total_sent'],
            'recent_alerts': len(recent_alerts),
            'by_priority': self.alert_stats['by_priority'].copy(),
            'by_channel': self.alert_stats['by_channel'].copy(),
            'error_count': self.alert_stats['errors'],
            'last_alert': self.alert_stats['last_alert'],
            'active_filters': len(self.filters),
            'rate_limit_status': self._get_rate_limit_status()
        }
    
    def configure_email(self, smtp_server, smtp_port, username, password, recipients):
        """Configura canal de email"""
        self.config['channels']['email'].update({
            'enabled': True,
            'smtp_server': smtp_server,
            'smtp_port': smtp_port,
            'username': username,
            'password': password,
            'recipients': recipients if isinstance(recipients, list) else [recipients]
        })
        
        print("📧 Canal de email configurado")
    
    def configure_discord(self, webhook_url, mention_roles=None):
        """Configura canal de Discord"""
        self.config['channels']['discord'].update({
            'enabled': True,
            'webhook_url': webhook_url,
            'mention_roles': mention_roles or []
        })
        
        print("🎮 Canal de Discord configurado")
    
    def configure_telegram(self, bot_token, chat_ids):
        """Configura canal de Telegram"""
        self.config['channels']['telegram'].update({
            'enabled': True,
            'bot_token': bot_token,
            'chat_ids': chat_ids if isinstance(chat_ids, list) else [chat_ids]
        })
        
        print("📱 Canal de Telegram configurado")
    
    def _process_alert(self, alert_data):
        """Procesa y normaliza datos de alerta"""
        
        processed = {
            'id': f"ALERT_{int(datetime.now().timestamp())}",
            'type': alert_data.get('type', 'UNKNOWN'),
            'priority': alert_data.get('priority', 'MEDIUM'),
            'title': alert_data.get('title', 'Sin título'),
            'message': alert_data.get('message', 'Sin mensaje'),
            'timestamp': alert_data.get('timestamp', datetime.now()),
            'source': alert_data.get('source', 'UNKNOWN'),
            'data': alert_data.get('data', {}),
            'channels': alert_data.get('channels', list(self.channels.keys()))
        }
        
        # Validaciones básicas
        if not processed['title'] or not processed['message']:
            self.logger.warning("Alerta con título o mensaje vacío")
            return None
        
        return processed
    
    def _should_send_alert(self, alert):
        """Verifica si debe enviarse la alerta según filtros"""
        
        # Filtro de horas silenciosas
        if self.config['filters']['quiet_hours']['enabled']:
            if self._is_quiet_hours():
                return False
        
        # Filtros de calidad para FVGs
        if alert['type'] == 'FVG_DETECTED':
            fvg_data = alert.get('fvg', {})
            quality_score = fvg_data.get('quality_score', 0)
            
            if quality_score < self.config['filters']['min_quality_score']:
                return False
            
            symbol = fvg_data.get('symbol', '')
            if symbol in self.config['filters']['blocked_symbols']:
                return False
        
        # Filtros personalizados
        for filter_info in self.filters:
            try:
                if not filter_info['func'](alert):
                    return False
            except Exception as e:
                self.logger.error(f"Error en filtro {filter_info['name']}: {e}")
        
        return True
    
    def _check_rate_limits(self, alert):
        """Verifica límites de velocidad"""
        
        priority = alert['priority']
        limit = self.config['rate_limits'].get(priority, 999)
        
        # Contar alertas de esta prioridad en la última hora
        hour_ago = datetime.now() - timedelta(hours=1)
        recent_count = sum(1 for a in self.alert_history 
                          if a['priority'] == priority and a['timestamp'] > hour_ago)
        
        if recent_count >= limit:
            self.logger.warning(f"Rate limit alcanzado para prioridad {priority}")
            return False
        
        return True
    
    def _check_grouping(self, alert):
        """Verifica si debe agrupar con alertas recientes"""
        
        if not self.config['grouping']['enabled']:
            return alert
        
        window = timedelta(minutes=self.config['grouping']['window_minutes'])
        cutoff = datetime.now() - window
        
        # Buscar alertas similares recientes
        similar_alerts = [a for a in self.alert_history 
                         if a['type'] == alert['type'] 
                         and a['timestamp'] > cutoff
                         and a.get('group_id') is None]
        
        if len(similar_alerts) > 0:
            # Crear alerta agrupada
            group_id = f"GROUP_{int(datetime.now().timestamp())}"
            alert['group_id'] = group_id
            alert['grouped_count'] = len(similar_alerts) + 1
            alert['title'] = f"📊 {alert['title']} (x{alert['grouped_count']})"
            
            # Marcar alertas anteriores como agrupadas
            for similar in similar_alerts:
                similar['group_id'] = group_id
        
        return alert
    
    def _send_to_channels(self, alert):
        """Envía alerta a todos los canales habilitados"""
        
        success = False
        
        for channel_name, channel_config in self.config['channels'].items():
            if not channel_config.get('enabled', False):
                continue
            
            try:
                if channel_name == 'console':
                    self._send_console(alert, channel_config)
                elif channel_name == 'email':
                    self._send_email(alert, channel_config)
                elif channel_name == 'discord':
                    self._send_discord(alert, channel_config)
                elif channel_name == 'telegram':
                    self._send_telegram(alert, channel_config)
                
                success = True
                
            except Exception as e:
                self.logger.error(f"Error enviando a {channel_name}: {e}")
        
        return success
    
    def _send_console(self, alert, config):
        """Envía alerta a consola"""
        
        priority_colors = {
            'HIGH': '🔴',
            'MEDIUM': '🟡', 
            'LOW': '🟢'
        }
        
        color = priority_colors.get(alert['priority'], '⚪')
        timestamp = alert['timestamp'].strftime('%H:%M:%S')
        
        print(f"\n{color} ALERTA [{alert['priority']}] - {timestamp}")
        print(f"📋 {alert['title']}")
        print(f"💬 {alert['message']}")
        
        if config.get('show_details', False) and alert.get('data'):
            print(f"📊 Detalles: {json.dumps(alert['data'], indent=2, default=str)[:200]}...")
        
        print("-" * 50)
    
    def _send_email(self, alert, config):
        """Envía alerta por email"""
        
        if not config.get('recipients'):
            return
        
        template = self.templates.get('email', self._get_default_email_template())
        
        # Preparar mensaje
        msg = MimeMultipart()
        msg['From'] = config['username']
        msg['Subject'] = f"[FVG Alert] {alert['title']}"
        
        # Generar contenido HTML
        html_content = template.format(
            title=alert['title'],
            message=alert['message'],
            priority=alert['priority'],
            timestamp=alert['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            alert_id=alert['id'],
            source=alert['source']
        )
        
        msg.attach(MimeText(html_content, 'html'))
        
        # Enviar a todos los destinatarios
        server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
        server.starttls()
        server.login(config['username'], config['password'])
        
        for recipient in config['recipients']:
            msg['To'] = recipient
            server.send_message(msg)
            del msg['To']
        
        server.quit()
    
    def _send_discord(self, alert, config):
        """Envía alerta a Discord"""
        
        webhook_url = config.get('webhook_url')
        if not webhook_url:
            return
        
        # Preparar embed
        color_map = {'HIGH': 0xFF0000, 'MEDIUM': 0xFFFF00, 'LOW': 0x00FF00}
        color = color_map.get(alert['priority'], 0x808080)
        
        embed = {
            "title": alert['title'],
            "description": alert['message'],
            "color": color,
            "timestamp": alert['timestamp'].isoformat(),
            "fields": [
                {"name": "Prioridad", "value": alert['priority'], "inline": True},
                {"name": "Fuente", "value": alert['source'], "inline": True},
                {"name": "ID", "value": alert['id'], "inline": True}
            ]
        }
        
        payload = {"embeds": [embed]}
        
        # Menciones si están configuradas
        mentions = config.get('mention_roles', [])
        if mentions and alert['priority'] == 'HIGH':
            payload['content'] = ' '.join(f"<@&{role_id}>" for role_id in mentions)
        
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
    
    def _send_telegram(self, alert, config):
        """Envía alerta a Telegram"""
        
        bot_token = config.get('bot_token')
        chat_ids = config.get('chat_ids', [])
        
        if not bot_token or not chat_ids:
            return
        
        # Formatear mensaje
        priority_emoji = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}
        emoji = priority_emoji.get(alert['priority'], '⚪')
        
        message = f"{emoji} *{alert['title']}*\n\n{alert['message']}\n\n"
        message += f"🏷️ Prioridad: `{alert['priority']}`\n"
        message += f"🕒 Tiempo: `{alert['timestamp'].strftime('%H:%M:%S')}`\n"
        message += f"📍 Fuente: `{alert['source']}`"
        
        # Enviar a todos los chats
        for chat_id in chat_ids:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, json=payload)
            response.raise_for_status()
    
    def _initialize_channels(self):
        """Inicializa canales de notificación"""
        # Implementación básica - se expande según necesidades
        pass
    
    def _initialize_templates(self):
        """Inicializa plantillas de mensajes"""
        
        self.templates['email'] = self._get_default_email_template()
    
    def _get_default_email_template(self):
        """Plantilla por defecto para emails"""
        
        return """
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="background: #f5f5f5; padding: 20px; border-radius: 5px;">
                <h2 style="color: #2c3e50;">🏢 FVG Alert System - Piso 3</h2>
                <div style="background: white; padding: 15px; border-radius: 5px; margin: 15px 0;">
                    <h3 style="color: #e74c3c;">{title}</h3>
                    <p style="font-size: 16px;">{message}</p>
                    <hr>
                    <p><strong>Prioridad:</strong> <span style="color: #e67e22;">{priority}</span></p>
                    <p><strong>Timestamp:</strong> {timestamp}</p>
                    <p><strong>Alert ID:</strong> {alert_id}</p>
                    <p><strong>Fuente:</strong> {source}</p>
                </div>
                <p style="font-size: 12px; color: #7f8c8d;">
                    Este es un mensaje automático del Sistema FVG del Piso 3.
                </p>
            </div>
        </body>
        </html>
        """
    
    def _calculate_fvg_priority(self, fvg_data):
        """Calcula prioridad basada en datos del FVG"""
        
        quality_score = fvg_data.get('quality_score', 0)
        gap_size = fvg_data.get('gap_size_pips', 0)
        
        if quality_score >= 8.5 or gap_size >= 10:
            return 'HIGH'
        elif quality_score >= 7.0 or gap_size >= 5:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _is_quiet_hours(self):
        """Verifica si está en horas silenciosas"""
        
        quiet_config = self.config['filters']['quiet_hours']
        if not quiet_config.get('enabled', False):
            return False
        
        now = datetime.now().time()
        start_time = datetime.strptime(quiet_config['start'], '%H:%M').time()
        end_time = datetime.strptime(quiet_config['end'], '%H:%M').time()
        
        if start_time <= end_time:
            return start_time <= now <= end_time
        else:  # Cruza medianoche
            return now >= start_time or now <= end_time
    
    def _update_stats(self, alert):
        """Actualiza estadísticas de alertas"""
        
        self.alert_stats['total_sent'] += 1
        self.alert_stats['by_priority'][alert['priority']] += 1
        self.alert_stats['last_alert'] = alert['timestamp']
        
        # Estadísticas por canal
        for channel in alert.get('channels', []):
            if channel not in self.alert_stats['by_channel']:
                self.alert_stats['by_channel'][channel] = 0
            self.alert_stats['by_channel'][channel] += 1
    
    def _get_rate_limit_status(self):
        """Obtiene estado actual de rate limits"""
        
        hour_ago = datetime.now() - timedelta(hours=1)
        status = {}
        
        for priority, limit in self.config['rate_limits'].items():
            recent_count = sum(1 for a in self.alert_history 
                             if a['priority'] == priority and a['timestamp'] > hour_ago)
            
            status[priority] = {
                'used': recent_count,
                'limit': limit,
                'remaining': max(0, limit - recent_count),
                'percentage': (recent_count / limit) * 100 if limit > 0 else 0
            }
        
        return status


if __name__ == "__main__":
    # Ejecutar sistema de alertas en modo producción
    print("🔔 Alert System - Modo Producción")
    print("="*50)
    
    # Crear sistema configurado para producción
    alert_system = AlertSystem({
        "rate_limits": {
            "HIGH": 50,     # 50 alertas HIGH por hora en producción
            "MEDIUM": 30,   # 30 alertas MEDIUM por hora
            "LOW": 20       # 20 alertas LOW por hora
        },
        "filters": {
            "min_quality_score": 7.0,  # Solo FVGs de alta calidad
            "blocked_symbols": [],
            "quiet_hours": {
                "enabled": True,
                "start": "22:00",
                "end": "06:00"
            }
        }
    })
    
    # Configurar filtros de producción
    def production_filter(alert):
        """Filtro para alertas de producción - solo alta calidad"""
        if alert['type'] == 'FVG_DETECTED':
            fvg = alert.get('fvg', {})
            quality = fvg.get('quality_score', 0)
            return quality >= 7.5  # Solo FVGs excelentes
        return True
    
    alert_system.add_filter(production_filter, "production_quality_filter")
    
    print("✅ Sistema de alertas configurado para producción")
    print("� Listo para recibir alertas reales del sistema FVG")
    print("⚙️ Configurar canales de notificación según necesidades")
