import typer
from typing import Annotated
from app.database import create_db_and_tables, get_session, drop_all
from app.models import User
from fastapi import Depends
from sqlmodel import select
from sqlalchemy.exc import IntegrityError

cli = typer.Typer()

@cli.command(help="Initialize the database by dropping all existing tables and creating new ones. Adds a default user 'bob' to the database.")
def initialize():
    with get_session() as db: # Get a connection to the database
        drop_all() # delete all tables
        create_db_and_tables() #recreate all tables
       # bob = User('bob', 'bob@mail.com', 'bobpass') # Create a new user (in memory)
        bob = User(username='bob', email='bob@mail.com', password='bobpass')
        db.add(bob) # Tell the database about this new data
        db.commit() # Tell the database persist the data
        db.refresh(bob) # Update the user (we use this to get the ID from the db)
        print("Database Initialized")


@cli.command(help="Display a greeting message.")
def main(name: Annotated[str, typer.Argument(help="Name to greet", metavar="✨username✨")] = "World"):
    print(f"Hello {name}")


@cli.command(help="Retrieve a user by username.")
def get_user(username: str = typer.Option(..., help="The username to search for")):
    with get_session() as db: # Get a connection to the database
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found!')
            return
        print(user)
    

@cli.command(help="Display all users in the database.")
def get_all_users():
     with get_session() as db:
        all_users = db.exec(select(User)).all()
        if not all_users:
            print("No users found")
        else:
            for user in all_users:
                print(user)


@cli.command(help="Update a user's email address.")
def change_email(username: str = typer.Option(..., help="The username of the user to update"), new_email: str = typer.Option(..., help="The new email address")):
    with get_session() as db: # Get a connection to the database
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found! Unable to update email.')
            return
        user.email = new_email
        db.add(user)
        db.commit()
        print(f"Updated {user.username}'s email to {user.email}")

@cli.command(help="Create a new user in the database.")
def create_user(username: str = typer.Option(..., help="The username for the new user"), email: str = typer.Option(..., help="The email address for the new user"), password: str = typer.Option(..., help="The password for the new user")):
    with get_session() as db: # Get a connection to the database
        newuser = User(username=username, email=email, password=password)
        try:
            db.add(newuser)
            db.commit()
        except IntegrityError as e:
            db.rollback() #let the database undo any previous steps of a transaction
            #print(e.orig) #optionally print the error raised by the database
            print("Username or email already taken!") #give the user a useful message
        else:
            print(newuser) # print the newly created user

@cli.command(help="Delete a user from the database by username.")
def delete_user(username: str = typer.Option(..., help="The username of the user to delete")):
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found! Unable to delete user.')
            return
        db.delete(user)
        db.commit()
        print(f'{username} deleted')

#exercise 1
# @cli.command()
# def get_partial_user(username:str, email:str, password:str):
# @cli.command()
# def get_partial_user(username: str = None, email: str = None, password: str = None):
#     with get_session() as db: # Get a connection to the database
        # user = db.exec(select(User).where(User.username == username)).first()
        # if not user:
        #     print(f'{username} not found!')
        #     return
        # print(user)
        # if username:
        #     user = db.exec(select(User).where(User.username == username)).first()
        #     if not user:
        #         print(f'{username} not found!')
        #         return
        # if email:
        #     user = db.exec(select(User).where(User.email == email)).first()
        #     if not user:
        #         print(f'{email} not found!')
        #         return
        # if password:
        #     user = db.exec(select(User).where(User.password == password)).first()
        #     if not user:
        #         print(f'User with provided password not found!')
        #         return
        # print(user)    
@cli.command()
def get_partial_user(
    search_by: str = typer.Option(..., prompt="Search by (username/email/password)"),
    value: str = typer.Option(..., prompt="Enter value")
):
    with get_session() as db:
        if search_by.lower() == "username":
            user = db.exec(select(User).where(User.username == value)).first()
        elif search_by.lower() == "email":
            user = db.exec(select(User).where(User.email == value)).first()
        elif search_by.lower() == "password":
            user = db.exec(select(User).where(User.password == value)).first()
        
        if not user:
            print(f"User not found!")
            return
        print(user)

#exercise 2
@cli.command()
def get_user_range(limit: int = 10, offset: int = 0):
    with get_session() as db:
        users = db.exec(select(User).offset(offset).limit(limit)).all()
        if not users:
            print("No users found in the specified range")
        else:
            for user in users:
                print(user)




if __name__ == "__main__":
    cli()