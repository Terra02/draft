import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import httpx
import asyncio
from typing import Dict, List, Optional
import json

# Настройка страницы
st.set_page_config(
    page_title="Movie Tracker Analytics",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Стили CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    .section-header {
        color: #1f77b4;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

class AnalyticsApp:
    def __init__(self):
        self.api_url = st.secrets.get("API_URL", "http://localhost:8000")
        self.client = httpx.AsyncClient(base_url=self.api_url, timeout=30.0)

    async def get_data(self, endpoint: str) -> Optional[Dict]:
        """Получить данные из API"""
        try:
            response = await self.client.get(endpoint)
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Ошибка API: {response.status_code}")
                return None
        except Exception as e:
            st.error(f"Ошибка подключения: {e}")
            return None

    async def get_system_overview(self) -> Optional[Dict]:
        """Получить обзор системы"""
        return await self.get_data("/api/v1/analytics/system/overview")

    async def get_content_stats(self) -> Optional[Dict]:
        """Получить статистику контента"""
        return await self.get_data("/api/v1/analytics/content/stats")

    async def get_users(self) -> List[Dict]:
        """Получить список пользователей"""
        data = await self.get_data("/api/v1/users/")
        return data if data else []

    async def get_user_analytics(self, user_id: int) -> Optional[Dict]:
        """Получить аналитику пользователя"""
        return await self.get_data(f"/api/v1/analytics/user/{user_id}?days=365")

async def main():
    app = AnalyticsApp()
    
    # Заголовок приложения
    st.markdown('<h1 class="main-header">🎬 Movie Tracker Analytics</h1>', unsafe_allow_html=True)
    
    # Сайдбар с навигацией
    st.sidebar.title("📊 Навигация")
    page = st.sidebar.radio(
        "Выберите раздел:",
        ["📈 Обзор системы", "👥 Пользователи", "🎬 Контент", "📊 Детальная аналитика"]
    )
    
    if page == "📈 Обзор системы":
        await show_system_overview(app)
    elif page == "👥 Пользователи":
        await show_users_analytics(app)
    elif page == "🎬 Контент":
        await show_content_analytics(app)
    elif page == "📊 Детальная аналитика":
        await show_detailed_analytics(app)

async def show_system_overview(app: AnalyticsApp):
    """Показать обзор системы"""
    st.markdown('<h2 class="section-header">📈 Обзор системы</h2>', unsafe_allow_html=True)
    
    with st.spinner("Загрузка данных..."):
        overview_data = await app.get_system_overview()
    
    if not overview_data:
        st.error("Не удалось загрузить данные системы")
        return
    
    # Ключевые метрики
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="👥 Всего пользователей",
            value=overview_data.get('total_users', 0),
            delta=None
        )
    
    with col2:
        st.metric(
            label="🔥 Активных пользователей",
            value=overview_data.get('active_users', 0),
            delta=None
        )
    
    with col3:
        st.metric(
            label="🎬 Всего контента",
            value=overview_data.get('total_content', 0),
            delta=None
        )
    
    with col4:
        st.metric(
            label="📊 Всего просмотров",
            value=overview_data.get('total_views', 0),
            delta=None
        )
    
    # Графики
    col1, col2 = st.columns(2)
    
    with col1:
        # Распределение по типам контента
        content_types = overview_data.get('content_types', {})
        if content_types:
            fig = px.pie(
                values=list(content_types.values()),
                names=list(content_types.keys()),
                title="📁 Распределение по типам контента",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Активность пользователей
        user_activity = overview_data.get('user_activity', {})
        if user_activity:
            dates = list(user_activity.keys())
            views = list(user_activity.values())
            
            fig = px.line(
                x=dates, y=views,
                title="📈 Активность просмотров (последние 7 дней)",
                labels={'x': 'Дата', 'y': 'Количество просмотров'}
            )
            fig.update_traces(line=dict(color='#1f77b4', width=3))
            st.plotly_chart(fig, use_container_width=True)

async def show_users_analytics(app: AnalyticsApp):
    """Показать аналитику пользователей"""
    st.markdown('<h2 class="section-header">👥 Аналитика пользователей</h2>', unsafe_allow_html=True)
    
    with st.spinner("Загрузка данных пользователей..."):
        users = await app.get_users()
    
    if not users:
        st.error("Не удалось загрузить данные пользователей")
        return
    
    # Таблица пользователей
    st.subheader("Список пользователей")
    users_df = pd.DataFrame(users)
    
    # Преобразование дат
    if 'created_at' in users_df.columns:
        users_df['created_at'] = pd.to_datetime(users_df['created_at'])
        users_df['Дата регистрации'] = users_df['created_at'].dt.strftime('%Y-%m-%d %H:%M')
    
    # Отображаем только нужные колонки
    display_columns = ['id', 'username', 'first_name', 'last_name', 'Дата регистрации']
    available_columns = [col for col in display_columns if col in users_df.columns]
    
    st.dataframe(
        users_df[available_columns],
        use_container_width=True,
        hide_index=True
    )
    
    # График регистраций
    st.subheader("📊 Регистрации пользователей")
    
    if 'created_at' in users_df.columns:
        users_df['date'] = users_df['created_at'].dt.date
        reg_counts = users_df.groupby('date').size().reset_index(name='count')
        
        fig = px.line(
            reg_counts,
            x='date',
            y='count',
            title='Динамика регистраций пользователей',
            labels={'date': 'Дата', 'count': 'Количество регистраций'}
        )
        fig.update_traces(line=dict(color='#ff7f0e', width=3))
        st.plotly_chart(fig, use_container_width=True)

async def show_content_analytics(app: AnalyticsApp):
    """Показать аналитику контента"""
    st.markdown('<h2 class="section-header">🎬 Аналитика контента</h2>', unsafe_allow_html=True)
    
    with st.spinner("Загрузка статистики контента..."):
        content_stats = await app.get_content_stats()
    
    if not content_stats:
        st.error("Не удалось загрузить статистику контента")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎭 Самые просматриваемые фильмы")
        top_movies = content_stats.get('most_watched_movies', [])
        if top_movies:
            movies_df = pd.DataFrame(top_movies)
            if not movies_df.empty:
                fig = px.bar(
                    movies_df.head(10),
                    x='view_count',
                    y='title',
                    orientation='h',
                    title='Топ 10 фильмов по просмотрам',
                    color='view_count',
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Нет данных о фильмах")
        else:
            st.info("Нет данных о фильмах")
    
    with col2:
        st.subheader("📺 Самые просматриваемые сериалы")
        top_series = content_stats.get('most_watched_series', [])
        if top_series:
            series_df = pd.DataFrame(top_series)
            if not series_df.empty:
                fig = px.bar(
                    series_df.head(10),
                    x='view_count',
                    y='title',
                    orientation='h',
                    title='Топ 10 сериалов по просмотрам',
                    color='view_count',
                    color_continuous_scale='Plasma'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Нет данных о сериалах")
        else:
            st.info("Нет данных о сериалах")
    
    # Контент с наивысшим рейтингом
    st.subheader("⭐ Контент с наивысшим рейтингом")
    top_rated = content_stats.get('highest_rated_content', [])
    if top_rated:
        rated_df = pd.DataFrame(top_rated)
        if not rated_df.empty:
            fig = px.bar(
                rated_df.head(15),
                x='average_rating',
                y='title',
                orientation='h',
                title='Топ 15 контента по рейтингу',
                color='average_rating',
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Нет данных о рейтингах")
    else:
        st.info("Нет данных о рейтингах")

async def show_detailed_analytics(app: AnalyticsApp):
    """Показать детальную аналитику"""
    st.markdown('<h2 class="section-header">📊 Детальная аналитика</h2>', unsafe_allow_html=True)
    
    st.info("""
    В этом разделе представлена расширенная аналитика системы.
    Используйте фильтры ниже для настройки отображаемых данных.
    """)
    
    # Фильтры
    col1, col2, col3 = st.columns(3)
    
    with col1:
        date_range = st.selectbox(
            "Период анализа:",
            ["Последние 30 дней", "Последние 90 дней", "Последний год", "Все время"]
        )
    
    with col2:
        content_type = st.selectbox(
            "Тип контента:",
            ["Все", "Фильмы", "Сериалы"]
        )
    
    with col3:
        metric_type = st.selectbox(
            "Метрика:",
            ["Просмотры", "Рейтинги", "Активность"]
        )
    
    # Заглушка для расширенной аналитики
    st.warning("🚧 Раздел детальной аналитики находится в разработке")
    
    # Пример дополнительных графиков
    st.subheader("📈 Пример аналитики")
    
    # Создаем пример данных для демонстрации
    sample_dates = pd.date_range(start='2024-01-01', end='2024-12-01', freq='M')
    sample_views = [100, 150, 200, 180, 220, 250, 300, 280, 320, 350, 400, 380]
    sample_ratings = [7.8, 8.1, 7.9, 8.3, 8.0, 8.2, 8.1, 8.4, 8.3, 8.5, 8.4, 8.6]
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.line(
            x=sample_dates,
            y=sample_views,
            title="📊 Динамика просмотров (пример)",
            labels={'x': 'Месяц', 'y': 'Количество просмотров'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.line(
            x=sample_dates,
            y=sample_ratings,
            title="⭐ Динамика среднего рейтинга (пример)",
            labels={'x': 'Месяц', 'y': 'Средний рейтинг'}
        )
        st.plotly_chart(fig, use_container_width=True)

# Запуск приложения
if __name__ == "__main__":
    asyncio.run(main())