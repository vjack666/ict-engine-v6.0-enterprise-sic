#!/usr/bin/env python3
"""
🎯 MARKET DATA WIDGET - WIDGET DE DATOS DE MERCADO
===============================================

Widget para mostrar datos de mercado en tiempo real.
"""

from rich.panel import Panel
from rich.table import Table
from typing import Dict, Any

class MarketDataWidget:
    """Widget de datos de mercado"""
    
    def render(self, market_data: Dict[str, Any]) -> Panel:
        """Renderizar widget de datos de mercado"""
        
        # Crear tabla de mercado
        table = Table(title="💹 Market Data", show_header=True, header_style="bold cyan")
        table.add_column("Símbolo", style="white", no_wrap=True)
        table.add_column("Precio", style="yellow")
        table.add_column("Cambio", style="green")
        table.add_column("Volatilidad", style="blue")
        table.add_column("Tendencia", style="magenta")
        
        # Agregar datos de cada símbolo
        for symbol, data in market_data.items():
            trend_color = "green" if data['trend'] == 'bullish' else "red" if data['trend'] == 'bearish' else "yellow"
            change_color = "green" if data['change_pips'] >= 0 else "red"
            
            table.add_row(
                symbol,
                f"{data['price']:.5f}",
                f"[{change_color}]{data['change_pips']:+.1f} pips[/{change_color}]",
                f"{data['volatility']:.1f} pips",
                f"[{trend_color}]{data['trend']}[/{trend_color}]"
            )
        
        return Panel(table, title="📊 Real-Time Market Data", border_style="cyan")
