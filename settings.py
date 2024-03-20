from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    superkey: str
    jwt_key: str
    jwt_algo: str
    email_sender: str
    email_password: str

settings=Settings()