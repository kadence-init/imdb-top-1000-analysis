"""
Основной модуль для запуска интерактивного дашборда "IMDb Explorer".

Этот скрипт использует Streamlit для создания веб-интерфейса,
который позволяет пользователям в реальном времени взаимодействовать
с результатами анализа данных.
"""

import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

# Импортируем наши модули
import config
from db_utils import execute_sql_from_file
from analysis_utils import draw_correlation_on_ax, clean_and_convert_to_numeric

# --------------------------------------------------------------------------
# --- БЛОК ЗАГРУЗКИ И КЭШИРОВАНИЯ ДАННЫХ ---
# --------------------------------------------------------------------------


@st.cache_data
def load_and_prepare_data():
    """
    Загружает и предварительно подготавливает все данные для дашборда.

    Эта функция обернута в декоратор `@st.cache_data`, что является
    ключевой оптимизацией в Streamlit. Функция выполнится полностью
    только один раз. При последующих взаимодействиях с UI (например,
    выбор в selectbox), Streamlit будет мгновенно возвращать уже
    загруженные и обработанные данные из кэша, делая приложение отзывчивым.

    Returns:
        Кортеж из двух DataFrame: (directors_df, full_df).
        Возвращает пустые DataFrame в случае ошибки.
    """
    try:
        # Используем 'with' для гарантии закрытия соединения
        with sqlite3.connect(config.DB_PATH) as conn:
            directors_df = execute_sql_from_file(conn, config.SQL_TOP_DIRECTORS_PATH)
            full_df = pd.read_sql_query(f"SELECT * FROM {config.TABLE_NAME}", conn)

        # Важно: предварительная очистка данных происходит здесь,
        # чтобы результат кэшировался уже в готовом для анализа виде.
        # Это решает проблему с потерей состояния при перезапусках скрипта Streamlit.
        full_df["Gross_Clean"] = clean_and_convert_to_numeric(full_df["Gross"])

        return directors_df, full_df

    except Exception as e:
        # Элегантная обработка ошибки: если БД не готова, дашборд
        # покажет информативное сообщение, а не упадет с ошибкой.
        st.error(
            f"Ошибка загрузки данных: {e}. "
            f"Убедитесь, что вы запустили файл imdb_start."
        )
        return pd.DataFrame(), pd.DataFrame()


# --------------------------------------------------------------------------
# --- ГЛАВНАЯ ФУНКЦИЯ ДЛЯ ПОСТРОЕНИЯ UI ---
# --------------------------------------------------------------------------


