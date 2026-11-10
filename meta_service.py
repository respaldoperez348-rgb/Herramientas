import platform
import sys
from datetime import datetime
from typing import Dict, Any

class MetaService:
    """Service for handling application metadata, configs, and health metrics."""
    
    def __init__(self, config_provider):
        # Inject environment variables or config manager here
        self.config = config_provider
        self._start_time = datetime.utcnow()

    def get_app_info(self) -> Dict[str, Any]:
        """Returns standard metadata about the running application."""
        return {
            "app_name": self.config.get("APP_NAME", "Habito API"),
            "version": self.config.get("APP_VERSION", "1.0.0"),
            "environment": self.config.get("ENVIRONMENT", "development"),
            "uptime_seconds": (datetime.utcnow() - self._start_time).total_seconds()
        }

    def get_system_health(self) -> Dict[str, Any]:
        """Runs basic diagnostic checks for system health."""
        # In a real app, you would ping the DB, Redis, etc. here
        db_status = self._check_db_connection()
        
        return {
            "status": "healthy" if db_status else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "python_version": sys.version.split(" ")[0],
            "os": platform.system(),
            "dependencies": {
                "database": "connected" if db_status else "disconnected"
            }
        }

    def get_feature_flags(self, user_id: str = None) -> Dict[str, bool]:
        """Retrieves active feature flags, optionally scoped to a user."""
        base_flags = {
            "enable_dark_mode": True,
            "enable_social_sharing": self.config.get("ENABLE_SOCIAL", False),
            "beta_analytics_dashboard": False
        }
        
        # Example of user-targeted feature flags
        if user_id and user_id in self.config.get("BETA_USERS", []):
            base_flags["beta_analytics_dashboard"] = True
            
        return base_flags

    def _check_db_connection(self) -> bool:
        """Internal method to verify database connectivity."""
        try:
            # Simulate DB ping
            return True
        except Exception:
            return False
