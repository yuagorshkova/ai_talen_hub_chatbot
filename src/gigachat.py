import os

from langchain_gigachat import GigaChat
from typing_extensions import TypedDict


class GigaChatConfig(TypedDict):
    model: str
    profanity_check: bool
    base_url: str
    timeout: int


class GigaChatAuth(TypedDict):
    user: str
    password: str
    verify_ssl_certs: bool


gigachat_config: GigaChatConfig = {
    "model": os.getenv("MODEL", "GigaChat-2-Max"),
    "profanity_check": os.getenv("PROFANITY_CHECK", "false").lower() == "true",
    "base_url": os.getenv("GIGACHAT_BASE_URL", "https://gigachat.sberdevices.ru/v1"),
    "timeout": int(os.getenv("GIGACHAT_TIMEOUT", "30")),
}

gigachat_auth: GigaChatAuth = {
    "user": os.getenv("GIGACHAT_USER", "required"),
    "password": os.getenv("GIGACHAT_PASSWORD", "required"),
    "verify_ssl_certs": False,
}


def get_gigachat() -> GigaChat:
    llm = GigaChat(
        verbose=os.getenv("GIGACHAT_VERBOSE", "false").lower() == "true",
        **gigachat_config,
        **gigachat_auth,
    )
    return llm


gigachat = get_gigachat()
