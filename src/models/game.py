from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    ai_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), default="in_progress", server_default="in_progress"
    )
    user_score: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    ai_score: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    current_round: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user: Mapped["User"] = relationship(foreign_keys=[user_id])  # noqa: F821
    ai_user: Mapped["User"] = relationship(foreign_keys=[ai_user_id])  # noqa: F821
    rounds: Mapped[list["GameRound"]] = relationship(
        back_populates="game", order_by="GameRound.round_number"
    )
    hands: Mapped[list["GamePlayerHand"]] = relationship(back_populates="game")


class GameRound(Base):
    __tablename__ = "game_rounds"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    game_id: Mapped[int] = mapped_column(
        ForeignKey("games.id", ondelete="CASCADE"), nullable=False
    )
    round_number: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    track_id: Mapped[int] = mapped_column(
        ForeignKey("tracks.id", ondelete="CASCADE"), nullable=False
    )
    user_driver_id: Mapped[int | None] = mapped_column(
        ForeignKey("drivers.id", ondelete="CASCADE"), nullable=True
    )
    ai_driver_id: Mapped[int | None] = mapped_column(
        ForeignKey("drivers.id", ondelete="CASCADE"), nullable=True
    )
    user_power: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_power: Mapped[float | None] = mapped_column(Float, nullable=True)
    winner: Mapped[str | None] = mapped_column(String(10), nullable=True)

    game: Mapped["Game"] = relationship(back_populates="rounds")
    track: Mapped["Track"] = relationship()  # noqa: F821
    user_driver: Mapped["Driver | None"] = relationship(
        foreign_keys=[user_driver_id]
    )  # noqa: F821
    ai_driver: Mapped["Driver | None"] = relationship(
        foreign_keys=[ai_driver_id]
    )  # noqa: F821


class GamePlayerHand(Base):
    __tablename__ = "game_player_hands"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    game_id: Mapped[int] = mapped_column(
        ForeignKey("games.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    driver_id: Mapped[int] = mapped_column(
        ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False
    )
    is_played: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )

    game: Mapped["Game"] = relationship(back_populates="hands")
    user: Mapped["User"] = relationship()  # noqa: F821
    driver: Mapped["Driver"] = relationship()  # noqa: F821
