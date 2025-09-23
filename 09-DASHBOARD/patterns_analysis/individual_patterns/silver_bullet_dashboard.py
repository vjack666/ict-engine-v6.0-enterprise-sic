# ========== PUNTO DE ENTRADA ROBUSTO ========== #
# (Este bloque se mueve al final del archivo para asegurar que SilverBulletDashboard esté definido)

# ========== PUNTO DE ENTRADA PRINCIPAL ========== #
import time

def run_analysis_loop(dashboard, symbol: str = "EURUSD", timeframe: str = "M15", interval: int = 10):
    """Loop de análisis continuo para mantener el dashboard activo y actualizado."""
    print("\n=== SILVER BULLET DASHBOARD (LIVE) ===\n")
    print("Presiona Ctrl+C para salir.\n")
    try:
        while True:
            result = dashboard.analyze_pattern(symbol, timeframe, force_refresh=True)
            layout = dashboard.create_dashboard_layout(result)
            print("\033c", end="")  # Limpiar pantalla (ANSI)
            print(layout)
            print(f"\n[Actualizando en {interval} segundos...]")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n[EXIT] Dashboard cerrado por el usuario.")



# ========== PUNTO DE ENTRADA ROBUSTO ========== #


# (Mover este bloque al final del archivo para asegurar que SilverBulletDashboard esté definido)

