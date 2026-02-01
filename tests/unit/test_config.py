"""
Unit tests for the configuration system.
"""

import os
import pytest
from dynamic_functioneer.config import (
    ModelConfig,
    ExecutionConfig,
    PathConfig,
    DynamicFunctioneerConfig,
    get_config,
    set_config,
    reset_config,
)


class TestModelConfig:
    """Test ModelConfig dataclass."""

    def test_default_values(self):
        """Test default configuration values."""
        config = ModelConfig()
        assert config.default_model == "gpt-4.1-mini"
        assert config.error_correction_model == "gpt-4o"
        assert config.hot_swap_model == "gpt-4o"
        assert config.max_tokens == 1024
        assert config.temperature == 0.5

    def test_custom_values(self):
        """Test setting custom values."""
        config = ModelConfig(
            default_model="claude-3-opus",
            max_tokens=2048,
            temperature=0.7
        )
        assert config.default_model == "claude-3-opus"
        assert config.max_tokens == 2048
        assert config.temperature == 0.7


class TestExecutionConfig:
    """Test ExecutionConfig dataclass."""

    def test_default_values(self):
        """Test default execution configuration."""
        config = ExecutionConfig()
        assert config.fix_dynamically is True
        assert config.error_retry_attempts == 3
        assert config.keep_ok_version is True
        assert config.unit_test_enabled is False

    def test_custom_values(self):
        """Test custom execution configuration."""
        config = ExecutionConfig(
            fix_dynamically=False,
            error_retry_attempts=5,
            unit_test_enabled=True
        )
        assert config.fix_dynamically is False
        assert config.error_retry_attempts == 5
        assert config.unit_test_enabled is True


class TestPathConfig:
    """Test PathConfig dataclass."""

    def test_default_paths(self):
        """Test default path configuration."""
        config = PathConfig()
        assert config.prompt_dir == "./dynamic_functioneer/prompts"
        assert config.dynamic_code_prefix == "d_"
        assert config.test_file_prefix == "test_"


class TestDynamicFunctioneerConfig:
    """Test main configuration class."""

    def test_default_config(self):
        """Test default configuration."""
        config = DynamicFunctioneerConfig()
        assert isinstance(config.model, ModelConfig)
        assert isinstance(config.execution, ExecutionConfig)
        assert isinstance(config.paths, PathConfig)

    def test_from_env_no_env_vars(self, monkeypatch):
        """Test from_env with no environment variables."""
        # Clear any existing env vars
        for key in ['DF_DEFAULT_MODEL', 'DF_ERROR_MODEL', 'DF_MAX_TOKENS',
                    'DF_TEMPERATURE', 'DF_ERROR_RETRIES', 'DF_FIX_DYNAMICALLY',
                    'DF_UNIT_TEST']:
            monkeypatch.delenv(key, raising=False)

        config = DynamicFunctioneerConfig.from_env()
        assert config.model.default_model == "gpt-4.1-mini"  # default

    def test_from_env_with_env_vars(self, monkeypatch):
        """Test from_env with environment variables."""
        monkeypatch.setenv('DF_DEFAULT_MODEL', 'claude-3-opus')
        monkeypatch.setenv('DF_MAX_TOKENS', '2048')
        monkeypatch.setenv('DF_TEMPERATURE', '0.8')
        monkeypatch.setenv('DF_ERROR_RETRIES', '5')
        monkeypatch.setenv('DF_FIX_DYNAMICALLY', 'false')
        monkeypatch.setenv('DF_UNIT_TEST', 'true')

        config = DynamicFunctioneerConfig.from_env()
        assert config.model.default_model == 'claude-3-opus'
        assert config.model.max_tokens == 2048
        assert config.model.temperature == 0.8
        assert config.execution.error_retry_attempts == 5
        assert config.execution.fix_dynamically is False
        assert config.execution.unit_test_enabled is True

    def test_from_env_invalid_values(self, monkeypatch):
        """Test from_env with invalid values (should be ignored)."""
        monkeypatch.setenv('DF_MAX_TOKENS', 'invalid')
        monkeypatch.setenv('DF_TEMPERATURE', 'invalid')
        monkeypatch.setenv('DF_ERROR_RETRIES', 'invalid')

        config = DynamicFunctioneerConfig.from_env()
        # Should fall back to defaults
        assert config.model.max_tokens == 1024
        assert config.model.temperature == 0.5
        assert config.execution.error_retry_attempts == 3


class TestConfigGlobalFunctions:
    """Test global configuration functions."""

    def test_get_config(self):
        """Test get_config returns a config instance."""
        config = get_config()
        assert isinstance(config, DynamicFunctioneerConfig)

    def test_set_config(self):
        """Test set_config and get_config."""
        custom_config = DynamicFunctioneerConfig()
        custom_config.model.default_model = "custom-model"

        set_config(custom_config)
        retrieved = get_config()
        assert retrieved.model.default_model == "custom-model"

        # Reset for other tests
        reset_config()

    def test_reset_config(self):
        """Test reset_config."""
        # Set custom config
        custom_config = DynamicFunctioneerConfig()
        custom_config.model.default_model = "custom-model"
        set_config(custom_config)

        # Reset
        reset_config()
        config = get_config()
        # Should be back to defaults (or from env)
        assert isinstance(config, DynamicFunctioneerConfig)
