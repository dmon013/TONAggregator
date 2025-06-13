# backend/models/app.py
# from typing import Optional, List
# from pydantic import BaseModel, HttpUrl

# class App(BaseModel):
#     id: Optional[str] = None
#     name: str
#     description: str
#     developer_name: str
#     icon_url: HttpUrl
#     tma_url: HttpUrl
#     category_id: str
#     tags: Optional[List[str]] =
#     avg_rating: Optional[float] = 0.0
#     review_count: Optional[int] = 0

# class Category(BaseModel):
#     id: Optional[str] = None
#     name: str
#     description: Optional[str] = None

# class Review(BaseModel):
#     id: Optional[str] = None
#     app_id: str
#     user_id: str # Telegram user ID
#     user_name: str # Telegram user first_name or username
#     rating: int # 1-5
#     comment: Optional[str] = None
#     created_at: Optional[str] = None # Хранить как ISO строку или Firestore Timestamp