#!/usr/bin/env python3
"""
🎯 PATTERN TEMPLATE - CONEXIÓN DIRECTA CON SISTEMA REAL
======================================================

Template que se conecta ÚNICAMENTE con módulos reales del sistema ICT Engine v6.0 Enterprise.
NO usa datos hardcodeados ni simulados.

Auto-generado por PatternFactory
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

from analysis.premium_discount.premium_discount_analyzer import PremiumDiscountAnalyzer
from datetime import datetime

# Configurar rutas para acceso a módulos reales del core
dashboard_root = Path(__file__).parent.parent.parent
project_root = dashboard_root.parent
sys.path.insert(0, str(project_root / "01-CORE"))

# Importar clases base con path correcto para módulos generados
sys.path.insert(0, str(Path(__file__).parent.parent))
from base_pattern_module import BasePatternDashboard, PatternAnalysisResult, PatternDashboardUtils


class SilverBulletDashboard(BasePatternDashboard):
    """
    Dashboard para patrón REAL conectado con sistema ICT Engine v6.0 Enterprise
    
    PRINCIPIO: NUNCA datos hardcodeados - SIEMPRE sistema real
    """
    

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("silver_bullet", config)
        # Variables para conexión con sistema real
        self.real_pattern_detector = None
        self.real_data_manager = None
        self.real_config = None
        self.advanced_pattern_module = None
        # Instanciar el analizador premium/discount centralizado
        self.premium_discount_analyzer = PremiumDiscountAnalyzer()
        # Configurar rutas del proyecto
        self.project_root = project_root
        # Conectar con sistema real
        self._connect_to_real_system()
        
    def _connect_to_real_system(self):
        """Conectar con los módulos reales del sistema ICT Engine"""
        print(f"🔌 Conectando {self.pattern_name} con sistema real...")
        
        # 1. Conectar con Pattern Detector principal
        try:
            from ict_engine.pattern_detector import PatternDetector
            self.real_pattern_detector = PatternDetector()
            print(f"✅ {self.pattern_name}: PatternDetector real conectado")
        except ImportError as e:
            print(f"⚠️ {self.pattern_name}: No se pudo conectar PatternDetector principal: {e}")
        
        # 2. Intentar conectar con módulo enterprise específico
        try:
            if self.pattern_name == 'silver_bullet':
                from ict_engine.advanced_patterns.silver_bullet_enterprise import SilverBulletDetectorEnterprise
                self.advanced_pattern_module = SilverBulletDetectorEnterprise()
                print(f"✅ {self.pattern_name}: Módulo enterprise conectado")
            elif self.pattern_name == 'judas_swing':
                from ict_engine.advanced_patterns.judas_swing_enterprise import JudasSwingDetectorEnterprise
                self.advanced_pattern_module = JudasSwingDetectorEnterprise()
                print(f"✅ {self.pattern_name}: Módulo enterprise conectado")
            elif self.pattern_name == 'liquidity_grab':
                from ict_engine.advanced_patterns.liquidity_grab_enterprise import LiquidityGrabDetectorEnterprise
                self.advanced_pattern_module = LiquidityGrabDetectorEnterprise()
                print(f"✅ {self.pattern_name}: Módulo enterprise conectado")
        except ImportError as e:
            print(f"ℹ️ {self.pattern_name}: Módulo enterprise no disponible: {e}")
        
        # 3. Conectar con Data Manager real (Singleton optimizado)
        try:
            from data_management.ict_data_manager_singleton import get_ict_data_manager
            self.real_data_manager = get_ict_data_manager()
            print(f"✅ {self.pattern_name}: ICTDataManager singleton conectado")
        except ImportError:
            try:
                from data_management.mt5_data_manager import MT5DataManager
                self.real_data_manager = MT5DataManager()
                print(f"✅ {self.pattern_name}: MT5DataManager real conectado")
            except ImportError as e:
                print(f"⚠️ {self.pattern_name}: No se pudo conectar con DataManager: {e}")
        
        # 4. Cargar configuración real del sistema
        self._load_real_system_config()
    
    def _load_real_system_config(self):
        """Cargar configuración real del sistema ICT Engine"""
        try:
            import json
            config_paths = [
                self.project_root / "01-CORE" / "config" / "real_trading_config.json",
                self.project_root / "01-CORE" / "config" / "ict_patterns_config.json",
                self.project_root / "01-CORE" / "config" / "trading_symbols_config.json"
            ]
            
            self.real_config = {}
            for config_path in config_paths:
                if config_path.exists():
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                        self.real_config.update(config_data)
                        print(f"✅ {self.pattern_name}: Configuración cargada desde {config_path.name}")
            
            if not self.real_config:
                print(f"⚠️ {self.pattern_name}: No se encontraron configuraciones reales")
                
        except Exception as e:
            print(f"⚠️ {self.pattern_name}: Error cargando configuración real: {e}")
            self.real_config = {}
    

    def _perform_pattern_analysis(self, symbol: str, timeframe: str) -> PatternAnalysisResult:
        """Análisis REAL del patrón usando sistema ICT Engine y filtro premium/discount"""
        result = PatternAnalysisResult(
            pattern_name=self.pattern_name,
            symbol=symbol,
            timeframe=timeframe,
            timestamp=datetime.now(),
            confidence=0.0,
            strength=0.0,
            direction="NEUTRAL",
            entry_zone=(0.0, 0.0),
            stop_loss=0.0,
            take_profit_1=0.0,
            analysis_id=f"{self.pattern_name}_{symbol}_{timeframe}_{int(datetime.now().timestamp())}"
        )
        try:
            # 1. Obtener datos reales del mercado
            market_data = self._get_real_market_data(symbol, timeframe)
            if not market_data:
                result.narrative = "Datos de mercado no disponibles en el sistema real"
                return result

            # 2. Calcular estado premium/discount usando el módulo centralizado
            last_candle = market_data[-1] if isinstance(market_data, list) and market_data else market_data
            if isinstance(last_candle, dict):
                pd_state = self.premium_discount_analyzer.analyze_market_state(last_candle)
            else:
                pd_state = {'state': 'unknown', 'reason': 'invalid_candle'}
            result.raw_data = {}
            result.raw_data['premium_discount_state'] = pd_state
            result.narrative = f"Market state: {pd_state.get('state','unknown').upper()} | Equilibrium: {pd_state.get('equilibrium','?'):.5f}"

            # 3. Usar detector real del patrón
            pattern_signals = self._detect_with_real_system(market_data, symbol, timeframe)

            # 4. Filtrar setups según premium/discount (solo setups long en discount, short en premium)
            valid_signals = []
            for sig in pattern_signals:
                direction = str(sig.get('direction','NEUTRAL')).upper()
                if direction == 'LONG' and pd_state.get('state') == 'discount':
                    valid_signals.append(sig)
                elif direction == 'SHORT' and pd_state.get('state') == 'premium':
                    valid_signals.append(sig)

            if valid_signals:
                best_signal = max(valid_signals, key=lambda x: x.get('confidence', 0))
                # Extraer datos REALES de la señal
                result.confidence = float(best_signal.get('confidence', 0.0))
                result.strength = float(best_signal.get('strength', 0.0))
                result.direction = str(best_signal.get('direction', 'NEUTRAL')).upper()
                entry_zone = best_signal.get('entry_zone', (0.0, 0.0))
                if isinstance(entry_zone, (list, tuple)) and len(entry_zone) >= 2:
                    result.entry_zone = (float(entry_zone[0]), float(entry_zone[1]))
                result.stop_loss = float(best_signal.get('stop_loss', 0.0))
                result.take_profit_1 = float(best_signal.get('take_profit_1', 0.0))
                result.take_profit_2 = best_signal.get('take_profit_2')
                if result.take_profit_2:
                    result.take_profit_2 = float(result.take_profit_2)
                result.risk_reward_ratio = float(best_signal.get('risk_reward_ratio', 0.0))
                result.probability = float(best_signal.get('probability', 0.0))
                result.session = str(best_signal.get('session', 'UNKNOWN'))
                result.confluences = best_signal.get('confluences', [])
                result.invalidation_criteria = str(best_signal.get('invalidation_criteria', ''))
                result.narrative += f"\nPatrón {self.pattern_name} detectado por sistema real"
                result.raw_data = best_signal
                result.raw_data['premium_discount_state'] = pd_state
            else:
                result.narrative += f"\nNo setups válidos según market state (solo LONG en discount, SHORT en premium)"
        except Exception as e:
            result.narrative = f"Error en análisis real: {str(e)}"
            print(f"⚠️ Error analizando {self.pattern_name} con sistema real: {e}")
        return result
    
    def _get_real_market_data(self, symbol: str, timeframe: str) -> Optional[Any]:
        """Obtener datos REALES del mercado (NO simulados)"""
        try:
            if self.real_data_manager is None:
                print(f"⚠️ {self.pattern_name}: DataManager no disponible")
                return None
            
            # Usar método real del data manager
            if hasattr(self.real_data_manager, 'get_candles'):
                # MT5DataManager
                candles = self.real_data_manager.get_candles(symbol, timeframe, 100)
                print(f"✅ {self.pattern_name}: Datos reales obtenidos de MT5DataManager")
                return candles
            elif hasattr(self.real_data_manager, 'get_current_data'):
                # ICTDataManager
                data = self.real_data_manager.get_current_data(symbol, timeframe)
                print(f"✅ {self.pattern_name}: Datos reales obtenidos de ICTDataManager")
                return data
            else:
                print(f"⚠️ {self.pattern_name}: Método de obtención de datos no encontrado")
                return None
                
        except Exception as e:
            print(f"⚠️ {self.pattern_name}: Error obteniendo datos reales: {e}")
            return None
    
    def _detect_with_real_system(self, market_data: Any, symbol: str, timeframe: str) -> List[Dict[str, Any]]:
        """Detectar patrón usando sistema REAL (NO simulado)"""
        signals = []
        
        try:
            # 1. Intentar usar módulo enterprise específico primero
            if self.advanced_pattern_module:
                try:
                    if hasattr(self.advanced_pattern_module, 'detect'):
                        enterprise_result = self.advanced_pattern_module.detect(market_data, symbol, timeframe)
                        if enterprise_result:
                            signals.append(self._process_real_signal(enterprise_result))
                            print(f"✅ {self.pattern_name}: Señal detectada por módulo enterprise")
                except Exception as e:
                    print(f"⚠️ {self.pattern_name}: Error en módulo enterprise: {e}")
            
            # 2. Usar detector principal si no hay señales enterprise
            if not signals and self.real_pattern_detector:
                try:
                    detector_method_name = f'_detect_{self.pattern_name}'
                    
                    if hasattr(self.real_pattern_detector, detector_method_name):
                        detector_method = getattr(self.real_pattern_detector, detector_method_name)
                        detection_result = detector_method(market_data, symbol, timeframe)
                        
                        if isinstance(detection_result, list):
                            for signal in detection_result:
                                signals.append(self._process_real_signal(signal))
                        elif detection_result:
                            signals.append(self._process_real_signal(detection_result))
                        
                        print(f"✅ {self.pattern_name}: Señal detectada por PatternDetector principal")
                    
                    # Fallback: usar detect_patterns general
                    elif hasattr(self.real_pattern_detector, 'detect_patterns'):
                        general_patterns = self.real_pattern_detector.detect_patterns(market_data, timeframe)
                        
                        for pattern in general_patterns:
                            if (hasattr(pattern, 'pattern_type') and 
                                self.pattern_name.lower() in str(pattern.pattern_type).lower()):
                                signals.append(self._process_real_signal(pattern))
                        
                        if signals:
                            print(f"✅ {self.pattern_name}: Señal detectada por detect_patterns general")
                    
                except Exception as e:
                    print(f"⚠️ {self.pattern_name}: Error en detector principal: {e}")
        
        except Exception as e:
            print(f"⚠️ {self.pattern_name}: Error general en detección: {e}")
        
        return signals
    
    def _process_real_signal(self, signal: Any) -> Dict[str, Any]:
        """Procesar señal REAL del sistema (NO generar datos fake)"""
        try:
            # Extraer información REAL según el tipo de señal
            if hasattr(signal, '__dict__'):
                # Objeto PatternSignal o similar
                return {
                    'confidence': getattr(signal, 'confidence', getattr(signal, 'strength', 0.0)),
                    'strength': getattr(signal, 'strength', 0.0),
                    'direction': str(getattr(signal, 'direction', 'NEUTRAL')).upper(),
                    'entry_zone': getattr(signal, 'entry_zone', (0.0, 0.0)),
                    'stop_loss': getattr(signal, 'stop_loss', 0.0),
                    'take_profit_1': getattr(signal, 'take_profit_1', 0.0),
                    'take_profit_2': getattr(signal, 'take_profit_2', None),
                    'risk_reward_ratio': getattr(signal, 'risk_reward_ratio', 0.0),
                    'probability': getattr(signal, 'probability', 0.0),
                    'session': str(getattr(signal, 'session', 'UNKNOWN')),
                    'confluences': getattr(signal, 'confluences', []),
                    'invalidation_criteria': getattr(signal, 'invalidation_criteria', ''),
                    'narrative': getattr(signal, 'narrative', f'Patrón {self.pattern_name} del sistema real'),
                    'source': 'real_system'
                }
            elif isinstance(signal, dict):
                # Dictionary signal ya procesado
                signal['source'] = 'real_system'
                return signal
            else:
                # Intentar extraer propiedades básicas
                return {
                    'confidence': getattr(signal, 'confidence', 0.0),
                    'strength': getattr(signal, 'strength', 0.0),
                    'direction': 'NEUTRAL',
                    'entry_zone': (0.0, 0.0),
                    'stop_loss': 0.0,
                    'take_profit_1': 0.0,
                    'risk_reward_ratio': 0.0,
                    'probability': 0.0,
                    'session': 'UNKNOWN',
                    'confluences': [],
                    'invalidation_criteria': '',
                    'narrative': f'Señal de {self.pattern_name} detectada por sistema real',
                    'source': 'real_system'
                }
        
        except Exception as e:
            print(f"⚠️ {self.pattern_name}: Error procesando señal real: {e}")
            return {
                'confidence': 0.0,
                'strength': 0.0,
                'direction': 'NEUTRAL',
                'entry_zone': (0.0, 0.0),
                'stop_loss': 0.0,
                'take_profit_1': 0.0,
                'risk_reward_ratio': 0.0,
                'probability': 0.0,
                'session': 'UNKNOWN',
                'confluences': [],
                'invalidation_criteria': '',
                'narrative': f'Error procesando señal real de {self.pattern_name}',
                'source': 'real_system_error'
            }
    

    def create_dashboard_layout(self, result: PatternAnalysisResult) -> str:
        """Crear layout del dashboard mostrando datos REALES y estado premium/discount"""
        utils = PatternDashboardUtils()
        has_real_data = result.confidence > 0 or result.raw_data.get('source') == 'real_system'
        conf_color = utils.get_confidence_color(result.confidence)
        direction_emoji = utils.get_direction_emoji(result.direction)
        tf_display = utils.format_timeframe_display(result.timeframe)
        system_status = "🔌 SISTEMA REAL" if has_real_data else "⚠️ DATOS NO DISPONIBLES"
        # Mostrar estado premium/discount
        pd_state = result.raw_data.get('premium_discount_state', {})
        pd_str = f"{pd_state.get('state','?').upper()} | Eq: {pd_state.get('equilibrium','?'):.5f}" if pd_state else "-"
        layout = f"""
