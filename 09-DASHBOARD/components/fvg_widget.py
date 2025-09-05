#!/usr/bin/env python3
"""
🎯 FVG STATS WIDGET - WIDGET DE ESTADÍSTICAS FVG
==============================================

Widget para mostrar estadísticas de Fair Value Gaps.
"""

from rich.panel import Panel
from rich.table import Table
from typing import Dict, Any

class FVGStatsWidget:
    """Widget de estadísticas FVG"""
    
    def render(self, fvg_stats: Dict[str, Any]) -> Panel:
        """Renderizar widget de FVG stats"""
        
        # Crear tabla de estadísticas
        table = Table(title="📈 Fair Value Gaps", show_header=True, header_style="bold magenta")
        table.add_column("Métrica", style="cyan", no_wrap=True)
        table.add_column("Valor", style="green")
        
        # Agregar filas de estadísticas
        table.add_row("Total FVGs", str(fvg_stats.get('total_fvgs_all_pairs', 0)))
        table.add_row("FVGs Activos", str(fvg_stats.get('active_fvgs', 0)))
        table.add_row("Rellenados Hoy", str(fvg_stats.get('filled_fvgs_today', 0)))
        table.add_row("Gap Promedio", f"{fvg_stats.get('avg_gap_size_pips', 0):.2f} pips")
        table.add_row("Tasa de Éxito", f"{fvg_stats.get('success_rate_percent', 0):.1f}%")
        
        return Panel(table, title="📊 FVG Statistics", border_style="blue")
