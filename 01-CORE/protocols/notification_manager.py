#!/usr/bin/env python3
"""
📢 NOTIFICATION MANAGER - ICT ENGINE v6.0 ENTERPRISE
==================================================

Sistema centralizado de notificaciones para el ICT Engine.
Soporta múltiples canales (console, file, email, dashboard) 
y tipos de notificación con prioridades y filtros.

CARACTERÍSTICAS PRINCIPALES:
✅ Múltiples canales de notificación
✅ Prioridades y filtros avanzados
✅ Templates personalizables
✅ Rate limiting inteligente
✅ Historial y auditoría
✅ Integración con ConfigManager
✅ Retry automático para fallos
✅ Notificaciones batch y streaming

Autor: ICT Engine v6.0 Enterprise Team
Fecha: 15 Septiembre 2025
"""

import os
import json
import smtplib
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
import logging
import asyncio
from collections import defaultdict, deque

# Imports seguros
try:
    from ..smart_trading_logger import SmartTradingLogger
    LOGGER_AVAILABLE = True
except ImportError:
    LOGGER_AVAILABLE = False
    SmartTradingLogger = None

try:
    # Ajustar ruta correcta hacia config_manager (subir un nivel a config)
    from ..config.config_manager import get_config  # type: ignore
    CONFIG_AVAILABLE = True
except ImportError:  # Fallback seguro
    CONFIG_AVAILABLE = False
    def get_config(key: str, default=None):  # type: ignore
        return default


