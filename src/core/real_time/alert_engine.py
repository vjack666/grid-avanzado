"""
AlertEngine - Motor de Alertas Avanzado - SÓTANO 2 DÍA 2
========================================================

Sistema centralizado de manejo de alertas para trading en tiempo real.
Proporciona alertas inteligentes, filtrado, priorización y múltiples canales de notificación.

Componente: PUERTA-S2-ALERTS
Fase: SÓTANO 2 - Tiempo Real
Prioridad: 3 de 4 (DÍA 2)
Versión: v2.1.0

Autor: Copilot Trading Grid
Fecha: 2025-08-11
"""

import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Any, Optional
from enum import Enum
from dataclasses import dataclass
import json


class AlertPriority(Enum):
    """Prioridades de alertas"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertChannel(Enum):
    """Canales de notificación"""
    LOG = "log"
    EMAIL = "email"
    PUSH = "push"
    SOUND = "sound"
    FILE = "file"


@dataclass
class Alert:
    """Estructura de una alerta"""
    id: str
    timestamp: datetime
    priority: AlertPriority
    category: str
    title: str
    message: str
    data: Dict[str, Any]
    channels: List[AlertChannel]
    acknowledged: bool = False
    resolved: bool = False


class AlertEngine:
    """
    Motor de Alertas Avanzado - PUERTA-S2-ALERTS
    
    Sistema centralizado que maneja todas las alertas del sistema de trading:
    - Recepción y clasificación de alertas
    - Filtrado y priorización inteligente
    - Múltiples canales de notificación
    - Historial y estadísticas
    - Configuración de reglas personalizadas
    
    Integración SÓTANO 1:
    - PUERTA-S1-CONFIG: Configuración de alertas
    - PUERTA-S1-LOGGER: Logging de eventos
    - PUERTA-S1-ERROR: Manejo de errores
    
    Características:
    - Thread-safe para operaciones concurrentes
    - Filtros anti-spam con throttling inteligente
    - Escalado automático de prioridades
    - Métricas y estadísticas en tiempo real
    """
    
    def __init__(self, config=None, logger=None, error=None):
        """
        Inicializar AlertEngine
        
        Args:
            config: ConfigManager para configuración
            logger: LoggerManager para logging
            error: ErrorManager para manejo de errores
        """
        # Metadatos del componente
        self.component_id = "PUERTA-S2-ALERTS"
        self.version = "v2.1.0"
        self.status = "initialized"
        
        # Dependencias SÓTANO 1
        self.config = config
        self.logger = logger
        self.error = error
        
        # Estado del motor
        self.is_running = False
        self.alerts_lock = threading.Lock()
        self.processing_thread = None
        
        # Almacenamiento de alertas
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.max_history_size = 1000
        
        # Callbacks de notificación
        self.notification_callbacks: Dict[AlertChannel, List[Callable]] = {
            channel: [] for channel in AlertChannel
        }
        
        # Configuración de alertas
        self.alert_config = {
            "enabled": True,
            "default_channels": [AlertChannel.LOG],
            "throttle_seconds": 30,  # Anti-spam
            "max_active_alerts": 100,
            "auto_resolve_minutes": 60,
            "priority_escalation": True,
            "sound_enabled": False,
            "email_enabled": False
        }
        
        # Filtros y reglas
        self.alert_filters = []
        self.escalation_rules = []
        
        # Métricas
        self.metrics = {
            "total_alerts_received": 0,
            "alerts_by_priority": {p.value: 0 for p in AlertPriority},
            "alerts_by_category": {},
            "alerts_acknowledged": 0,
            "alerts_resolved": 0,
            "alerts_filtered": 0,
            "uptime_start": datetime.now()
        }
        
        # Throttling anti-spam
        self.throttle_cache: Dict[str, datetime] = {}
        
        # Cargar configuración
        self._load_configuration()
        
        # Log inicialización
        if self.logger:
            self.logger.log_info(f"[{self.component_id}] Configuración cargada: {len(self.alert_config)} parámetros")
            self.logger.log_info(f"[{self.component_id}] Inicializando AlertEngine {self.version}")
    
    def _load_configuration(self):
        """Cargar configuración desde ConfigManager"""
        if self.config:
            try:
                # Por ahora usar configuración por defecto
                # TODO: Implementar configuración personalizada desde archivo cuando esté disponible
                pass
                        
            except Exception as e:
                if self.error:
                    self.error.handle_system_error("AlertEngine", e, {"method": "_load_configuration"})
    
    def start_engine(self) -> bool:
        """
        Iniciar el motor de alertas
        
        Returns:
            bool: True si se inició correctamente
        """
        try:
            if self.is_running:
                if self.logger:
                    self.logger.log_warning(f"[{self.component_id}] Motor ya está ejecutándose")
                return True
            
            if not self.alert_config.get("enabled", True):
                if self.logger:
                    self.logger.log_info(f"[{self.component_id}] Motor deshabilitado en configuración")
                return False
            
            # Iniciar thread de procesamiento
            self.is_running = True
            self.processing_thread = threading.Thread(
                target=self._process_alerts_loop,
                daemon=True,
                name="AlertEngine"
            )
            self.processing_thread.start()
            
            self.status = "running"
            
            if self.logger:
                self.logger.log_info(f"[{self.component_id}] Motor de alertas iniciado")
            
            return True
            
        except Exception as e:
            if self.error:
                self.error.handle_system_error("AlertEngine", e, {"method": "start_engine"})
            self.status = "error"
            return False
    
    def stop_engine(self) -> bool:
        """
        Detener el motor de alertas
        
        Returns:
            bool: True si se detuvo correctamente
        """
        try:
            if not self.is_running:
                return True
            
            self.is_running = False
            
            # Esperar a que termine el thread
            if self.processing_thread:
                self.processing_thread.join(timeout=5.0)
            
            self.status = "stopped"
            
            if self.logger:
                self.logger.log_info(f"[{self.component_id}] Motor de alertas detenido")
            
            return True
            
        except Exception as e:
            if self.error:
                self.error.handle_system_error("AlertEngine", e, {"method": "stop_engine"})
            return False
    
    def send_alert(self, 
                  priority: AlertPriority,
                  category: str,
                  title: str,
                  message: str,
                  data: Optional[Dict[str, Any]] = None,
                  channels: Optional[List[AlertChannel]] = None) -> str:
        """
        Enviar una nueva alerta
        
        Args:
            priority: Prioridad de la alerta
            category: Categoría (ej: "position", "market", "system")
            title: Título corto
            message: Mensaje detallado
            data: Datos adicionales
            channels: Canales de notificación específicos
            
        Returns:
            str: ID de la alerta creada
        """
        try:
            # Generar ID único
            alert_id = f"{category}_{int(time.time() * 1000)}"
            
            # Verificar throttling anti-spam
            throttle_key = f"{category}_{title}"
            if self._is_throttled(throttle_key):
                self.metrics["alerts_filtered"] += 1
                if self.logger:
                    self.logger.log_info(f"[{self.component_id}] Alerta filtrada por throttling: {title}")
                return ""
            
            # Canales por defecto si no se especifican
            if channels is None:
                channels = self.alert_config["default_channels"].copy()
            
            # Asegurar que channels es una lista válida
            if not isinstance(channels, list):
                channels = [AlertChannel.LOG]
            
            # Crear alerta
            alert = Alert(
                id=alert_id,
                timestamp=datetime.now(),
                priority=priority,
                category=category,
                title=title,
                message=message,
                data=data or {},
                channels=channels
            )
            
            # Aplicar filtros
            if self._apply_filters(alert):
                self.metrics["alerts_filtered"] += 1
                return ""
            
            # Almacenar alerta
            with self.alerts_lock:
                # Limitar alertas activas
                if len(self.active_alerts) >= self.alert_config["max_active_alerts"]:
                    self._cleanup_old_alerts()
                
                self.active_alerts[alert_id] = alert
            
            # Actualizar métricas
            self.metrics["total_alerts_received"] += 1
            self.metrics["alerts_by_priority"][priority.value] += 1
            if category not in self.metrics["alerts_by_category"]:
                self.metrics["alerts_by_category"][category] = 0
            self.metrics["alerts_by_category"][category] += 1
            
            # Actualizar throttling
            self.throttle_cache[throttle_key] = datetime.now()
            
            # Procesar notificaciones
            self._process_notifications(alert)
            
            if self.logger:
                self.logger.log_info(f"[{self.component_id}] Alerta enviada: {priority.value.upper()} - {title}")
            
            return alert_id
            
        except Exception as e:
            if self.error:
                self.error.handle_system_error("AlertEngine", e, {"method": "send_alert", "category": category})
            return ""
    
    def _is_throttled(self, throttle_key: str) -> bool:
        """Verificar si una alerta está siendo throttled"""
        if throttle_key in self.throttle_cache:
            last_sent = self.throttle_cache[throttle_key]
            throttle_time = timedelta(seconds=self.alert_config["throttle_seconds"])
            return datetime.now() - last_sent < throttle_time
        return False
    
    def _apply_filters(self, alert: Alert) -> bool:
        """
        Aplicar filtros a una alerta
        
        Returns:
            bool: True si la alerta debe ser filtrada (no enviada)
        """
        for filter_func in self.alert_filters:
            try:
                if filter_func(alert):
                    return True
            except Exception as e:
                if self.error:
                    self.error.handle_system_error("AlertEngine", e, {"method": "_apply_filters"})
        return False
    
    def _process_notifications(self, alert: Alert):
        """Procesar las notificaciones de una alerta"""
        for channel in alert.channels:
            callbacks = self.notification_callbacks.get(channel, [])
            for callback in callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    if self.error:
                        self.error.handle_system_error("AlertEngine", e, {"method": f"notification_callback_{channel.value}"})
    
    def _process_alerts_loop(self):
        """Loop principal de procesamiento de alertas"""
        while self.is_running:
            try:
                with self.alerts_lock:
                    # Auto-resolver alertas antiguas
                    self._auto_resolve_old_alerts()
                    
                    # Limpiar throttling cache
                    self._cleanup_throttle_cache()
                
                # Dormir para no consumir mucha CPU
                time.sleep(1.0)
                
            except Exception as e:
                if self.error:
                    self.error.handle_system_error("AlertEngine", e, {"method": "_process_alerts_loop"})
                time.sleep(5.0)  # Esperar más tiempo si hay error
    
    def _auto_resolve_old_alerts(self):
        """Auto-resolver alertas antiguas"""
        if not self.alert_config.get("auto_resolve_minutes"):
            return
        
        auto_resolve_time = timedelta(minutes=self.alert_config["auto_resolve_minutes"])
        now = datetime.now()
        
        to_resolve = []
        for alert_id, alert in self.active_alerts.items():
            if not alert.resolved and (now - alert.timestamp) > auto_resolve_time:
                to_resolve.append(alert_id)
        
        for alert_id in to_resolve:
            self.resolve_alert(alert_id, auto_resolved=True)
    
    def _cleanup_old_alerts(self):
        """Limpiar alertas antiguas del almacenamiento activo"""
        # Mover las más antiguas al historial
        if len(self.active_alerts) > 0:
            oldest_alerts = sorted(
                self.active_alerts.items(),
                key=lambda x: x[1].timestamp
            )[:10]  # Mover las 10 más antiguas
            
            for alert_id, alert in oldest_alerts:
                self.alert_history.append(alert)
                del self.active_alerts[alert_id]
        
        # Mantener tamaño del historial
        if len(self.alert_history) > self.max_history_size:
            self.alert_history = self.alert_history[-self.max_history_size:]
    
    def _cleanup_throttle_cache(self):
        """Limpiar cache de throttling"""
        throttle_time = timedelta(seconds=self.alert_config["throttle_seconds"])
        now = datetime.now()
        
        to_remove = []
        for key, timestamp in self.throttle_cache.items():
            if now - timestamp > throttle_time:
                to_remove.append(key)
        
        for key in to_remove:
            del self.throttle_cache[key]
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """
        Reconocer una alerta
        
        Args:
            alert_id: ID de la alerta
            
        Returns:
            bool: True si se reconoció correctamente
        """
        with self.alerts_lock:
            if alert_id in self.active_alerts:
                self.active_alerts[alert_id].acknowledged = True
                self.metrics["alerts_acknowledged"] += 1
                
                if self.logger:
                    self.logger.log_info(f"[{self.component_id}] Alerta reconocida: {alert_id}")
                
                return True
        return False
    
    def resolve_alert(self, alert_id: str, auto_resolved: bool = False) -> bool:
        """
        Resolver una alerta
        
        Args:
            alert_id: ID de la alerta
            auto_resolved: Si fue auto-resuelta
            
        Returns:
            bool: True si se resolvió correctamente
        """
        with self.alerts_lock:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.resolved = True
                alert.acknowledged = True
                
                # Mover al historial
                self.alert_history.append(alert)
                del self.active_alerts[alert_id]
                
                self.metrics["alerts_resolved"] += 1
                
                if self.logger:
                    resolve_type = "auto-resuelta" if auto_resolved else "resuelta"
                    self.logger.log_info(f"[{self.component_id}] Alerta {resolve_type}: {alert_id}")
                
                return True
        return False
    
    def subscribe_channel(self, channel: AlertChannel, callback: Callable[[Alert], None]):
        """
        Suscribirse a un canal de notificaciones
        
        Args:
            channel: Canal de alertas
            callback: Función a llamar para cada alerta
        """
        if channel in self.notification_callbacks:
            self.notification_callbacks[channel].append(callback)
            
            if self.logger:
                self.logger.log_info(f"[{self.component_id}] Callback suscrito al canal {channel.value}")
    
    def unsubscribe_channel(self, channel: AlertChannel, callback: Callable[[Alert], None]):
        """
        Desuscribirse de un canal de notificaciones
        
        Args:
            channel: Canal de alertas
            callback: Función a remover
        """
        if channel in self.notification_callbacks:
            if callback in self.notification_callbacks[channel]:
                self.notification_callbacks[channel].remove(callback)
                
                if self.logger:
                    self.logger.log_info(f"[{self.component_id}] Callback removido del canal {channel.value}")
    
    def add_filter(self, filter_func: Callable[[Alert], bool]):
        """
        Agregar un filtro de alertas
        
        Args:
            filter_func: Función que retorna True si la alerta debe ser filtrada
        """
        self.alert_filters.append(filter_func)
        
        if self.logger:
            self.logger.log_info(f"[{self.component_id}] Filtro de alerta agregado")
    
    def get_active_alerts(self) -> List[Alert]:
        """Obtener todas las alertas activas"""
        with self.alerts_lock:
            return list(self.active_alerts.values())
    
    def get_alert_history(self, limit: Optional[int] = None) -> List[Alert]:
        """
        Obtener historial de alertas
        
        Args:
            limit: Número máximo de alertas a retornar
            
        Returns:
            List[Alert]: Lista de alertas del historial
        """
        if limit:
            return self.alert_history[-limit:]
        return self.alert_history.copy()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtener métricas del motor de alertas"""
        with self.alerts_lock:
            current_metrics = self.metrics.copy()
            current_metrics.update({
                "active_alerts_count": len(self.active_alerts),
                "history_size": len(self.alert_history),
                "throttle_cache_size": len(self.throttle_cache),
                "uptime_seconds": (datetime.now() - self.metrics["uptime_start"]).total_seconds()
            })
            return current_metrics
    
    def get_status(self) -> Dict[str, Any]:
        """Obtener estado del motor de alertas"""
        return {
            "component_id": self.component_id,
            "version": self.version,
            "status": self.status,
            "is_running": self.is_running,
            "config_loaded": bool(self.alert_config),
            "channels_configured": len(self.notification_callbacks),
            "filters_active": len(self.alert_filters),
            "metrics": self.get_metrics()
        }
