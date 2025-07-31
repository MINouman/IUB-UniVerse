# import os
# import sys
# import json
# import re
# from contextlib import asynccontextmanager
# from datetime import datetime
# from collections import defaultdict

# import uvicorn
# from dotenv import load_dotenv
# from fastapi import FastAPI, HTTPException, Request
# from fastapi.responses import JSONResponse
# from langchain_core.output_parsers import StrOutputParser
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.runnables import RunnablePassthrough
# from langchain_groq import ChatGroq
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_pinecone import PineconeVectorStore
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from pinecone import Pinecone, ServerlessSpec
# from pydantic import BaseModel
# from huggingface_hub import InferenceClient

# load_dotenv()

# PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# HF_TOKEN = os.getenv("HF_TOKEN")

# if not PINECONE_API_KEY or not GROQ_API_KEY:
#     raise ValueError("PINECONE_API_KEY and GROQ_API_KEY must be set in the .env file.")

# os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2", "false")
# os.environ["LANGCHAIN_PROJECT"] = "UniVerse-IUB"
# os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")

# INDEX_NAME = "updated-universe-iub-v3"
# EMBEDDING_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
# LLM_MODEL_NAME = "llama3-8b-8192"
# PINECONE_CLOUD = "aws"
# PINECONE_REGION = "us-east-1"

# PDF_RESOURCES_PATH = "pdf_resources"
# JSON_RESOURCES_PATH = "." 

# events_data = []
# news_data = []
# notices_data = []
# research_data = []
# rag_chain = None

# def load_json_data():
#     global events_data, news_data, notices_data, research_data
#     print("Loading dynamic JSON data...")
#     try:
#         with open("iub_events.json", "r") as f:
#             events_data = json.load(f)
#         with open("iub_news_events.json", "r") as f:
#             news_data = json.load(f)
#         with open("iub_notices.json", "r") as f:
#             notices_data = json.load(f)
#         with open("iub_research_projects.json", "r") as f:
#             research_data = json.load(f)
#         print("Successfully loaded all JSON files.")
#     except FileNotFoundError as e:
#         print(f"Error: {e}. Make sure all JSON files are in the correct directory.")
#     except json.JSONDecodeError as e:
#         print(f"Error decoding JSON: {e}")


# def load_and_split_documents():
#     from langchain_community.document_loaders import (
#         UnstructuredPDFLoader,
#         JSONLoader,
#     )
#     all_docs = []
#     print("Loading RAG documents...")

#     print("Splitting RAG documents into chunks...")
#     text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
#     return []


# def ingest_data():
#     print("--- Starting RAG Data Ingestion ---")



# def format_docs(docs):
#     return "\n\n".join(doc.page_content for doc in docs)

# def setup_rag_chain():
#     print("Setting up RAG chain...")
#     embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
#     vector_store = PineconeVectorStore.from_existing_index(
#         index_name=INDEX_NAME, embedding=embeddings
#     )
#     retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 6})
#     llm = ChatGroq(model=LLM_MODEL_NAME, temperature=0)
#     prompt_template = """
#     You are a helpful assistant for Independent University, Bangladesh (IUB).
#     Base your answers solely on the content of the provided documents.
#     Do not use external knowledge or make assumptions beyond what is explicitly stated.
#     Provide accurate and concise answers. If the answer cannot be found in the
#     provided context, politely state that the information is not available in the
#     documents and suggest checking the official university website.
#     Context:
#     {context}
#     Question:
#     {user_question}
#     Answer:
#     """
#     prompt = ChatPromptTemplate.from_template(prompt_template)
#     chain = (
#         {"context": retriever | format_docs, "user_question": RunnablePassthrough()}
#         | prompt
#         | llm
#         | StrOutputParser()
#     )
#     print("RAG chain setup complete.")
#     return chain

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """Handles application startup and shutdown events."""
#     global rag_chain
#     load_json_data() 
#     rag_chain = setup_rag_chain()
#     yield
#     print("Shutting down...")


# app = FastAPI(
#     title="IUB UniVerse ",
#     description="Information portal for Independent University, Bangladesh (IUB).",
#     version="1",
#     lifespan=lifespan,
# )


# class ChatRequest(BaseModel):
#     question: str


