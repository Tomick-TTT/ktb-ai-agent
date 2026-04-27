# Importing the libraries
import streamlit as st
import os
from dotenv import load_dotenv
from tavily import TavilyClient
from groq import Groq

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
    ["Researcher | Content Creator | SEO Optimizer", "LinkedIn Post Generator", "Product Researcher"]
)

# Initialise the GROQ Client
client = Groq(api_key=GROQ_API_KEY)

# 3. MAIN INTERFACE
st.title('🤖 Klugekopf TechBridge AI Agent')
st.info(f"Currently acting as your **{mode}**.")

# Input topic
topic = st.text_input("What would you like to research today?", placeholder="e.g., AI in Project Management")

# 4. EXECUTION LOGIC
if st.button('Generate Content'):
    if topic:
        with st.spinner('Agents are working...'):
            tavily = TavilyClient(api_key=TAVILY_API_KEY)
            research = tavily.search(query=topic, search_depth='advanced')
            research_text = '\n'.join([r['content'] for r in research['results']])

            if not research_text:
                st.error("No research data found. Try a different topic.")
            else:
                # STEP 2: Persona Logic
                prompts = {
                    "Researcher | Content Creator | SEO Optimizer": f"""
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
                    - eCommerce Optimization (Suggested title and 5 key selling points)
                    """
                }

                # STEP 3: Generation (Groq)
                final_prompt = prompts[mode]
                
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": final_prompt}],
                    temperature=0.7
                )

                # ALL THE DISPLAY AND PDF LOGIC MUST STAY INSIDE THIS 'else' BLOCK
                output = completion.choices[0].message.content
                
                # STEP 4: DISPLAY RESULTS
                st.success("Task Completed!")
                st.markdown("---")
                st.markdown(output)
            