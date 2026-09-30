import streamlit as st
from backend.gemini_assistant import AssistantError, chat_reply
from utils.theme import inject_css, hero

st.set_page_config(page_title="AI Assistant | GeoXAI-Bore", page_icon="✦", layout="wide")
inject_css()
with st.sidebar:
    st.page_link("app.py", label="Overview")
    st.page_link("pages/6_AI_Assistant.py", label="AI Assistant")

hero("Powered by Gemini", "GeoXAI farmer assistant", "Ask in English or Telugu about your borewell, pump, risk result, or CSV file.")
language_label = st.radio("Answer language", ["English", "తెలుగు"], horizontal=True)
language = "te" if language_label == "తెలుగు" else "en"
st.info("You can use simple words. For high-risk or electrical problems, contact a qualified field technician.")
st.caption("Messages are sent to Gemini. Share a prediction here to discuss it; check AI guidance against field observations.")
if "assistant_messages" not in st.session_state:
    st.session_state.assistant_messages = []
if st.button("Clear chat"):
    st.session_state.assistant_messages = []
    st.rerun()
for message in st.session_state.assistant_messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
if question := st.chat_input("Ask a question"):
    if len(question) > 4000:
        st.error("Please keep each message under 4,000 characters.")
        st.stop()
    if question.strip():
        messages = st.session_state.assistant_messages + [{"role": "user", "content": question.strip()}]
        with st.chat_message("user"):
            st.write(question)
        try:
            with st.spinner("Thinking…"):
                reply = chat_reply(
                    [{**item, "content": item["content"][:4000]} for item in messages[-19:]],
                    language=language,
                )
            st.session_state.assistant_messages = messages + [{"role": "assistant", "content": reply}]
            st.rerun()
        except AssistantError as error:
            st.error(str(error))
