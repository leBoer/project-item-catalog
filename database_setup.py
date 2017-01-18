import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(205))

    @property
    def serialize(self):
        # Return object data in easily serializable format
        return{
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'picture': self.picture,
        }


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        # Return object data in easily serializable format
        return{
            'id': self.id,
            'name': self.name,
            'user': self.user.name,
        }


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(250), nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    created = Column(DateTime, default=datetime.datetime.utcnow)

    @property
    def serialize(self):
        # Return object data in easily serializable format
        return{
            'id': self.id,
            'name': self.name,
            'description:': self.description,
            'category': self.category.name,
            'user': self.user.name,
        }


engine = create_engine('sqlite:///itemcatalog.db', encoding='utf8')

Base.metadata.create_all(engine)
