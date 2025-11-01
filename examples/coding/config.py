"""Configuration module for Azure OpenAI setup."""

import os
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


def load_env_file(env_path: Optional[str] = None) -> None:
    """Load environment variables from .env file.
    
    Args:
        env_path: Path to .env file. If None, looks for .env in project root.
    """
    if load_dotenv is None:
        # python-dotenv not installed, skip loading .env file
        return
    
    if env_path is None:
        # Look for .env file in project root (go up from examples/coding/)
        project_root = Path(__file__).parent.parent.parent
        env_path = project_root / ".env"
    else:
        env_path = Path(env_path)
    
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)


def setup_azure_openai(
    api_key: Optional[str] = None,
    endpoint: Optional[str] = None,
    api_version: Optional[str] = None,
    load_env: bool = True,
) -> None:
    """Setup Azure OpenAI environment variables.
    
    LangChain's init_chat_model supports Azure OpenAI when these environment variables are set.
    The model identifier should be in format "azure_openai/{deployment_name}".
    
    Args:
        api_key: Azure OpenAI API key. If not provided, reads from environment variable AZURE_OPENAI_API_KEY.
        endpoint: Azure OpenAI endpoint URL. If not provided, reads from environment variable AZURE_OPENAI_ENDPOINT.
        api_version: Azure OpenAI API version. Defaults to "2024-02-15-preview" if not provided.
        load_env: Whether to load .env file first. Defaults to True.
    """
    # Load .env file if requested and available
    if load_env:
        load_env_file()
    # Set API key
    if api_key:
        os.environ["AZURE_OPENAI_API_KEY"] = api_key
    elif "AZURE_OPENAI_API_KEY" not in os.environ:
        raise ValueError(
            "Azure OpenAI API key not found. Please set AZURE_OPENAI_API_KEY environment variable or pass api_key parameter."
        )
    
    # Set endpoint
    if endpoint:
        os.environ["AZURE_OPENAI_ENDPOINT"] = endpoint
    elif "AZURE_OPENAI_ENDPOINT" not in os.environ:
        raise ValueError(
            "Azure OpenAI endpoint not found. Please set AZURE_OPENAI_ENDPOINT environment variable or pass endpoint parameter."
        )
    
    # Set API version (with default)
    # LangChain expects OPENAI_API_VERSION for Azure OpenAI
    if api_version:
        os.environ["AZURE_OPENAI_API_VERSION"] = api_version
        os.environ["OPENAI_API_VERSION"] = api_version
    elif "AZURE_OPENAI_API_VERSION" in os.environ:
        # If AZURE_OPENAI_API_VERSION is set, also set OPENAI_API_VERSION
        os.environ["OPENAI_API_VERSION"] = os.environ["AZURE_OPENAI_API_VERSION"]
    elif "OPENAI_API_VERSION" not in os.environ:
        default_version = "2024-02-15-preview"
        os.environ["AZURE_OPENAI_API_VERSION"] = default_version
        os.environ["OPENAI_API_VERSION"] = default_version


def get_azure_model_name(deployment_name: str = "gpt-4o-mini") -> str:
    """Get Azure OpenAI deployment name for init_chat_model.
    
    Args:
        deployment_name: The Azure deployment name. Defaults to "gpt-4o-mini".
        
    Returns:
        str: The deployment name (used directly with model_provider="azure").
    """
    return deployment_name

