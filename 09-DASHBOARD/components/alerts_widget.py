#!/usr/bin/env python3
"""
🎯 ALERTS WIDGET - WIDGET DE ALERTAS
================================

Widget para mostrar alertas del sistema.
"""

from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from typing import Dict, Any, List
from datetime import datetime

class AlertsWidget:
    """Widget de alertas del sistema"""
    
    def render(self, alerts: List[Dict[str, Any]]) -> Panel:
        """Renderizar widget de alertas"""
        
        if not alerts:
            content = Text("✅ No hay alertas activas", style="green")
            return Panel(content, title="🚨 System Alerts", border_style="green")
        
        # Crear tabla de alertas
        table = Table(show_header=True, header_style="bold red")
        table.add_column("Severidad", style="white", no_wrap=True, width=10)
        table.add_column("Mensaje", style="white", min_width=30)
        table.add_column("Tiempo", style="dim", width=12)
        
        # Agregar alertas (máximo 8 más recientes)
        recent_alerts = alerts[-8:] if len(alerts) > 8 else alerts
        
        for alert in reversed(recent_alerts):  # Más recientes primero
            severity = alert.get('severity', 'low')
            
            # Color coding por severidad
            severity_icons = {
                'low': '🔵 LOW',
                'medium': '🟡 MED', 
                'high': '🟠 HIGH',
                'critical': '🔴 CRIT'
            }
            
            severity_colors = {
                'low': 'blue',
                'medium': 'yellow',
                'high': 'orange3', 
                'critical': 'red'
            }
            
            severity_text = severity_icons.get(severity, '⚪ UNK')
            severity_color = severity_colors.get(severity, 'white')
            
            # Formatear mensaje (truncar si es muy largo)
            message = alert.get('message', 'Sin mensaje')
            if len(message) > 40:
                message = message[:37] + "..."
            
            # Formatear tiempo
            timestamp = alert.get('timestamp')
            if isinstance(timestamp, datetime):
                time_str = timestamp.strftime('%H:%M:%S')
            elif isinstance(timestamp, str):
                try:
                    time_str = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).strftime('%H:%M:%S')
                except:
                    time_str = 'N/A'
            else:
                time_str = 'N/A'
            
            table.add_row(
                f"[{severity_color}]{severity_text}[/{severity_color}]",
                message,
                time_str
            )
        
        # Agregar resumen si hay muchas alertas
        if len(alerts) > 8:
            summary_text = f"\n💡 Mostrando las 8 alertas más recientes de {len(alerts)} total"
            table.caption = summary_text
        
        return Panel(table, title="🚨 System Alerts", border_style="red")
