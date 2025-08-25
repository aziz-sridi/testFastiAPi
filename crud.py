from sqlalchemy.orm import Session

from schemas import User




def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(User)
        .order_by(User.id)    
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_user(db: Session,name:str,email:str):
    newuser=User(name=name,email=email)
    db.add(newuser)
    db.commit()
    db.refresh(newuser)
    return newuser
def update_user(db: Session, user_id: int,name:str=None,email:str=None):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    if name:
        db_user.name=name
    if email:
        db_user.email=email
    db.commit()
    db.refresh(db_user)
   
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = get_user_by_id(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user
