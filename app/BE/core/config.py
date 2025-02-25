from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    #DB_USERNAME: str
    #DB_HOST: str
    #DB_PASSWORD: str
    #DB_PORT: str
    MONGODB_URI:str = "mongodb://junchan:1234@3.34.178.2:27017/"
    #@property
    #def MONGODB_URI(self) -> str:
    #    if self.DB_USERNAME and self.DB_PASSWORD and self.DB_HOST and self.DB_PORT:
    #        URI = f"mongodb://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/"
    #    else:
    #        URI = "mongodb://junchan:1234@3.34.178.2:27017/"
    #    return URI

    class Config:
        env_file = ".env"  # 로컬 개발시 .env 파일을 사용하려면


settings = Settings()
print(settings.MONGODB_URI)