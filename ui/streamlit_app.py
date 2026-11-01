
import uuid

import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="HR Multi-Agent Assistant",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 HR Multi-Agent Assistant")
st.caption(
    "Ask about company policies, leave rules, "
    "or submit a leave request."
)


# Initialize session state for this browser session.
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []


with st.sidebar:
    st.subheader("HR Assistant")
    st.write("Available capabilities:")
    st.markdown(
        """
        - 📘 Company policy questions
        - 📅 Leave policy questions
        - 📝 Leave applications
        """
    )

    st.caption("Powered by Ollama, LangGraph, RAG and MCP.")

    if st.button("New conversation", use_container_width=True):
        st.session_state.conversation_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()


# Render previous messages.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Suggested questions.
if not st.session_state.messages:
    st.markdown("### Try asking")
    suggestions = [
        "What are the normal working hours?",
        "How many annual leave days are allowed?",
        "I want to apply for leave.",
    ]

    for suggestion in suggestions:
        if st.button(suggestion, use_container_width=True):
            st.session_state.pending_question = suggestion
            st.rerun()


# Accept either a typed question or a suggested question.
typed_question = st.chat_input(
    "Ask a policy question or request leave..."
)

suggested_question = st.session_state.pop(
    "pending_question", None
)

question = typed_question or suggested_question


if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question,
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Finding the right agent..."):
            try:
                response = requests.post(
                    f"{API_URL}/chat",
                    json={
                        "query": question,
                        "conversation_id": (
                            st.session_state.conversation_id
                        ),
                    },
                    timeout=180,
                )

                response.raise_for_status()
                data = response.json()

                # Keep the ID returned by the backend.
                st.session_state.conversation_id = (
                    data["conversation_id"]
                )

                answer = data.get(
                    "answer",
                    "The assistant returned no answer.",
                )

                st.markdown(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                })

            except requests.exceptions.ConnectionError:
                answer = (
                    "Cannot connect to the HR API. "
                    "Please ensure FastAPI is running on port 8000."
                )
                st.error(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                })

            except requests.exceptions.Timeout:
                answer = (
                    "The request timed out. Please check the "
                    "backend logs and try again."
                )
                st.error(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                })

            except requests.exceptions.RequestException as exc:
                answer = f"Request failed: {exc}"
                st.error(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                })
