from sqlalchemy import ForeignKey, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class Track(Base):
    __tablename__ = "tracks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    country_id: Mapped[int] = mapped_column(
        ForeignKey("countries.id", ondelete="CASCADE"), nullable=False
    )
    laps: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    circuit_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    country: Mapped["Country"] = relationship(back_populates="tracks")  # noqa: F821
    driver_tracks: Mapped[list["DriverTrackRel"]] = relationship(
        back_populates="track"
    )  # noqa: F821
