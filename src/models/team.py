from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    country_id: Mapped[int] = mapped_column(
        ForeignKey("countries.id", ondelete="CASCADE"), nullable=False
    )
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    country: Mapped["Country"] = relationship(back_populates="teams")  # noqa: F821
    team_drivers: Mapped[list["TeamDriverRel"]] = relationship(
        back_populates="team"
    )  # noqa: F821