[bold cyan]🎯 {self.pattern_name.upper().replace('_', ' ')} - {result.symbol}[/bold cyan]
[cyan]{'─' * 50}[/cyan]
{system_status}

[bold]💡 ANÁLISIS DEL SISTEMA REAL[/bold]
• Timeframe: [bold]{tf_display}[/bold]
• Dirección: {direction_emoji} [bold]{result.direction}[/bold]
• Confianza: [{conf_color}]{result.confidence:.1f}%[/{conf_color}]
• Fuerza: [bold]{result.strength:.1f}%[/bold]
• Market State: [bold]{pd_str}[/bold]"""

        if has_real_data and result.entry_zone != (0.0, 0.0):
            layout += f"""

[bold]💰 NIVELES REALES DEL SISTEMA[/bold]
• Zona Entrada: [{utils.format_price(result.entry_zone[0], result.symbol)} - {utils.format_price(result.entry_zone[1], result.symbol)}]
• Stop Loss: [bold red]{utils.format_price(result.stop_loss, result.symbol)}[/bold red]
• Take Profit 1: [bold green]{utils.format_price(result.take_profit_1, result.symbol)}[/bold green]"""

            if result.take_profit_2:
                layout += f"\n• Take Profit 2: [bold green]{utils.format_price(result.take_profit_2, result.symbol)}[/bold green]"
        
        # Métricas reales
        if has_real_data:
            rr_color = "green" if result.risk_reward_ratio >= 2.0 else "yellow" if result.risk_reward_ratio >= 1.5 else "red"
            layout += f"""

