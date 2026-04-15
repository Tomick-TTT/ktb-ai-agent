#Importing the libraries
import streamlit as st
import os
from dotenv import load_dotenv
from tavily import TavilyClient
from groq import Groq

#Loading api_keys
load_dotenv()
def get_secret(key):
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key)

TAVILY_API_KEY = get_secret('TAVILY_API_KEY')
GROQ_API_KEY = get_secret('GROQ_API_KEY')

#initialise the GROQ Client
client = Groq(api_key=GROQ_API_KEY)

#set up the page
st.set_page_config(page_title='Klugekopf TechBridge AI Agent', page_icon='🤖')
st.title('🤖 Klugekopf TechBridge AI Agent')
st.subheader('Researcher | Content Creator | SEO Optimizer')

#input topic
topic = st.text_input('Enter a topic to research and write about:')

#add button to main logic
if st.button('Generate Content'):
    if topic:
        with st.spinner('Agents are working...'):
            tavily = TavilyClient(api_key=TAVILY_API_KEY)
            research = tavily.search(query=topic, search_depth='advanced')
            research_text = '\n'.join([r['content'] for r in research['results']])
               
                
            #Build the Agent Prompt
            prompt = f"""
            You are a team of 3 AI agents:
            1. Researcher - You have found this information: {research_text}
            2. Content Creator - Write a detailed blog post about: {topic}
            3. SEO Optimizer - Optimize the blog post with keywords, meta description and SEO tips
            Please provide:
            - A full blog post
            - Meta description
            - Recommended keywords
            - SEO tips
            """

        response = client.chat.completions.create(
                model='llama-3.3-70b-versatile',
                messages=[{'role': 'user', 'content': prompt}]
            )
        st.success('Done!')
        st.markdown('### Generated Content')
        st.write(response.choices[0].message.content)
    else:
        st.warning('Please enter a topic first!')