from abc import ABC as AbstractClass
from acrobot.utils.secrets_manager import SecretsManager


class DefaultSettings(AbstractClass):
    def __init__(self):
        self.ENV_LOADED = True
        self.SLACK_BOT_TOKEN = ""
        self.SLACK_VERIFICATION_TOKEN = ""
        self.SLACK_SIGNING_SECRET = ""
        DB_PASSWORD = ""
        DB_USER = "postgres"
        DB_NAME = "acrobot"
        DB_HOST = "localhost"
        self.SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False

    def get_secrets(self, secret_name, aws_region):
        return SecretsManager().get_secret(secret_name, aws_region)
