"""
Модуль утилит для взаимодействия с базой данных SQLite.

Этот файл инкапсулирует всю логику работы с базой данных,
следуя принципу разделения ответственности. Функции спроектированы
так, чтобы быть универсальными и работать с любым активным
соединением SQLite.
"""

import pandas as pd
import sqlite3
import config
from matplotlib.axes import Axes


def write_df_to_table(conn: sqlite3.Connection, df: pd.DataFrame, table_name: str):
    """Записывает DataFrame в таблицу базы данных SQLite.

    Используется метод `df.to_sql`, который является высокоуровневой
    оберткой Pandas для эффективной загрузки данных в SQL-таблицы.

    Параметр `if_exists='replace'` выбран для актуальности:
    каждый запуск оркестратора полностью перезаписывает таблицу,
    гарантируя свежесть и консистентность данных.

    Args:
        conn: Активное соединение с базой данных SQLite.
        df: DataFrame, который необходимо записать.
        table_name: Имя целевой таблицы в базе данных.
    """
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';"
    )
    if cursor.fetchone() is None:
        print(f"Таблица '{table_name}' не найдена. Создаем и наполняем из {df}...")
        df.to_sql(table_name, conn, index=False, if_exists="replace")
        print("База данных успешно создана.")
    else:
        print("База данных уже существует. Пропускаем создание.")


def execute_sql_from_file(conn: sqlite3.Connection, sql_file_path: str) -> pd.DataFrame:
    """Выполняет SQL-запрос из файла и возвращает результат в виде DataFrame.

    Эта функция позволяет отделить SQL-логику от Python-кода, что улучшает
    читаемость и упрощает поддержку сложных запросов.

    Args:
        conn: Активное соединение с базой данных SQLite.
        sql_file_path: Путь к файлу .sql с запросом.

    Returns:
        DataFrame с результатами выполнения SQL-запроса.
        Возвращает пустой DataFrame в случае любой ошибки.
    """
    try:
        with open(sql_file_path, "r", encoding="utf-8") as f:
            sql_query = f.read()

        # pd.read_sql_query - это мощный метод Pandas для выполнения
        # запросов и немедленной упаковки результата в DataFrame.
        df = pd.read_sql_query(sql_query, conn)
        return df

    except FileNotFoundError:
        print(f"[ОШИБКА] SQL-файл не найден по пути: {sql_file_path}")
        return pd.DataFrame()
    except Exception as e:
        print(
            f"[ОШИБКА] Ошибка при выполнении SQL-запроса из файла '{sql_file_path}': {e}"
        )
        return pd.DataFrame()
