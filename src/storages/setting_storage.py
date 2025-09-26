from pathlib import Path

from pydantic.functional_validators import field_validator
from pydantic_settings import (
    BaseSettings,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    api_id: int
    api_hash: str
    sessions_dir: str = "sessions"

    @field_validator("api_id")
    def validate_api_id(cls, v: int) -> int:
        if v < 1:
            raise ValueError("API ID must be a positive number")
        return v

    @field_validator("api_hash")
    def validate_api_hash(cls, v: str) -> str:
        if not v:
            raise ValueError("API Hash cannot be empty")
        return v

    @field_validator("sessions_dir")
    def validate_sessions_dir(cls, v: str) -> str:
        path = Path(v)
        path.mkdir(exist_ok=True, parents=True)

        return str(path)

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
        json_file="storage/settings.json",
        json_file_encoding="utf-8",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ):
        return (
            init_settings,
            env_settings,
            JsonConfigSettingsSource(settings_cls),
            dotenv_settings,
            file_secret_settings,
        )


settings = Settings()
