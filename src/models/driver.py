from sqlalchemy import ForeignKey, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class Driver(Base):
    __tablename__ = "drivers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    number: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    country_id: Mapped[int] = mapped_column(
        ForeignKey("countries.id", ondelete="CASCADE"), nullable=False
    )
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    country: Mapped["Country"] = relationship(back_populates="drivers")  # noqa: F821
    team_drivers: Mapped[list["TeamDriverRel"]] = relationship(
        back_populates="driver"
    )  # noqa: F821
    driver_skills: Mapped[list["DriverSkillRel"]] = relationship(
        back_populates="driver"
    )  # noqa: F821
    driver_tracks: Mapped[list["DriverTrackRel"]] = relationship(
        back_populates="driver"
    )  # noqa: F821
