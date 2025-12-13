import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
import altair as alt
import httpx
import pandas as pd
import streamlit as st

DEFAULT_API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")
DATA_LIMIT = 300

st.set_page_config(
    page_title="Аналитика",
    page_icon="🎬",
    layout="wide",
    #initial_sidebar_state="expanded",
)

def _build_client(api_url: str) -> httpx.Client:
    return httpx.Client(base_url=api_url, timeout=10.0)

def _time_range_to_days(label: str) -> int:
    mapping = {
        "Все время": 365,
    }
    return mapping.get(label, 30)

@st.cache_data(show_spinner=False, ttl=120)
def fetch_user_analytics(api_url: str, user_id: int, days: int) -> Optional[Dict[str, Any]]:
    try:
        with _build_client(api_url) as client:
            response = client.get(f"/api/v1/analytics/user/{user_id}", params={"days": days})
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as exc:
        st.error(f"Не удалось загрузить аналитику пользователя: {exc}")
        return None
    
@st.cache_data(show_spinner=False, ttl=120)
def fetch_user_timeline(api_url: str, user_id: int, period: str = "monthly") -> List[Dict[str, Any]]:
    try:
        with _build_client(api_url) as client:
            response = client.get(
                f"/api/v1/analytics/user/{user_id}/timeline", params={"period": period}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", []) if isinstance(data, dict) else []
    except httpx.HTTPError as exc:
        st.error(f"Не удалось загрузить временную аналитику: {exc}")
        return []


@st.cache_data(show_spinner=False, ttl=120)
def fetch_view_history(api_url: str, user_id: int, limit: int = DATA_LIMIT) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    page_size = min(limit, 100)
    try:
        with _build_client(api_url) as client:
            skip = 0
            while len(records) < limit:
                response = client.get(
                    f"/api/v1/view-history/user/{user_id}",
                    params={"skip": skip, "limit": min(page_size, limit - len(records))},
                )
                response.raise_for_status()
                chunk = response.json()
                if not chunk:
                    break
                records.extend(chunk)
                if len(chunk) < page_size:
                    break
                skip += page_size
    except httpx.HTTPError as exc:
        st.error(f"Не удалось загрузить историю просмотров: {exc}")
    return records


@st.cache_data(show_spinner=False, ttl=120)
def resolve_user_id(api_url: str, identifier: int) -> Optional[int]:
    try:
        with _build_client(api_url) as client:
            tg_response = client.get(f"/api/v1/users/telegram/{identifier}")
            if tg_response.status_code == 200:
                return tg_response.json().get("id")

            st.warning("Пользователь не найден. Проверьте Telegram ID.")
    except httpx.HTTPError as exc:
        st.error(f"Не удалось определить пользователя: {exc}")
    return None


def build_dataframe(
    history: List[Dict[str, Any]], start_date: datetime, end_date: datetime
) -> pd.DataFrame:
    rows = []
    for record in history:
        watched_at = pd.to_datetime(record.get("watched_at"))
        if not pd.isna(watched_at) and watched_at.tzinfo is not None:
            watched_at = watched_at.tz_convert(None)
        if pd.isna(watched_at) or watched_at < start_date or watched_at > end_date:
            continue

        content = record.get("content") or {}
        content_type = content.get("content_type") or record.get("content_type")
        rows.append(
            {
                "title": content.get("title")
                or record.get("content_title")
                or "Без названия",
                "content_type": content_type,
                "user_rating": record.get("rating"),
                "watch_date": watched_at,
            }
        )

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    df["watch_day"] = df["watch_date"].dt.date.astype(str)
    df["content_type_display"] = (
        df["content_type"].map({"movie": "Фильм", "series": "Сериал (Эпизод)"}).fillna("Неизвестно")
    )
    return df

def format_duration(total_minutes: float) -> Tuple[str, str]:
    hours = round(total_minutes / 60, 1)
    days = round(hours / 24, 1)
    return f"{hours:,}", f"{days:,}"


def _filter_timeline(
    data: List[Dict[str, Any]], start: datetime, end: datetime
) -> pd.DataFrame:
    timeline_rows = []
    for row in data:
        period_raw = row.get("period") or row.get("month")
        if not period_raw:
            continue
        period_dt = pd.to_datetime(period_raw)
        if not pd.isna(period_dt) and period_dt.tzinfo is not None:
            period_dt = period_dt.tz_convert(None)
        if pd.isna(period_dt) or period_dt < start or period_dt > end:
            continue
        timeline_rows.append(
            {
                "watch_period": period_dt.strftime("%Y-%m-%d"),
                "Количество": row.get("view_count", 0),
            }
        )
    return pd.DataFrame(timeline_rows)


# --- Заголовок и фильтры ---
st.title("🎬 Аналитика Просмотров")

st.markdown(
    "Здесь вы найдете все ключевые метрики и статистику по просмотренным фильмам и сериалам,")

st.sidebar.header("Фильтры и настройки")
api_url_input = st.sidebar.text_input(
    "API URL",
    value=DEFAULT_API_URL,
)
user_identifier = st.sidebar.number_input(
    "Telegram ID",
    min_value=1,
    value=1,
    step=1,
    help="Можно вводить Telegram ID — система найдёт нужного пользователя автоматически.",
)


days = _time_range_to_days("Все время")
end_date = datetime.now()
start_date = end_date - timedelta(days=days)
api_url = api_url_input.rstrip("/")

resolved_user_id = resolve_user_id(api_url, user_identifier)
if resolved_user_id is None:
    st.stop()

analytics = fetch_user_analytics(api_url, resolved_user_id, days)
timeline = fetch_user_timeline(api_url, resolved_user_id, period="daily")
history_records = fetch_view_history(api_url, resolved_user_id, limit=DATA_LIMIT)
df = build_dataframe(history_records, start_date, end_date)

if df.empty and not analytics:
    st.warning("Нет данных для отображения. Проверьте фильтры или наличие записей в базе.")
    st.stop()


# --- KPI (Ключевые показатели эффективности) ---
st.header("📊 Ключевые Метрики")

total_items = analytics.get("total_views") if analytics else len(df)
total_movies = analytics.get("movies_views") if analytics else int((df["content_type"] == "movie").sum())
total_series_episodes = (
    analytics.get("series_views") if analytics else int((df["content_type"] == "series").sum())
)
avg_rating = (
    analytics.get("average_rating") if analytics else round(df["user_rating"].dropna().mean(), 2)
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Всего Просмотров", value=total_items)
    st.metric(label="Средний Рейтинг", value=avg_rating)
with col2: 
    st.metric(label="Всего Фильмов", value=total_movies)
    st.metric(label="Всего Эпизодов Сериалов", value=total_series_episodes)

st.divider()

# --- Графики Аналитики ---

st.header("📈 Визуализация Данных")
st.subheader("Количество Просмотров по Дням")

daily_counts = _filter_timeline(timeline, start_date, end_date)
if daily_counts.empty and not df.empty:
    daily_counts = (
        df.groupby("watch_day").size().reset_index(name="Количество").rename(columns={"watch_day": "watch_period"})
    )

if daily_counts.empty:
    st.info("Недостаточно данных для построения графика по дням.")
else:
    chart_daily = alt.Chart(daily_counts).mark_bar(color="#6366f1").encode(
        x=alt.X("watch_period", title="Дата просмотра", sort="ascending"),
        y=alt.Y("Количество", title="Количество просмотров"),
        tooltip=["watch_period", "Количество"],
    ).properties(height=300)

    st.altair_chart(chart_daily.interactive(), use_container_width=True)

st.subheader("Соотношение Фильмов и Сериалов")
type_counts = df.groupby("content_type_display").size().reset_index(name="Количество")

if type_counts.empty:
    st.info("Нет данных для построения диаграммы по типам контента.")
else:
    chart_type = alt.Chart(type_counts).mark_arc(outerRadius=120).encode(
        theta=alt.Theta(field="Количество", type="quantitative"),color=alt.Color(field="content_type_display", title="Тип контента"),
        tooltip=["content_type_display", "Количество"],
    ).properties(height=350)
    

    st.altair_chart(chart_type, use_container_width=True)
    st.markdown("---")
    st.markdown(
        f"**Всего фильмов:** {total_movies} | **Всего эпизодов:** {total_series_episodes}"
    )

st.header("📖 Последние Просмотры")

if df.empty:
    st.info("Нет недавних просмотров в выбранном диапазоне.")
else:
    recent_views = df.sort_values(by="watch_date", ascending=False)[
        ["title", "content_type_display", "user_rating", "watch_date"]
    ].head(10)
    recent_views.columns = [
        "Название",
        "Тип",
        "Рейтинг",
        "Дата Просмотра",
    ]
    st.dataframe(recent_views, use_container_width=True)

st.divider()
