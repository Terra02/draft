import streamlit as st
import pandas as pd
import plotly.express as px
import httpx
import asyncio

st.set_page_config(
    page_title="Главная панель",
    page_icon="🏠",
    layout="wide"
)

st.title("Главная панель управления")

async def get_quick_stats():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://api:8000/api/v1/analytics/system/overview")
            if response.status_code == 200:
                return response.json()
    except Exception:
        return None

async def main():
    stats = await get_quick_stats()
    
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👥 Пользователи", stats.get('total_users', 0))
        with col2:
            st.metric("🎬 Контент", stats.get('total_content', 0))
        with col3:
            st.metric("📊 Просмотры", stats.get('total_views', 0))
    else:
        st.error("Не удалось загрузить данные")

if __name__ == "__main__":
    asyncio.run(main())