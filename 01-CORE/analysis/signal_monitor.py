"""
SignalMonitor
Monitor de señales y alertas para Silver Bullet Enterprise v6.0
"""

class SignalMonitor:
    def __init__(self):
        self.active_signals = []
        self.alerts = []

    def add_signal(self, signal: dict):
        """
        Agrega una nueva señal activa al monitor.
        """
        self.active_signals.append(signal)

    def remove_signal(self, signal_id: str):
        """
        Elimina una señal activa por su ID.
        """
        self.active_signals = [s for s in self.active_signals if s.get('id') != signal_id]

    def get_active_signals(self) -> list:
        """
        Retorna la lista de señales activas.
        """
        return self.active_signals.copy()

    def add_alert(self, alert: dict):
        """
        Agrega una nueva alerta al monitor.
        """
        self.alerts.append(alert)

    def get_alerts(self) -> list:
        """
        Retorna la lista de alertas actuales.
        """
        return self.alerts.copy()
