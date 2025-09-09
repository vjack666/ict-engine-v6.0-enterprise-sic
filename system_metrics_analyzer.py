#!/usr/bin/env python3
"""
📊 ICT Engine v6.0 Enterprise - Generador de Métricas del Sistema
================================================================
Análisis automatizado de logs y performance del sistema enterprise
"""

import re
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict, Counter

class ICTSystemAnalyzer:
    def __init__(self, log_content):
        """Inicializar analizador con contenido de logs"""
        self.log_content = log_content
        self.metrics = {}
        self.components = defaultdict(int)
        self.errors = []
        self.warnings = []
        self.success_indicators = []
        
    def extract_component_initializations(self):
        """Extraer métricas de inicialización de componentes"""
        patterns = {
            'AdvancedCandleDownloader': r'AdvancedCandleDownloader v6\.0 Enterprise inicializado',
            'SmartMoneyAnalyzer': r'Smart Money Concepts Analyzer v6\.0 Enterprise inicializado',
            'ICTDataManager': r'ICT Data Manager inicializado',
            'PatternDetector': r'Pattern Detector v6\.0 Enterprise inicializado',
            'UnifiedMemorySystem': r'UnifiedMemorySystem v6\.1 integrado exitosamente',
            'SilverBulletEnterprise': r'Silver Bullet Detector Enterprise v6\.0 inicializado correctamente',
            'JudasSwingEnterprise': r'Judas Swing Detector Enterprise v6\.0 inicializado correctamente'
        }
        
        for component, pattern in patterns.items():
            count = len(re.findall(pattern, self.log_content, re.IGNORECASE))
            self.components[component] = count
            
        return self.components
    
    def extract_pattern_analysis(self):
        """Analizar patrones detectados"""
        patterns_section = re.search(
            r'📊 Total patrones descubiertos: (\d+)(.*?)🔍 Verificando módulos dashboard existentes',
            self.log_content, re.DOTALL
        )
        
        if patterns_section:
            total_patterns = int(patterns_section.group(1))
            patterns_text = patterns_section.group(2)
            
            # Extraer patrones enterprise
            enterprise_patterns = re.findall(r'• (.*?): .*?\[ENTERPRISE\]', patterns_text)
            standard_patterns = re.findall(r'• (.*?): .*?(?!\[ENTERPRISE\])', patterns_text)
            standard_patterns = [p for p in standard_patterns if p not in enterprise_patterns]
            
            return {
                'total_patterns': total_patterns,
                'enterprise_patterns': len(enterprise_patterns),
                'standard_patterns': len(standard_patterns),
                'enterprise_list': enterprise_patterns,
                'standard_list': standard_patterns
            }
        return {}
    
    def extract_errors_warnings(self):
        """Extraer errores y warnings"""
        # Errores
        error_patterns = [
            r'❌ (.*?)(?=\n)',
            r'ERROR.*?:(.*?)(?=\n)',
            r'cannot import name.*?(?=\n)'
        ]
        
        for pattern in error_patterns:
            self.errors.extend(re.findall(pattern, self.log_content, re.IGNORECASE))
        
        # Warnings
        warning_patterns = [
            r'⚠️ (.*?)(?=\n)',
            r'WARNING.*?:(.*?)(?=\n)',
            r'ℹ️.*?no disponible.*?:(.*?)(?=\n)'
        ]
        
        for pattern in warning_patterns:
            self.warnings.extend(re.findall(pattern, self.log_content, re.IGNORECASE))
        
        return {
            'errors': len(self.errors),
            'warnings': len(self.warnings),
            'error_list': self.errors[:5],  # Top 5
            'warning_list': self.warnings[:5]  # Top 5
        }
    
    def extract_success_metrics(self):
        """Extraer métricas de éxito"""
        success_patterns = [
            r'✅ (.*?)(?=\n)',
            r'SUCCESS.*?:(.*?)(?=\n)',
            r'conectado - (.*?)(?=\n)'
        ]
        
        for pattern in success_patterns:
            self.success_indicators.extend(re.findall(pattern, self.log_content, re.IGNORECASE))
        
        return {
            'success_count': len(self.success_indicators),
            'key_successes': self.success_indicators[:10]  # Top 10
        }
    
    def extract_performance_metrics(self):
        """Extraer métricas de performance"""
        # Configuraciones de performance
        storage_config = re.search(r'Storage Mode: (.*?) -', self.log_content)
        cache_config = re.search(r'Full storage with (\d+\w+) cache', self.log_content)
        concurrent_config = re.search(r'Max Concurrent Downloads: (\d+)', self.log_content)
        thread_safety = re.search(r'Thread-Safety: (ACTIVADO|DESACTIVADO)', self.log_content)
        
        return {
            'storage_mode': storage_config.group(1) if storage_config else 'Unknown',
            'cache_size': cache_config.group(1) if cache_config else 'Unknown',
            'max_concurrent': int(concurrent_config.group(1)) if concurrent_config else 0,
            'thread_safety': thread_safety.group(1) == 'ACTIVADO' if thread_safety else False
        }
    
    def extract_system_info(self):
        """Extraer información del sistema"""
        # Símbolos configurados
        symbols = re.search(r"Símbolos críticos: \[(.*?)\]", self.log_content)
        timeframes = re.search(r"Timeframes críticos: \[(.*?)\]", self.log_content)
        
        # Estado final del dashboard
        dashboard_status = re.search(r'✅ DASHBOARD ENTERPRISE OPERATIVO', self.log_content)
        
        return {
            'symbols': symbols.group(1).replace("'", "").split(', ') if symbols else [],
            'timeframes': timeframes.group(1).replace("'", "").split(', ') if timeframes else [],
            'dashboard_operational': bool(dashboard_status)
        }
    
    def generate_comprehensive_analysis(self):
        """Generar análisis completo"""
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'system_version': 'ICT Engine v6.0 Enterprise',
            'analysis_type': 'Post-Cleanup System Analysis',
            'component_initializations': self.extract_component_initializations(),
            'pattern_analysis': self.extract_pattern_analysis(),
            'error_analysis': self.extract_errors_warnings(),
            'success_metrics': self.extract_success_metrics(),
            'performance_config': self.extract_performance_metrics(),
            'system_info': self.extract_system_info()
        }
        
        # Calcular health score
        analysis['health_score'] = self.calculate_health_score(analysis)
        
        return analysis
    
    def calculate_health_score(self, analysis):
        """Calcular score de salud del sistema"""
        score = 100
        
        # Penalizar por errores
        error_count = analysis['error_analysis']['errors']
        score -= error_count * 10
        
        # Penalizar por warnings
        warning_count = analysis['error_analysis']['warnings']
        score -= warning_count * 2
        
        # Bonus por patrones enterprise
        enterprise_count = analysis['pattern_analysis'].get('enterprise_patterns', 0)
        score += enterprise_count * 5
        
        # Bonus por dashboard operativo
        if analysis['system_info']['dashboard_operational']:
            score += 10
        
        # Bonus por thread safety
        if analysis['performance_config']['thread_safety']:
            score += 5
        
        return max(0, min(100, score))

