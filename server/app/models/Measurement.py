from ipaddress import IPv4Address, IPv6Address

from sqlalchemy import ForeignKey, Integer, SmallInteger, Double, Text, BigInteger, PrimaryKeyConstraint
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.dialects.postgresql import INET
from server.app.models.Base import Base
from server.app.models.Time import Time


class Measurement(Base):
    __tablename__ = "measurements"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    ntp_server_ip: Mapped[str] = mapped_column(INET, nullable=True)
    ntp_server_name: Mapped[str] = mapped_column(Text, nullable=True)
    ntp_version: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    ntp_server_ref_parent: Mapped[str | None] = mapped_column(INET, nullable=True)
    ref_name: Mapped[str] = mapped_column(Text, nullable=True)

    time_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("times.id"), nullable=True)
    time_offset: Mapped[float] = mapped_column(Double, nullable=True)

    rtt: Mapped[float] = mapped_column(Double, nullable=True)
    stratum: Mapped[int] = mapped_column(Integer, nullable=True)
    precision: Mapped[float] = mapped_column(Double, nullable=True)
    reachability: Mapped[str] = mapped_column(Text, nullable=True)
    root_delay: Mapped[int] = mapped_column(BigInteger, nullable=True)
    ntp_last_sync_time: Mapped[int] = mapped_column(BigInteger, nullable=True)
    root_delay_prec: Mapped[int] = mapped_column(BigInteger, nullable=True)
    ntp_last_sync_time_prec: Mapped[int] = mapped_column(BigInteger, nullable=True)
    vantage_point_ip: Mapped[str] = mapped_column(INET, nullable=True)

    timestamps: Mapped["Time"] = relationship("Time", backref="measurements")
