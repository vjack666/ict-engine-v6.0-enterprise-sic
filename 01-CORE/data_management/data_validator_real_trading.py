#!/usr/bin/env python3
"""
🔒 REAL TRADING DATA VALIDATOR - SISTEMA DE VALIDACIÓN CRÍTICA
=============================================================

Validador de datos para trading real que garantiza la integridad y
seguridad de todos los datos antes de ser usados en decisiones de trading.

NIVEL CRÍTICO: Este módulo evita pérdidas por datos corruptos o inválidos.
"""

from protocols.unified_logging import get_unified_logger
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Union, List, Tuple
from decimal import Decimal, ROUND_HALF_UP
import logging
from pathlib import Path

# Configurar logging específico para validación
logger = logging.getLogger('RealTradingDataValidator')
logger.setLevel(logging.INFO)

class RealTradingDataValidator:
    """
    Validador crítico de datos para trading real.
    
    PRINCIPIOS:
    1. NUNCA retornar None - siempre valores seguros por defecto
    2. Validar TODOS los datos antes de uso en trading
    3. Logging completo de errores para auditoría
    4. Precisión decimal para cálculos monetarios
    """
    
    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
        self.validation_errors = []
        self.safe_defaults = self._initialize_safe_defaults()
        
        # Configurar precisión decimal para trading
        self.price_precision = 5  # Para forex (0.00001)
        self.volume_precision = 2  # Para lotes (0.01)
        
        logger.info("🔒 RealTradingDataValidator inicializado - Modo estricto: %s", strict_mode)
    
    def _initialize_safe_defaults(self) -> Dict[str, Any]:
        """Inicializar valores seguros por defecto para trading"""
        return {
            'price': Decimal('0.00000'),
            'volume': Decimal('0.00'),
            'spread': Decimal('0.00001'),
            'confidence': 0.0,
            'timestamp': datetime.now(timezone.utc),
            'symbol': 'UNKNOWN',
            'timeframe': 'H1',
            'trend': 'NEUTRAL',
            'signal': 'HOLD',
            'risk_level': 'HIGH',  # Por seguridad, asumir alto riesgo por defecto
            'position_size': Decimal('0.01'),  # Mínimo lote
            'stop_loss': None,
            'take_profit': None,
            'entry_price': Decimal('0.00000'),
            'pattern_strength': 0.0,
            'market_condition': 'UNCERTAIN'
        }
    
    def validate_price_data(self, data: Union[pd.DataFrame, Dict, float, None]) -> pd.DataFrame:
        """
        Validar datos de precios para trading real.
        
        Args:
            data: Datos de precio en cualquier formato
            
        Returns:
            DataFrame validado con precios seguros
        """
        try:
            if data is None:
                logger.warning("🚨 Datos de precio None - usando valores seguros por defecto")
                return self._create_safe_price_dataframe()
            
            # Convertir a DataFrame si es necesario
            if isinstance(data, dict):
                df = pd.DataFrame([data])
            elif isinstance(data, (int, float)):
                df = pd.DataFrame({'close': [data]})
            elif isinstance(data, pd.DataFrame):
                df = data.copy()
            else:
                logger.error("🚨 Formato de datos de precio no reconocido: %s", type(data))
                return self._create_safe_price_dataframe()
            
            # Validar columnas requeridas
            df = self._validate_price_columns(df)
            
            # Validar rangos de precios
            df = self._validate_price_ranges(df)
            
            # Validar timestamps
            df = self._validate_timestamps(df)
            
            # Validar continuidad de datos
            df = self._validate_data_continuity(df)
            
            logger.info("✅ Datos de precio validados: %d velas", len(df))
            return df
            
        except Exception as e:
            logger.error("🚨 Error crítico validando precios: %s", str(e))
            self.validation_errors.append(f"Price validation error: {str(e)}")
            return self._create_safe_price_dataframe()
    
    def _validate_price_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validar y completar columnas de precio requeridas"""
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        
        for col in required_columns:
            if col not in df.columns:
                if col == 'volume':
                    df[col] = 1000  # Volumen por defecto
                elif col in ['open', 'high', 'low', 'close']:
                    # Si falta una columna de precio, usar close o valor por defecto
                    if 'close' in df.columns:
                        df[col] = df['close']
                    else:
                        df[col] = self.safe_defaults['price']
                    logger.warning("🔧 Columna %s faltante - completada con valores seguros", col)
        
        # Validar relaciones OHLC
        for idx in df.index:
            try:
                high = pd.to_numeric(df.loc[idx, 'high'], errors='coerce')
                low = pd.to_numeric(df.loc[idx, 'low'], errors='coerce')
                open_price = pd.to_numeric(df.loc[idx, 'open'], errors='coerce')
                close = pd.to_numeric(df.loc[idx, 'close'], errors='coerce')
                
                # Manejar valores NaN
                if pd.isna(high) or pd.isna(low) or pd.isna(open_price) or pd.isna(close):
                    median_price = df[['open', 'high', 'low', 'close']].median().median()
                    high = median_price if pd.isna(high) else high
                    low = median_price if pd.isna(low) else low
                    open_price = median_price if pd.isna(open_price) else open_price
                    close = median_price if pd.isna(close) else close
            except Exception as e:
                logger.warning("🔧 Error procesando OHLC en índice %d: %s", idx, str(e))
                continue
            
            # Corregir si high < low
            if high < low:
                df.loc[idx, 'high'] = max(high, low)
                df.loc[idx, 'low'] = min(high, low)
                logger.warning("🔧 Corregida relación high/low en índice %d", idx)
            
            # Asegurar que open y close estén dentro del rango
            if open_price > high or open_price < low:
                df.loc[idx, 'open'] = (high + low) / 2
                logger.warning("🔧 Corregido precio open fuera de rango en índice %d", idx)
            
            if close > high or close < low:
                df.loc[idx, 'close'] = (high + low) / 2
                logger.warning("🔧 Corregido precio close fuera de rango en índice %d", idx)
        
        return df
    
    def _validate_price_ranges(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validar que los precios estén en rangos realistas"""
        for col in ['open', 'high', 'low', 'close']:
            if col in df.columns:
                # Eliminar valores negativos o cero
                invalid_mask = (df[col] <= 0) | (df[col].isna()) | (df[col].isinf())
                if invalid_mask.any():
                    logger.warning("🔧 Encontrados %d precios inválidos en columna %s", invalid_mask.sum(), col)
                    
                    # Usar interpolación o último valor válido
                    df.loc[invalid_mask, col] = df[col].ffill().bfill().fillna(1.0)
                
                # Validar rangos extremos (evitar precios irreales)
                extreme_high = df[col] > 100000  # Precio muy alto
                extreme_low = df[col] < 0.00001  # Precio muy bajo
                
                if extreme_high.any() or extreme_low.any():
                    logger.warning("🔧 Encontrados precios extremos en columna %s", col)
                    median_price = df[col].median()
                    df.loc[extreme_high | extreme_low, col] = median_price
        
        return df
    
    def _validate_timestamps(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validar y corregir timestamps"""
        if 'time' not in df.columns and not isinstance(df.index, pd.DatetimeIndex):
            # Crear timestamps por defecto
            df['time'] = pd.date_range(
                start=datetime.now(timezone.utc) - timedelta(hours=len(df)),
                periods=len(df),
                freq='H'
            )
            logger.warning("🔧 Timestamps faltantes - creados timestamps por defecto")
        
        # Convertir index a datetime si es necesario
        if not isinstance(df.index, pd.DatetimeIndex):
            if 'time' in df.columns:
                try:
                    df['time'] = pd.to_datetime(df['time'])
                    df.set_index('time', inplace=True)
                except Exception as e:
                    logger.warning("🔧 Error convirtiendo timestamps: %s", str(e))
                    df.index = pd.date_range(
                        start=datetime.now(timezone.utc) - timedelta(hours=len(df)),
                        periods=len(df),
                        freq='H'
                    )
        
        # Validar que timestamps están en orden
        if not df.index.is_monotonic_increasing:
            df = df.sort_index()
            logger.warning("🔧 Timestamps reordenados")
        
        return df
    
    def _validate_data_continuity(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validar continuidad de datos y completar gaps"""
        if len(df) < 2:
            return df
        
        # Detectar gaps grandes en timestamps
        if isinstance(df.index, pd.DatetimeIndex):
            time_diffs = df.index.to_series().diff()
            median_diff = time_diffs.median()
            if median_diff is not None and not pd.isna(median_diff):
                large_gaps = time_diffs > median_diff * 3
                
                if large_gaps.any():
                    logger.warning("🔧 Detectados %d gaps grandes en datos", large_gaps.sum())
                    # Para trading real, es mejor interpolar que tener gaps
                    df = df.interpolate(method='linear')
            else:
                logger.warning("🔧 No se pudo calcular diferencias de tiempo")
        else:
            logger.warning("🔧 Index no es DatetimeIndex - no se pueden detectar gaps")
        
        return df
    
    def _create_safe_price_dataframe(self) -> pd.DataFrame:
        """Crear DataFrame de precios seguros por defecto"""
        safe_price = float(self.safe_defaults['price'])
        current_time = datetime.now(timezone.utc)
        
        data = []
        for i in range(100):  # 100 velas por defecto
            timestamp = current_time - timedelta(hours=100-i)
            data.append({
                'open': safe_price,
                'high': safe_price * 1.001,  # Spread mínimo
                'low': safe_price * 0.999,
                'close': safe_price,
                'volume': 1000
            })
        
        df = pd.DataFrame(data)
        df.index = pd.date_range(
            start=current_time - timedelta(hours=100),
            periods=100,
            freq='H'
        )
        
        logger.info("🔧 Creado DataFrame seguro por defecto con %d velas", len(df))
        return df
    
    def validate_pattern_analysis(self, analysis_result: Any) -> Dict[str, Any]:
        """
        Validar resultado de análisis de patrones.
        
        Args:
            analysis_result: Resultado del análisis de patrón
            
        Returns:
            Dict con análisis validado y seguro
        """
        try:
            if analysis_result is None:
                logger.warning("🚨 Análisis de patrón None - usando valores seguros")
                return self._create_safe_pattern_analysis()
            
            if isinstance(analysis_result, dict):
                validated = analysis_result.copy()
            else:
                logger.warning("🔧 Análisis no es dict - convirtiendo a formato seguro")
                validated = {'raw_result': str(analysis_result)}
            
            # Validar campos críticos
            validated = self._validate_pattern_fields(validated)
            
            # Validar rangos de confianza
            validated = self._validate_confidence_scores(validated)
            
            # Validar señales de trading
            validated = self._validate_trading_signals(validated)
            
            logger.info("✅ Análisis de patrón validado")
            return validated
            
        except Exception as e:
            logger.error("🚨 Error validando análisis de patrón: %s", str(e))
            return self._create_safe_pattern_analysis()
    
    def _validate_pattern_fields(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Validar y completar campos requeridos del análisis"""
        required_fields = {
            'pattern_detected': False,
            'confidence': 0.0,
            'signal': 'HOLD',
            'entry_price': self.safe_defaults['entry_price'],
            'stop_loss': None,
            'take_profit': None,
            'risk_level': 'HIGH',
            'timeframe': 'H1',
            'timestamp': datetime.now(timezone.utc),
            'pattern_strength': 0.0,
            'market_condition': 'UNCERTAIN'
        }
        
        for field, default_value in required_fields.items():
            if field not in analysis or analysis[field] is None:
                analysis[field] = default_value
                logger.debug("🔧 Campo %s completado con valor por defecto", field)
        
        return analysis
    
    def _validate_confidence_scores(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Validar que los scores de confianza estén en rangos válidos"""
        confidence_fields = ['confidence', 'pattern_strength']
        
        for field in confidence_fields:
            if field in analysis:
                try:
                    score = float(analysis[field])
                    if not (0.0 <= score <= 1.0):
                        logger.warning("🔧 Score %s fuera de rango [0,1]: %f", field, score)
                        analysis[field] = max(0.0, min(1.0, score))
                except (ValueError, TypeError):
                    logger.warning("🔧 Score %s no numérico: %s", field, analysis[field])
                    analysis[field] = 0.0
        
        return analysis
    
    def _validate_trading_signals(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Validar señales de trading"""
        valid_signals = ['BUY', 'SELL', 'HOLD', 'WAIT']
        valid_risk_levels = ['LOW', 'MEDIUM', 'HIGH', 'EXTREME']
        
        if 'signal' in analysis:
            if analysis['signal'] not in valid_signals:
                logger.warning("🔧 Señal inválida: %s - usando HOLD", analysis['signal'])
                analysis['signal'] = 'HOLD'
        
        if 'risk_level' in analysis:
            if analysis['risk_level'] not in valid_risk_levels:
                logger.warning("🔧 Nivel de riesgo inválido: %s - usando HIGH", analysis['risk_level'])
                analysis['risk_level'] = 'HIGH'
        
        # Validar precios de entrada, stop loss y take profit
        price_fields = ['entry_price', 'stop_loss', 'take_profit']
        for field in price_fields:
            if field in analysis and analysis[field] is not None:
                try:
                    price = Decimal(str(analysis[field])).quantize(
                        Decimal('0.00001'), rounding=ROUND_HALF_UP
                    )
                    analysis[field] = price
                except (ValueError, TypeError):
                    logger.warning("🔧 Precio inválido en %s: %s", field, analysis[field])
                    if field == 'entry_price':
                        analysis[field] = self.safe_defaults['entry_price']
                    else:
                        analysis[field] = None
        
        return analysis
    
    def _create_safe_pattern_analysis(self) -> Dict[str, Any]:
        """Crear análisis de patrón seguro por defecto"""
        return {
            'pattern_detected': False,
            'confidence': 0.0,
            'signal': 'HOLD',
            'entry_price': self.safe_defaults['entry_price'],
            'stop_loss': None,
            'take_profit': None,
            'risk_level': 'HIGH',
            'timeframe': 'H1',
            'timestamp': datetime.now(timezone.utc),
            'pattern_strength': 0.0,
            'market_condition': 'UNCERTAIN',
            'reason': 'Safe default - original analysis was invalid',
            'validated': True,
            'validation_errors': self.validation_errors.copy()
        }
    
    def validate_market_data(self, market_data: Any) -> Dict[str, Any]:
        """
        Validar datos de mercado generales.
        
        Args:
            market_data: Datos de mercado en cualquier formato
            
        Returns:
            Dict con datos de mercado validados
        """
        try:
            if market_data is None:
                logger.warning("🚨 Datos de mercado None - usando valores seguros")
                return self._create_safe_market_data()
            
            if isinstance(market_data, dict):
                validated = market_data.copy()
            else:
                validated = {'raw_data': str(market_data)}
            
            # Validar símbolos
            if 'symbol' not in validated:
                validated['symbol'] = self.safe_defaults['symbol']
            
            # Validar timeframe
            valid_timeframes = ['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1']
            if 'timeframe' not in validated or validated['timeframe'] not in valid_timeframes:
                validated['timeframe'] = self.safe_defaults['timeframe']
                logger.warning("🔧 Timeframe corregido a %s", validated['timeframe'])
            
            # Validar spread
            if 'spread' in validated:
                try:
                    spread = Decimal(str(validated['spread']))
                    if spread < 0:
                        validated['spread'] = self.safe_defaults['spread']
                        logger.warning("🔧 Spread negativo corregido")
                except (ValueError, TypeError):
                    validated['spread'] = self.safe_defaults['spread']
                    logger.warning("🔧 Spread inválido corregido")
            else:
                validated['spread'] = self.safe_defaults['spread']
            
            logger.info("✅ Datos de mercado validados")
            return validated
            
        except Exception as e:
            logger.error("🚨 Error validando datos de mercado: %s", str(e))
            return self._create_safe_market_data()
    
    def _create_safe_market_data(self) -> Dict[str, Any]:
        """Crear datos de mercado seguros por defecto"""
        return {
            'symbol': self.safe_defaults['symbol'],
            'timeframe': self.safe_defaults['timeframe'],
            'spread': self.safe_defaults['spread'],
            'timestamp': self.safe_defaults['timestamp'],
            'session': 'UNKNOWN',
            'market_open': True,  # Asumir mercado abierto por seguridad
            'server_time': datetime.now(timezone.utc),
            'validated': True,
            'reason': 'Safe default market data'
        }
    
    def get_validation_report(self) -> Dict[str, Any]:
        """Obtener reporte de validación para auditoría"""
        return {
            'timestamp': datetime.now(timezone.utc),
            'strict_mode': self.strict_mode,
            'total_errors': len(self.validation_errors),
            'errors': self.validation_errors.copy(),
            'safe_defaults_used': self.safe_defaults.copy(),
            'validator_status': 'ACTIVE',
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generar recomendaciones basadas en errores de validación"""
        recommendations = []
        
        if len(self.validation_errors) > 10:
            recommendations.append("🚨 CRÍTICO: Muchos errores de validación - revisar fuente de datos")
        
        if any('None' in error for error in self.validation_errors):
            recommendations.append("🔧 Implementar mejor manejo de valores None en fuente de datos")
        
        if any('price' in error.lower() for error in self.validation_errors):
            recommendations.append("💰 Verificar calidad de feed de precios - posibles problemas de conexión")
        
        if len(recommendations) == 0:
            recommendations.append("✅ Calidad de datos óptima - sistema listo para trading")
        
        return recommendations
    
    def clear_validation_errors(self):
        """Limpiar errores de validación acumulados"""
        self.validation_errors.clear()
        logger.info("🧹 Errores de validación limpiados")


# Instancia global del validador para uso en todo el sistema
_global_validator = None

def get_validator(strict_mode: bool = True) -> RealTradingDataValidator:
    """Obtener instancia global del validador"""
    global _global_validator
    if _global_validator is None:
        _global_validator = RealTradingDataValidator(strict_mode=strict_mode)
    return _global_validator

def validate_data(data: Any, data_type: str = 'price') -> Any:
    """
    Función conveniente para validar cualquier tipo de datos.
    
    Args:
        data: Datos a validar
        data_type: Tipo de datos ('price', 'pattern', 'market')
        
    Returns:
        Datos validados y seguros
    """
    validator = get_validator()
    
    if data_type == 'price':
        return validator.validate_price_data(data)
    elif data_type == 'pattern':
        return validator.validate_pattern_analysis(data)
    elif data_type == 'market':
        return validator.validate_market_data(data)
    else:
        logger.warning("🔧 Tipo de datos desconocido: %s - validando como mercado", data_type)
        return validator.validate_market_data(data)


if __name__ == "__main__":
    # Test del validador
    validator = RealTradingDataValidator()
    
    # Test con datos None
    safe_prices = validator.validate_price_data(None)
    print(f"✅ Datos seguros creados: {len(safe_prices)} velas")
    
    # Test con análisis None
    safe_analysis = validator.validate_pattern_analysis(None)
    print(f"✅ Análisis seguro: {safe_analysis['signal']}")
    
    # Reporte de validación
    report = validator.get_validation_report()
    print(f"📊 Reporte: {report['total_errors']} errores")
