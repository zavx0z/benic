from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship


class BaseModelTask:
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True, nullable=False)
    description = Column(String)
    creation_date = Column(DateTime, server_default=func.now())