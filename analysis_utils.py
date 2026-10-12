"""
Модуль утилит для анализа данных в проекте "IMDb Explorer".

Этот файл содержит "чистые" функции, отвечающие за конкретные
аналитические и вычислительные задачи. Они спроектированы так, чтобы
быть универсальными, тестируемыми и независимыми от конкретного
источника данных или интерфейса.
"""

import pandas as pd
from matplotlib.axes import Axes


def clean_and_convert_to_numeric(series: pd.Series) -> pd.Series:
    """Очищает столбец Pandas (Series) и преобразует его в числовой тип.

    Эта функция является ключевым компонентом пайплайна очистки данных.
    Она отказоустойчиво обрабатывает строковые данные, которые могут содержать
    нечисловые символы (например, знаки валют, разделители тысяч).

    Использование `pd.to_numeric` с параметром `errors='coerce'` является
    промышленным стандартом для безопасного преобразования типов, так как
    это позволяет избежать падения всего скрипта из-за одного некорректного значения.

    Args:
        series: Входной столбец Pandas (Series) для очистки.

    Returns:
        Новый столбец Pandas (Series) с числовым типом данных (float64)
        и значениями NaN на месте неконвертируемых строк.
    """
    # Явное преобразование в строку необходимо для использования строковых методов (.str)
    series_as_str = series.astype(str)
    # Регулярное выражение удаляет все символы, кроме цифр и десятичной точки.
    cleaned_series = series_as_str.str.replace(r"[^\d.]", "", regex=True)
    # 'errors="coerce"' - это ключевой элемент: все, что не может быть
    # преобразовано, станет Null-значением (NaN), а не вызовет ошибку.
    numeric_series = pd.to_numeric(cleaned_series, errors="coerce")
    return numeric_series


def draw_correlation_on_ax(
    ax: Axes,
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    title: str,
    xlabel: str,
    ylabel: str,
):
    """Строит диаграмму рассеяния (scatter plot) на предоставленном объекте Axes.

    Эта функция следует принципу разделения ответственности. Она не создает
    и не управляет жизненным циклом фигуры Matplotlib, а только выполняет
    задачу отрисовки данных на уже существующем "холсте" (Axes).
    Такой подход делает функцию переиспользуемой и позволяет встраивать
    ее в сложные, составные визуализации.

    Args:
        ax: Объект осей Matplotlib (ax), на котором будет нарисован график.
        df: DataFrame, содержащий данные для визуализации.
        x_column: Название столбца для оси X.
        y_column: Название столбца для оси Y.
        title: Заголовок для данного конкретного графика.
        xlabel: Подпись для оси X.
        ylabel: Подпись для оси Y.
    """
    # Создание копии DataFrame - лучшая практика, чтобы избежать
    # нежелательных изменений в исходном объекте (side effects).
    df_transformed = df.copy()

    # Динамическая очистка данных прямо перед визуализацией.
    df_transformed[x_column] = clean_and_convert_to_numeric(df_transformed[x_column])
    df_transformed[y_column] = clean_and_convert_to_numeric(df_transformed[y_column])
    df_transformed = df_transformed.dropna(subset=[x_column, y_column])

    # Основная логика отрисовки. Все команды применяются к объекту `ax`,
    # а не к глобальному состоянию `plt`.
    ax.scatter(df_transformed[x_column], df_transformed[y_column], alpha=0.5)
    ax.set_title(title, fontsize=10)
    ax.set_xlabel(xlabel, fontsize=8)
    ax.set_ylabel(ylabel, fontsize=8)
    ax.grid(True)
