import time
import json
import statistics
from collections import defaultdict
from src.config import load_config
from src.vector_store import VectorDB
from src.rag_chain import get_rag_chain
from src.visualization import generate_markdown_report


def run():
    # 1. Инициализация
    print("[STATUS] Инициализация компонентов системы...")
    config = load_config()
    vdb = VectorDB(config)
    rag_chain = get_rag_chain(config, vdb)

    if not rag_chain:
        print("[ERROR] Не удалось инициализировать RAG-цепочку. Проверьте наличие векторного индекса.")
        return

    # 2. Загрузка датасета
    dataset_path = "test_dataset_expanded.json"
    try:
        with open(dataset_path, "r", encoding="utf-8") as f:
            dataset = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Файл тестовых данных '{dataset_path}' не найден.")
        return

    results = []
    print(f"[INFO] Начало процедуры тестирования. Количество сценариев: {len(dataset)}")

    category_metrics = defaultdict(list)

    for i, item in enumerate(dataset, 1):
        print(f"[{i}/{len(dataset)}] Обработка сценария: {item['question'][:50]}... ({item['category']})")
        start_step = time.time()

        try:
            response = rag_chain.invoke({"input": item["question"]})
            prediction = response['answer']
            context_found = len(response['context']) > 0
        except Exception as e:
            prediction = f"System Error: {e}"
            context_found = False

        latency = time.time() - start_step

        # Формальная логика оценки
        score = 0
        if context_found:
            score += 3
        if len(prediction) > 20:
            score += 2

        # Корректировка для негативных тестов
        if "generalization" in item['category'] and not context_found and "нет информации" in prediction.lower():
            score = 5

        row = {
            'category': item['category'],
            'question': item['question'],
            'prediction': prediction,
            'score': score,
            'latency': latency,
            'explanation': "Автоматизированная оценка"
        }
        results.append(row)
        category_metrics[item['category']].append(score)

    total_time = sum(r['latency'] for r in results)

    # Вывод статистики в консоль
    print("\n[SUMMARY] Результаты тестирования по категориям:")
    for cat, scores in category_metrics.items():
        avg = statistics.mean(scores)
        print(f"   - {cat}: {avg:.2f} / 5.00")

    # Генерация отчета
    generate_markdown_report(
        results=results,
        total_time=total_time,
        output_file="VALIDATION_REPORT.md",
        model_name=f"{config['app_name']} v1.0"
    )


if __name__ == "__main__":
    run()