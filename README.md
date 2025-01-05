# DynamicFunctioneer
Auto-generate and improve Python methods with decorators powered by LLMs.

## Prerequisites

A version of Python 3.8 or higher is required.

Before proceeding, install uv to manage the virtual environment and dependencies:

For macOS and Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

For Windows:

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

After installing, ensure uv is accessible by verifying the version:

```bash
uv --version
```

If `uv` is not recognized, ensure the installation path (e.g., `~/.local/bin` on macOS/Linux or `%USERPROFILE%\.local\bin` on Windows) is added to your system's PATH environment variable.


## Installation

Clone the repository:

```bash
git clone https://github.com/eramireztorres/DynamicFunctioneer.git
```

Navigate to the directory:

```bash
cd DynamicFunctioneer
```

### Create virtual environment

You can create and manage the environment using `uv`:

```bash
uv venv
```

After creating the environment, activate it:

- **Linux/Mac**: `source .venv/bin/activate`
- **Windows**: `.venv\Scripts\activate`

Make sure to activate this environment whenever working with Gpt4CLI.

### Install the package:

```bash
uv sync
uv run python setup.py install
```

For development purposes, you can use editable mode, so replace the latest with:

```bash
uv sync
uv run python setup.py develop
```
