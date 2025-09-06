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
from datetime import datetime

# Configurar rutas para acceso a módulos reales del core
dashboard_root = Path(__file__).parent.parent.parent
project_root = dashboard_root.parent
sys.path.insert(0, str(project_root / "01-CORE"))

# Importar clases base con path correcto para módulos generados
sys.path.insert(0, str(Path(__file__).parent.parent))
from base_pattern_module import BasePatternDashboard, PatternAnalysisResult, PatternDashboardUtils


class FalseBreakoutV6Dashboard(BasePatternDashboard):
    """
    Dashboard para patrón REAL conectado con sistema ICT Engine v6.0 Enterprise
    
    PRINCIPIO: NUNCA datos hardcodeados - SIEMPRE sistema real
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("false_breakout_v6", config)

        # Configurar project_root para resolver warnings
        self.project_root = Path(__file__).parent.parent.parent.parent.absolute()
        
        # Variables para conexión con sistema real
        self.real_pattern_detector = None
        self.real_data_manager = None
        self.real_config = None
        self.advanced_pattern_module = None
        
        # Conectar con sistema real
        self._connect_to_real_system()
        
    def _connect_to_real_system(self):
        """Conectar con los módulos reales del sistema ICT Engine"""
        print(f"🔌 Conectando {self.pattern_name} con sistema real...")
        
        # 1. Conectar con Pattern Detector principal
        try:
            from analysis.pattern_detector import PatternDetector
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
                from ict_engine.advanced_patterns.judas_swing_enterprise import JudasSwingEnterprise
                self.advanced_pattern_module = JudasSwingEnterprise()
                print(f"✅ {self.pattern_name}: Módulo enterprise conectado")
            elif self.pattern_name == 'liquidity_grab':
                from ict_engine.advanced_patterns.liquidity_grab_enterprise import LiquidityGrabEnterprise
                self.advanced_pattern_module = LiquidityGrabEnterprise()
                print(f"✅ {self.pattern_name}: Módulo enterprise conectado")
        except ImportError as e:
            print(f"ℹ️ {self.pattern_name}: Módulo enterprise no disponible: {e}")
        
        # 3. Conectar con Data Manager real
        try:
            from data_management.ict_data_manager import ICTDataManager
            self.real_data_manager = ICTDataManager()
            print(f"✅ {self.pattern_name}: ICTDataManager real conectado")
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
        """Análisis REAL del patrón usando sistema ICT Engine"""
        
        # Crear resultado base
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
            raw_market_data = self._get_real_market_data(symbol, timeframe)
            if not raw_market_data:
                result.narrative = "Datos de mercado no disponibles en el sistema real"
                return result
            
            # 🔒 VALIDAR DATOS DE MERCADO ANTES DE USAR
            market_data = self.validate_market_data(raw_market_data)
            if not market_data or len(market_data) == 0:
                result.narrative = "Datos de mercado inválidos - falló validación de seguridad"
                return result
            
            # 2. Usar detector real del patrón
            pattern_signals = self._detect_with_real_system(market_data, symbol, timeframe)
            
            if pattern_signals:
                # Procesar señal real (NO inventar datos)
                best_signal = max(pattern_signals, key=lambda x: x.get('confidence', 0))
                
                # 🔒 VALIDAR RESULTADO DEL PATRÓN ANTES DE USAR
                validated_signal = self.validate_pattern_result(best_signal)
                
                # Extraer datos VALIDADOS de la señal
                result.confidence = float(validated_signal.get('confidence', 0.0))
                result.strength = float(validated_signal.get('strength', 0.0))
                result.direction = str(validated_signal.get('direction', 'NEUTRAL')).upper()
                
                # Niveles validados (NO hardcodeados)
                entry_zone = validated_signal.get('entry_zone', (0.0, 0.0))
                if isinstance(entry_zone, (list, tuple)) and len(entry_zone) >= 2:
                    result.entry_zone = (float(entry_zone[0]), float(entry_zone[1]))
                
                result.stop_loss = float(validated_signal.get('stop_loss', 0.0))
                result.take_profit_1 = float(validated_signal.get('take_profit_1', 0.0))
                result.take_profit_2 = validated_signal.get('take_profit_2')
                if result.take_profit_2:
                    result.take_profit_2 = float(result.take_profit_2)
                
                # Métricas validadas
                result.risk_reward_ratio = float(validated_signal.get('risk_reward_ratio', 0.0))
                result.probability = float(validated_signal.get('probability', 0.0))
                
                # Contexto validado
                result.session = str(validated_signal.get('session', 'UNKNOWN'))
                result.confluences = validated_signal.get('confluences', [])
                result.invalidation_criteria = str(validated_signal.get('invalidation_criteria', ''))
                result.narrative = str(validated_signal.get('narrative', f'Patrón {self.pattern_name} detectado por sistema real'))
                
                # Guardar datos validados para debugging
                result.raw_data = best_signal
                
            else:
                result.narrative = f"No se detectaron señales de {self.pattern_name} en el sistema real"
        
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
        """Crear layout del dashboard mostrando datos REALES"""
        
        # Utilidades para formateo
        utils = PatternDashboardUtils()
        
        # Verificar si tenemos datos reales
        has_real_data = result.confidence > 0 or result.raw_data.get('source') == 'real_system'
        
        # Colores y emojis basados en datos reales
        conf_color = utils.get_confidence_color(result.confidence)
        direction_emoji = utils.get_direction_emoji(result.direction)
        tf_display = utils.format_timeframe_display(result.timeframe)
        
        # Status del sistema real
        system_status = "🔌 SISTEMA REAL" if has_real_data else "⚠️ DATOS NO DISPONIBLES"
        
        # Construir layout con datos reales
        layout = f"""
[bold cyan]🎯 {self.pattern_name.upper().replace('_', ' ')} - {result.symbol}[/bold cyan]
[cyan]{'─' * 50}[/cyan]
{system_status}

[bold]💡 ANÁLISIS DEL SISTEMA REAL[/bold]
• Timeframe: [bold]{tf_display}[/bold]
• Dirección: {direction_emoji} [bold]{result.direction}[/bold]
• Confianza: [{conf_color}]{result.confidence:.1f}%[/{conf_color}]
• Fuerza: [bold]{result.strength:.1f}%[/bold]"""

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
def create_dashboard(config: Optional[Dict[str, Any]] = None) -> FalseBreakoutV6Dashboard:
    """Crear instancia del dashboard de false_breakout_v6"""
    return FalseBreakoutV6Dashboard(config)
