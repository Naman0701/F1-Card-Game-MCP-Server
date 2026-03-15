from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class Country(Base):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(3), unique=True, nullable=False)

    drivers: Mapped[list["Driver"]] = relationship(
        back_populates="country"
    )  # noqa: F821
    teams: Mapped[list["Team"]] = relationship(back_populates="country")  # noqa: F821
    tracks: Mapped[list["Track"]] = relationship(back_populates="country")  # noqa: F821
