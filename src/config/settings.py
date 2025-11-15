"""
Application Configuration
Runtime configuration and settings management
"""
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import json

class Config:
    """Application configuration manager"""
    
    def __init__(self, env: str = "production"):
        self.env = env
        self.base_dir = Path(__file__).parent.parent.parent
        self.config_file = self.base_dir / "config.json"
        
        # Load configuration
        self._config = self._load_config()
        
        # Setup logging
        self._setup_logging()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            "app": {
                "name": "StocksV2 Dashboard",
                "version": "2.0.0",
                "port": 8501,
                "debug": self.env == "development"
            },
            "cache": {
                "enabled": True,
                "ttl": 300,
                "dir": "data/cache",
                "db_name": "market_data.db"
            },
            "api": {
                "yfinance": {
                    "rate_limit": 2000,
                    "timeout": 10,
                    "retries": 3
                },
                "reddit": {
                    "client_id": os.getenv("REDDIT_CLIENT_ID", ""),
                    "client_secret": os.getenv("REDDIT_CLIENT_SECRET", ""),
                    "user_agent": os.getenv("REDDIT_USER_AGENT", "StocksV2App/1.0")
                },
                "news": {
                    "api_key": os.getenv("NEWS_API_KEY", "")
                }
            },
            "features": {
                "sentiment_analysis": True,
                "options_analysis": True,
                "crypto_analysis": True,
                "institutional_data": True,
                "debug_panel": self.env == "development"
            },
            "logging": {
                "level": "INFO" if self.env == "production" else "DEBUG",
                "dir": "logs",
                "file": "dashboard.log",
                "max_size": 10485760,  # 10MB
                "backup_count": 5
            },
            "display": {
                "theme": "light",
                "chart_height": 600,
                "max_rows": 100,
                "decimals": 2
            }
        }
        
        # Try to load from file
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                    # Merge with defaults
                    default_config.update(file_config)
            except Exception as e:
                logging.warning(f"Could not load config file: {e}. Using defaults.")
        
        return default_config
    
    def _setup_logging(self):
        """Setup application logging"""
        log_config = self._config.get("logging", {})
        log_dir = Path(log_config.get("dir", "logs"))
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / log_config.get("file", "dashboard.log")
        log_level = getattr(logging, log_config.get("level", "INFO"))
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Application started in {self.env} mode")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot notation key"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value by dot notation key"""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
            self.logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            self.logger.error(f"Could not save configuration: {e}")
    
    def reload(self):
        """Reload configuration from file"""
        self._config = self._load_config()
        self.logger.info("Configuration reloaded")
    
    @property
    def is_debug(self) -> bool:
        """Check if debug mode is enabled"""
        return self.get("app.debug", False)
    
    @property
    def is_cache_enabled(self) -> bool:
        """Check if caching is enabled"""
        return self.get("cache.enabled", True)
    
    @property
    def cache_ttl(self) -> int:
        """Get cache TTL"""
        return self.get("cache.ttl", 300)
    
    def __repr__(self) -> str:
        return f"<Config env={self.env}>"


# Global configuration instance
_config_instance: Optional[Config] = None


def get_config(env: str = None) -> Config:
    """Get global configuration instance"""
    global _config_instance
    
    if _config_instance is None:
        if env is None:
            env = os.getenv("ENV", "production")
        _config_instance = Config(env=env)
    
    return _config_instance


def reset_config():
    """Reset global configuration instance"""
    global _config_instance
    _config_instance = None
