"""
Configuration management for Quranic Roots Analysis API
Phase 2: Backend API & Analytics Engine
"""

from pydantic import Field
from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application settings
    app_name: str = Field("Quranic Roots Analysis API", env="APP_NAME")
    app_version: str = Field("2.0.0", env="APP_VERSION")
    debug: bool = Field(False, env="DEBUG")
    environment: str = Field("development", env="ENVIRONMENT")
    
    # Server settings
    host: str = Field("0.0.0.0", env="HOST")
    port: int = Field(8000, env="PORT")
    reload: bool = Field(True, env="RELOAD")
    workers: int = Field(1, env="WORKERS")
    
    # CORS settings
    cors_origins: List[str] = Field(
        ["http://localhost:3000", "http://localhost:3001"], 
        env="CORS_ORIGINS"
    )
    cors_allow_credentials: bool = Field(True, env="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: List[str] = Field(["*"], env="CORS_ALLOW_METHODS")
    cors_allow_headers: List[str] = Field(["*"], env="CORS_ALLOW_HEADERS")
    
    # Database settings
    database_url: str = Field(
        "postgresql://user:password@localhost:5432/quranic_roots",
        env="DATABASE_URL"
    )
    database_echo: bool = Field(False, env="DATABASE_ECHO")
    database_pool_size: int = Field(10, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(20, env="DATABASE_MAX_OVERFLOW")
    
    # Redis settings
    redis_url: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    redis_password: Optional[str] = Field(None, env="REDIS_PASSWORD")
    redis_decode_responses: bool = Field(True, env="REDIS_DECODE_RESPONSES")
    
    # Cache settings
    cache_ttl: int = Field(3600, env="CACHE_TTL")  # 1 hour default
    cache_prefix: str = Field("quranic_api:", env="CACHE_PREFIX")
    enable_caching: bool = Field(True, env="ENABLE_CACHING")
    
    # Security settings
    secret_key: str = Field(
        "your-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    algorithm: str = Field("HS256", env="ALGORITHM")
    
    # API settings
    api_v1_prefix: str = Field("/api/v1", env="API_V1_PREFIX")
    max_query_limit: int = Field(1000, env="MAX_QUERY_LIMIT")
    default_query_limit: int = Field(50, env="DEFAULT_QUERY_LIMIT")
    rate_limit_per_minute: int = Field(60, env="RATE_LIMIT_PER_MINUTE")
    
    # Data file paths
    data_directory: str = Field("./", env="DATA_DIRECTORY")
    enhanced_dataset_file: str = Field(
        "quran-enhanced-phase1.csv", 
        env="ENHANCED_DATASET_FILE"
    )
    frequency_analysis_file: str = Field(
        "root-frequency-analysis.csv",
        env="FREQUENCY_ANALYSIS_FILE"
    )
    cooccurrence_matrix_file: str = Field(
        "root-cooccurrence-matrix.csv",
        env="COOCCURRENCE_MATRIX_FILE"
    )
    
    # Analytics settings
    enable_advanced_analytics: bool = Field(True, env="ENABLE_ADVANCED_ANALYTICS")
    clustering_default_k: int = Field(8, env="CLUSTERING_DEFAULT_K")
    cooccurrence_min_threshold: int = Field(2, env="COOCCURRENCE_MIN_THRESHOLD")
    network_analysis_enabled: bool = Field(True, env="NETWORK_ANALYSIS_ENABLED")
    
    # Logging settings
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_format: str = Field(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    log_file: Optional[str] = Field(None, env="LOG_FILE")
    
    # Export settings
    export_directory: str = Field("./exports", env="EXPORT_DIRECTORY")
    export_url_expiry_hours: int = Field(24, env="EXPORT_URL_EXPIRY_HOURS")
    max_export_records: int = Field(10000, env="MAX_EXPORT_RECORDS")
    
    # Monitoring settings
    enable_metrics: bool = Field(True, env="ENABLE_METRICS")
    metrics_port: int = Field(8001, env="METRICS_PORT")
    health_check_timeout: int = Field(5, env="HEALTH_CHECK_TIMEOUT")
    
    @property
    def database_config(self) -> dict:
        """Get database configuration dictionary"""
        return {
            "url": self.database_url,
            "echo": self.database_echo,
            "pool_size": self.database_pool_size,
            "max_overflow": self.database_max_overflow
        }
    
    @property
    def redis_config(self) -> dict:
        """Get Redis configuration dictionary"""
        config = {
            "url": self.redis_url,
            "decode_responses": self.redis_decode_responses
        }
        if self.redis_password:
            config["password"] = self.redis_password
        return config
    
    @property
    def cors_config(self) -> dict:
        """Get CORS configuration dictionary"""
        return {
            "allow_origins": self.cors_origins,
            "allow_credentials": self.cors_allow_credentials,
            "allow_methods": self.cors_allow_methods,
            "allow_headers": self.cors_allow_headers
        }
    
    def get_data_file_path(self, filename: str) -> Path:
        """Get full path for a data file"""
        # Always look relative to the project root, not the backend directory
        backend_dir = Path(__file__).parent
        project_root = backend_dir.parent
        
        # Try project root first (most common case)
        project_path = project_root / filename
        if project_path.exists():
            return project_path
            
        # Try backend directory as fallback
        backend_path = backend_dir / filename
        if backend_path.exists():
            return backend_path
            
        # Try the configured data directory
        data_dir_path = Path(self.data_directory) / filename
        if data_dir_path.exists():
            return data_dir_path
            
        # Return project root path as default (even if file doesn't exist)
        return project_path
    
    def get_export_file_path(self, filename: str) -> Path:
        """Get full path for an export file"""
        export_dir = Path(self.export_directory)
        export_dir.mkdir(exist_ok=True)
        return export_dir / filename
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Create global settings instance
settings = Settings()

# Environment-specific configurations
class DevelopmentSettings(Settings):
    """Development environment settings"""
    debug: bool = True
    reload: bool = True
    database_echo: bool = True
    log_level: str = "DEBUG"

class ProductionSettings(Settings):
    """Production environment settings"""
    debug: bool = False
    reload: bool = False
    database_echo: bool = False
    log_level: str = "WARNING"
    workers: int = 4
    
    # Override with production-safe defaults
    cors_origins: List[str] = ["https://your-frontend-domain.com"]
    secret_key: str = Field(..., env="SECRET_KEY")  # Required in production

class TestingSettings(Settings):
    """Testing environment settings"""
    database_url: str = "sqlite:///./test.db"
    redis_url: str = "redis://localhost:6379/1"  # Different DB for tests
    cache_ttl: int = 60  # Shorter cache for tests
    enable_caching: bool = False  # Disable caching in tests

def get_settings() -> Settings:
    """
    Get settings based on environment
    
    Returns:
        Settings instance appropriate for current environment
    """
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "production":
        return ProductionSettings()
    elif environment == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()

# Global settings instance (can be overridden in tests)
current_settings = get_settings()

# Export commonly used settings
DATABASE_URL = current_settings.database_url
REDIS_URL = current_settings.redis_url
SECRET_KEY = current_settings.secret_key
API_V1_PREFIX = current_settings.api_v1_prefix
CORS_ORIGINS = current_settings.cors_origins 