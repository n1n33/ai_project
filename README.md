# EduRAG: Local Educational RAG System

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3-green)](https://www.langchain.com/)
[![Ollama](https://img.shields.io/badge/Ollama-Local-orange)](https://ollama.ai/)
[![CUDA](https://img.shields.io/badge/CUDA-12.x-brightgreen)](https://developer.nvidia.com/cuda-toolkit)
[![GPU Required](https://img.shields.io/badge/Device-GPU%20Required-red)](https://www.nvidia.com/)

Автономная система вопросно-ответного поиска (Retrieval-Augmented Generation) для обработки образовательных материалов по точным наукам. Проект обеспечивает полный цикл работы с документами: парсинг (PDF, Markdown, DOCX), векторизацию контента и генерацию ответов с использованием LLM **Qwen 2.5**.

## Оглавление

- [Ключевые возможности](#ключевые-возможности)
- [Системные требования](#системные-требования)
- [Установка и настройка](#установка-и-настройка)
- [Запуск приложения](#запуск-приложения)
- [Структура проекта](#структура-проекта)
- [Устранение неполадок](#устранение-неполадок)
- [Лицензия](#лицензия)

## Ключевые возможности

- **Локальная обработка данных** — все вычисления (эмбеддинги, инференс LLM) выполняются локально без передачи данных в облачные сервисы
- **Контекстно-зависимая генерация** — механизм `History Aware Retriever` для корректной обработки уточняющих запросов с учётом истории диалога
- **Мультиформатность** — поддержка индексации документов: `.pdf`, `.docx`, `.txt`, `.md`
- **Кросслингвистический поиск** — модель `intfloat/multilingual-e5-base` для семантического поиска (англоязычные документы + русскоязычные запросы)
- **GPU-акселерация** — FAISS + PyTorch с поддержкой CUDA для ускорения векторизации и поиска

## Системные требования

### Аппаратное обеспечение

| Компонент | Минимум | Рекомендуется |
|-----------|---------|--------------|
| **GPU** | NVIDIA с CUDA | RTX 3060 12GB+ |
| **CUDA** | 12.x | 12.4 |
| **RAM** | 16 ГБ | 32 ГБ |
| **Накопитель** | HDD | SSD (быстрая загрузка весов) |

### Программное обеспечение

- **ОС:** Windows 10/11, Linux
- **Python:** 3.10+
- **Ollama:** актуальная версия
- **NVIDIA Drivers:** 550.x+

## Установка и настройка

### Подготовка LLM (Ollama)

Загрузите модель с расширенным контекстным окном:

```bash
# Загрузка базовой модели
ollama pull qwen2.5:14b-instruct-q3_K_M

# Создание пользовательской конфигурации
ollama create edu-qwen-14b -f Modelfile
```

**Примечание:** Файл `Modelfile` должен находиться в корне проекта.

### Настройка окружения Python

```powershell
# Создание виртуального окружения
python -m venv .venv

# Активация (Windows PowerShell)
.\.venv\Scripts\activate

# Активация (Linux/macOS)
source .venv/bin/activate
```

### Установка зависимостей

**Установка PyTorch с поддержкой CUDA 12.4:**

```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

**Установка основных библиотек:**

```powershell
pip install \
    langchain==0.3.12 \
    langchain-community==0.3.12 \
    langchain-ollama \
    langchain-huggingface \
    faiss-cpu \
    sentence-transformers \
    streamlit \
    streamlit-extras \
    pypdf \
    python-docx \
    python-dotenv \
    loguru
```

### Конфигурация

Параметры работы системы задаются в `config.yaml`:

```yaml
# Путь к директории с исходными документами для индексации
data_path: "data/raw/math_dataset"

# Модель для создания векторных представлений текста
embedding_model: "intfloat/multilingual-e5-base"
embedding_device: "cuda"

# Параметры разбиения текста (Chunking)
chunk_size: 800       # Символов в одном фрагменте
chunk_overlap: 150    # Перекрытие для сохранения контекста
search_k: 5           # Релевантных фрагментов на запрос
```

## Запуск приложения

```powershell
# 1. Разместите документы в директорию data/raw/math_dataset
# 2. Запустите приложение
streamlit run app.py

# 3. В веб-интерфейсе (http://localhost:8501)
#    нажмите "Пересобрать базу знаний"
```

**При первом запуске:** будет загружена модель эмбеддингов (~1.1 ГБ).

## Структура проекта

```
edu_rag_project/
├── .venv/                      # Виртуальное окружение Python
├── data/
│   ├── raw/                    # Исходные документы для индексации
│   └── processed/              # Векторный индекс FAISS
├── src/
│   ├── config.py               # Загрузка конфигурации
│   ├── document_loader.py      # Парсинг документов (PDF, DOCX и т.д.)
│   ├── rag_chain.py            # Логика RAG и управление историей
│   └── vector_store.py         # Работа с векторным хранилищем
├── app.py                      # Веб-интерфейс (Streamlit)
├── config.yaml                 # Конфигурационный файл
├── Modelfile                   # Спецификация модели Ollama
├── download_data.py            # Утилита для загрузки датасетов
└── README.md                   # Документация
```

## Устранение неполадок

### CUDA not available / Switching to CPU

**Причина:** Установлена версия PyTorch только для CPU.

**Решение:**

```powershell
pip uninstall torch -y
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

### ModuleNotFoundError: No module named 'langchain.chains'

**Причина:** Несовместимость версий или некорректная установка.

**Решение:** Убедитесь, что используется виртуальное окружение `.venv` и установлены указанные версии библиотек.

### CUDA out of memory

**Причина:** Нехватка видеопамяти (VRAM).

**Решение:** Уменьшите параметры в `config.yaml`:

```yaml
chunk_size: 512          # Вместо 800
```

Или в `Modelfile`:

```
parameter num_ctx 4096   # Вместо большего значения
```

### Total files loaded: 0

**Причина:** Неверно указан путь к данным.

**Решение:** Проверьте параметр `data_path` в `config.yaml`. Путь должен указывать на конечную директорию с файлами:

```yaml
data_path: "data/raw/math_dataset"  # Должны быть файлы .pdf, .docx и т.д.
```

## Лицензия

[Укажите лицензию проекта]

---

**Поддержка и вклад:** [Контактная информация / ссылки на репозиторий]