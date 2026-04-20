# Importing the libraries
import streamlit as st
import os
from dotenv import load_dotenv
from tavily import TavilyClient
from groq import Groq
from fpdf import FPDF

# 1. SETUP: Must be the first Streamlit command
st.set_page_config(page_title='Klugekopf TechBridge AI Agent', page_icon='🤖')

# Loading api_keys
load_dotenv()
def get_secret(key):
    try:
        # Check Streamlit Cloud secrets first, then local .env
        return st.secrets[key] if key in st.secrets else os.getenv(key)
    except Exception:
        return os.getenv(key)

TAVILY_API_KEY = get_secret('TAVILY_API_KEY')
GROQ_API_KEY = get_secret('GROQ_API_KEY')

# 2. SIDEBAR ORGANIZATION
st.sidebar.title("🛠️ Agent Settings")

# Persona Selector
mode = st.sidebar.selectbox(
    "Select Agent Mode:",
    ["General Research & Blog", "LinkedIn Post Generator", "Product Researcher"]
)

# Technical options
with st.sidebar.expander("Search Options"):
    search_depth = st.radio("Search Depth:", ["basic", "advanced"], index=1)
    max_results = st.slider("Max Results:", 1, 10, 5)

st.sidebar.divider()

# Initialise the GROQ Client
client = Groq(api_key=GROQ_API_KEY)

# 3. MAIN INTERFACE
st.title('🤖 Klugekopf TechBridge AI Agent')
st.info(f"Currently acting as your **{mode}**.")

# Input topic
topic = st.text_input("What would you like to research today?", placeholder="e.g., AI in Project Management")

# 4. EXECUTION LOGIC (Everything inside this block only runs on click)
if st.button("Generate Output"):
    if not topic:
        st.warning("Please enter a topic first!")
    else:
        with st.spinner(f"Agents are processing {mode}..."):
            # STEP 1: Research (Tavily)
            tavily = TavilyClient(api_key=TAVILY_API_KEY)
            search_response = tavily.search(query=topic, search_depth=search_depth, max_results=max_results)
            research_text = "\n".join([r['content'] for r in search_response['results']])
            
            if not research_text:
                st.error("No research data found. Try a different topic.")
            else:
                # STEP 2: Persona Logic
                prompts = {
                    "General Research & Blog": f"""
                    You are a team of 3 AI agents:
                    1. Researcher - You have found this information: {research_text}
                    2. Content Creator - Write a detailed blog post about: {topic}
                    3. SEO Optimizer - Optimize the blog post with keywords, meta description and SEO tips
                    
                    Please provide:
                    - A full blog post
                    - Meta description
                    - Recommended keywords
                    - SEO tips
                    """,
                    
                    "LinkedIn Post Generator": f"""
                    ROLE: Content Strategist. 
                    TASK: Transform this research into a viral, "Humanized" LinkedIn post about {topic}.
                    DATA: {research_text}
                    
                    INSTRUCTION: Use a professional yet conversational tone. 
                    Please provide:
                    - A punchy hook
                    - 3-5 key value points
                    - A call to action (CTA)
                    - Relevant hashtags
                    """,
                    
                    "Product Researcher": f"""
                    ROLE: E-commerce Market Analyst. 
                    TASK: Conduct deep-dive product research on: {topic}.
                    DATA: {research_text}
                    
                    Please provide:
                    - Market Demand analysis
                    - Competitor Insights
                    - Target Audience needs
                    - eBay Optimization (Suggested title and 5 key selling points)
                    """
                }

                # STEP 3: Generation (Groq)
                final_prompt = prompts[mode]
                
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": final_prompt}],
                    temperature=0.7
                )
                
                output = completion.choices[0].message.content
                
                # STEP 4: DISPLAY RESULTS
                st.success("Task Completed!")
                st.markdown("---")
                st.markdown(output)
                
                # STEP 5: PDF GENERATION (Inside the button click)
                try:
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=12)
                    
                    # Title
                    pdf.set_font("Arial", 'B', 16)
                    pdf.cell(200, 10, txt=f"Analysis Report: {topic}", ln=True, align='C')
                    pdf.ln(10)
                    
                    # Content
                    pdf.set_font("Arial", size=11)
                    clean_text = output.encode('latin-1', 'ignore').decode('latin-1')
                    pdf.multi_cell(0, 10, txt=clean_text)
                    
                    pdf_bytes = pdf.output(dest='S').encode('latin-1')
                    
                    # Show Download Button in Sidebar
                    st.sidebar.success("✅ File Ready!")
                    st.sidebar.download_button(
                        label="📥 Download as PDF",
                        data=pdf_bytes,
                        file_name=f"{mode.replace(' ', '_')}_{topic.replace(' ', '_')}.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.sidebar.error("PDF generation error. Results are still visible above.")