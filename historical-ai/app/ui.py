import streamlit as st
import sys
import os
import time

# Add project root to path so we can import app.main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import ask_historical_ai

# Page Config
st.set_page_config(
    page_title="Historical AI (1890)",
    page_icon="📜",
    layout="centered"
)

# Custom CSS for aesthetics
st.markdown("""
    <style>
    .stApp {
        background-color: #f4f1ea;
        color: #2c241b;
        font-family: 'Georgia', serif;
    }
    .main-title {
        color: #4a3b2a;
        font-family: 'Garamond', serif;
        font-weight: bold;
        text-align: center;
        font-size: 3rem;
        margin-bottom: 0px;
        text-shadow: 2px 2px 4px #d3c4a8;
    }
    .subtitle {
        color: #6b5744;
        text-align: center;
        font-style: italic;
        margin-bottom: 30px;
    }
    .warning-box {
        background-color: #e8d0b3;
        padding: 15px;
        border-radius: 5px;
        border: 2px solid #c2a886;
        color: #5c4021;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    /* Streamlit Button Styling */
    .stButton > button {
        background-color: #4a3b2a !important;
        color: #f4f1ea !important;
        border: 2px solid #2c241b !important;
        font-family: 'Courier New', monospace !important;
        font-weight: bold !important;
        font-size: 1.2rem !important;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #6b5744 !important;
        border-color: #4a3b2a !important;
        transform: scale(1.02);
    }
    .stTextArea textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #c2a886 !important;
        font-family: 'Georgia', serif;
    }
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #dfd3c3;
        color: #5c4021;
        text-align: center;
        padding: 15px;
        font-size: 0.9rem;
        border-top: 3px solid #c2a886;
        z-index: 1000;
    }
    </style>
""", unsafe_allow_html=True)

# Header Section
st.markdown("<h1 class='main-title'>Historically Bounded AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Strictly Pre-1900 Knowledge • Offline Execution</p>", unsafe_allow_html=True)

# Warning Notice
st.markdown("""
    <div class='warning-box'>
        ⚠️ NOTICE: This system operates on knowledge available strictly before 31 December 1899.
        Any reference to modern technology, events, or concepts will be refused.
    </div>
""", unsafe_allow_html=True)

# Input Section
query = st.text_area("Enter your inquiry here:", 
                     placeholder="e.g., Explain Darwin's theory of evolution...", 
                     height=100)

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ System Settings")
    mode_selection = st.radio(
        "Operation Mode:",
        ["Mock Mode (Demo)", "Real Mode (GPT-2/Local)"],
        index=0
    )
    
    model_path = "mock"
    if "Real" in mode_selection:
        model_path = st.text_input("HuggingFace Model ID:", value="gpt2")
        st.caption("Note: First run will download the model (~500MB).")
    
    if st.button("Reset System"):
        st.session_state.clear()
        st.rerun()
    
    # Debug Info
    try:
        import torch
        import transformers
        st.success(f"ML Drivers Active (Torch {torch.__version__})")
    except ImportError:
        st.error("ML Drivers Missing! System limited to Mock Mode.")
    
    from app.llm import ML_AVAILABLE
    from app.main import llm
    
    if llm and llm.load_error:
        st.error(f"Model Load Failed: {llm.load_error}")
        st.caption("Falling back to Mock Engine.")
    elif not ML_AVAILABLE:
         st.warning("Internal State: Mock Only")

# Logic
if "history" not in st.session_state:
    st.session_state.history = []

@st.cache_resource(hash_funcs={str: lambda x: x})
def get_backend(selected_model):
    from app.main import initialize_system
    # Force re-init if needed by accessing private globals or just relying on the function
    # For this simple app, we just call it.
    initialize_system(model_path=selected_model)
    return True

# Ensure backend is ready
with st.spinner(f"Initializing 1890 Archives ({model_path})..."):
    get_backend(model_path)

col1, col2, col3 = st.columns([1,2,1])
with col2:
    ask_button = st.button("Consult the Archives", use_container_width=True)

if ask_button and query:
    if len(query.strip()) == 0:
        st.error("Please enter a valid inquiry.")
    else:
        with st.spinner("Searching dusty manuscripts..."):
            result = ask_historical_ai(query)
            st.session_state.last_result = result
            
if "last_result" in st.session_state:
    result = st.session_state.last_result
    # Use container to keep results visible
    res_container = st.container()
    with res_container:
        if result["status"] == "ok":
            st.success("Record Retrieved Successfully")
            st.markdown("### Answer")
            st.write(result["answer"])
            
            if result.get("sources"):
                st.markdown("---")
                st.markdown("**Sources Consulted:**")
                for src in result["sources"]:
                    st.caption(f"• {src}")
                    
        elif result["status"] == "refused":
            st.warning("Inquiry Refused")
            st.markdown(f"**Reason:** {result['answer']}")
            
        else: # Error
            st.error("System Failure")
            st.code(result["answer"])
elif ask_button:
    st.info("Pardon? You haven't asked anything.")

# Footer
st.markdown("""
<div class='footer'>
    Offline System • RAG Architecture • No Internet Access • 1890 Edition
</div>
""", unsafe_allow_html=True)
