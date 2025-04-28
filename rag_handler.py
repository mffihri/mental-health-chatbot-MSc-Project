"""
RAG (Retrieval Augmented Generation) Module for DeepSeek Chatbot

This module implements RAG functionality to enhance responses by retrieving
relevant context from a knowledge base before generating responses.
"""

import os
import logging
from typing import List, Dict, Any, Optional

# Import Langchain components
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import SKLearnVectorStore
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.document_loaders import WebBaseLoader
    from langchain.schema import Document
    from langchain.prompts import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_ollama import ChatOllama
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("Langchain modules not available. RAG functionality will be disabled.")
    print("To enable, install: pip install langchain langchain_community scikit-learn langchain-ollama sentence-transformers")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RAGHandler:
    """
    Handles Retrieval Augmented Generation for the DeepSeek Chatbot.
    """
    
    def __init__(self, model_name="deepseek-r1:1.5b", temperature=0.2):
        """
        Initialize the RAG Handler.
        
        Args:
            model_name (str): The Ollama model to use
            temperature (float): The temperature for generation
        """
        if not LANGCHAIN_AVAILABLE:
            logger.warning("Langchain modules not available. RAG functionality disabled.")
            self.enabled = False
            return
            
        self.enabled = True
        self.model_name = model_name
        self.temperature = temperature
        self.vectorstore = None
        self.retriever = None
        self.documents = []
        self.llm = None
        self.rag_chain = None
        
        # Initialize the language model
        try:
            self.llm = ChatOllama(
                model=model_name,
                temperature=temperature,
            )
            logger.info(f"Successfully initialized ChatOllama with model {model_name}")
        except Exception as e:
            logger.error(f"Error initializing ChatOllama: {str(e)}")
            self.enabled = False
            
        # Initialize the prompt template
        self.prompt = PromptTemplate(
            template="""You are a supportive mental health assistant.
            Use the following information to answer the user's question accurately and with empathy.
            If the retrieved information doesn't provide an answer, rely on your general knowledge but be transparent about it.
            
            User message: {question}
            
            Retrieved information:
            {context}
            
            Your response should be supportive, compassionate, and helpful. 
            If appropriate, suggest coping strategies or resources while acknowledging the user's feelings.
            """,
            input_variables=["question", "context"],
        )
        
        # Create the chain
        if self.enabled and self.llm:
            self.rag_chain = self.prompt | self.llm | StrOutputParser()
            
    def load_documents(self, documents: List[Dict[str, str]]) -> bool:
        """
        Load documents into the RAG system.
        
        Args:
            documents: List of document dictionaries with 'content' and 'metadata'
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.enabled:
            return False
            
        try:
            # Convert to Langchain Document format
            self.documents = [
                Document(page_content=doc['content'], metadata=doc.get('metadata', {}))
                for doc in documents
            ]
            
            logger.info(f"Loaded {len(self.documents)} documents into RAG handler")
            
            # Process documents
            return self._process_documents()
        except Exception as e:
            logger.error(f"Error loading documents: {str(e)}")
            return False
    
    def _process_documents(self) -> bool:
        """
        Process loaded documents by splitting and creating a vector store.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.documents:
            logger.warning("No documents to process")
            return False
            
        try:
            # Split documents
            text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                chunk_size=500, 
                chunk_overlap=50
            )
            doc_splits = text_splitter.split_documents(self.documents)
            
            # Create embeddings and vector store
            # Using HuggingFaceEmbeddings as a local alternative to OpenAI embeddings
            embeddings = HuggingFaceEmbeddings(
                model_name="all-MiniLM-L6-v2"  # A lightweight embedding model
            )
            
            self.vectorstore = SKLearnVectorStore.from_documents(
                documents=doc_splits,
                embedding=embeddings,
            )
            
            self.retriever = self.vectorstore.as_retriever(k=3)  # Get top 3 results
            
            logger.info(f"Successfully processed {len(doc_splits)} document chunks")
            return True
            
        except Exception as e:
            logger.error(f"Error processing documents: {str(e)}")
            return False
    
    def load_from_urls(self, urls: List[str]) -> bool:
        """
        Load documents from a list of URLs.
        
        Args:
            urls: List of URLs to load
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.enabled:
            return False
            
        try:
            # Load documents from URLs
            docs = []
            for url in urls:
                try:
                    loader = WebBaseLoader(url)
                    url_docs = loader.load()
                    docs.extend(url_docs)
                    logger.info(f"Loaded document from {url}")
                except Exception as e:
                    logger.error(f"Error loading from URL {url}: {str(e)}")
            
            self.documents = docs
            
            # Process the loaded documents
            return self._process_documents()
            
        except Exception as e:
            logger.error(f"Error in load_from_urls: {str(e)}")
            return False
            
    def load_from_files(self, file_paths: List[str]) -> bool:
        """
        Load documents from a list of file paths.
        TO BE IMPLEMENTED BY USER.
        
        Args:
            file_paths: List of file paths to load
            
        Returns:
            bool: True if successful, False otherwise
        """
        # This is a placeholder. The user will need to implement the specific file loading logic
        # based on their file types (PDF, DOCX, TXT, etc.)
        logger.info("load_from_files method needs to be implemented by the user")
        return False
            
    def query(self, question: str) -> Dict[str, Any]:
        """
        Query the RAG system with a question.
        
        Args:
            question: The user's question
            
        Returns:
            Dict containing the answer and retrieved contexts
        """
        if not self.enabled or not self.retriever or not self.rag_chain:
            return {
                "answer": None,
                "context_used": False,
                "error": "RAG system not properly initialized"
            }
            
        try:
            # Retrieve relevant documents
            retrieved_docs = self.retriever.invoke(question)
            
            if not retrieved_docs:
                return {
                    "answer": None, 
                    "context_used": False,
                    "error": "No relevant context found"
                }
                
            # Extract content from retrieved documents
            context = "\n\n".join([doc.page_content for doc in retrieved_docs])
            
            # Generate the answer
            answer = self.rag_chain.invoke({"question": question, "context": context})
            
            return {
                "answer": answer,
                "context_used": True,
                "retrieved_docs": [
                    {"content": doc.page_content, "metadata": doc.metadata}
                    for doc in retrieved_docs
                ]
            }
            
        except Exception as e:
            logger.error(f"Error querying RAG system: {str(e)}")
            return {
                "answer": None,
                "context_used": False,
                "error": str(e)
            }
    
    def is_enabled(self) -> bool:
        """Check if RAG functionality is enabled and ready."""
        return self.enabled and self.retriever is not None and self.rag_chain is not None