[bold]📊 MÉTRICAS DEL SISTEMA REAL[/bold]
• Risk/Reward: [{rr_color}]{result.risk_reward_ratio:.2f}[/{rr_color}]
• Probabilidad: [bold]{result.probability:.1f}%[/bold]
• Sesión: [bold]{result.session}[/bold]

[bold]🎯 RECOMENDACIONES BASADAS EN SISTEMA REAL[/bold]
• Scalping: [bold]{result.scalping_viability}[/bold]
• Intraday: [bold]{result.intraday_viability}[/bold]"""
            
            if result.recommended_timeframes:
                tf_list = ", ".join([utils.format_timeframe_display(tf) for tf in result.recommended_timeframes])
                layout += f"\n• TFs Recomendados: [bold]{tf_list}[/bold]"
        
        # Confluencias del sistema real
        if result.confluences:
            layout += f"""

[bold]🔄 CONFLUENCIAS DEL SISTEMA REAL[/bold]"""
            for confluence in result.confluences[:3]:  # Máximo 3
                layout += f"\n• {confluence}"
        
        # Narrativa del sistema real
        if result.narrative:
            layout += f"""

[bold]📝 ANÁLISIS DEL SISTEMA[/bold]
{result.narrative}"""
        
        # Criterios de invalidación reales
        if result.invalidation_criteria:
            layout += f"""

[bold red]⚠️ INVALIDACIÓN (SISTEMA REAL)[/bold red]
{result.invalidation_criteria}"""
        
        # Información de fuente
        source_info = result.raw_data.get('source', 'unknown')
        layout += f"""

[bold]🔍 FUENTE DE DATOS[/bold]
Sistema: {source_info}
Actualizado: {result.timestamp.strftime('%H:%M:%S')}
ID: {result.analysis_id}
"""
        
        return layout


# Función de creación para el factory
def create_dashboard(config: Optional[Dict[str, Any]] = None) -> SilverBulletDashboard:
    """Crear instancia del dashboard de silver_bullet"""
    return SilverBulletDashboard(config)