# def parse_funding_amount(amount_str: str) -> float:
#     if not isinstance(amount_str, str):
#         return 0.0
#     try:
#         cleaned_str = amount_str.lower().replace("bdt", "").replace("usd", "").replace(",", "").strip()
        
#         if 'lac' in cleaned_str or 'lakh' in cleaned_str:
#             value = float(re.sub(r'[^\d.]', '', cleaned_str.replace("lac", "").replace("lakh", "")))
#             return value * 100000
        
#         if 'e' in cleaned_str:
#              return float(cleaned_str)

#         return float(re.sub(r'[^\d.]', '', cleaned_str))
#     except (ValueError, TypeError):
#         return 0.0


# def parse_project_year(timeline_str: str) -> int | None:
#     if not isinstance(timeline_str, str):
#         return None
#     years = re.findall(r'\b\d{4}\b', timeline_str)
#     if years:
#         return int(years[0])
#     return None


# @app.get("/", summary="Root endpoint with a welcome message")
# async def root():
#     return {
#         "message": "Welcome to the UniVerse IUB API. Use the /docs endpoint to explore features."
#     }

# @app.post("/chat", summary="Ask a question to the RAG model")
# async def chat_with_rag(request: ChatRequest):
#     if not rag_chain:
#         raise HTTPException(
#             status_code=503,
#             detail="RAG chain is not available. The application might be starting up.",
#         )
#     if not request.question:
#         raise HTTPException(status_code=400, detail="Question cannot be empty.")
#     try:
#         response = rag_chain.invoke(request.question)
#         return {"answer": response}
#     except Exception as e:
#         print(f"Error invoking RAG chain: {e}")
#         raise HTTPException(
#             status_code=500, detail="An error occurred while processing your request."
#         )

# @app.get("/events", summary="Get a list of upcoming events")
# async def get_events():
#     """Returns a list of all university events. Ideal for a carousel display."""
#     return JSONResponse(content=events_data)


# @app.get("/news", summary="Get the latest news articles")
# async def get_news():
#     sorted_news = sorted(
#         news_data,
#         key=lambda x: datetime.strptime(x.get('date', '1 January 1970'), '%d %B %Y'),
#         reverse=True
#     )
#     return JSONResponse(content=sorted_news)


# @app.get("/notices", summary="Get current notices")
# async def get_notices():
#     valid_notices = [n for n in notices_data if isinstance(n.get('post_date'), str)]
    
#     sorted_notices = sorted(
#         valid_notices,
#         key=lambda x: datetime.strptime(x['post_date'], '%d/%m/%Y'),
#         reverse=True
#     )
#     return JSONResponse(content=sorted_notices)

# @app.get("/research/funding-by-year", summary="Get total research funding aggregated by year")
# async def get_funding_by_year():
#     funding_by_year = defaultdict(float)

#     for project in research_data:
#         if project.get("project_fund_category") == "Funded":
#             year = parse_project_year(project.get("project_timeline", ""))
#             amount = parse_funding_amount(project.get("funding_amount", ""))
            
#             if year and amount > 0:
#                 funding_by_year[year] += amount

#     if not funding_by_year:
#         return {"message": "No valid funding data could be aggregated by year."}

#     chart_data = [
#         {"year": year, "total_funding": round(total, 2)}
#         for year, total in sorted(funding_by_year.items())
#     ]

#     return JSONResponse(content=chart_data)


# if __name__ == "__main__":
#     if len(sys.argv) > 1 and sys.argv[1] == "ingest":
#         ingest_data()
#     else:
#         uvicorn.run(app, host="127.0.0.1", port=8000)

import os
import sys
import json
import re
from contextlib import asynccontextmanager
from datetime import datetime
from collections import defaultdict

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone, ServerlessSpec
from pydantic import BaseModel
from huggingface_hub import InferenceClient

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

if not PINECONE_API_KEY or not GROQ_API_KEY:
    raise ValueError("PINECONE_API_KEY and GROQ_API_KEY must be set in the .env file.")

os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2", "false")
os.environ["LANGCHAIN_PROJECT"] = "UniVerse-IUB"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")

INDEX_NAME = "updated-universe-iub-v3"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
LLM_MODEL_NAME = "llama3-8b-8192"
PINECONE_CLOUD = "aws"
PINECONE_REGION = "us-east-1"

