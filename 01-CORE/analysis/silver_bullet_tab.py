"""
SilverBulletTab
Módulo de pestaña Silver Bullet para dashboard enterprise v6.0
"""

class SilverBulletTab:
    def __init__(self):
        self.tab_name = "Silver Bullet"
        self.active = False
        self.data = {}

    def activate(self):
        """
        Activa la pestaña Silver Bullet en el dashboard.
        """
        self.active = True

    def deactivate(self):
        """
        Desactiva la pestaña Silver Bullet.
        """
        self.active = False

    def update_data(self, new_data: dict):
        """
        Actualiza los datos mostrados en la pestaña.
        """
        self.data.update(new_data)

    def get_data(self) -> dict:
        """
        Retorna los datos actuales de la pestaña.
        """
        return self.data.copy()
