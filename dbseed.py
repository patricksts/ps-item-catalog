from dbsetup import Place, Base, Thing, User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///places.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# USERS
User1 = User(name="Patrick Salazar", email="marcpsalazar@gmail.com")
session.add(User1)
session.commit()
print("User created: " + User1.name)

# PLACES
place1 = Place(user_id=1, name="My Closet")
session.add(place1)
session.commit()

place2 = Place(user_id=1, name="The Everything Drawer")
session.add(place2)
session.commit()


# THINGS
thing1 = Thing(
    user_id=1, name="Old Sock", description="smelly",
    category="Junk", place=place1)
session.add(thing1)
session.commit()

thing2 = Thing(
    user_id=1, name="Star Wars Poster", description="1977 Original",
    category="Heirloom", place=place1)
session.add(thing2)
session.commit()

thing3 = Thing(
    user_id=1, name="Gym Bag", description="full of cash",
    category="Other", place=place1)
session.add(thing3)
session.commit()

thing4 = Thing(
    user_id=1, name="Screwdriver", description="phillips",
    category="Tool", place=place1)
session.add(thing4)
session.commit()

thing5 = Thing(
    user_id=1, name="Pencil", description="No.2",
    category="Tool", place=place2)
session.add(thing5)
session.commit()

thing6 = Thing(
    user_id=1, name="hacky sack", description="really?",
    category="Other", place=place2)
session.add(thing6)
session.commit()

thing7 = Thing(
    user_id=1, name="broken tv", description="i'll fix it someday",
    category="Junk", place=place2)
session.add(thing7)
session.commit()

thing8 = Thing(
    user_id=1, name="taxidermy dog", description="uncle Sam's pet (formerly)",
    category="Heirloom", place=place2)
session.add(thing8)
session.commit()

places = session.query(Place).all()
for place in places:
    print("Added: " + place.name)
