# streamlit_app/utils/animations.py
"""
Анимации и эффекты для Streamlit приложения
"""

import streamlit as st
import time
from config.streamlit_config import ANIMATION_CONFIG


def show_thinking_animation():
    """Анимация 'AI думает' с прогресс баром"""
    thinking_container = st.empty()
    progress_container = st.empty()
    
    with thinking_container.container():
        st.markdown("""
        <div class="thinking-animation">
            <h3>🤖 ИИ анализирует ваш запрос...</h3>
        </div>
        """, unsafe_allow_html=True)
    
    # Прогресс бар с этапами
    stages = ANIMATION_CONFIG["thinking_stages"]
    stage_delay = ANIMATION_CONFIG["stage_delay"]
    
    progress_bar = progress_container.progress(0)
    status_text = progress_container.empty()
    
    for i, stage in enumerate(stages):
        status_text.info(stage)
        progress_bar.progress((i + 1) / len(stages))
        time.sleep(stage_delay)
    
    thinking_container.empty()
    progress_container.empty()


def add_auto_scroll_script():
    """Добавляет JavaScript для автоматического скролла к результатам"""
    delay = ANIMATION_CONFIG["auto_scroll_delay"]
    
    st.markdown(f"""
    <script>
    setTimeout(function() {{
        // Ищем секцию с анализом (последний stSubheader)
        const headers = document.querySelectorAll('[data-testid="stSubheader"]');
        if (headers.length > 0) {{
            const analysisHeader = headers[headers.length - 1];
            analysisHeader.scrollIntoView({{behavior: 'smooth', block: 'start'}});
        }}
    }}, {delay});
    </script>
    """, unsafe_allow_html=True)


def show_success_message(message: str, icon: str = "✅"):
    """Показывает сообщение об успехе с иконкой"""
    st.success(f"{icon} {message}")


def show_error_message(message: str, icon: str = "❌"):
    """Показывает сообщение об ошибке с иконкой"""
    st.error(f"{icon} {message}")


def show_info_message(message: str, icon: str = "ℹ️"):
    """Показывает информационное сообщение с иконкой"""
    st.info(f"{icon} {message}")