def main():
    """Función principal para análisis"""
    
    # Simular contenido de logs (en producción vendría de archivo)
    log_sample = """
    ℹ️  [AdvancedCandleDownloader v6.0] AdvancedCandleDownloader v6.0 Enterprise inicializado
    ℹ️  [AdvancedCandleDownloader v6.0] Storage Mode: FULL_STORAGE_ENTERPRISE - ENTERPRISE DEFAULT - Full storage with 2GB cache
    ℹ️  [AdvancedCandleDownloader v6.0] 🔒 Thread-Safety: ACTIVADO - Pandas optimizado para operaciones concurrentes
    ℹ️  [AdvancedCandleDownloader v6.0] 🚀 Max Concurrent Downloads: 3 (thread-safe)
    💰 Smart Money Concepts Analyzer v6.0 Enterprise inicializado
    🧠 ICTDataManager: Memoria Unificada v6.0 conectada (SIC + SLUC)
    📊 ICT Data Manager inicializado
       Símbolos críticos: ['EURUSD', 'GBPUSD', 'USDJPY']
       Timeframes críticos: ['H4', 'H1', 'M15']
    📊 Total patrones descubiertos: 11
      • judas_swing: analysis.pattern_detector [ENTERPRISE]
      • silver_bullet: analysis.pattern_detector [ENTERPRISE]
      • liquidity_grab: analysis.pattern_detector [ENTERPRISE]
    ℹ️ liquidity_grab: Módulo enterprise no disponible: cannot import name 'LiquidityGrabEnterprise'
    ✅ DASHBOARD ENTERPRISE OPERATIVO
    """
    
    analyzer = ICTSystemAnalyzer(log_sample)
    analysis = analyzer.generate_comprehensive_analysis()
    
    # Mostrar resultados
    print("📊 ANÁLISIS AUTOMATIZADO DEL SISTEMA")
    print("=" * 50)
    print(f"⏰ Timestamp: {analysis['timestamp']}")
    print(f"🎯 Health Score: {analysis['health_score']}/100")
    print(f"🔧 Componentes: {len(analysis['component_initializations'])}")
    print(f"🎯 Patrones: {analysis['pattern_analysis'].get('total_patterns', 0)}")
    print(f"❌ Errores: {analysis['error_analysis']['errors']}")
    print(f"⚠️ Warnings: {analysis['error_analysis']['warnings']}")
    print(f"✅ Dashboard: {'✅ Operativo' if analysis['system_info']['dashboard_operational'] else '❌ No operativo'}")
    
    return analysis

if __name__ == "__main__":
    analysis = main()
    
    # Guardar análisis en JSON
    output_file = Path(__file__).parent / f"system_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Análisis guardado en: {output_file}")
