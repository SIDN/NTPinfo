from ipaddress import IPv4Address, IPv6Address

from sqlalchemy import ForeignKey, Integer, SmallInteger, Double, Text, BigInteger, PrimaryKeyConstraint, TypeDecorator, \
    String, Dialect
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.sql.type_api import TypeEngine

from server.app.models.Base import Base
from server.app.models.Time import Time

class IPAddress(TypeDecorator):

    impl = INET

    def load_dialect_impl(self, dialect: Dialect) -> TypeEngine:
        """
            Wraps the INET type into an IPAddress type, which becomes a String for SQLite (test db), which doesn't support INET.
            Args:
                dialect (Dialect): dialect to use (PostgreSQL for prod / dev, SQLite for tests).
            Returns:
                TypeEngine: INET or String, based on dialect type.
            """
        if dialect.name == "sqlite":
            return dialect.type_descriptor(String())
        return dialect.type_descriptor(INET())

class Measurement(Base):
    __tablename__ = "measurements"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    ntp_server_ip: Mapped[str] = mapped_column(IPAddress, nullable=True)
    ntp_server_name: Mapped[str] = mapped_column(Text, nullable=True)
    ntp_version: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    ntp_server_ref_parent: Mapped[str | None] = mapped_column(IPAddress, nullable=True)
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
    vantage_point_ip: Mapped[str] = mapped_column(IPAddress, nullable=True)

    timestamps: Mapped["Time"] = relationship("Time", backref="measurements")