def run_dashboard():
    """
    Основная функция, которая строит и отображает все элементы дашборда.
    """
    # Устанавливаем конфигурацию страницы для более широкого макета
    st.set_page_config(layout="wide")

    # Загружаем данные. Streamlit сам управляет кэшированием.
    directors_df, full_df = load_and_prepare_data()

    # Проверяем, что данные успешно загрузились, прежде чем строить UI
    if directors_df.empty or full_df.empty:
        st.warning("Данные не загружены. Дальнейшее построение дашборда невозможно.")
        return

    # --- ЗАГОЛОВОК ---
    st.title("IMDb Explorer: Интерактивный Анализ")
    st.markdown(
        "Добро пожаловать в аналитическую панель для исследования топ-1000 фильмов IMDb."
    )

    st.divider()

    # --- БЛОК 1: РЕЙТИНГ РЕЖИССЕРОВ ---
    st.header("🏆 Рейтинг режиссеров десятилетия")
    st.markdown("""
        Этот рейтинг выявляет режиссеров, которые не просто сняли один успешный фильм, 
        а демонстрируют **стабильно высокое качество**, выпустив как минимум два фильма 
        с рейтингом выше 8.0 за последнее десятилетие.
        """)
    # Используем колонки для создания сбалансированного и профессионального вида
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader("Список лидеров")
        st.dataframe(directors_df)

    with col2:
        st.subheader("Визуализация рейтинга")

        # Горизонтальный бар-чарт - идеален для рейтингов
        fig, ax = plt.subplots(figsize=(6, 2.5))

        top_5_directors = directors_df.head(5)
        ax.barh(
            top_5_directors["Director"],
            top_5_directors["Average_Rating_Of_Top_Films"],
            color="#2a9d8f",
        )

        # Инвертируем ось Y, чтобы #1 был наверху
        ax.invert_yaxis()

        # Убираем лишние рамки для чистоты
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.tick_params(axis="y", length=0)

        # Добавляем подписи прямо на бары
        for index, value in enumerate(top_5_directors["Average_Rating_Of_Top_Films"]):
            ax.text(
                value - 0.2,
                index,
                f"{value:.2f}",
                color="white",
                ha="right",
                va="center",
                fontweight="bold",
            )

        st.pyplot(fig, width="stretch")

    st.divider()

    # --- БЛОК 2: ИНТЕРАКТИВНЫЙ ПРОФАЙЛЕР РЕЖИССЕРА ---
    st.header("🎬 Профайлер режиссера")
    st.markdown(
        "Выберите **любого** режиссера из топ-1000 фильмов для детального анализа его карьеры."
    )

    # st.selectbox - ключевой интерактивный элемент Streamlit
    all_directors_list = sorted(full_df["Director"].unique())
    selected_director = st.selectbox(
        label="Начните вводить имя режиссера:",
        options=all_directors_list,
        index=None,
        placeholder="Выберите режиссера...",
    )

    if selected_director:
        director_films_df = full_df[full_df["Director"] == selected_director].copy()

        st.subheader(f"Фильмография {selected_director} в топ-1000:")
        columns_to_show = [
            "Series_Title",
            "Released_Year",
            "IMDB_Rating",
            "Meta_score",
            "Genre",
        ]
        st.dataframe(director_films_df[columns_to_show])

        # st.metric - мощный компонент для отображения ключевых показателей (KPI)
        avg_rating = director_films_df["IMDB_Rating"].mean()
        avg_metascore = director_films_df["Meta_score"].mean()
        film_count = len(director_films_df)

        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Всего фильмов в топ-1000", film_count)
        kpi2.metric("Средний рейтинг IMDb", f"{avg_rating:.2f}")
        kpi3.metric("Средняя оценка критиков", f"{avg_metascore:.2f}")

    st.divider()

    # --- БЛОК 3: АНАЛИЗ ВЗАИМОСВЯЗЕЙ ---
    st.header("🔬 Анализ взаимосвязей: Критики, Зрители и Касса")
    st.markdown("Исследуем, как различные метрики успеха влияют друг на друга.")

    # Создаем единую фигуру Matplotlib с сеткой 1x3 для идеального выравнивания
    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(15, 4), constrained_layout=True)

    # Последовательно вызываем нашу утилиту-рисовальщик для каждой ячейки сетки
    draw_correlation_on_ax(
        ax=axes[0],
        df=full_df,
        x_column="Meta_score",
        y_column="IMDB_Rating",
        title="Критики vs. Зрители",
        xlabel="Оценка критиков",
        ylabel="Оценка зрителей",
    )
    draw_correlation_on_ax(
        ax=axes[1],
        df=full_df,
        x_column="IMDB_Rating",
        y_column="Gross",
        title="Зрители vs. Касса",
        xlabel="Оценка зрителей",
        ylabel="Кассовые сборы",
    )
    draw_correlation_on_ax(
        ax=axes[2],
        df=full_df,
        x_column="Meta_score",
        y_column="Gross",
        title="Критики vs. Касса",
        xlabel="Оценка критиков",
        ylabel="Кассовые сборы",
    )
    # Отображаем всю фигуру целиком
    st.pyplot(fig)

    # Выводы размещаются ПОСЛЕ визуализации для логичного повествования
    st.info(
        """
        **Ключевые инсайты из графиков:**
        *   **Мнение критиков и зрителей в целом совпадает**, но связь нельзя назвать сильной.
        *   **Прямой связи между высокими оценками критиков и кассовыми сборами практически нет.**
        *   **Связь между любовью зрителей и сборами существует, но она очень слабая.**
        """,
        icon="💡",
    )

    st.divider()

    # --- БЛОК 4: ЗАЛ СЛАВЫ ---
    st.header("🏆 Зал славы: Фильмы-рекордсмены")

    # Находим фильмы-рекордсмены, используя .loc и .idxmax()
    top_gross_movie = full_df.loc[full_df["Gross_Clean"].idxmax()]
    top_imdb_movie = full_df.loc[full_df["IMDB_Rating"].idxmax()]

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("💰 Самый кассовый фильм")
        st.success(
            f"**{top_gross_movie['Series_Title']}** ({top_gross_movie['Released_Year']})"
            f" - Сборы: ${top_gross_movie['Gross_Clean']:,.0f}"
        )
    with col_b:
        st.subheader("⭐ Любимец зрителей")
        st.success(
            f"**{top_imdb_movie['Series_Title']}** ({top_imdb_movie['Released_Year']}) "
            f"- Рейтинг IMDb: **{top_imdb_movie['IMDB_Rating']}**"
        )


# --------------------------------------------------------------------------
# --- ТОЧКА ВХОДА ---
# --------------------------------------------------------------------------
# Конструкция 'if __name__ == "__main__"' - это стандартная точка входа
# в Python, которая гарантирует, что код запустится, только когда
# файл выполняется напрямую.
if __name__ == "__main__":
    run_dashboard()
