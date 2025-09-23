"""
black_box_logs.py
Funciones básicas de logging para ICT Engine v6.0 compatible con SLUC v2.1
"""
import logging
from typing import Optional

# Logging básico

def log_info(message: str):
    logging.info(f"[BLACK_BOX][INFO] {message}")

def log_warning(message: str):
    logging.warning(f"[BLACK_BOX][WARNING] {message}")

def log_error(message: str):
    logging.error(f"[BLACK_BOX][ERROR] {message}")

def log_event(event: str, details: Optional[dict] = None):
    if details is None:
        details = {}
    logging.info(f"[BLACK_BOX][EVENT] {event} | {details}")

# SLUC v2.1 compatible stub

def sluc_log(event: str, msg: str, details: Optional[dict] = None):
    if details is None:
        details = {}
    logging.info(f"[SLUC][{event}] {msg} | {details}")
