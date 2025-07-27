IUB UniVerse
Project Overview and Objective
IUB UniVerse is an information hub designed for Independent University, Bangladesh (IUB). It provides a centralized platform for students, faculty, and staff to access various university-related information, including academic calendars, news, events, notices, research analytics, and a chatbot for answering queries. The objective is to make university information easily accessible and interactive, enhancing the user experience through a modern web interface and AI-powered assistance.
System Architecture
The system consists of two main components:

Backend API (main.py): Built with FastAPI, this component handles data loading from JSON files, sets up a Retrieval-Augmented Generation (RAG) pipeline for the chatbot, and exposes endpoints to access university data.

Frontend Application (app.py): Developed with Streamlit, this component provides a user-friendly web interface to interact with the backend API, displaying information in a structured and visually appealing manner.


The backend uses LangChain for the RAG pipeline, Pinecone for vector storage, HuggingFace for embeddings, and Groq for language model inference. The frontend integrates with the backend via HTTP requests to fetch and display data.
Setup Guide

Clone the repository:
git clone <repository_url>
cd <repository_directory>


Install required packages:
Ensure you have Python 3.8+ installed. Create a virtual environment and install dependencies:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

The requirements.txt should include:
fastapi
uvicorn
streamlit
langchain
pinecone-client
huggingface-hub
groq
pydantic
requests
pandas
plotly


Set up environment variables:
Create a .env file in the root directory with:
PINECONE_API_KEY=your_pinecone_api_key
GROQ_API_KEY=your_groq_api_key
HF_TOKEN=your_huggingface_token

Obtain these keys from Pinecone, Groq, and HuggingFace.

Run the FastAPI server:
uvicorn main:app --host 0.0.0.0 --port 8000


Run the Streamlit app:
In another terminal:
streamlit run app.py


Access the application:
Open your browser and navigate to http://localhost:8501.


Used Tools, Libraries, Packages



Tool/Library
Purpose



Streamlit
Web framework for building the frontend interface


FastAPI
Web framework for building the backend API


Uvicorn
ASGI server to run the FastAPI application


LangChain
Framework for building applications with LLMs, used for the RAG pipeline


Pinecone
Vector database for storing and retrieving document embeddings


HuggingFace
Provides pre-trained models for embeddings


Groq
Platform for running language models


Pydantic
Data validation and settings management


Requests
HTTP library for making API calls


Pandas
Data manipulation and analysis


Plotly
Interactive graphing library


Sample Queries and Output
Chatbot Query

Query: "What are the admission requirements for undergraduate programs?"
Output: "The admission requirements for undergraduate programs at IUB include a minimum GPA of 3.0 in SSC and HSC, passing the admission test, and submitting necessary documents. For more details, please visit the official university website."

API Endpoint

GET /events

Output:
[
  {
    "title": "Orientation Program",
    "date": "2025-08-15",
    "description": "Welcome event for new students."
  },
  ...
]



API Documentation
The backend API provides the following endpoints:



Endpoint
Method
Description



/
GET
Welcome message


/chat
POST
Send a query to the chatbot


/events
GET
List of upcoming events


/news
GET
List of latest news articles


/notices
GET
List of current notices


/research/funding-by-year
GET
Research funding by year


/calendar
GET
Full academic calendar


/calendar/{month}
GET
Events for a specific month


/calendar/events/type/{event_type}
GET
Events by type (e.g., academic, exam)


/calendar/upcoming
GET
Upcoming academic events


/calendar/integrated/{month}
GET
Integrated view for a month


/calendar/integrated/all
GET
Complete integrated calendar


For detailed usage and parameters, refer to the API documentation at http://localhost:8000/docs when the server is running.
Evaluation Matrix
To assess the system's performance, consider the following metrics:



Metric
Description
Measurement Method



Response Accuracy
How accurately the chatbot answers queries based on provided documents
User testing, comparison with ground truth


Retrieval Relevance
Relevance of document chunks retrieved for a query
Precision/recall of retrieved chunks


Response Time
Time taken to process a query and return a response
System monitoring, average latency


User Satisfaction
User feedback on usefulness and accuracy
Surveys, user ratings


These metrics can be gathered through user testing, automated evaluations, or system monitoring.
Design Decisions

Text Extraction Method:

Library Used: UnstructuredPDFLoader for PDFs and JSONLoader for JSON files.
Reason: These libraries, part of LangChain, are designed to handle various document formats efficiently, making them suitable for processing university data.
Challenges: PDFs can have complex layouts, which may lead to formatting issues during text extraction. UnstructuredPDFLoader is generally robust but may struggle with highly unstructured PDFs (e.g., those with images or tables).


Chunking Strategy:

Strategy: Character-based splitting with RecursiveCharacterTextSplitter, chunk_size=1000, chunk_overlap=100.
Reason: This approach divides text into manageable sizes for embedding models while maintaining context through overlapping chunks. It is effective for semantic retrieval as it preserves meaning across chunk boundaries, ensuring relevant information is not split inappropriately.
Why It Works: The overlap helps retain context, and the chunk size balances computational efficiency with semantic coherence.


Embedding Model:

Model Used: sentence-transformers/all-mpnet-base-v2 from HuggingFace.
Reason: This model is well-regarded for generating high-quality sentence embeddings that capture semantic meaning, making it suitable for retrieval tasks in a university context.
How It Works: The model maps sentences to dense vectors in a high-dimensional space, where semantically similar sentences are closer together, enabling effective similarity searches.


Query and Chunk Comparison:

Method: Similarity search using Pinecone’s vector database, likely employing cosine similarity.
Reason: Cosine similarity is a standard metric for measuring the similarity between embeddings in RAG systems. Pinecone provides scalable and efficient vector search capabilities, ideal for handling large datasets.
Storage Setup: Pinecone’s cloud-based vector store (updated-universe-iub-v3 index) ensures fast retrieval and scalability.


Ensuring Meaningful Comparison:

Approach: The RAG chain retrieves the top 6 most similar chunks and instructs the LLM (llama3-8b-8192 from Groq) to answer based solely on the provided context, avoiding external knowledge.
Handling Vague Queries: If a query is vague or lacks context, the retriever may not find highly relevant chunks, potentially leading to less accurate answers. The LLM is prompted to indicate if information is not available, helping manage user expectations.


Improving Relevance:

Potential Improvements:
Better Chunking: Adjusting chunk sizes or using semantic-based splitting to ensure chunks are more contextually coherent.
Advanced Embedding Models: Utilizing models fine-tuned on university-specific data or larger models for improved semantic capture.
Expanded Knowledge Base: Including more comprehensive and up-to-date documents to cover a wider range of queries.
Query Enhancement: Implementing techniques like query expansion to refine vague queries for better retrieval.
