import statistics
from datetime import datetime


def generate_markdown_report(results, total_time, output_file, model_name):
    """
    Формирует официальный отчет о результатах тестирования системы.
    """
    if not results:
        print("[WARNING] Данные для формирования отчета отсутствуют.")
        return

    # Расчет статистических показателей
    scores = [r['score'] for r in results]
    latencies = [r['latency'] for r in results]
    avg_score = statistics.mean(scores) if scores else 0

    # Формирование документа
    report = f"""# Протокол тестирования аналитической системы

**Дата формирования:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Наименование системы:** {model_name}
**Объем выборки:** {len(results)} тестовых сценариев

## 1. Сводные показатели эффективности
| Показатель | Значение | Комментарий |
|------------|----------|-------------|
| **Средняя оценка качества** | **{avg_score:.2f} / 5.00** | Целевой показатель > 4.0 |
| **Среднее время отклика** | {statistics.mean(latencies):.2f} с | Latency |
| **Медианное время отклика** | {statistics.median(latencies):.2f} с | Устойчивость системы |
| **Общее время выполнения** | {total_time:.1f} с | |

## 2. Распределение результатов
* **Высокое качество (5):** {scores.count(5)}
* **Удовлетворительное качество (3-4):** {scores.count(4) + scores.count(3)}
* **Низкое качество (1-2):** {scores.count(2) + scores.count(1)}
* **Отказ системы (0):** {scores.count(0)}

## 3. Детализация несоответствий (Оценка <= 3)
Ниже приведен список сценариев, требующих внимания разработчика.
"""
    for r in results:
        if r['score'] <= 3:
            report += f"""
### Сценарий: {r['question']}
* **Категория:** {r.get('category', 'N/A')}
* **Оценка системы:** {r['score']}
* **Фактический ответ:** {r['prediction']}
* **Время обработки:** {r['latency']:.2f} с
---
"""

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"[INFO] Отчет успешно сохранен в файл: {output_file}")
    except IOError as e:
        print(f"[ERROR] Ошибка записи файла отчета: {e}")