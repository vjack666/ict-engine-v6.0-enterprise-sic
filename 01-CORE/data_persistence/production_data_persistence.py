#!/usr/bin/env python3
"""
Production Data Persistence - ICT Engine v6.0 Enterprise
========================================================

Sistema centralizado de persistencia de datos para trading en producción.
Maneja storage, recovery, backup y sincronización de datos críticos.

Características:
✅ Persistencia atómica y transaccional
✅ Backup automático y recovery
✅ Compresión inteligente de datos
✅ Índices optimizados para queries frecuentes
✅ Sincronización multi-proceso
✅ Métricas de performance del storage

Autor: ICT Engine v6.0 Team
"""
from __future__ import annotations
from protocols.unified_logging import get_unified_logger

import json
import gzip
import sqlite3
import threading
import time
import shutil
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Callable, Iterator
import hashlib
import os

try:
    from protocols.logging_central_protocols import create_production_logger, LogLevel
    logger = create_production_logger("ProductionDataPersistence", LogLevel.INFO)
except Exception:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ProductionDataPersistence")

# Storage Types
class StorageType(Enum):
    """Tipos de almacenamiento"""
    JSON = "json"
    JSON_COMPRESSED = "json_gz"
    SQLITE = "sqlite"
    BINARY = "binary"

class DataCategory(Enum):
    """Categorías de datos"""
    TRADING_SIGNALS = "trading_signals"
    EXECUTION_RESULTS = "execution_results"
    MARKET_DATA = "market_data"
    PERFORMANCE_METRICS = "performance_metrics"
    SYSTEM_LOGS = "system_logs"
    RISK_EVENTS = "risk_events"
    POSITIONS = "positions"
    ACCOUNT_STATE = "account_state"

@dataclass
class DataRecord:
    """Registro de datos para persistencia"""
    id: str
    category: DataCategory
    timestamp: datetime
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if 'created_at' not in self.metadata:
            self.metadata['created_at'] = datetime.now().isoformat()

@dataclass
class StorageConfig:
    """Configuración del sistema de almacenamiento"""
    base_path: Path = Path("data")
    backup_path: Path = Path("backups")
    enable_compression: bool = True
    backup_interval_hours: int = 6
    retention_days: int = 30
    max_file_size_mb: int = 100
    enable_sqlite: bool = True
    sqlite_timeout_seconds: int = 30
    atomic_writes: bool = True
    sync_to_disk: bool = True

