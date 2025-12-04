from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List
import logging

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate

logger = logging.getLogger(__name__)

class CategoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_category_by_id(self, category_id: int) -> Optional[Category]:
        """Получить категорию по ID"""
        result = await self.db.execute(
            select(Category).where(Category.id == category_id)
        )
        return result.scalar_one_or_none()

    async def get_category_by_name(self, name: str) -> Optional[Category]:
        """Получить категорию по имени"""
        result = await self.db.execute(
            select(Category).where(Category.name == name)
        )
        return result.scalar_one_or_none()

    async def create_category(self, category_data: CategoryCreate) -> Category:
        """Создать новую категорию"""
        # Проверяем, существует ли категория с таким именем
        existing_category = await self.get_category_by_name(category_data.name)
        if existing_category:
            return existing_category

        category = Category(**category_data.model_dump())
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        logger.info(f"Created new category: {category.name}")
        return category

    async def update_category(self, category_id: int, category_data: CategoryUpdate) -> Optional[Category]:
        """Обновить категорию"""
        category = await self.get_category_by_id(category_id)
        if not category:
            return None

        update_data = category_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)

        await self.db.commit()
        await self.db.refresh(category)
        logger.info(f"Updated category: {category.name}")
        return category

    async def delete_category(self, category_id: int) -> bool:
        """Удалить категорию"""
        category = await self.get_category_by_id(category_id)
        if not category:
            return False

        await self.db.delete(category)
        await self.db.commit()
        logger.info(f"Deleted category: {category.name}")
        return True

    async def get_all_categories(self) -> List[Category]:
        """Получить все категории"""
        result = await self.db.execute(
            select(Category).order_by(Category.name)
        )
        return result.scalars().all()

    async def get_categories_with_stats(self) -> List[dict]:
        """Получить категории со статистикой количества контента"""
        from app.models.content import Content
        
        stmt = select(
            Category,
            func.count(Content.id).label('content_count')
        ).outerjoin(Content, Category.id == Content.category_id).group_by(Category.id)
        
        result = await self.db.execute(stmt)
        categories_with_stats = []
        for category, content_count in result:
            category_dict = {
                **category.__dict__,
                "content_count": content_count
            }
            categories_with_stats.append(category_dict)
        
        return categories_with_stats