from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger
from server.app.models.Base import Base


class Time(Base):
    __tablename__ = "times"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    client_sent: Mapped[int] = mapped_column(BigInteger, nullable=True)
    client_sent_prec: Mapped[int] = mapped_column(BigInteger, nullable=True)
    server_recv: Mapped[int] = mapped_column(BigInteger, nullable=True)
    server_recv_prec: Mapped[int] = mapped_column(BigInteger, nullable=True)
    server_sent: Mapped[int] = mapped_column(BigInteger, nullable=True)
    server_sent_prec: Mapped[int] = mapped_column(BigInteger, nullable=True)
    client_recv: Mapped[int] = mapped_column(BigInteger, nullable=True)
    client_recv_prec: Mapped[int] = mapped_column(BigInteger, nullable=True)
