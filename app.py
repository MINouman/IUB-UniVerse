import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from typing import Dict, List, Any

st.set_page_config(
    page_title="IUB UniVerse",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = "http://127.0.0.1:8000"

st.markdown("""
<style>
    .main {
        padding-top: 1rem;
    }
    
    .stApp > header {
        background-color: transparent;
    }
    
    .title-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .title-text {
        color: white;
        font-size: 3rem;
        font-weight: bold;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .subtitle-text {
        color: rgba(255,255,255,0.9); 
        font-size: 1.2rem;
        margin-top: 0.5rem;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    .chat-container {
        background: linear-gradient(145deg, #f8f9ff 0%, #e8f2ff 100%);
        color: #333;
        border-radius: 15px;
        padding: 1.5rem;
        border: 1px solid #e1e8f0;
        box-shadow: 0 5px 20px rgba(0,0,0,0.05);
    }
    
    .news-card, .event-card, .notice-card {
        background: white;
        color: #333;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-left: 4px solid #4CAF50;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .news-card:hover, .event-card:hover, .notice-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
    
    .event-card {
        border-left-color: #FF9800;
    }
    
    .notice-card {
        border-left-color: #f44336;
    }
    
    .calendar-event {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        box-shadow: 0 3px 10px rgba(0,0,0,0.15);
    }

    .calendar-event h4, .calendar-event p {
        color: white;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }
    
    .academic-event {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
    }
    
    .exam-event {
        background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
    }
    
    .holiday-event {
        background: linear-gradient(135deg, #FF9800 0%, #f57c00 100%);
    }
    
    .sidebar-section {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid #e9ecef;
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        text-transform: uppercase;
    }
    
    .status-online {
        background-color: #d4edda;
        color: #155724;
    }
    
    .status-offline {
        background-color: #f8d7da;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300) 
def fetch_data(endpoint: str) -> Dict[str, Any]:
    """Fetch data from API endpoint with caching."""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=10)
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": f"HTTP {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}

def send_chat_message(question: str) -> str:
    """Send chat message to RAG model."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={"question": question},
            timeout=30
        )
        if response.status_code == 200:
            return response.json().get("answer", "No response received.")
        else:
            return f"Error: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Connection error: {str(e)}"

def format_date(date_str: str, input_format: str = "%d %B %Y") -> str:
    """Format date string for display."""
    try:
        date_obj = datetime.strptime(date_str, input_format)
        return date_obj.strftime("%B %d, %Y")
    except:
        return date_str

def check_api_status() -> bool:
    """Check if API is accessible."""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'selected_month' not in st.session_state:
    st.session_state.selected_month = datetime.now().strftime("%B")

st.markdown("""
<div class="title-container">
    <h1 class="title-text">IUB UniVerse</h1>
    <p class="subtitle-text">Independent University, Bangladesh - Information Hub</p>
</div>
""", unsafe_allow_html=True)

api_status = check_api_status()
status_class = "status-online" if api_status else "status-offline"
status_text = "Online" if api_status else "Offline"

st.markdown(f"""
<div style="text-align: center; margin-bottom: 1rem;">
    <span class="status-badge {status_class}">API Status: {status_text}</span>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## Navigation")
    
    selected_section = st.selectbox(
        "Choose Section:",
        ["Dashboard", "Chatbot", "Academic Calendar", "News & Events", "Notices", "Research Analytics"],
        index=0
    )
    
    st.markdown("---")
    
    st.markdown("## Quick Stats")
    
    if api_status:
        events_data = fetch_data("/events")
        news_data = fetch_data("/news")
        notices_data = fetch_data("/notices")
        
        if events_data["success"]:
            st.metric("Upcoming Events", len(events_data["data"]))
        
        if news_data["success"]:
            st.metric("Latest News", len(news_data["data"]))
        
        if notices_data["success"]:
            st.metric("Active Notices", len(notices_data["data"]))
    else:
        st.error("API connection failed")
    

if selected_section == "Dashboard":
    st.markdown("## Dashboard Overview")
    
    if not api_status:
        st.error("API service is currently unavailable. Please check the connection.")
        st.stop()
    
    col1, col2, col3, col4 = st.columns(4)
    
    events_result = fetch_data("/events")
    news_result = fetch_data("/news")
    notices_result = fetch_data("/notices")
    funding_result = fetch_data("/research/funding-by-year")
    
    with col1:
        if events_result["success"]:
            st.metric("Events", len(events_result["data"]), delta="Active")
        else:
            st.metric("Events", "N/A", delta="Error")
    
    with col2:
        if news_result["success"]:
            st.metric("News Articles", len(news_result["data"]), delta="Latest")
        else:
            st.metric("News Articles", "N/A", delta="Error")
    
    with col3:
        if notices_result["success"]:
            st.metric("Notices", len(notices_result["data"]), delta="Current")
        else:
            st.metric("Notices", "N/A", delta="Error")
    
    with col4:
        if funding_result["success"] and isinstance(funding_result["data"], list):
            total_funding = sum([item.get("total_funding", 0) for item in funding_result["data"]])
            st.metric("Research Funding", f"৳{total_funding:,.0f}", delta="Total")
        else:
            st.metric("Research Funding", "N/A", delta="Error")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Recent News")
        if news_result["success"]:
            for news in news_result["data"][:3]:
                st.markdown(f"""
                <div class="news-card">
                    <h4>{news.get('title', 'No Title')}</h4>
                    <p><small>{format_date(news.get('date', ''))}</small></p>
                    <p>{news.get('description', 'No description available.')[:100]}...</p>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Upcoming Events")
        if events_result["success"]:
            for event in events_result["data"][:3]:
                st.markdown(f"""
                <div class="event-card">
                    <h4>{event.get('title', 'No Title')}</h4>
                    <p><small>{format_date(event.get('date', ''))}</small></p>
                    <p><small>{event.get('location', 'Location TBA')}</small></p>
                    <p>{event.get('description', 'No description available.')[:100]}...</p>
                </div>
                """, unsafe_allow_html=True)

elif selected_section == "Chatbot":
    st.markdown("## AI University Assistant")
    
    if not api_status:
        st.error("Chatbot service is currently unavailable.")
        st.stop()
    
    st.markdown("""
    <div class="chat-container">
        <p>Hello! I'm your IUB AI assistant. Ask me anything about:</p>
        <ul>
            <li>Academic programs and courses</li>
            <li>University policies and procedures</li>
            <li>Campus facilities and services</li>
            <li>Admission requirements</li>
            <li>Faculty information</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        for i, (question, answer) in enumerate(st.session_state.chat_history):
            st.markdown(f"""
            <div style="background: #e3f2fd; color: #333; padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
                <strong>You:</strong> {question}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="background: #f1f8e9; color: #333; padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
                <strong>Assistant:</strong> {answer}
            </div>
            """, unsafe_allow_html=True)
        
        # Chat input
        with st.form("chat_form", clear_on_submit=True):
            user_question = st.text_input("Ask your question:", placeholder="Type your question here...")
            col1, col2 = st.columns([1, 4])
            
            with col1:
                submitted = st.form_submit_button("Send 📤", use_container_width=True)
            
            if submitted and user_question:
                with st.spinner("🤔 Thinking..."):
                    response = send_chat_message(user_question)
                    st.session_state.chat_history.append((user_question, response))
                    st.rerun()

elif selected_section == "Academic Calendar":
    st.markdown("## Academic Calendar")
    
    if not api_status:
        st.error("Calendar service is currently unavailable.")
        st.stop()
    
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_month = st.selectbox("Select Month:", months, index=months.index(st.session_state.selected_month))
    
    with col2:
        view_type = st.selectbox("View Type:", ["Monthly", "Upcoming Events", "By Event Type"])
    
    if view_type == "Monthly":
        calendar_data = fetch_data(f"/calendar/{selected_month}")
        
        if calendar_data["success"]:
            st.markdown(f"### {selected_month} 2025")
            
            events = calendar_data["data"].get("events", [])
            if events:
                for event in events:
                    event_type = event.get("type", "academic").lower()
                    css_class = f"{event_type}-event" if event_type in ["academic", "exam", "holiday"] else "calendar-event"
                    
                    st.markdown(f"""
                    <div class="calendar-event {css_class}">
                        <h4>{event.get('description', 'No Description Available')}</h4>
                        <p><strong> Date:</strong> {event.get('date', 'TBA')}</p>
                        <p><strong> Type:</strong> {event.get('type', 'Academic').title()}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info(f"No events scheduled for {selected_month} 2025")
        else:
            st.error(f"Could not load calendar for {selected_month}")
    
    elif view_type == "Upcoming Events":
        upcoming_data = fetch_data("/calendar/upcoming")
        
        if upcoming_data["success"]:
            st.markdown("### Upcoming Academic Events")
            
            events = upcoming_data["data"].get("upcoming_events", [])[:10]  # Show first 10
            
            for event in events:
                event_type = event.get("type", "academic").lower()
                css_class = f"{event_type}-event" if event_type in ["academic", "exam", "holiday"] else "calendar-event"
                
                st.markdown(f"""
                <div class="calendar-event {css_class}">
                    <h4>{event.get('title', 'No Title')}</h4>
                    <p><strong> Date:</strong> {event.get('date', 'TBA')}</p>
                    <p><strong> Month:</strong> {event.get('month', 'Unknown')}</p>
                    <p><strong> Type:</strong> {event.get('type', 'Academic').title()}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error("Could not load upcoming events")
    
    else: 
        event_types = ["academic", "exam", "holiday", "registration", "administrative"]
        selected_type = st.selectbox("Select Event Type:", event_types)
        
        type_data = fetch_data(f"/calendar/events/type/{selected_type}")
        
        if type_data["success"]:
            st.markdown(f"### {selected_type.title()} Events")
            st.info(f"Found {type_data['data']['count']} {selected_type} events")
            
            events = type_data["data"].get("events", [])
            
            for event in events:
                css_class = f"{selected_type}-event" if selected_type in ["academic", "exam", "holiday"] else "calendar-event"
                
                st.markdown(f"""
                <div class="calendar-event {css_class}">
                    <h4>{event.get('title', 'No Title')}</h4>
                    <p><strong> Date:</strong> {event.get('date', 'TBA')}</p>
                    <p><strong> Month:</strong> {event.get('month', 'Unknown')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error(f"Could not load {selected_type} events")

elif selected_section == "News & Events":
    st.markdown("##News & Events")
    
    if not api_status:
        st.error("News & Events service is currently unavailable.")
        st.stop()
    
    tab1, tab2 = st.tabs(["Latest News", "Upcoming Events"])
    
    with tab1:
        news_data = fetch_data("/news")
        
        if news_data["success"]:
            st.markdown("### Recent University News")
            
            for news in news_data["data"]:
                st.markdown(f"""
                <div class="news-card">
                    <h3>{news.get('title', 'No Title')}</h3>
                    <p><strong> Published:</strong> {format_date(news.get('date', ''))}</p>
                    <p>{news.get('description', 'No description available.')}</p>
                    {f"<p><strong> <a href='{news.get('link', '#')}' target='_blank'>Read More</a></strong></p>" if news.get('link') else ""}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error("Could not load news data")
    
    with tab2:
        events_data = fetch_data("/events")
        
        if events_data["success"]:
            st.markdown("### Upcoming University Events")
            
            for event in events_data["data"]:
                st.markdown(f"""
                <div class="event-card">
                    <h3>{event.get('title', 'No Title')}</h3>
                    <p><strong> Date:</strong> {format_date(event.get('date', ''))}</p>
                    <p><strong> Location:</strong> {event.get('location', 'Location TBA')}</p>
                    <p>{event.get('description', 'No description available.')}</p>
                    {f"<p><strong>🔗 <a href='{event.get('link', '#')}' target='_blank'>Learn More</a></strong></p>" if event.get('link') else ""}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error("Could not load events data")

elif selected_section == "Notices":
    st.markdown("##  Official Notices")
    
    if not api_status:
        st.error(" Notices service is currently unavailable.")
        st.stop()
    
    notices_data = fetch_data("/notices")
    
    if notices_data["success"]:
        st.markdown("### Current University Notices")
        
        for notice in notices_data["data"]:
            st.markdown(f"""
            <div class="notice-card">
                <h3>{notice.get('title', 'No Title')}</h3>
                <p><strong> Posted:</strong> {notice.get('post_date', 'Unknown')}</p>
                <p><strong> Category:</strong> {notice.get('category', 'General')}</p>
                <p>{notice.get('description', 'No description available.')}</p>
                {f"<p><strong> <a href='{notice.get('link', '#')}' target='_blank'>View Notice</a></strong></p>" if notice.get('link') else ""}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.error("Could not load notices data")

elif selected_section == "Research Analytics":
    st.markdown("##  Research Funding Analytics")
    
    if not api_status:
        st.error(" Research analytics service is currently unavailable.")
        st.stop()
    
    funding_data = fetch_data("/research/funding-by-year")
    
    if funding_data["success"] and isinstance(funding_data["data"], list):
        df = pd.DataFrame(funding_data["data"])
        
        if not df.empty:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_funding = df['total_funding'].sum()
                st.metric(" Total Funding", f"৳{total_funding:,.0f}")
            
            with col2:
                avg_funding = df['total_funding'].mean()
                st.metric(" Average/Year", f"৳{avg_funding:,.0f}")
            
            with col3:
                years_count = len(df)
                st.metric(" Years Tracked", years_count)
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_bar = px.bar(
                    df, 
                    x='year', 
                    y='total_funding',
                    title='Research Funding by Year',
                    labels={'total_funding': 'Funding Amount (BDT)', 'year': 'Year'},
                    color='total_funding',
                    color_continuous_scale='viridis'
                )
                fig_bar.update_layout(
                    height=400,
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col2:
                # Line chart
                fig_line = px.line(
                    df, 
                    x='year', 
                    y='total_funding',
                    title='Funding Trend Over Time',
                    labels={'total_funding': 'Funding Amount (BDT)', 'year': 'Year'},
                    markers=True
                )
                fig_line.update_traces(
                    line=dict(color='#667eea', width=3),
                    marker=dict(size=8, color='#764ba2')
                )
                fig_line.update_layout(
                    height=400,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_line, use_container_width=True)
            
            # Data table
            st.markdown("### Detailed Funding Data")
            st.dataframe(
                df.style.format({'total_funding': '৳{:,.0f}'}),
                use_container_width=True
            )
        else:
            st.info("No funding data available for visualization")
    else:
        st.error("Could not load research funding data")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p><strong>IUB UniVerse</strong> | Independent University, Bangladesh</p>
</div>
""", unsafe_allow_html=True)