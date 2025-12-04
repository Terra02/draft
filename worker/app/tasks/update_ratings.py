import logging
from datetime import datetime
from app.services.imdb_service import IMDbService
from app.services.api_client import api_client

logger = logging.getLogger(__name__)

async def update_ratings_task():
    """Задача обновления рейтингов контента из внешних источников"""
    logger.info("🎯 Starting ratings update task...")

    try:
        # Получаем контент без рейтинга или с устаревшим рейтингом
        content_list = await api_client.get("/api/v1/content/")
        if not content_list:
            logger.info("No content found to update")
            return

        imdb_service = IMDbService()
        updated_count = 0
        error_count = 0

        for content in content_list.get('results', []):
            try:
                # Обновляем только контент с IMDb ID
                imdb_id = content.get('imdb_id')
                if not imdb_id:
                    continue

                # Получаем актуальные данные из IMDb
                imdb_data = await imdb_service.get_content_by_imdb_id(imdb_id)
                if imdb_data and imdb_data.get('imdb_rating'):
                    new_rating = imdb_data['imdb_rating']
                    current_rating = content.get('imdb_rating')
                    
                    # Обновляем только если рейтинг изменился
                    if new_rating != current_rating:
                        update_data = {"imdb_rating": new_rating}
                        success = await api_client.put(
                            f"/api/v1/content/{content['id']}", 
                            data=update_data
                        )
                        if success:
                            updated_count += 1
                            logger.info(f"Updated rating for {content['title']}: {new_rating}")
                        else:
                            error_count += 1
                            logger.warning(f"Failed to update {content['title']}")

            except Exception as e:
                error_count += 1
                logger.error(f"Error updating {content.get('title', 'Unknown')}: {e}")
                continue

        logger.info(f"✅ Ratings update completed. Updated: {updated_count}, Errors: {error_count}")

    except Exception as e:
        logger.error(f"❌ Ratings update task failed: {e}")
        raise