class NotificationPriority(Enum):
    """🚨 Prioridades de notificación"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class NotificationType(Enum):
    """📋 Tipos de notificación"""
    # System notifications
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"
    SYSTEM_ERROR = "system_error"
    SYSTEM_WARNING = "system_warning"
    
    # Trading notifications
    ORDER_BLOCK_DETECTED = "order_block_detected"
    PATTERN_CONFIRMED = "pattern_confirmed"
    TRADE_OPENED = "trade_opened"
    TRADE_CLOSED = "trade_closed"
    
    # Risk notifications
    RISK_THRESHOLD_EXCEEDED = "risk_threshold_exceeded"
    DRAWDOWN_WARNING = "drawdown_warning"
    EMERGENCY_STOP = "emergency_stop"
    
    # MT5 notifications
    MT5_CONNECTION_LOST = "mt5_connection_lost"
    MT5_CONNECTION_RESTORED = "mt5_connection_restored"
    MT5_ERROR = "mt5_error"
    
    # Performance notifications
    PERFORMANCE_ALERT = "performance_alert"
    MEMORY_WARNING = "memory_warning"
    CPU_WARNING = "cpu_warning"
    
    # Custom
    CUSTOM = "custom"


class NotificationChannel(Enum):
    """📡 Canales de notificación"""
    CONSOLE = "console"
    FILE = "file"
    EMAIL = "email"
    DASHBOARD = "dashboard"
    WEBHOOK = "webhook"
    TELEGRAM = "telegram"  # Para futuro


@dataclass
class NotificationTemplate:
    """📝 Template para notificaciones"""
    type: NotificationType
    channel: NotificationChannel
    title_template: str
    body_template: str
    format: str = "text"  # text, html, markdown
    variables: List[str] = field(default_factory=list)


@dataclass
class Notification:
    """📢 Estructura de notificación"""
    id: str
    type: NotificationType
    priority: NotificationPriority
    title: str
    message: str
    timestamp: datetime
    data: Dict[str, Any] = field(default_factory=dict)
    channels: List[NotificationChannel] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    sent_to: List[NotificationChannel] = field(default_factory=list)
    failed_channels: List[NotificationChannel] = field(default_factory=list)


class NotificationHandler:
    """🔧 Handler base para canales de notificación"""
    
    def __init__(self, channel: NotificationChannel, config: Optional[Dict[str, Any]] = None):
        self.channel = channel
        self.config = config or {}
        self.enabled = self.config.get('enabled', True)
        self.rate_limit = self.config.get('rate_limit', 0)  # 0 = no limit
        self._last_sent = {}
        self._send_history = deque(maxlen=1000)
    
    async def send(self, notification: Notification) -> bool:
        """📤 Enviar notificación"""
        if not self.enabled:
            return False
        
        # Check rate limiting
        if self._is_rate_limited(notification):
            return False
        
        try:
            success = await self._send_impl(notification)
            
            # Record send history
            self._send_history.append({
                'timestamp': datetime.now(),
                'notification_id': notification.id,
                'success': success
            })
            
            return success
            
        except Exception as e:
            logging.error(f"Error sending notification via {self.channel.value}: {e}")
            return False
    
    def _is_rate_limited(self, notification: Notification) -> bool:
        """⏱️ Verificar rate limiting"""
        if self.rate_limit <= 0:
            return False
        
        now = datetime.now()
        key = f"{notification.type.value}:{notification.priority.value}"
        
        if key in self._last_sent:
            elapsed = (now - self._last_sent[key]).total_seconds()
            if elapsed < self.rate_limit:
                return True
        
        self._last_sent[key] = now
        return False
    
    async def _send_impl(self, notification: Notification) -> bool:
        """🔧 Implementación específica del canal"""
        raise NotImplementedError("Must implement _send_impl")


class ConsoleHandler(NotificationHandler):
    """🖥️ Handler para notificaciones de consola"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(NotificationChannel.CONSOLE, config)
        self.colors = {
            NotificationPriority.LOW: '\033[37m',      # White
            NotificationPriority.MEDIUM: '\033[36m',   # Cyan
            NotificationPriority.HIGH: '\033[33m',     # Yellow
            NotificationPriority.CRITICAL: '\033[31m', # Red
            NotificationPriority.EMERGENCY: '\033[35m' # Magenta
        }
        self.color_reset = '\033[0m'
    
    async def _send_impl(self, notification: Notification) -> bool:
        """🖨️ Imprimir notificación en consola"""
        try:
            color = self.colors.get(notification.priority, '')
            timestamp = notification.timestamp.strftime("%H:%M:%S")
            priority_icon = self._get_priority_icon(notification.priority)
            
            message = (
                f"{color}[{timestamp}] {priority_icon} "
                f"{notification.title}{self.color_reset}\n"
                f"{notification.message}"
            )
            
            print(message)
            return True
            
        except Exception as e:
            logging.error(f"Console handler error: {e}")
            return False
    
    def _get_priority_icon(self, priority: NotificationPriority) -> str:
        """🎯 Obtener icono por prioridad"""
        icons = {
            NotificationPriority.LOW: "ℹ️",
            NotificationPriority.MEDIUM: "⚠️",
            NotificationPriority.HIGH: "🔥",
            NotificationPriority.CRITICAL: "🚨",
            NotificationPriority.EMERGENCY: "💥"
        }
        return icons.get(priority, "📢")


