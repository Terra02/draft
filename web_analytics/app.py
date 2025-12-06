import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime, timedelta

# --- Конфигурация страницы ---
st.set_page_config(
    page_title="Movie Tracker Аналитика",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Моковые данные (ЗАМЕНИТЕ НА РЕАЛЬНЫЕ ДАННЫЕ ИЗ БЭКЕНДА) ---

# Генерация данных за последний год
N_RECORDS = 150
start_date = datetime.now() - timedelta(days=365)

data = {
    'title': [f'Фильм {i+1}' for i in range(N_RECORDS)],
    'content_type': np.random.choice(['Фильм', 'Сериал (Эпизод)'], N_RECORDS, p=[0.7, 0.3]),
    'user_rating': np.random.randint(5, 11, N_RECORDS), # Рейтинг от 5 до 10
    'duration_minutes': np.random.randint(60, 150, N_RECORDS),
    'watch_date': [start_date + timedelta(days=np.random.randint(0, 365)) for _ in range(N_RECORDS)],
}

df = pd.DataFrame(data)
df['watch_month'] = df['watch_date'].dt.to_period('M').astype(str)

# Расчет ключевых метрик
total_items = len(df)
total_movies = df[df['content_type'] == 'Фильм'].shape[0]
total_series_episodes = df[df['content_type'] == 'Сериал (Эпизод)'].shape[0]

# Общее время просмотра
total_time_minutes = df['duration_minutes'].sum()
total_time_hours = round(total_time_minutes / 60, 1)
total_time_days = round(total_time_hours / 24, 1)

# Средний рейтинг
avg_rating = round(df['user_rating'].mean(), 2)

# --- Заголовок и фильтры ---

st.title("🎬 Аналитика Просмотров")
st.markdown("Здесь вы найдете все ключевые метрики и статистику по просмотренным фильмам и сериалам.")

# Временной фильтр (для примера, пока не используется в графиках)
time_range = st.sidebar.select_slider(
    'Выберите диапазон данных для анализа:',
    options=['Последние 7 дней', 'Последние 30 дней', 'Последние 6 месяцев', 'Последний год', 'Все время'],
    value='Последний год'
)
st.sidebar.markdown(f"**Текущий диапазон:** *{time_range}*")
st.sidebar.divider()

# --- KPI (Ключевые показатели эффективности) ---

st.header("📊 Ключевые Метрики")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Всего Просмотров", value=total_items)
with col2:
    st.metric(label="Общее Время Просмотра (часы)", value=f"{total_time_hours:,}")
with col3:
    st.metric(label="Средний Рейтинг", value=avg_rating)
with col4:
    st.metric(label="Всего Фильмов", value=total_movies)
    st.metric(label="Всего Эпизодов Сериалов", value=total_series_episodes)

st.divider()

# --- Графики Аналитики ---

st.header("📈 Визуализация Данных")

# 1. График: Количество просмотров по месяцам
st.subheader("Количество Просмотров по Месяцам")
# Группировка данных для графика
monthly_counts = df.groupby('watch_month').size().reset_index(name='Количество')
# Создание графика Altair
chart_monthly = alt.Chart(monthly_counts).mark_bar().encode(
    x=alt.X('watch_month', title='Месяц Просмотра'),
    y=alt.Y('Количество', title='Количество Просмотров'),
    tooltip=['watch_month', 'Количество'],
    color=alt.value("#6366f1") # Фирменный цвет Tailwind
).properties(
    height=300
).interactive() # Добавление интерактивности (зум, панорамирование)
st.altair_chart(chart_monthly, use_container_width=True)

# Разделение на две колонки для графиков
col_chart_1, col_chart_2 = st.columns(2)

with col_chart_1:
    # 2. График: Распределение по рейтингу
    st.subheader("Распределение по Вашему Рейтингу")
    rating_counts = df.groupby('user_rating').size().reset_index(name='Количество')
    # Преобразование рейтинга в строку для корректной оси (если нужно, иначе можно оставить int)
    rating_counts['user_rating'] = rating_counts['user_rating'].astype(str)

    chart_rating = alt.Chart(rating_counts).mark_bar().encode(
        x=alt.X('user_rating', title='Ваш Рейтинг', sort='ascending'),
        y=alt.Y('Количество', title='Число Просмотров'),
        tooltip=['user_rating', 'Количество'],
        color=alt.Color('user_rating', legend=None)
    ).properties(
        height=350
    ).interactive()
    st.altair_chart(chart_rating, use_container_width=True)

with col_chart_2:
    # 3. График: Процентное соотношение Фильмов и Сериалов
    st.subheader("Соотношение Фильмов и Сериалов")
    type_counts = df.groupby('content_type').size().reset_index(name='Количество')
    
    chart_type = alt.Chart(type_counts).mark_arc(outerRadius=120).encode(
        theta=alt.Theta(field="Количество", type="quantitative"),
        color=alt.Color(field="content_type", title="Тип контента"),
        tooltip=["content_type", "Количество", alt.Tooltip("Количество", format=".1%")]
    ).properties(
        height=350
    )

    text = alt.Chart(type_counts).mark_text(radius=140).encode(
        theta=alt.Theta(field="Количество", type="quantitative", stack=True),
        text=alt.Text("Количество", format=".1%"),
        order=alt.Order("Количество", sort="descending"),
        color=alt.value("black")
    )
    
    st.altair_chart(chart_type, use_container_width=True)
    st.markdown("---")
    st.markdown(f"**Всего фильмов:** {total_movies} | **Всего эпизодов:** {total_series_episodes}")

# --- Таблица последних просмотров ---
st.header("📖 Последние Просмотры")
# Сортировка по дате и показ последних 10 записей
recent_views = df.sort_values(by='watch_date', ascending=False)[['title', 'content_type', 'user_rating', 'duration_minutes', 'watch_date']].head(10)
recent_views.columns = ['Название', 'Тип', 'Рейтинг', 'Продолжительность (мин)', 'Дата Просмотра']
st.dataframe(recent_views, use_container_width=True)

st.divider()
st.caption("Приложение Streamlit для веб-аналитики Movie Tracker. Данные сейчас моковые.")