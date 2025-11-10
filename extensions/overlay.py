"""
Placeholder / exemple pour futurs overlays.
Tu pourras y mettre une classe OverlayManager qui crée une fenêtre transparente au-dessus du jeu.
"""

class OverlayManager:
    def __init__(self):
        self.enabled = False

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def toggle(self):
        self.enabled = not self.enabled

# TODO: implémenter la fenêtre PyQt transparente et la logique d'affichage