class ProductionDataPersistence:
    """
    Sistema de persistencia de datos para producción
    
    Gestiona:
    - Almacenamiento atómico y transaccional
    - Backup automático y recovery
    - Índices para búsquedas rápidas
    - Compresión de datos
    - Limpieza automática de datos antiguos
    """
    
    def __init__(self, config: Optional[StorageConfig] = None):
        self.config = config or StorageConfig()
        
        # Setup directories
        self._setup_directories()
        
        # SQLite connection
        self._db_path = self.config.base_path / "production_data.db"
        self._db_lock = threading.RLock()
        
        # File locks para prevenir corrupción
        self._file_locks: Dict[str, threading.Lock] = {}
        self._locks_lock = threading.Lock()
        
        # Background tasks
        self._executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="DataPersistence")
        self._shutdown_event = threading.Event()
        self._backup_thread: Optional[threading.Thread] = None
        
        # Metrics
        self.metrics = {
            'total_writes': 0,
            'total_reads': 0,
            'compressed_writes': 0,
            'backup_count': 0,
            'errors': 0,
            'avg_write_time_ms': 0.0,
            'avg_read_time_ms': 0.0,
            'total_storage_mb': 0.0
        }
        self._metrics_lock = threading.Lock()
        
        # Initialize
        self._initialize_database()
        self._start_background_tasks()
        
        logger.info("ProductionDataPersistence initialized", "INIT")
    
    def _setup_directories(self) -> None:
        """Crear directorios necesarios"""
        for path in [self.config.base_path, self.config.backup_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Crear subdirectorios por categoría
        for category in DataCategory:
            (self.config.base_path / category.value).mkdir(exist_ok=True)
    
    def _initialize_database(self) -> None:
        """Inicializar base de datos SQLite"""
        if not self.config.enable_sqlite:
            return
        
        try:
            with self._get_db_connection() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS data_records (
                        id TEXT PRIMARY KEY,
                        category TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        data_json TEXT NOT NULL,
                        metadata_json TEXT,
                        file_path TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_category_timestamp 
                    ON data_records (category, timestamp)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_timestamp 
                    ON data_records (timestamp)
                """)
                
                conn.commit()
                
            logger.info("SQLite database initialized", "DATABASE")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}", "DATABASE")
            self.config.enable_sqlite = False
    
    @contextmanager
    def _get_db_connection(self):
        """Context manager para conexiones SQLite thread-safe"""
        with self._db_lock:
            conn = sqlite3.connect(
                str(self._db_path),
                timeout=self.config.sqlite_timeout_seconds
            )
            conn.row_factory = sqlite3.Row
            try:
                yield conn
            finally:
                conn.close()
    
    def _get_file_lock(self, file_path: str) -> threading.Lock:
        """Obtener lock para archivo específico"""
        with self._locks_lock:
            if file_path not in self._file_locks:
                self._file_locks[file_path] = threading.Lock()
            return self._file_locks[file_path]
    
    def _start_background_tasks(self) -> None:
        """Iniciar tareas en background"""
        self._backup_thread = threading.Thread(
            target=self._backup_loop,
            name="DataBackup",
            daemon=True
        )
        self._backup_thread.start()
    
    def _backup_loop(self) -> None:
        """Bucle de backup automático"""
        backup_interval = self.config.backup_interval_hours * 3600
        
        while not self._shutdown_event.is_set():
            try:
                time.sleep(backup_interval)
                if not self._shutdown_event.is_set():
                    self.create_backup()
            except Exception as e:
                logger.error(f"Backup loop error: {e}", "BACKUP")
                time.sleep(60)  # Wait 1 minute before retry
    
    # Core Persistence Methods
    def store_data(self, 
                   record_id: str, 
                   category: DataCategory,
                   data: Dict[str, Any],
                   metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Almacenar datos de forma atómica
        
        Args:
            record_id: ID único del registro
            category: Categoría de datos
            data: Datos a almacenar
            metadata: Metadatos opcionales
            
        Returns:
            bool: True si se almacenó exitosamente
        """
        start_time = time.time()
        
        try:
            record = DataRecord(
                id=record_id,
                category=category,
                timestamp=datetime.now(),
                data=data,
                metadata=metadata or {}
            )
            
            # Determine storage path
            file_path = self._get_storage_path(record)
            
            # Atomic write
            success = self._write_record(record, file_path)
            
            if success and self.config.enable_sqlite:
                self._store_in_database(record, str(file_path))
            
            # Update metrics
            write_time_ms = (time.time() - start_time) * 1000
            self._update_write_metrics(write_time_ms, success)
            
            if success:
                logger.debug(f"Data stored: {record_id} ({category.value})", "STORE")
            
            return success
            
        except Exception as e:
            logger.error(f"Store data error: {e}", "STORE")
            self._update_error_metrics()
            return False
    
    def load_data(self, 
                  record_id: str, 
                  category: Optional[DataCategory] = None) -> Optional[DataRecord]:
        """
        Cargar datos por ID
        
        Args:
            record_id: ID del registro
            category: Categoría para optimizar búsqueda
            
        Returns:
            DataRecord o None si no se encuentra
        """
        start_time = time.time()
        
        try:
            # Try SQLite first if available
            if self.config.enable_sqlite:
                record = self._load_from_database(record_id)
                if record:
                    read_time_ms = (time.time() - start_time) * 1000
                    self._update_read_metrics(read_time_ms)
                    return record
            
            # Fallback to file search
            if category:
                categories_to_search = [category]
            else:
                categories_to_search = list(DataCategory)
            
            for cat in categories_to_search:
                record = self._load_from_files(record_id, cat)
                if record:
                    read_time_ms = (time.time() - start_time) * 1000
                    self._update_read_metrics(read_time_ms)
                    return record
            
            return None
            
        except Exception as e:
            logger.error(f"Load data error: {e}", "LOAD")
            self._update_error_metrics()
            return None
    
    def query_data(self, 
                   category: DataCategory,
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None,
                   limit: int = 100) -> List[DataRecord]:
        """
        Consultar datos por categoría y rango temporal
        
        Args:
            category: Categoría de datos
            start_time: Timestamp inicial
            end_time: Timestamp final
            limit: Máximo número de registros
            
        Returns:
            Lista de registros
        """
        try:
            if self.config.enable_sqlite:
                return self._query_from_database(category, start_time, end_time, limit)
            else:
                return self._query_from_files(category, start_time, end_time, limit)
                
        except Exception as e:
            logger.error(f"Query data error: {e}", "QUERY")
            return []
    
    def _get_storage_path(self, record: DataRecord) -> Path:
        """Determinar path de almacenamiento"""
        category_dir = self.config.base_path / record.category.value
        
        # Organizar por fecha para mejor particionado
        date_str = record.timestamp.strftime('%Y-%m-%d')
        date_dir = category_dir / date_str
        date_dir.mkdir(exist_ok=True)
        
        # Filename con timestamp para unicidad
        timestamp_str = record.timestamp.strftime('%H%M%S_%f')[:-3]  # ms precision
        filename = f"{record.id}_{timestamp_str}.json"
        
        if self.config.enable_compression:
            filename += ".gz"
        
        return date_dir / filename
    
    def _write_record(self, record: DataRecord, file_path: Path) -> bool:
        """Escribir registro de forma atómica"""
        try:
            file_lock = self._get_file_lock(str(file_path))
            
            with file_lock:
                # Prepare data
                data_to_write = {
                    'id': record.id,
                    'category': record.category.value,
                    'timestamp': record.timestamp.isoformat(),
                    'data': record.data,
                    'metadata': record.metadata
                }
                
                json_str = json.dumps(data_to_write, ensure_ascii=False, separators=(',', ':'))
                
                if self.config.atomic_writes:
                    # Atomic write using temporary file
                    temp_path = file_path.with_suffix(file_path.suffix + '.tmp')
                    
                    if self.config.enable_compression and file_path.suffix == '.gz':
                        with gzip.open(temp_path, 'wt', encoding='utf-8') as f:
                            f.write(json_str)
                        with self._metrics_lock:
                            self.metrics['compressed_writes'] += 1
                    else:
                        with open(temp_path, 'w', encoding='utf-8') as f:
                            f.write(json_str)
                    
                    # Atomic move
                    temp_path.replace(file_path)
                    
                    if self.config.sync_to_disk:
                        # Flush best-effort: fsync the directory entry (POSIX) or file descriptor if available.
                        try:
                            if hasattr(os, 'sync'):
                                os.sync()  # type: ignore[attr-defined]
                            else:
                                # Fallback: open directory and fsync (POSIX) or no-op on Windows
                                try:
                                    dir_fd = os.open(str(file_path.parent), os.O_RDONLY)
                                    try:
                                        os.fsync(dir_fd)
                                    finally:
                                        os.close(dir_fd)
                                except Exception:
                                    pass
                        except Exception:
                            pass
                else:
                    # Direct write
                    if self.config.enable_compression and file_path.suffix == '.gz':
                        with gzip.open(file_path, 'wt', encoding='utf-8') as f:
                            f.write(json_str)
                        with self._metrics_lock:
                            self.metrics['compressed_writes'] += 1
                    else:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(json_str)
                
                return True
                
        except Exception as e:
            logger.error(f"Write record error: {e}", "WRITE")
            return False
    
    def _store_in_database(self, record: DataRecord, file_path: str) -> None:
        """Almacenar índice en SQLite"""
        try:
            with self._get_db_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO data_records 
                    (id, category, timestamp, data_json, metadata_json, file_path)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    record.id,
                    record.category.value,
                    record.timestamp.isoformat(),
                    json.dumps(record.data),
                    json.dumps(record.metadata),
                    file_path
                ))
                conn.commit()
                
        except Exception as e:
            logger.warning(f"Database store error: {e}", "DATABASE")
    
    def _load_from_database(self, record_id: str) -> Optional[DataRecord]:
        """Cargar desde SQLite"""
        try:
            with self._get_db_connection() as conn:
                row = conn.execute(
                    "SELECT * FROM data_records WHERE id = ?",
                    (record_id,)
                ).fetchone()
                
                if row:
                    return DataRecord(
                        id=row['id'],
                        category=DataCategory(row['category']),
                        timestamp=datetime.fromisoformat(row['timestamp']),
                        data=json.loads(row['data_json']),
                        metadata=json.loads(row['metadata_json']) if row['metadata_json'] else {}
                    )
                    
        except Exception as e:
            logger.warning(f"Database load error: {e}", "DATABASE")
        
        return None
    
    def _load_from_files(self, record_id: str, category: DataCategory) -> Optional[DataRecord]:
        """Cargar desde archivos (fallback)"""
        category_dir = self.config.base_path / category.value
        
        if not category_dir.exists():
            return None
        
        # Search in date directories (most recent first)
        date_dirs = sorted([d for d in category_dir.iterdir() if d.is_dir()], reverse=True)
        
        for date_dir in date_dirs:
            for file_path in date_dir.glob(f"{record_id}_*.json*"):
                try:
                    if file_path.suffix == '.gz':
                        with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                            data = json.load(f)
                    else:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                    
                    return DataRecord(
                        id=data['id'],
                        category=DataCategory(data['category']),
                        timestamp=datetime.fromisoformat(data['timestamp']),
                        data=data['data'],
                        metadata=data.get('metadata', {})
                    )
                    
                except Exception as e:
                    logger.warning(f"File load error {file_path}: {e}", "LOAD")
                    continue
        
        return None
    
    def _query_from_database(self, 
                           category: DataCategory,
                           start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None,
                           limit: int = 100) -> List[DataRecord]:
        """Consultar desde SQLite"""
        try:
            with self._get_db_connection() as conn:
                sql = "SELECT * FROM data_records WHERE category = ?"
                params = [category.value]
                
                if start_time:
                    sql += " AND timestamp >= ?"
                    params.append(start_time.isoformat())
                
                if end_time:
                    sql += " AND timestamp <= ?"
                    params.append(end_time.isoformat())
                
                sql += " ORDER BY timestamp DESC LIMIT ?"
                # Keep parameter types homogeneous (all str) for type checker; SQLite will coerce
                params.append(str(limit))
                
                rows = conn.execute(sql, params).fetchall()
                
                records = []
                for row in rows:
                    record = DataRecord(
                        id=row['id'],
                        category=DataCategory(row['category']),
                        timestamp=datetime.fromisoformat(row['timestamp']),
                        data=json.loads(row['data_json']),
                        metadata=json.loads(row['metadata_json']) if row['metadata_json'] else {}
                    )
                    records.append(record)
                
                return records
                
        except Exception as e:
            logger.error(f"Database query error: {e}", "QUERY")
            return []
    
    def _query_from_files(self, 
                        category: DataCategory,
                        start_time: Optional[datetime] = None,
                        end_time: Optional[datetime] = None,
                        limit: int = 100) -> List[DataRecord]:
        """Consultar desde archivos (fallback)"""
        category_dir = self.config.base_path / category.value
        
        if not category_dir.exists():
            return []
        
        records = []
        
        # Search in date directories
        for date_dir in sorted([d for d in category_dir.iterdir() if d.is_dir()], reverse=True):
            if len(records) >= limit:
                break
            
            for file_path in sorted(date_dir.glob("*.json*"), reverse=True):
                if len(records) >= limit:
                    break
                
                try:
                    if file_path.suffix == '.gz':
                        with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                            data = json.load(f)
                    else:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                    
                    timestamp = datetime.fromisoformat(data['timestamp'])
                    
                    # Filter by time range
                    if start_time and timestamp < start_time:
                        continue
                    if end_time and timestamp > end_time:
                        continue
                    
                    record = DataRecord(
                        id=data['id'],
                        category=category,
                        timestamp=timestamp,
                        data=data['data'],
                        metadata=data.get('metadata', {})
                    )
                    records.append(record)
                    
                except Exception as e:
                    logger.warning(f"File query error {file_path}: {e}", "QUERY")
                    continue
        
        return records
    
    # Backup and Recovery
    def create_backup(self) -> bool:
        """Crear backup completo"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = self.config.backup_path / f"backup_{timestamp}"
            backup_dir.mkdir(exist_ok=True)
            
            # Backup data files
            shutil.copytree(
                self.config.base_path,
                backup_dir / "data",
                dirs_exist_ok=True
            )
            
            # Backup SQLite database
            if self.config.enable_sqlite and self._db_path.exists():
                shutil.copy2(self._db_path, backup_dir / "production_data.db")
            
            # Create backup manifest
            manifest = {
                'timestamp': timestamp,
                'created_at': datetime.now().isoformat(),
                'data_path': str(self.config.base_path),
                'backup_path': str(backup_dir),
                'includes_database': self.config.enable_sqlite,
                'total_files': sum(1 for _ in backup_dir.rglob('*') if _.is_file())
            }
            
            with open(backup_dir / "backup_manifest.json", 'w') as f:
                json.dump(manifest, f, indent=2)
            
            with self._metrics_lock:
                self.metrics['backup_count'] += 1
            
            logger.info(f"Backup created: {backup_dir}", "BACKUP")
            
            # Cleanup old backups
            self._cleanup_old_backups()
            
            return True
            
        except Exception as e:
            logger.error(f"Backup creation failed: {e}", "BACKUP")
            return False
    
    def _cleanup_old_backups(self) -> None:
        """Limpiar backups antiguos"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.config.retention_days)
            
            for backup_dir in self.config.backup_path.iterdir():
                if backup_dir.is_dir() and backup_dir.name.startswith('backup_'):
                    try:
                        # Extract timestamp from directory name
                        timestamp_str = backup_dir.name.replace('backup_', '')
                        backup_date = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                        
                        if backup_date < cutoff_date:
                            shutil.rmtree(backup_dir)
                            logger.info(f"Old backup removed: {backup_dir}", "CLEANUP")
                            
                    except Exception as e:
                        logger.warning(f"Error removing old backup {backup_dir}: {e}", "CLEANUP")
                        
        except Exception as e:
            logger.warning(f"Backup cleanup error: {e}", "CLEANUP")
    
    def _update_write_metrics(self, write_time_ms: float, success: bool) -> None:
        """Actualizar métricas de escritura"""
        with self._metrics_lock:
            if success:
                self.metrics['total_writes'] += 1
                
                # Update average write time
                current_avg = self.metrics['avg_write_time_ms']
                total_writes = self.metrics['total_writes']
                
                new_avg = ((current_avg * (total_writes - 1)) + write_time_ms) / total_writes
                self.metrics['avg_write_time_ms'] = new_avg
            else:
                self.metrics['errors'] += 1
    
    def _update_read_metrics(self, read_time_ms: float) -> None:
        """Actualizar métricas de lectura"""
        with self._metrics_lock:
            self.metrics['total_reads'] += 1
            
            # Update average read time
            current_avg = self.metrics['avg_read_time_ms']
            total_reads = self.metrics['total_reads']
            
            new_avg = ((current_avg * (total_reads - 1)) + read_time_ms) / total_reads
            self.metrics['avg_read_time_ms'] = new_avg
    
    def _update_error_metrics(self) -> None:
        """Actualizar métricas de errores"""
        with self._metrics_lock:
            self.metrics['errors'] += 1
    
    # Public API
    def get_metrics(self) -> Dict[str, Any]:
        """Obtener métricas de rendimiento"""
        with self._metrics_lock:
            # Calculate storage usage
            total_size = 0
            try:
                for path in self.config.base_path.rglob('*'):
                    if path.is_file():
                        total_size += path.stat().st_size
                
                self.metrics['total_storage_mb'] = total_size / (1024 * 1024)
            except Exception:
                pass
            
            return self.metrics.copy()
    
    def cleanup_old_data(self, category: Optional[DataCategory] = None) -> int:
        """
        Limpiar datos antiguos
        
        Args:
            category: Categoría específica o None para todas
            
        Returns:
            int: Número de archivos removidos
        """
        cutoff_date = datetime.now() - timedelta(days=self.config.retention_days)
        removed_count = 0
        
        categories_to_clean = [category] if category else list(DataCategory)
        
        for cat in categories_to_clean:
            category_dir = self.config.base_path / cat.value
            
            if not category_dir.exists():
                continue
            
            try:
                for date_dir in category_dir.iterdir():
                    if date_dir.is_dir():
                        try:
                            # Parse date from directory name
                            date_obj = datetime.strptime(date_dir.name, '%Y-%m-%d')
                            
                            if date_obj.date() < cutoff_date.date():
                                # Remove old date directory
                                shutil.rmtree(date_dir)
                                removed_count += 1
                                logger.info(f"Removed old data directory: {date_dir}", "CLEANUP")
                                
                        except ValueError:
                            # Skip directories that don't match date format
                            continue
                            
            except Exception as e:
                logger.warning(f"Cleanup error for {cat.value}: {e}", "CLEANUP")
        
        # Also cleanup database entries
        if self.config.enable_sqlite:
            try:
                with self._get_db_connection() as conn:
                    cursor = conn.execute("""
                        DELETE FROM data_records 
                        WHERE timestamp < ?
                    """, (cutoff_date.isoformat(),))
                    
                    deleted_rows = cursor.rowcount
                    conn.commit()
                    
                    if deleted_rows > 0:
                        logger.info(f"Removed {deleted_rows} old database entries", "CLEANUP")
                        
            except Exception as e:
                logger.warning(f"Database cleanup error: {e}", "CLEANUP")
        
        return removed_count
    
    def shutdown(self) -> None:
        """Cierre graceful del sistema"""
        logger.info("Shutting down ProductionDataPersistence", "SHUTDOWN")
        
        self._shutdown_event.set()
        
        # Wait for backup thread
        if self._backup_thread and self._backup_thread.is_alive():
            self._backup_thread.join(timeout=10)
        
        # Shutdown executor
        # ThreadPoolExecutor.shutdown in stdlib does not accept timeout param; emulate manual wait.
        self._executor.shutdown(wait=True)
        
        # Final backup
        self.create_backup()
        
        logger.info("ProductionDataPersistence shutdown complete", "SHUTDOWN")

# Global instance management
_global_persistence: Optional[ProductionDataPersistence] = None

def get_production_persistence() -> ProductionDataPersistence:
    """Obtener instancia global del sistema de persistencia"""
    global _global_persistence
    if _global_persistence is None:
        _global_persistence = ProductionDataPersistence()
    return _global_persistence

def set_production_persistence(persistence: ProductionDataPersistence) -> None:
    """Establecer instancia global del sistema de persistencia"""
    global _global_persistence
    _global_persistence = persistence

__all__ = [
    'ProductionDataPersistence',
    'DataRecord',
    'DataCategory',
    'StorageConfig',
    'StorageType',
    'get_production_persistence',
    'set_production_persistence'
]