import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from database import get_db, Product
from models import ProductCreate, ProductUpdate, ProductResponse
from kafka_producer import kafka_producer
from shared.schemas.events import ProductCreatedEvent, InventoryUpdatedEvent

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    """Create a new product."""
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    # Publish product created event
    event = ProductCreatedEvent(
        product_id=db_product.id,
        name=db_product.name,
        price=db_product.price,
        stock=db_product.stock,
        created_at=datetime.utcnow()
    )
    kafka_producer.publish("product.created", event.dict(), key=str(db_product.id))

    logger.info(f"Product created: {db_product.id}")
    return db_product


@router.get("/", response_model=List[ProductResponse])
async def list_products(
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    db: Session = Depends(get_db)
):
    """List all products with optional filtering."""
    query = db.query(Product).filter(Product.is_active == True)
    
    if category:
        query = query.filter(Product.category == category)
    
    products = query.offset(skip).limit(limit).all()
    return products


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get a product by ID."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db)
):
    """Update a product."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    update_data = product_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    product.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(product)

    # Publish inventory update if stock changed
    if "stock" in update_data:
        event = InventoryUpdatedEvent(
            product_id=product.id,
            quantity_change=update_data["stock"] - product.stock,
            new_stock=product.stock,
            updated_at=datetime.utcnow()
        )
        kafka_producer.publish("inventory.updated", event.dict(), key=str(product.id))

    logger.info(f"Product updated: {product_id}")
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Delete (deactivate) a product."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    product.is_active = False
    product.updated_at = datetime.utcnow()
    db.commit()
    
    logger.info(f"Product deleted: {product_id}")
    return None

