from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Item, User

engine = create_engine('sqlite:///itemcatalog.db', encoding='utf8')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Create categories
category1 = Category(user_id=1, name="RPG")
session.add(category1)
session.commit()

category2 = Category(user_id=1, name="Sports")
session.add(category2)
session.commit()

category3 = Category(user_id=1, name="FPS")
session.add(category3)
session.commit()

# Create items
item1 = Item(user_id=1, name="The Witcher 3",
             description="You play as a legendary witcher",
             category=category1)
session.add(item1)
session.commit()

item2 = Item(user_id=1, name="Final Fantasy XV",
             description="A group of guys on a roadtrip to save the world",
             category=category1)
session.add(item2)
session.commit()

item3 = Item(user_id=1, name="FIFA 16",
             description="A game of soccer, basically the same as every other",
             category=category2)
session.add(item3)
session.commit()

item4 = Item(user_id=1, name="DOOM 3D",
             description="Aliens are on the loose, and you are going to shut them down",
             category=category3)
session.add(item4)
session.commit()

item5 = Item(user_id=1, name="Battlefield 1",
             description="As a soldier, you fight an online battle during WW1 (I think)",
             category=category1)
session.add(item5)
session.commit()

print "Added users, categories, and items!"