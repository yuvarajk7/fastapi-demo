from fastapi import APIRouter, Depends,Query,status,Path
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.crud.product import product_repository
from app.schemas.product import ProductCreate,ProductResponse
from app.core.responses import not_found
from typing import Optional,List
from app.dependencies.auth import get_authenticated_user

router = APIRouter(
    prefix="/products",
    tags=["Products"],
    dependencies=[Depends(get_authenticated_user())]
)

@router.get(
    "/", 
    response_model=List[ProductResponse],
    summary="List all products",
    description="Retrieve a paginated list of products with optional search filtering."
)
def list_products(
    search: Optional[str] = Query(None, description="Search term for filtering products"),
    skip: int = Query(0, ge=0, description="Number of rows to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to retreive"),
    db: Session = Depends(get_db)
):
    """
    Retrieve products with optional search and pagination
    """

    if search:
        return product_repository.search(db, search, skip=skip, limit=limit)
    else:
        return product_repository.get_all(db, skip=skip, limit=limit)

@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Get product by ID",
    description="Retrieve detailed information about a specific product by its ID.",
    responses={
        status.HTTP_200_OK: {
            "description": "Product found successfully",
            "model": ProductResponse
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Product not found",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Product not found",
                        "details": {
                            "resource_type": "Product",
                            "resource_id": "123"
                        }
                    }
                }
            }
        }
    }
)
def get_product(
    product_id: int = Path(..., description="The unique ID of the product to retrieve"),
    db: Session = Depends(get_db)):
    """
    Retrieve a product by ID 
    """
    product = product_repository.get(db, product_id)
    if not product:
       not_found("Product", product_id)
    return product

@router.post("/")
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """
    Create a new product
    """
    return product_repository.create(
        db, 
        name=product.name,
        description=product.description,
        sku=product.sku,
        price=product.price
    )

