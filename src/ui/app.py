"""Streamlit UI for Doc Assist."""

import streamlit as st
import requests
import json
import os
import time


# Configure page
st.set_page_config(
    page_title="Doc Assist",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Set API URL
API_URL = os.environ.get("API_URL", "http://localhost:8082")


def call_api(question, top_k):
    """
    Call the Doc Assist API.
    
    Args:
        question: User question
        top_k: Number of documents to retrieve
        
    Returns:
        API response or error message
    """
    try:
        response = requests.post(
            f"{API_URL}/answer",
            json={"question": question, "top_k": top_k},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API error: {str(e)}"}


def format_code(answer):
    """
    Format code blocks in the answer.
    
    Args:
        answer: Answer text
        
    Returns:
        Formatted answer with syntax highlighting
    """
    # Streamlit already handles markdown code blocks well
    return answer


def main():
    """Main Streamlit app."""
    st.title("Doc Assist – Documentation QA")
    st.markdown("""
    Ask questions about Python, NumPy, Pandas, or other libraries to get accurate answers with code examples.
    """)
    
    # Sidebar
    st.sidebar.header("Settings")
    top_k = st.sidebar.slider("Number of passages to retrieve", 1, 10, 5)
    
    # Query input
    query = st.text_input("Ask a question about Python/NumPy/Pandas docs:")
    
    # Submit button
    if st.button("Answer") and query:
        with st.spinner("Thinking..."):
            start_time = time.time()
            result = call_api(query, top_k)
            elapsed_time = time.time() - start_time
            
            if "error" in result:
                st.error(result["error"])
            else:
                # Display answer
                st.markdown("### Answer")
                st.markdown(format_code(result["answer"]))
                
                # Display timing
                st.caption(f"Response time: {elapsed_time:.2f} seconds")
                
                # Display citations/notes if any
                if result["citations"]:
                    st.markdown("### Citations / Notes")
                    for c in result["citations"]:
                        st.info(json.dumps(c))
                
                # Display flags if any
                if result["flags"]:
                    st.markdown("### Flags")
                    for flag in result["flags"]:
                        st.warning(flag)
                
                # Display retrieved contexts
                st.markdown("### Retrieved Contexts")
                for i, (ctx, score) in enumerate([(x[0]["text"], x[1]) for x in result["contexts"]]):
                    with st.expander(f"Context {i+1} (score={score:.3f})"):
                        st.code(ctx)
    
    # Footer
    st.markdown("---")
    st.caption("Doc Assist - Retrieval-Augmented Generation for Software Documentation")


if __name__ == "__main__":
    main()