PDF_RESOURCES_PATH = "pdf_resources"
JSON_RESOURCES_PATH = "." 

events_data = []
news_data = []
notices_data = []
research_data = []
calendar_data = []
rag_chain = None

def load_json_data():
    global events_data, news_data, notices_data, research_data, calendar_data
    print("Loading dynamic JSON data...")
    try:
        with open("iub_events.json", "r") as f:
            events_data = json.load(f)
        with open("iub_news_events.json", "r") as f:
            news_data = json.load(f)
        with open("iub_notices.json", "r") as f:
            notices_data = json.load(f)
        with open("iub_research_projects.json", "r") as f:
            research_data = json.load(f)
        
        try:
            with open("academic_calendar_2025.json", "r") as f:
                calendar_data = json.load(f)
        except FileNotFoundError:
            print("Warning: academic_calendar_2025.json not found. Calendar endpoints will be empty.")
            calendar_data = {"year": 2025, "months": {}}
            
        print("Successfully loaded all JSON files.")
    except FileNotFoundError as e:
        print(f"Error: {e}. Make sure all JSON files are in the correct directory.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")


def load_and_split_documents():
    from langchain_community.document_loaders import (
        UnstructuredPDFLoader,
        JSONLoader,
    )
    all_docs = []
    print("Loading RAG documents...")

    print("Splitting RAG documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    return []


def ingest_data():
    print("--- Starting RAG Data Ingestion ---")



def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def setup_rag_chain():
    print("Setting up RAG chain...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vector_store = PineconeVectorStore.from_existing_index(
        index_name=INDEX_NAME, embedding=embeddings
    )
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 6})
    llm = ChatGroq(model=LLM_MODEL_NAME, temperature=0)
    prompt_template = """
    You are a helpful assistant for Independent University, Bangladesh (IUB).
    Base your answers solely on the content of the provided documents.
    Do not use external knowledge or make assumptions beyond what is explicitly stated.
    Provide accurate and concise answers. If the answer cannot be found in the
    provided context, politely state that the information is not available in the
    documents and suggest checking the official university website.
    Context:
    {context}
    Question:
    {user_question}
    Answer:
    """
    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = (
        {"context": retriever | format_docs, "user_question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    print("RAG chain setup complete.")
    return chain

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles application startup and shutdown events."""
    global rag_chain
    load_json_data() 
    rag_chain = setup_rag_chain()
    yield
    print("Shutting down...")


app = FastAPI(
    title="IUB UniVerse ",
    description="Information portal for Independent University, Bangladesh (IUB).",
    version="1",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)


class ChatRequest(BaseModel):
    question: str


def parse_funding_amount(amount_str: str) -> float:
    if not isinstance(amount_str, str):
        return 0.0
    try:
        cleaned_str = amount_str.lower().replace("bdt", "").replace("usd", "").replace(",", "").strip()
        
        if 'lac' in cleaned_str or 'lakh' in cleaned_str:
            value = float(re.sub(r'[^\d.]', '', cleaned_str.replace("lac", "").replace("lakh", "")))
            return value * 100000
        
        if 'e' in cleaned_str:
             return float(cleaned_str)

        return float(re.sub(r'[^\d.]', '', cleaned_str))
    except (ValueError, TypeError):
        return 0.0


def parse_project_year(timeline_str: str) -> int | None:
    if not isinstance(timeline_str, str):
        return None
    years = re.findall(r'\b\d{4}\b', timeline_str)
    if years:
        return int(years[0])
    return None


@app.get("/", summary="Root endpoint with a welcome message")
async def root():
    return {
        "message": "Welcome to the UniVerse IUB API. Use the /docs endpoint to explore features."
    }

@app.post("/chat", summary="Ask a question to the RAG model")
async def chat_with_rag(request: ChatRequest):
    if not rag_chain:
        raise HTTPException(
            status_code=503,
            detail="RAG chain is not available. The application might be starting up.",
        )
    if not request.question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    try:
        response = rag_chain.invoke(request.question)
        return {"answer": response}
    except Exception as e:
        print(f"Error invoking RAG chain: {e}")
        raise HTTPException(
            status_code=500, detail="An error occurred while processing your request."
        )

@app.get("/events", summary="Get a list of upcoming events")
async def get_events():
    """Returns a list of all university events. Ideal for a carousel display."""
    return JSONResponse(content=events_data)


@app.get("/news", summary="Get the latest news articles")
async def get_news():
    sorted_news = sorted(
        news_data,
        key=lambda x: datetime.strptime(x.get('date', '1 January 1970'), '%d %B %Y'),
        reverse=True
    )
    return JSONResponse(content=sorted_news)


@app.get("/notices", summary="Get current notices")
async def get_notices():
    valid_notices = [n for n in notices_data if isinstance(n.get('post_date'), str)]
    
    sorted_notices = sorted(
        valid_notices,
        key=lambda x: datetime.strptime(x['post_date'], '%d/%m/%Y'),
        reverse=True
    )
    return JSONResponse(content=sorted_notices)

@app.get("/research/funding-by-year", summary="Get total research funding aggregated by year")
async def get_funding_by_year():
    funding_by_year = defaultdict(float)

    for project in research_data:
        if project.get("project_fund_category") == "Funded":
            year = parse_project_year(project.get("project_timeline", ""))
            amount = parse_funding_amount(project.get("funding_amount", ""))
            
            if year and amount > 0:
                funding_by_year[year] += amount

    if not funding_by_year:
        return {"message": "No valid funding data could be aggregated by year."}

    chart_data = [
        {"year": year, "total_funding": round(total, 2)}
        for year, total in sorted(funding_by_year.items())
    ]

    return JSONResponse(content=chart_data)


@app.get("/calendar", summary="Get the complete academic calendar")
async def get_calendar():
    """Returns the complete academic calendar for the year."""
    return JSONResponse(content=calendar_data)


@app.get("/calendar/{month}", summary="Get events for a specific month")
async def get_calendar_month(month: str):
    """Returns events for a specific month. Month should be full name (e.g., 'January')."""
    month_title = month.title()
    
    if month_title not in calendar_data.get("months", {}):
        raise HTTPException(
            status_code=404, 
            detail=f"Month '{month_title}' not found. Available months: {list(calendar_data.get('months', {}).keys())}"
        )
    
    return JSONResponse(content={
        "month": month_title,
        "year": calendar_data.get("year", 2025),
        "events": calendar_data["months"][month_title]["events"]
    })


@app.get("/calendar/events/type/{event_type}", summary="Get events by type")
async def get_events_by_type(event_type: str):
    """Returns all events of a specific type (academic, exam, holiday, registration, administrative)."""
    all_events = []
    
    for month_name, month_data in calendar_data.get("months", {}).items():
        for event in month_data.get("events", []):
            if event.get("type") == event_type:
                event_copy = event.copy()
                event_copy["month"] = month_name
                all_events.append(event_copy)
    
    if not all_events:
        available_types = set()
        for month_data in calendar_data.get("months", {}).values():
            for event in month_data.get("events", []):
                available_types.add(event.get("type"))
        
        raise HTTPException(
            status_code=404,
            detail=f"No events found for type '{event_type}'. Available types: {list(available_types)}"
        )
    
    return JSONResponse(content={
        "event_type": event_type,
        "count": len(all_events),
        "events": all_events
    })


@app.get("/calendar/upcoming", summary="Get upcoming academic events")
async def get_upcoming_events():
    """Returns upcoming academic events based on current date."""
    from datetime import datetime, date
    
    current_month = datetime.now().strftime("%B")
    current_day = datetime.now().day
    
    upcoming_events = []
    months_order = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]
    
    # Find current month index
    try:
        current_month_idx = months_order.index(current_month)
    except ValueError:
        current_month_idx = 0
    
    # Get events from current month onwards
    for i in range(len(months_order)):
        month_idx = (current_month_idx + i) % len(months_order)
        month_name = months_order[month_idx]
        
        if month_name in calendar_data.get("months", {}):
            for event in calendar_data["months"][month_name].get("events", []):
                event_copy = event.copy()
                event_copy["month"] = month_name
                upcoming_events.append(event_copy)
    
    return JSONResponse(content={
        "current_date": datetime.now().strftime("%Y-%m-%d"),
        "upcoming_events": upcoming_events[:20]  # Limit to next 20 events
    })


@app.get("/calendar/integrated/{month}", summary="Get integrated calendar with events, news, and notices")
async def get_integrated_calendar_month(month: str):
    """Returns academic calendar events along with related university events, news, and notices for a specific month."""
    month_title = month.title()
    
    if month_title not in calendar_data.get("months", {}):
        raise HTTPException(
            status_code=404, 
            detail=f"Month '{month_title}' not found. Available months: {list(calendar_data.get('months', {}).keys())}"
        )
    
    # Get academic calendar events
    academic_events = calendar_data["months"][month_title]["events"]
    
    # Filter university events, news, and notices by month (basic date matching)
    month_num = datetime.strptime(month_title, "%B").month
    
    # Filter events (assuming they have date fields)
    related_events = []
    for event in events_data:
        if isinstance(event.get('date'), str):
            try:
                event_date = datetime.strptime(event['date'], '%d %B %Y')
                if event_date.month == month_num:
                    event_copy = event.copy()
                    event_copy['source'] = 'university_events'
                    related_events.append(event_copy)
            except ValueError:
                continue
    
    # Filter news
    related_news = []
    for news in news_data:
        if isinstance(news.get('date'), str):
            try:
                news_date = datetime.strptime(news['date'], '%d %B %Y')
                if news_date.month == month_num:
                    news_copy = news.copy()
                    news_copy['source'] = 'news'
                    related_news.append(news_copy)
            except ValueError:
                continue
    
    # Filter notices
    related_notices = []
    for notice in notices_data:
        if isinstance(notice.get('post_date'), str):
            try:
                notice_date = datetime.strptime(notice['post_date'], '%d/%m/%Y')
                if notice_date.month == month_num:
                    notice_copy = notice.copy()
                    notice_copy['source'] = 'notices'
                    related_notices.append(notice_copy)
            except ValueError:
                continue
    
    return JSONResponse(content={
        "month": month_title,
        "year": calendar_data.get("year", 2025),
        "academic_events": academic_events,
        "university_events": related_events,
        "news": related_news,
        "notices": related_notices,
        "total_items": len(academic_events) + len(related_events) + len(related_news) + len(related_notices)
    })


@app.get("/calendar/integrated/all", summary="Get complete integrated calendar")
async def get_integrated_calendar():
    """Returns complete calendar with academic events, university events, news, and notices organized by month."""
    integrated_calendar = {
        "year": calendar_data.get("year", 2025),
        "months": {}
    }
    
    months_order = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]
    
    for month_name in months_order:
        month_num = datetime.strptime(month_name, "%B").month
        
        # Get academic events
        academic_events = calendar_data.get("months", {}).get(month_name, {}).get("events", [])
        
        # Filter university events
        university_events = []
        for event in events_data:
            if isinstance(event.get('date'), str):
                try:
                    event_date = datetime.strptime(event['date'], '%d %B %Y')
                    if event_date.month == month_num:
                        event_copy = event.copy()
                        event_copy['source'] = 'university_events'
                        university_events.append(event_copy)
                except ValueError:
                    continue
        
        # Filter news
        news_items = []
        for news in news_data:
            if isinstance(news.get('date'), str):
                try:
                    news_date = datetime.strptime(news['date'], '%d %B %Y')
                    if news_date.month == month_num:
                        news_copy = news.copy()
                        news_copy['source'] = 'news'
                        news_items.append(news_copy)
                except ValueError:
                    continue
        
        # Filter notices
        notice_items = []
        for notice in notices_data:
            if isinstance(notice.get('post_date'), str):
                try:
                    notice_date = datetime.strptime(notice['post_date'], '%d/%m/%Y')
                    if notice_date.month == month_num:
                        notice_copy = notice.copy()
                        notice_copy['source'] = 'notices'
                        notice_items.append(notice_copy)
                except ValueError:
                    continue
        
        integrated_calendar["months"][month_name] = {
            "academic_events": academic_events,
            "university_events": university_events,
            "news": news_items,
            "notices": notice_items,
            "total_items": len(academic_events) + len(university_events) + len(news_items) + len(notice_items)
        }
    
    return JSONResponse(content=integrated_calendar)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "ingest":
        ingest_data()
    else:
        uvicorn.run(app, host="127.0.0.1", port=8000)