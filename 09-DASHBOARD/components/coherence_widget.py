#!/usr/bin/env python3
"""
🎯 COHERENCE ANALYSIS WIDGET - WIDGET DE ANÁLISIS DE COHERENCIA
=============================================================

Widget para mostrar análisis de coherencia del mercado.
"""

from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from typing import Dict, Any

class CoherenceAnalysisWidget:
    """Widget de análisis de coherencia"""
    
    def render(self, coherence_data: Dict[str, Any]) -> Panel:
        """Renderizar widget de análisis de coherencia"""
        
        # Crear contenido de coherencia
        content = Text()
        
        # Título
        content.append("🧠 ANÁLISIS DE COHERENCIA\n\n", style="bold magenta")
        
        # Métricas principales
        volatility = coherence_data.get('volatility', 0)
        momentum = coherence_data.get('momentum', 0)
        coherence_score = coherence_data.get('coherence_score', 0)
        kill_zone = coherence_data.get('kill_zone_active', False)
        
        # Color coding para métricas
        vol_color = "green" if volatility >= 8 else "yellow" if volatility >= 5 else "red"
        momentum_color = "green" if momentum > 0 else "red"
        score_color = "green" if coherence_score >= 70 else "yellow" if coherence_score >= 50 else "red"
        
        content.append(f"📊 Volatilidad: ", style="white")
        content.append(f"{volatility:.1f} pips\n", style=vol_color)
        
        content.append(f"⚡ Momentum: ", style="white")
        content.append(f"{momentum:+.2f} pips\n", style=momentum_color)
        
        content.append(f"🎯 Score Coherencia: ", style="white")
        content.append(f"{coherence_score}/100\n", style=score_color)
        
        content.append(f"🕒 Kill Zone: ", style="white")
        kz_text = "✅ ACTIVA" if kill_zone else "❌ INACTIVA"
        kz_color = "green" if kill_zone else "red"
        content.append(f"{kz_text}\n\n", style=kz_color)
        
        # Estado del mercado
        market_state = coherence_data.get('market_state', 'N/A')
        content.append(f"📈 Estado: ", style="white")
        state_color = "green" if "NORMAL" in market_state else "yellow" if "CAUTIOUS" in market_state else "red"
        content.append(f"{market_state}\n\n", style=state_color)
        
        # Recomendación
        recommendation = coherence_data.get('trading_recommendation', {})
        if recommendation:
            content.append("💡 RECOMENDACIÓN:\n", style="bold yellow")
            content.append(f"• Acción: {recommendation.get('action', 'N/A')}\n", style="cyan")
            content.append(f"• Razón: {recommendation.get('reason', 'N/A')}\n", style="white")
            confidence = recommendation.get('confidence', 0)
            conf_color = "green" if confidence >= 80 else "yellow" if confidence >= 60 else "red"
            content.append(f"• Confianza: {confidence}%", style=conf_color)
        
        return Panel(content, title="🧠 Market Coherence Analysis", border_style="magenta")
