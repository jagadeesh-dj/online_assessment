from server import db
from sqlalchemy import Integer, Column, VARCHAR, DATE, BIGINT



class Tracker(db.Model):
    __tablename__ = "user_steps"

    id = Column(Integer,autoincrement=True)
    username = Column(VARCHAR(255), nullable=False, unique=True)
    date = Column(Date, nullable=False)
    steps = Column(BIGINT(), nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self.id

