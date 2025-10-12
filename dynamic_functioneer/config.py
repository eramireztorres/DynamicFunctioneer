"""
Configuration management for DynamicFunctioneer.

This module centralizes all configuration values and provides a clean interface
for accessing and overriding defaults.
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ModelConfig:
    """Configuration for LLM model settings."""

    default_model: str = "gpt-4o-mini"
    error_correction_model: str = "gpt-4o"
    hot_swap_model: str = "gpt-4o"
    max_tokens: int = 1024
    temperature: float = 0.5
    error_max_tokens: int = 2048
    error_temperature: float = 0.7


@dataclass
class ExecutionConfig:
    """Configuration for code execution and error handling."""

    fix_dynamically: bool = True
    error_retry_attempts: int = 3
    keep_ok_version: bool = True
    unit_test_enabled: bool = False


@dataclass
class PathConfig:
    """Configuration for file paths."""

    prompt_dir: str = "./dynamic_functioneer/prompts"
    dynamic_code_prefix: str = "d_"
    test_file_prefix: str = "test_"


@dataclass
class DynamicFunctioneerConfig:
    """
    Main configuration class for DynamicFunctioneer.

    This class aggregates all configuration settings and provides
    environment variable overrides where appropriate.
    """

    model: ModelConfig = field(default_factory=ModelConfig)
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)
    paths: PathConfig = field(default_factory=PathConfig)

    @classmethod
    def from_env(cls) -> 'DynamicFunctioneerConfig':
        """
        Create configuration from environment variables.

        Environment variables:
            - DF_DEFAULT_MODEL: Override default model
            - DF_ERROR_MODEL: Override error correction model
            - DF_MAX_TOKENS: Override max tokens
            - DF_TEMPERATURE: Override temperature
            - DF_ERROR_RETRIES: Override error retry attempts
            - DF_FIX_DYNAMICALLY: Override fix_dynamically setting
            - DF_UNIT_TEST: Override unit test setting

        Returns:
            Configuration instance with environment overrides applied.
        """
        config = cls()

        # Model configuration from environment
        if default_model := os.getenv('DF_DEFAULT_MODEL'):
            config.model.default_model = default_model

        if error_model := os.getenv('DF_ERROR_MODEL'):
            config.model.error_correction_model = error_model

        if max_tokens_str := os.getenv('DF_MAX_TOKENS'):
            try:
                config.model.max_tokens = int(max_tokens_str)
            except ValueError:
                pass

        if temperature_str := os.getenv('DF_TEMPERATURE'):
            try:
                config.model.temperature = float(temperature_str)
            except ValueError:
                pass

        # Execution configuration from environment
        if error_retries_str := os.getenv('DF_ERROR_RETRIES'):
            try:
                config.execution.error_retry_attempts = int(error_retries_str)
            except ValueError:
                pass

        if fix_dyn_str := os.getenv('DF_FIX_DYNAMICALLY'):
            config.execution.fix_dynamically = fix_dyn_str.lower() in ('true', '1', 'yes')

        if unit_test_str := os.getenv('DF_UNIT_TEST'):
            config.execution.unit_test_enabled = unit_test_str.lower() in ('true', '1', 'yes')

        return config


# Global default configuration instance
_default_config: Optional[DynamicFunctioneerConfig] = None


def get_config() -> DynamicFunctioneerConfig:
    """
    Get the global configuration instance.

    Returns:
        The global configuration instance. Creates one from environment
        if it doesn't exist yet.
    """
    global _default_config
    if _default_config is None:
        _default_config = DynamicFunctioneerConfig.from_env()
    return _default_config


def set_config(config: DynamicFunctioneerConfig) -> None:
    """
    Set a custom global configuration instance.

    Args:
        config: The configuration instance to use globally.
    """
    global _default_config
    _default_config = config


def reset_config() -> None:
    """Reset configuration to defaults from environment."""
    global _default_config
    _default_config = DynamicFunctioneerConfig.from_env()
