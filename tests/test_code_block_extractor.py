import pytest
from dynamic_functioneer.llm_response_cleaner import CodeBlockExtractor

@pytest.mark.parametrize(
    "description, input_text, expected_output",
    [
        (
            "Single code block",
            """
            This is an example:
            ```python
            def add(a, b):
                return a + b
            ```
            End of response.
            """,
            "def add(a, b):\n    return a + b",
        ),
        (
            "No code block present",
            """
            Hello, there's no code here at all.
            Just a regular message with no triple backticks.
            """,
            # No code block, so output should be the original text
            """
            Hello, there's no code here at all.
            Just a regular message with no triple backticks.
            """.strip(),
        ),
        (
            "Multiple code blocks, only extract first",
            """
            Code block one:
            ```python
            def foo():
                return 'foo'
            ```
            Then some text...
            ```python
            def bar():
                return 'bar'
            ```
            """,
            "def foo():\n    return 'foo'",
        ),
        (
            "Unclosed code block",
            """
            Let's see an unclosed code block:
            ```python
            def unclosed():
                return 42
            # missing the ending ```
            Hope we handle it gracefully.
            """,
            # Should extract from the start of ```python to the end of text
            "def unclosed():\n    return 42\n# missing the ending ```\nHope we handle it gracefully."
        ),
        (
            "Code block missing language (should treat as no python block)",
            """
            ``` 
            def subtract(a, b):
                return a - b
            ```
            """,
            # Because there's no "```python", we do not treat this as a Python code block
            """
            ``` 
            def subtract(a, b):
                return a - b
            ```
            """.strip(),
        ),
        (
            "Empty string input",
            "",
            ""  # No code at all
        ),
    ],
)
def test_extract_code_block(description, input_text, expected_output):
    """
    Tests CodeBlockExtractor.extract_code_block() behavior under various conditions:
      1. Single code block
      2. No code block
      3. Multiple code blocks (verify only first is returned)
      4. Unclosed code block
      5. Code block missing language spec
      6. Empty string input
    """
    # Act
    extracted = CodeBlockExtractor.extract_code_block(input_text)

    # Assert
    assert extracted == expected_output.strip(), f"Failed test: {description}"
