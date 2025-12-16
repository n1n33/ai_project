import streamlit as st
import time
from src.config import load_config
from src.document_loader import DocumentLoader
from src.vector_store import VectorDB
from src.rag_chain import get_rag_chain

# Загрузка настроек
config = load_config()

st.set_page_config(
    page_title=config['app_name'],
    page_icon="🎓",
    layout="wide"
)

# Стилизация
st.markdown("""
<style>
    .stChatMessage {border-radius: 10px; padding: 10px;}
    .stSpinner {text-align: center;}
</style>
""", unsafe_allow_html=True)

st.title(f"🎓 {config['app_name']}")

# Инициализация истории чата
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- САЙДБАР (Настройки и База) ---
with st.sidebar:
    st.header("⚙️ Управление базой знаний")

    st.info(f"LLM: {config['llm_model']}\nDevice: {config['embedding_device'].upper()}")

    if st.button("🔄 Пересобрать базу знаний", type="primary"):
        with st.status("Обновление индекса...", expanded=True) as status:
            st.write("📂 Чтение файлов...")
            loader = DocumentLoader(config['data_path'])
            docs = loader.load_documents()

            if docs:
                st.write(f"🧩 Разбиение на чанки и векторизация ({len(docs)} док.)...")
                vdb = VectorDB(config)
                vdb.create_vector_db(docs)
                status.update(label="Готово!", state="complete", expanded=False)
                st.success(f"База обновлена! Всего документов: {len(docs)}")
            else:
                status.update(label="Ошибка", state="error")
                st.error("Файлы не найдены в папке data/raw")

    st.divider()
    st.markdown("### Загруженные файлы:")
    # Простое отображение списка файлов, если база существует
    try:
        import os

        files = os.listdir(config['data_path'])
        if files:
            for f in files:
                st.caption(f"📄 {f}")
        else:
            st.caption("Папка пуста")
    except:
        pass

# --- ЧАТ ---
# Отрисовка истории
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Ввод пользователя
if prompt := st.chat_input("Задайте вопрос по лекциям или документам..."):
    # Добавляем в историю
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Генерация ответа
    with st.chat_message("assistant"):
        vdb = VectorDB(config)
        rag_chain = get_rag_chain(config, vdb)

        if rag_chain:
            start_time = time.time()
            with st.spinner("Qwen изучает материалы..."):
                try:
                    response = rag_chain.invoke({"input": prompt})
                    answer = response['answer']
                    context = response['context']

                    # Вывод ответа
                    st.markdown(answer)

                    # Блок с источниками (Expander)
                    with st.expander("📚 Использованные источники"):
                        seen_sources = set()
                        for doc in context:
                            source = doc.metadata.get('source_file', 'Неизвестный файл')
                            page = doc.metadata.get('page', 'Неизвестная стр.')  # Для PDF

                            # Формируем уникальную строку источника
                            source_info = f"{source}"
                            if 'page' in doc.metadata:
                                source_info += f" (стр. {page + 1})"

                            if source_info not in seen_sources:
                                st.markdown(f"- **{source_info}**")
                                # Можно показать фрагмент текста, если нужно:
                                # st.caption(doc.page_content[:200] + "...")
                                seen_sources.add(source_info)

                    elapsed = time.time() - start_time
                    st.caption(f"⏱️ Время генерации: {elapsed:.2f} сек.")

                    # Сохраняем ответ ассистента в историю
                    st.session_state.messages.append({"role": "assistant", "content": answer})

                except Exception as e:
                    st.error(f"Произошла ошибка при генерации: {e}")
        else:
            st.warning("⚠️ База знаний не найдена. Пожалуйста, нажмите 'Пересобрать базу знаний' в меню слева.")