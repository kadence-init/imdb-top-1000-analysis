# --- Этап 1: Загрузка, проверка и очистка данных ---

# Шаг 1: Импортируем наши библиотеки и задаем константы
import os
import pandas as pd
import matplotlib.pyplot as plt

FILE_PATH = 'imdb_top_1000.csv'
ACTOR_NAME = 'Willem Dafoe'

# Шаг 2: Безопасно загружаем данные
if os.path.exists(FILE_PATH):
    df = pd.read_csv(FILE_PATH)
    print("Файл успешно загружен.")
else:
    print(f"Ошибка: Файл по пути {FILE_PATH} не найден.")
    exit() # Важно: если файла нет, прекращаем выполнение скрипта

# Шаг 3: Проверка на дубликаты названий
duplicates = df[df.duplicated(subset=['Series_Title'], keep=False)]
if not duplicates.empty:
    print("\n--- Найдены дубликаты в названиях фильмов ---")
    print(duplicates[['Series_Title', 'Released_Year', 'IMDB_Rating', 'Director']])
else:
    print("\n--- Дубликатов в названиях не найдено ---")

# Шаг 4: Проверка на пропущенные значения
missing_values = df.isnull().sum()
print("\n--- Колонки с пропущенными значениями и их количество ---")
print(missing_values[missing_values > 0])


# --- Этап 2: Анализ фильмографии Уиллема Дефо ---

# Проводим анализ на исходном, полном DataFrame 'df'
actor_filter = (
    (df['Star1'] == ACTOR_NAME) |
    (df['Star2'] == ACTOR_NAME) |
    (df['Star3'] == ACTOR_NAME) |
    (df['Star4'] == ACTOR_NAME)
)
actor_movies = df[actor_filter]
print(f"\n--- Фильмы с участием {ACTOR_NAME} из топ-1000 ---")
if not actor_movies.empty:
    print(actor_movies[['Series_Title', 'Released_Year', 'IMDB_Rating', 'Meta_score', 'Director']])
else:
    print(f"{ACTOR_NAME} не найден в топ-4 актеров в данном наборе данных.")


# --- Этап 3: Анализ корреляции между оценками критиков и зрителей ---

# Шаг 3.1: Локальная очистка данных ТОЛЬКО для этой задачи
df_for_correlation = df.dropna(subset=['Meta_score', 'IMDB_Rating'])

# Шаг 3.2: Расчет коэффициента корреляции
correlation = df_for_correlation['IMDB_Rating'].corr(df_for_correlation['Meta_score'])
print(f"\n--- Анализ корреляции (на {len(df_for_correlation)} фильмах) ---")
print(f"Коэффициент корреляции между IMDB_Rating и Meta_score: {correlation:.2f}")

# Шаг 3.3: Визуализация
plt.figure(figsize=(10, 6))
plt.scatter(df_for_correlation['Meta_score'], df_for_correlation['IMDB_Rating'], alpha=0.5)

plt.title('Корреляция между оценками критиков (Meta_score) и зрителей (IMDB_Rating)')
plt.xlabel('Оценка критиков (Meta_score)')
plt.ylabel('Оценка зрителей (IMDB_Rating)')
plt.grid(True)

plt.savefig('rating_correlation.png')
print("График корреляции сохранен в файл 'rating_correlation.png'")
plt.show()
