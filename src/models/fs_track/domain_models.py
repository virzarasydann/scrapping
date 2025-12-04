from dataclasses import dataclass


@dataclass
class LoginCredentials:
    username: str
    password: str


@dataclass
class JobCreationResult:
    success: bool
    status_code: int
    message: str = ""
