import os


class Config:
    """
    Configuración general del sistema HabitTracker.
    """

    APP_NAME = "HabitTracker"
    VERSION = "1.0.0"

    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", "5000"))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///habittracker.db"
    )
