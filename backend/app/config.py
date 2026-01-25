"""
类型安全的配置管理模块
使用 Pydantic Settings 从环境变量加载配置
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置类 - 所有配置通过环境变量加载"""
    
    # API Keys
    dashscope_api_key: str = ""
    modelscope_api_key: str = ""
    minimax_api_key: str = ""
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 7860
    debug: bool = False
    
    # Proxy Configuration
    proxy_timeout: int = 120
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # 忽略未定义的环境变量


@lru_cache()
def get_settings() -> Settings:
    """获取缓存的配置实例（单例模式）"""
    return Settings()


# 全局配置实例
settings = get_settings()
