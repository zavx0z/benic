from sqlalchemy import Column, Integer, String, func, DateTime


class BaseModelApp:
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    created_at = Column(DateTime, server_default=func.now())