class FileHandler(NotificationHandler):
    """📁 Handler para notificaciones en archivo"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(NotificationChannel.FILE, config)
        cfg = config or {}
        self.file_path = Path(cfg.get('file_path', '05-LOGS/general/notifications.jsonl'))
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._file_lock = threading.Lock()
    
    async def _send_impl(self, notification: Notification) -> bool:
        """💾 Escribir notificación a archivo"""
        try:
            with self._file_lock:
                notification_data = {
                    'id': notification.id,
                    'type': notification.type.value,
                    'priority': notification.priority.value,
                    'title': notification.title,
                    'message': notification.message,
                    'timestamp': notification.timestamp.isoformat(),
                    'data': notification.data
                }
                
                with open(self.file_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(notification_data, ensure_ascii=False) + '\n')
                
                return True
                
        except Exception as e:
            logging.error(f"File handler error: {e}")
            return False


class EmailHandler(NotificationHandler):
    """📧 Handler para notificaciones por email"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(NotificationChannel.EMAIL, config)
        cfg = config or {}
        self.smtp_server = cfg.get('smtp_server', 'localhost')
        self.smtp_port = cfg.get('smtp_port', 587)
        self.username = cfg.get('username', '')
        self.password = cfg.get('password', '')
        self.from_email = cfg.get('from_email', 'ict-engine@localhost')
        self.to_emails = cfg.get('to_emails', [])
        self.use_tls = cfg.get('use_tls', True)
    
    async def _send_impl(self, notification: Notification) -> bool:
        """📨 Enviar notificación por email"""
        if not self.to_emails:
            return False
        
        try:
            # Crear mensaje
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[ICT Engine] {notification.title}"
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            msg['Date'] = formatdate(localtime=True)
            
            # Crear contenido
            text_content = self._create_text_content(notification)
            html_content = self._create_html_content(notification)
            
            msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))
            
            # Enviar
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                if self.username:
                    server.login(self.username, self.password)
                
                server.sendmail(self.from_email, self.to_emails, msg.as_string())
            
            return True
            
        except Exception as e:
            logging.error(f"Email handler error: {e}")
            return False
    
    def _create_text_content(self, notification: Notification) -> str:
        """📝 Crear contenido de texto"""
        content = f"""
ICT Engine v6.0 Enterprise - Notification

Type: {notification.type.value}
Priority: {notification.priority.value}
Time: {notification.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

{notification.title}

{notification.message}

---
Additional Data:
{json.dumps(notification.data, indent=2) if notification.data else 'None'}
        """
        return content.strip()
    
    def _create_html_content(self, notification: Notification) -> str:
        """🎨 Crear contenido HTML"""
        priority_colors = {
            NotificationPriority.LOW: '#6c757d',
            NotificationPriority.MEDIUM: '#17a2b8',
            NotificationPriority.HIGH: '#ffc107',
            NotificationPriority.CRITICAL: '#dc3545',
            NotificationPriority.EMERGENCY: '#6f42c1'
        }
        
        color = priority_colors.get(notification.priority, '#6c757d')
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 20px;">
            <div style="border-left: 5px solid {color}; padding-left: 20px;">
                <h2 style="color: {color}; margin: 0;">ICT Engine v6.0 Enterprise</h2>
                <p style="color: #666; margin: 5px 0;">Notification Alert</p>
            </div>
            
            <div style="margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-radius: 5px;">
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="font-weight: bold; padding: 5px 10px 5px 0;">Type:</td>
                        <td style="padding: 5px 0;">{notification.type.value}</td>
                    </tr>
                    <tr>
                        <td style="font-weight: bold; padding: 5px 10px 5px 0;">Priority:</td>
                        <td style="padding: 5px 0; color: {color}; font-weight: bold;">{notification.priority.value.upper()}</td>
                    </tr>
                    <tr>
                        <td style="font-weight: bold; padding: 5px 10px 5px 0;">Time:</td>
                        <td style="padding: 5px 0;">{notification.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</td>
                    </tr>
                </table>
            </div>
            
            <div style="margin: 20px 0;">
                <h3 style="color: {color};">{notification.title}</h3>
                <p style="line-height: 1.6; color: #333;">{notification.message}</p>
            </div>
            
            <div style="margin-top: 30px; padding: 15px; background-color: #e9ecef; border-radius: 5px; font-size: 12px; color: #6c757d;">
                <p style="margin: 0;"><strong>ICT Engine v6.0 Enterprise</strong> - Automated Trading System</p>
                <p style="margin: 5px 0 0 0;">Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </body>
        </html>
        """
        
        return html_content


class DashboardHandler(NotificationHandler):
    """📊 Handler para notificaciones de dashboard"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(NotificationChannel.DASHBOARD, config)
        cfg = config or {}
        self.notifications_file = Path('04-DATA/notifications/dashboard_notifications.json')
        self.notifications_file.parent.mkdir(parents=True, exist_ok=True)
        self.max_notifications = cfg.get('max_notifications', 100)
        self._file_lock = threading.Lock()
    
    async def _send_impl(self, notification: Notification) -> bool:
        """📊 Guardar notificación para dashboard"""
        try:
            with self._file_lock:
                # Cargar notificaciones existentes
                notifications = []
                if self.notifications_file.exists():
                    with open(self.notifications_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        notifications = data.get('notifications', [])
                
                # Agregar nueva notificación
                notification_data = {
                    'id': notification.id,
                    'type': notification.type.value,
                    'priority': notification.priority.value,
                    'title': notification.title,
                    'message': notification.message,
                    'timestamp': notification.timestamp.isoformat(),
                    'data': notification.data
                }
                
                notifications.insert(0, notification_data)  # Más reciente primero
                
                # Limitar cantidad
                notifications = notifications[:self.max_notifications]
                
                # Guardar
                with open(self.notifications_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'notifications': notifications,
                        'last_updated': datetime.now().isoformat(),
                        'total_count': len(notifications)
                    }, f, indent=2, ensure_ascii=False)
                
                return True
                
        except Exception as e:
            logging.error(f"Dashboard handler error: {e}")
            return False


class NotificationManager:
    """
    📢 GESTOR DE NOTIFICACIONES ENTERPRISE
    ====================================
    
    Sistema centralizado para gestionar todas las notificaciones del ICT Engine.
    Soporta múltiples canales, prioridades y tipos con retry automático.
    """
    
    def __init__(self, config_manager=None):
        """
        Inicializar NotificationManager
        
        Args:
            config_manager: Gestor de configuración (opcional)
        """
        # Logger
        self.logger = self._setup_logger()
        
        # Config
        self.config = config_manager
        
        # Handlers
        self.handlers: Dict[NotificationChannel, NotificationHandler] = {}
        self._setup_handlers()
        
        # Templates
        self.templates: Dict[str, NotificationTemplate] = {}
        self._setup_default_templates()
        
        # Notification queue y workers
        self.notification_queue = asyncio.Queue()
        self.retry_queue = asyncio.Queue()
        self._workers_running = False
        self._worker_tasks = []
        
        # Statistics
        self.stats = {
            'total_sent': 0,
            'total_failed': 0,
            'by_channel': defaultdict(int),
            'by_priority': defaultdict(int),
            'by_type': defaultdict(int),
            'last_notification': None
        }
        
        # History
        self.notification_history = deque(maxlen=1000)
        
        # Thread safety
        self._lock = threading.RLock()
        
        self.logger.info("✅ NotificationManager initialized")
    
    def _setup_logger(self) -> logging.Logger:
        """📝 Configurar logger con compatibilidad de tipos"""
        if LOGGER_AVAILABLE and SmartTradingLogger:
            raw_logger = SmartTradingLogger("NotificationManager")
            if isinstance(raw_logger, logging.Logger):  # ya compatible
                return raw_logger
            base_logger = logging.getLogger("NotificationManager")
            if not base_logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                base_logger.addHandler(handler)
                base_logger.setLevel(logging.INFO)

            class _Adapter(logging.Logger):  # type: ignore[misc]
                def __init__(self, delegate: Any):
                    super().__init__("NotificationManagerAdapter")
                    self._delegate = delegate
                    for h in base_logger.handlers:
                        self.addHandler(h)
                    self.setLevel(base_logger.level)

                def info(self, msg: str, *a: Any, **kw: Any) -> None:
                    try:
                        self._delegate.info(msg, *a, **kw)
                    except AttributeError:
                        base_logger.info(msg, *a, **kw)

                def warning(self, msg: str, *a: Any, **kw: Any) -> None:
                    try:
                        self._delegate.warning(msg, *a, **kw)
                    except AttributeError:
                        base_logger.warning(msg, *a, **kw)

                def error(self, msg: str, *a: Any, **kw: Any) -> None:
                    try:
                        self._delegate.error(msg, *a, **kw)
                    except AttributeError:
                        base_logger.error(msg, *a, **kw)

                def debug(self, msg: str, *a: Any, **kw: Any) -> None:
                    try:
                        self._delegate.debug(msg, *a, **kw)
                    except AttributeError:
                        base_logger.debug(msg, *a, **kw)

                def exception(self, msg: str, *a: Any, **kw: Any) -> None:
                    try:
                        self._delegate.exception(msg, *a, **kw)
                    except AttributeError:
                        base_logger.exception(msg, *a, **kw)

            return _Adapter(raw_logger)
        logger = logging.getLogger("NotificationManager")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _setup_handlers(self):
        """⚙️ Configurar handlers de notificación"""
        # Configuración por defecto
        default_config = {
            'console': {'enabled': True},
            'file': {'enabled': True, 'file_path': '05-LOGS/general/notifications.jsonl'},
            'email': {'enabled': False},  # Configurar según entorno
            'dashboard': {'enabled': True, 'max_notifications': 100}
        }
        
        # Usar configuración del ConfigManager si está disponible
        if CONFIG_AVAILABLE:
            alerts_raw = get_config('alerts.channels', default_config)
        else:
            alerts_raw = default_config
        alerts_config: Dict[str, Any] = alerts_raw if isinstance(alerts_raw, dict) else default_config
        
        # Crear handlers
        if alerts_config.get('console', {}).get('enabled', False):
            self.handlers[NotificationChannel.CONSOLE] = ConsoleHandler(alerts_config.get('console', {}))
        
        if alerts_config.get('file', {}).get('enabled', False):
            self.handlers[NotificationChannel.FILE] = FileHandler(alerts_config.get('file', {}))
        
        if alerts_config.get('email', {}).get('enabled', False):
            email_config = alerts_config.get('email', {})
            # Agregar configuración de email desde ConfigManager o environment
            email_config.update({
                'smtp_server': get_config('email.smtp_server', 'localhost') if CONFIG_AVAILABLE else 'localhost',
                'smtp_port': get_config('email.smtp_port', 587) if CONFIG_AVAILABLE else 587,
                'username': get_config('email.username', '') if CONFIG_AVAILABLE else '',
                'password': get_config('email.password', '') if CONFIG_AVAILABLE else '',
                'from_email': get_config('email.from_email', 'ict-engine@localhost') if CONFIG_AVAILABLE else 'ict-engine@localhost',
                'to_emails': get_config('email.to_emails', []) if CONFIG_AVAILABLE else []
            })
            self.handlers[NotificationChannel.EMAIL] = EmailHandler(email_config)
        
        if alerts_config.get('dashboard', {}).get('enabled', False):
            self.handlers[NotificationChannel.DASHBOARD] = DashboardHandler(alerts_config.get('dashboard', {}))
        
        self.logger.info(f"✅ Initialized {len(self.handlers)} notification handlers")
    
    def _setup_default_templates(self):
        """📋 Configurar templates por defecto"""
        # System templates
        self.templates['system_start'] = NotificationTemplate(
            type=NotificationType.SYSTEM_START,
            channel=NotificationChannel.CONSOLE,
            title_template="🚀 System Started",
            body_template="ICT Engine v6.0 Enterprise has started successfully at {timestamp}"
        )
        
        self.templates['order_block_detected'] = NotificationTemplate(
            type=NotificationType.ORDER_BLOCK_DETECTED,
            channel=NotificationChannel.DASHBOARD,
            title_template="📊 Order Block Detected",
            body_template="New order block detected on {symbol} at {price} ({timeframe})"
        )
        
        self.templates['risk_threshold_exceeded'] = NotificationTemplate(
            type=NotificationType.RISK_THRESHOLD_EXCEEDED,
            channel=NotificationChannel.EMAIL,
            title_template="🚨 Risk Threshold Exceeded",
            body_template="Risk threshold exceeded: {metric} = {value} (limit: {limit})"
        )
        
        # Más templates según sea necesario...
    
    async def start_workers(self, num_workers: int = 3):
        """👷 Iniciar workers de procesamiento"""
        if self._workers_running:
            return
        
        self._workers_running = True
        
        # Worker principal
        self._worker_tasks.append(
            asyncio.create_task(self._notification_worker())
        )
        
        # Workers de retry
        for i in range(num_workers - 1):
            self._worker_tasks.append(
                asyncio.create_task(self._retry_worker())
            )
        
        self.logger.info(f"✅ Started {len(self._worker_tasks)} notification workers")
    
    async def stop_workers(self):
        """🛑 Detener workers"""
        self._workers_running = False
        
        # Cancelar tasks
        for task in self._worker_tasks:
            task.cancel()
        
        # Esperar a que terminen
        await asyncio.gather(*self._worker_tasks, return_exceptions=True)
        
        self._worker_tasks.clear()
        self.logger.info("✅ Stopped all notification workers")
    
    async def _notification_worker(self):
        """👷 Worker principal de notificaciones"""
        while self._workers_running:
            try:
                # Obtener notificación de la cola
                notification = await asyncio.wait_for(
                    self.notification_queue.get(),
                    timeout=1.0
                )
                
                await self._process_notification(notification)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error in notification worker: {e}")
    
    async def _retry_worker(self):
        """🔄 Worker de reintentos"""
        while self._workers_running:
            try:
                # Obtener notificación de retry
                notification = await asyncio.wait_for(
                    self.retry_queue.get(),
                    timeout=2.0
                )
                
                # Esperar antes de reintentar
                await asyncio.sleep(2 ** notification.retry_count)  # Backoff exponencial
                
                await self._process_notification(notification)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error in retry worker: {e}")
    
    async def _process_notification(self, notification: Notification):
        """🔄 Procesar notificación individual"""
        try:
            success_channels = []
            failed_channels = []
            
            # Determinar canales si no están especificados
            if not notification.channels:
                notification.channels = self._get_default_channels(notification)
            
            # Enviar a cada canal
            for channel in notification.channels:
                if channel not in self.handlers:
                    failed_channels.append(channel)
                    continue
                
                try:
                    success = await self.handlers[channel].send(notification)
                    
                    if success:
                        success_channels.append(channel)
                        self.stats['by_channel'][channel.value] += 1
                    else:
                        failed_channels.append(channel)
                        
                except Exception as e:
                    self.logger.error(f"Error sending to {channel.value}: {e}")
                    failed_channels.append(channel)
            
            # Actualizar estadísticas
            notification.sent_to.extend(success_channels)
            notification.failed_channels.extend(failed_channels)
            
            if success_channels:
                self.stats['total_sent'] += len(success_channels)
                self.stats['by_priority'][notification.priority.value] += 1
                self.stats['by_type'][notification.type.value] += 1
                self.stats['last_notification'] = datetime.now().isoformat()
            
            if failed_channels and notification.retry_count < notification.max_retries:
                # Reencolar para retry solo en canales fallidos
                notification.channels = failed_channels
                notification.retry_count += 1
                await self.retry_queue.put(notification)
            elif failed_channels:
                self.stats['total_failed'] += len(failed_channels)
            
            # Agregar al historial
            with self._lock:
                self.notification_history.append({
                    'id': notification.id,
                    'timestamp': notification.timestamp.isoformat(),
                    'type': notification.type.value,
                    'priority': notification.priority.value,
                    'success_channels': [c.value for c in success_channels],
                    'failed_channels': [c.value for c in failed_channels],
                    'retry_count': notification.retry_count
                })
                
        except Exception as e:
            self.logger.error(f"Error processing notification {notification.id}: {e}")
    
    def _get_default_channels(self, notification: Notification) -> List[NotificationChannel]:
        """📡 Obtener canales por defecto según tipo y prioridad"""
        channels = []
        
        # Según prioridad
        if notification.priority in [NotificationPriority.CRITICAL, NotificationPriority.EMERGENCY]:
            channels.extend([NotificationChannel.CONSOLE, NotificationChannel.FILE, NotificationChannel.EMAIL, NotificationChannel.DASHBOARD])
        elif notification.priority == NotificationPriority.HIGH:
            channels.extend([NotificationChannel.CONSOLE, NotificationChannel.FILE, NotificationChannel.DASHBOARD])
        elif notification.priority == NotificationPriority.MEDIUM:
            channels.extend([NotificationChannel.FILE, NotificationChannel.DASHBOARD])
        else:  # LOW
            channels.extend([NotificationChannel.FILE])
        
        # Filtrar solo canales disponibles
        return [c for c in channels if c in self.handlers]
    
    def notify(self,
               type: Union[NotificationType, str],
               title: str,
               message: str,
               priority: NotificationPriority = NotificationPriority.MEDIUM,
               data: Optional[Dict[str, Any]] = None,
               channels: Optional[List[NotificationChannel]] = None) -> str:
        """
        📢 Enviar notificación
        
        Args:
            type: Tipo de notificación
            title: Título de la notificación
            message: Mensaje de la notificación  
            priority: Prioridad de la notificación
            data: Datos adicionales
            channels: Canales específicos (opcional)
            
        Returns:
            ID de la notificación
        """
        try:
            # Convertir type si es string
            if isinstance(type, str):
                try:
                    type = NotificationType(type)
                except ValueError:
                    type = NotificationType.CUSTOM
            
            # Generar ID único
            notification_id = f"ntf_{int(time.time() * 1000)}"
            
            # Crear notificación
            notification = Notification(
                id=notification_id,
                type=type,
                priority=priority,
                title=title,
                message=message,
                timestamp=datetime.now(),
                data=data or {},
                channels=channels or []
            )
            
            # Agregar a la cola
            if self._workers_running:
                asyncio.create_task(self.notification_queue.put(notification))
            else:
                # Si no hay workers, procesar sincrónicamente
                asyncio.run(self._process_notification(notification))
            
            self.logger.debug(f"📢 Notification queued: {notification_id} - {title}")
            return notification_id
            
        except Exception as e:
            self.logger.error(f"Error creating notification: {e}")
            return ""
    
    def notify_system_start(self):
        """🚀 Notificación de inicio del sistema"""
        return self.notify(
            NotificationType.SYSTEM_START,
            "Sistema ICT Engine Iniciado",
            f"ICT Engine v6.0 Enterprise se ha iniciado exitosamente a las {datetime.now().strftime('%H:%M:%S')}",
            NotificationPriority.MEDIUM
        )
    
    def notify_order_block_detected(self, symbol: str, price: float, timeframe: str, data: Optional[Dict[str, Any]] = None):
        """📊 Notificación de order block detectado"""
        return self.notify(
            NotificationType.ORDER_BLOCK_DETECTED,
            f"Order Block Detectado - {symbol}",
            f"Nuevo order block detectado en {symbol} a precio {price} en timeframe {timeframe}",
            NotificationPriority.MEDIUM,
            data or {'symbol': symbol, 'price': price, 'timeframe': timeframe}
        )
    
    def notify_risk_threshold_exceeded(self, metric: str, value: float, limit: float):
        """🚨 Notificación de umbral de riesgo excedido"""
        return self.notify(
            NotificationType.RISK_THRESHOLD_EXCEEDED,
            "Umbral de Riesgo Excedido",
            f"El indicador {metric} ha alcanzado {value:.2f}, superando el límite de {limit:.2f}",
            NotificationPriority.HIGH,
            {'metric': metric, 'value': value, 'limit': limit}
        )
    
    def notify_mt5_connection_lost(self):
        """🔌 Notificación de conexión MT5 perdida"""
        return self.notify(
            NotificationType.MT5_CONNECTION_LOST,
            "Conexión MT5 Perdida",
            "Se ha perdido la conexión con MetaTrader 5. Intentando reconectar...",
            NotificationPriority.CRITICAL
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """📊 Obtener estadísticas de notificaciones"""
        with self._lock:
            return {
                'total_sent': self.stats['total_sent'],
                'total_failed': self.stats['total_failed'],
                'by_channel': dict(self.stats['by_channel']),
                'by_priority': dict(self.stats['by_priority']),
                'by_type': dict(self.stats['by_type']),
                'last_notification': self.stats['last_notification'],
                'queue_size': self.notification_queue.qsize() if hasattr(self.notification_queue, 'qsize') else 0,
                'retry_queue_size': self.retry_queue.qsize() if hasattr(self.retry_queue, 'qsize') else 0,
                'handlers_count': len(self.handlers),
                'workers_running': self._workers_running,
                'history_count': len(self.notification_history)
            }
    
    def get_recent_notifications(self, limit: int = 50) -> List[Dict[str, Any]]:
        """📋 Obtener notificaciones recientes"""
        with self._lock:
            return list(self.notification_history)[-limit:]
    
    def health_check(self) -> Dict[str, Any]:
        """🏥 Verificar salud del sistema de notificaciones"""
        try:
            status = {
                'status': 'healthy',
                'handlers': {
                    channel.value: {'enabled': handler.enabled}
                    for channel, handler in self.handlers.items()
                },
                'workers_running': self._workers_running,
                'queue_sizes': {
                    'notification_queue': self.notification_queue.qsize() if hasattr(self.notification_queue, 'qsize') else 0,
                    'retry_queue': self.retry_queue.qsize() if hasattr(self.retry_queue, 'qsize') else 0
                },
                'statistics': self.get_statistics(),
                'errors': []
            }
            
            # Verificar handlers
            for channel, handler in self.handlers.items():
                if not handler.enabled:
                    status['errors'].append(f"Handler {channel.value} is disabled")
            
            # Verificar workers
            if not self._workers_running:
                status['errors'].append("Notification workers are not running")
            
            if status['errors']:
                status['status'] = 'degraded'
            
            return status
            
        except Exception as e:
            return {
                'status': 'critical',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


# Singleton instance
_global_notification_manager: Optional[NotificationManager] = None
_notification_lock = threading.Lock()


def get_notification_manager(config_manager=None, force_new: bool = False) -> NotificationManager:
    """
    🏭 Factory function para obtener NotificationManager singleton
    
    Args:
        config_manager: Gestor de configuración
        force_new: Forzar nueva instancia
        
    Returns:
        Instancia de NotificationManager
    """
    global _global_notification_manager
    
    with _notification_lock:
        if _global_notification_manager is None or force_new:
            _global_notification_manager = NotificationManager(config_manager)
        
        return _global_notification_manager


def notify(type: Union[NotificationType, str],
          title: str,
          message: str,
          priority: NotificationPriority = NotificationPriority.MEDIUM,
          data: Optional[Dict[str, Any]] = None,
          channels: Optional[List[NotificationChannel]] = None) -> str:
    """
    🎯 Función de conveniencia para enviar notificación
    """
    return get_notification_manager().notify(type, title, message, priority, data, channels)


async def test_notification_manager():
    """🧪 Test function para validar NotificationManager"""
    print("🧪 Testing NotificationManager...")
    
    try:
        # Test initialization
        notif_manager = NotificationManager()
        print("✅ NotificationManager initialized successfully")
        
        # Start workers
        await notif_manager.start_workers()
        print("✅ Workers started")
        
        # Test notifications
        id1 = notif_manager.notify(
            NotificationType.SYSTEM_START,
            "Test Notification",
            "This is a test notification",
            NotificationPriority.HIGH
        )
        print(f"✅ Notification sent: {id1}")
        
        # Wait a bit for processing
        await asyncio.sleep(2)
        
        # Check statistics
        stats = notif_manager.get_statistics()
        print(f"✅ Statistics: {stats['total_sent']} sent, {stats['total_failed']} failed")
        
        # Health check
        health = notif_manager.health_check()
        print(f"✅ Health check: {health['status']}")
        
        # Stop workers
        await notif_manager.stop_workers()
        print("✅ Workers stopped")
        
        print("🎉 NotificationManager test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ NotificationManager test failed: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(test_notification_manager())