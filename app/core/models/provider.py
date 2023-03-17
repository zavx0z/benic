from sqlalchemy import Column, Integer, String

from shared import Base


class Provider(Base):
    __tablename__ = "provider"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), index=True, nullable=False)
    description = Column(String)
