from core.models.app import BaseModelApp
from shared import Base


class AppResource(Base, BaseModelApp):
    __tablename__ = "app_resource"
