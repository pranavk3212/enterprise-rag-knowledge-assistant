import streamlit as st

from enterprise_rag.service import EnterpriseRAG

st.set_page_config(page_title="Enterprise Knowledge Assistant", page_icon="📚")
st.title("Enterprise Knowledge Assistant")
st.caption("Answers are generated only from retrieved company documents and include citations.")

if "history" not in st.session_state:
    st.session_state.history = []

question = st.chat_input("Ask about company policies, benefits, or security")
if question:
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        with st.spinner("Searching the knowledge base..."):
            try:
                result = EnterpriseRAG().answer(question)
                st.markdown(result.answer)
                with st.expander("Retrieved evidence"):
                    for source in result.sources:
                        st.markdown(f"**{source.label}**")
                        st.write(source.text)
                st.session_state.history.append((question, result.answer))
            except Exception as error:
                st.error(str(error))

with st.sidebar:
    st.header("Setup")
    st.write("Run `rag ingest` after adding or changing documents.")
    st.write("The default index is stored locally in `data/chroma/`.")
