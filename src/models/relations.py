from sqlalchemy import (
    CheckConstraint,
    Float,
    ForeignKey,
    SmallInteger,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class TeamDriverRel(Base):
    __tablename__ = "team_driver_rel"
    __table_args__ = (
        UniqueConstraint(
            "team_id", "driver_id", "season_year", name="uq_team_driver_season"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
    )
    driver_id: Mapped[int] = mapped_column(
        ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False
    )
    season_year: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    team: Mapped["Team"] = relationship(back_populates="team_drivers")  # noqa: F821
    driver: Mapped["Driver"] = relationship(back_populates="team_drivers")  # noqa: F821


class DriverSkillRel(Base):
    __tablename__ = "driver_skill_rel"
    __table_args__ = (
        UniqueConstraint("driver_id", "skill_id", name="uq_driver_skill"),
        CheckConstraint("value >= 0 AND value <= 100", name="ck_skill_value_range"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    driver_id: Mapped[int] = mapped_column(
        ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False
    )
    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id", ondelete="CASCADE"), nullable=False
    )
    value: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    driver: Mapped["Driver"] = relationship(
        back_populates="driver_skills"
    )  # noqa: F821
    skill: Mapped["Skill"] = relationship(back_populates="driver_skills")  # noqa: F821


class DriverTrackRel(Base):
    __tablename__ = "driver_track_rel"
    __table_args__ = (
        UniqueConstraint("driver_id", "track_id", name="uq_driver_track"),
        CheckConstraint(
            "multiplier >= 0.5 AND multiplier <= 2.0", name="ck_multiplier_range"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    driver_id: Mapped[int] = mapped_column(
        ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False
    )
    track_id: Mapped[int] = mapped_column(
        ForeignKey("tracks.id", ondelete="CASCADE"), nullable=False
    )
    multiplier: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

    driver: Mapped["Driver"] = relationship(
        back_populates="driver_tracks"
    )  # noqa: F821
    track: Mapped["Track"] = relationship(back_populates="driver_tracks")  # noqa: F821
