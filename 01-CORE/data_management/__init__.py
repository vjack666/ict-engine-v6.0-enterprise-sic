#!/usr/bin/env python3
"""
Data Management Module - ICT Engine v6.1.0 Enterprise SIC
=======================================================

Módulo de gestión de datos integrado con SIC v3.1 Enterprise.
Contiene herramientas avanzadas para descarga, procesamiento y
almacenamiento de datos financieros.

Componentes:
- AdvancedCandleDownloader: Descarga inteligente de velas
- CandleCoordinator: Coordinación de descargas
- DataProcessor: Procesamiento avanzado de datos
- CacheManager: Gestión de cache predictivo

Autor: ICT Engine v6.1.0 Enterprise Team
Versión: v6.1.0-enterprise
Fecha: Agosto 2025
"""

__version__ = "6.0.0-enterprise"
__author__ = "ICT Engine v6.1.0 Enterprise Team"

# Importaciones principales (lazy loading habilitado)
try:
    from .advanced_candle_downloader import (
        AdvancedCandleDownloader,
        get_advanced_candle_downloader,
        create_download_request,
        DownloadStats,
        DownloadRequest,
        DownloadStatus
    )
    _ADVANCED_CANDLE_DOWNLOADER_AVAILABLE = True
except ImportError as e:
    _ADVANCED_CANDLE_DOWNLOADER_AVAILABLE = False
    _IMPORT_ERROR = str(e)

# Exports principales
__all__ = [
    'AdvancedCandleDownloader',
    'get_advanced_candle_downloader', 
    'create_download_request',
    'DownloadStats',
    'DownloadRequest',
    'DownloadStatus'
]

# Información del módulo
MODULE_INFO = {
    'name': 'data_management',
    'version': __version__,
    'description': 'Advanced data management with SIC v3.1 integration',
    'components': {
        'advanced_candle_downloader': _ADVANCED_CANDLE_DOWNLOADER_AVAILABLE
    },
    'sic_integration': 'v3.1'
}

def get_module_status():
    """Obtiene el estado del módulo data_management"""
    return {
        'version': __version__,
        'advanced_candle_downloader': _ADVANCED_CANDLE_DOWNLOADER_AVAILABLE,
        'import_error': _IMPORT_ERROR if not _ADVANCED_CANDLE_DOWNLOADER_AVAILABLE else None
    }
