from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(
    prefix="/items",
    tags=["Items"]
)

@router.get("/", response_model=List[schemas.ItemResponse])
def read_items(
    skip: int = 0, 
    limit: int = 100, 
    current_user: models.User = Depends(auth.get_current_user), 
    db: Session = Depends(get_db)):
    print(f"[ITEMS] Fetching items for user: {current_user.username}")
    items = db.query(models.Item).filter(models.Item.user_id == current_user.id).offset(skip).limit(limit).all()
    print(f"[ITEMS] Found {len(items)} items for user: {current_user.username}")
    return items

@router.post("/", response_model=schemas.ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(
    item: schemas.ItemCreate, 
    current_user: models.User = Depends(auth.get_current_user), 
    db: Session = Depends(get_db)):
    print(f"[ITEMS] Creating item for user {current_user.username}: {item.name}")
    existing_item = db.query(models.Item).filter(
        models.Item.name == item.name,
        models.Item.user_id == current_user.id
    ).first()
    if existing_item:
        raise HTTPException(status_code=400, detail="Item already exists")
    new_item = models.Item(
        name=item.name,
        description=item.description,
        quantity=item.quantity,
        price=item.price,
        user_id=current_user.id
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    print(f"[ITEMS] Item created successfully - ID: {new_item.id}, Name: {new_item.name}")
    return new_item
@router.get("/name/{item_id}", response_model=schemas.ItemResponse)
def read_item_by_name(
    item_id: str,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    print(f"[ITEMS] Fetching item {item_id} for user {current_user.username}")

    item = db.query(models.Item).filter(
        models.Item.name == item_id,
        models.Item.user_id == current_user.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
@router.put("/name/{item_id}", response_model=schemas.ItemResponse)
def update_item_by_name(
    item_id: str,
    item_update: schemas.ItemUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    print(f"[ITEMS] Updating item {item_id} for user {current_user.username}")

    item = db.query(models.Item).filter(
        models.Item.name == item_id,
        models.Item.user_id == current_user.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    for key, value in item_update.dict(exclude_unset=True).items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    print(f"[ITEMS] Item updated successfully - ID: {item.id}, Name: {item.name}")
    return item

@router.delete("/name/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item_by_name(
    item_id: str,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    print(f"[ITEMS] Deleting item by name for user {current_user.username}: {item_id}")

    item = db.query(models.Item).filter(
        models.Item.name == item_id,
        models.Item.user_id == current_user.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    print(f"[ITEMS] Item deleted successfully - Name: {item.name}")
    return None