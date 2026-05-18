"""Limitation de débit — dimensionné pour des millions d'utilisateurs."""
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class BurstAnonThrottle(AnonRateThrottle):
    scope = 'anon_burst'


class BurstUserThrottle(UserRateThrottle):
    scope = 'user_burst'


class AuthAnonThrottle(AnonRateThrottle):
    """Login / inscription — anti brute-force."""
    scope = 'auth'


class LocationUserThrottle(UserRateThrottle):
    """Mises à jour GPS fréquentes."""
    scope = 'location'


class QuizUserThrottle(UserRateThrottle):
    scope = 'quiz'
