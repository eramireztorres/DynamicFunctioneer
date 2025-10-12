"""
Protocol interfaces for DynamicFunctioneer.

This module defines Protocol classes (PEP 544) for structural subtyping,
allowing for better interface segregation and LSP compliance.
"""

from typing import Protocol, Optional, List, Dict, Any, runtime_checkable


@runtime_checkable
class ModelAPIProtocol(Protocol):
    """
    Base protocol for model APIs.

    This defines the minimal interface that all model APIs must implement.
    """

    def get_response(self, prompt: str, **kwargs: Any) -> Optional[str]:
        """
        Get a response from the model based on the prompt.

        Args:
            prompt: The input prompt text.
            **kwargs: Additional model-specific parameters.

        Returns:
            The model's response text, or None if request failed.
        """
        ...


@runtime_checkable
class ConversationalModelProtocol(ModelAPIProtocol, Protocol):
    """
    Protocol for models that support conversation history.

    This extends the base ModelAPIProtocol with conversational capabilities.
    """

    conversation_history: List[Dict[str, str]]

    def continue_conversation(
        self,
        new_prompt: str,
        **kwargs: Any
    ) -> Optional[str]:
        """
        Continue a conversation with the model.

        Args:
            new_prompt: The new user prompt to add to the conversation.
            **kwargs: Additional model-specific parameters.

        Returns:
            The model's response text, or None if request failed.
        """
        ...

    def reset_conversation(self) -> None:
        """Reset the conversation history."""
        ...


@runtime_checkable
class TestRunnerProtocol(Protocol):
    """
    Protocol for test execution strategies.

    This allows pluggable test runners (subprocess, pytest, unittest, etc.).
    """

    def run_test(self, test_file_path: str) -> bool:
        """
        Run a test file and return success status.

        Args:
            test_file_path: Path to the test file to execute.

        Returns:
            True if all tests passed, False otherwise.
        """
        ...


@runtime_checkable
class CodeLoaderProtocol(Protocol):
    """
    Protocol for loading dynamically generated code.

    This defines the interface for module import/reload operations.
    """

    def load_function(self, function_name: str):
        """
        Load a function from a dynamic module.

        Args:
            function_name: Name of the function to load.

        Returns:
            The loaded function object.

        Raises:
            ImportError: If the function cannot be loaded.
        """
        ...


@runtime_checkable
class CodeStorageProtocol(Protocol):
    """
    Protocol for code storage operations.

    This defines the interface for saving and loading code from files.
    """

    def save_code(self, code: str) -> None:
        """
        Save code to storage.

        Args:
            code: The code content to save.
        """
        ...

    def load_code(self) -> str:
        """
        Load code from storage.

        Returns:
            The code content.

        Raises:
            FileNotFoundError: If the code file doesn't exist.
        """
        ...

    def code_exists(self) -> bool:
        """
        Check if code exists in storage.

        Returns:
            True if code file exists, False otherwise.
        """
        ...
