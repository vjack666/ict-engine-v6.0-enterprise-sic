#!/usr/bin/env python3
"""
🔧 CATEGORIZADOR AUTOMÁTICO DE LOGS
ICT Engine v6.0 Enterprise - Categoriza logs según reglas definidas
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

class LogCategorizer:
    """🔧 Sistema de categorización automática de logs"""
    
    def __init__(self):
        self.rules = self._load_rules()
        
    def _load_rules(self) -> Dict:
        """Cargar reglas de categorización"""
        rules_file = Path("01-CORE/config/log_categorization_rules.json")
        if rules_file.exists():
            try:
                with open(rules_file) as f:
                    return json.load(f)
            except:
                pass
        
        # Reglas por defecto
        return self._default_rules()
    
    def _default_rules(self) -> Dict:
        """Reglas de categorización por defecto"""
        return {
            'application': {'keywords': ['system', 'startup', 'ict_engine'], 'priority': 1},
            'market_data': {'keywords': ['market', 'price', 'candle'], 'priority': 4},
            'patterns': {'keywords': ['pattern', 'signal', 'analysis'], 'priority': 3},
            'dashboard': {'keywords': ['dashboard', 'ui', 'display'], 'priority': 2},
            'trading': {'keywords': ['trading', 'order', 'position'], 'priority': 6},
            'general': {'keywords': ['general'], 'priority': 0}
        }
    
    def categorize_log_line(self, log_line: str) -> str:
        """
        Categorizar una línea de log según las reglas
        
        Args:
            log_line: Línea de log a categorizar
            
        Returns:
            Nombre de la categoría
        """
        log_lower = log_line.lower()
        best_category = 'application'  # Default
        highest_priority = 0
        
        for category, rule_config in self.rules.items():
            keywords = rule_config.get('keywords', [])
            exclude_keywords = rule_config.get('exclude_keywords', [])
            priority = rule_config.get('priority', 1)
            
            # Verificar si contiene keywords de la categoría
            has_keywords = any(keyword in log_lower for keyword in keywords)
            has_excluded = any(exclude in log_lower for exclude in exclude_keywords)
            
            if has_keywords and not has_excluded and priority > highest_priority:
                best_category = category
                highest_priority = priority
        
        return best_category
    
    def get_target_log_file(self, category: str, date: Optional[str] = None) -> Path:
        """
        Obtener archivo de destino para la categoría
        
        Args:
            category: Categoría del log
            date: Fecha en formato YYYY-MM-DD (opcional)
            
        Returns:
            Path al archivo de destino
        """
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        logs_base = Path("05-LOGS")
        
        category_paths = {
            'application': logs_base / "application" / f"ict_engine_{date}.log",
            'fvg_memory': logs_base / "fvg_memory" / f"fvg_memory_{date}.log",
            'market_data': logs_base / "market_data" / f"market_data_{date}.log",
            'patterns': logs_base / "patterns" / f"patterns_{date}.log",
            'dashboard': logs_base / "dashboard" / f"dashboard_{date}.log",
            'trading': logs_base / "trading" / f"trading_{date}.log",
            'system_status': logs_base / "system_status" / f"system_status_{date}.log",
            'general': logs_base / "general" / f"general_{date}.log"
        }
        
        target_file = category_paths.get(category, category_paths['application'])
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        return target_file
    
    def categorize_and_route_log(self, log_line: str, write_to_file: bool = False) -> Dict:
        """
        Categorizar log y opcionalmente escribirlo al archivo apropiado
        
        Args:
            log_line: Línea de log
            write_to_file: Si escribir al archivo
            
        Returns:
            Información de la categorización
        """
        category = self.categorize_log_line(log_line)
        target_file = self.get_target_log_file(category)
        
        result = {
            'category': category,
            'target_file': str(target_file),
            'written': False
        }
        
        if write_to_file:
            try:
                with open(target_file, 'a', encoding='utf-8') as f:
                    f.write(log_line + '\n' if not log_line.endswith('\n') else log_line)
                result['written'] = True
            except Exception as e:
                result['error'] = str(e)
        
        return result
    
    def get_categorization_stats(self) -> Dict:
        """Obtener estadísticas de las reglas de categorización"""
        return {
            'total_categories': len(self.rules),
            'categories': list(self.rules.keys()),
            'rules_loaded': True
        }

# Instancia global
LOG_CATEGORIZER = LogCategorizer()

def categorize_log(log_line: str) -> str:
    """Función de conveniencia para categorizar un log"""
    return LOG_CATEGORIZER.categorize_log_line(log_line)

def route_log_to_file(log_line: str) -> Dict:
    """Función de conveniencia para categorizar y escribir log"""
    return LOG_CATEGORIZER.categorize_and_route_log(log_line, write_to_file=True)

def get_target_file_for_category(category: str) -> Path:
    """Función de conveniencia para obtener archivo destino"""
    return LOG_CATEGORIZER.get_target_log_file(category)
