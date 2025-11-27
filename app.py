import streamlit as st
import os
import zipfile
import tempfile
import shutil

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

st.set_page_config("Codebase Teacher", layout='wide')
st.title("Cloud-Based Codebase Teacher")

# api_key = st.sidebar.text_input("Enter Groq API Key", type="password")
# if not api_key:
#     st.info("Please enter a Groq API Key to proceed. Get one at console.groq.com")
#     st.stop()

def process_zip_file(uploaded_zip):
    documents = []
    IGNORE_DIRS = {'venv', 'env', '.git', '__pycache__', 'node_modules', 'etc', 'Include', 'Lib', 'Scripts', 'share'}
    ALLOWED_EXTENSIONS = {'.py', '.js', '.md', '.txt', '.json'}
    
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, 'uploaded.zip')
        print(zip_path)
        with open(zip_path, 'wb') as f:
            f.write(uploaded_zip.getvalue())
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        for dirpath, dirnames, filenames in os.walk(temp_dir):
            dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
            
            for f in filenames:
                file_extension = os.path.splitext(f)[1]
                if file_extension in ALLOWED_EXTENSIONS:
                    print("allowed")
                    full_path = os.path.join(dirpath, f)
                    try:
                        loader = TextLoader(full_path, encoding="utf-8")
                        docs = loader.load()
                        for doc in docs:
                            doc.metadata['file_name'] = f
                            documents.append(doc)
                        print("Some docs loaded")
                    except Exception:
                        continue
    return documents

if 'vectorstore' not in st.session_state:
    st.session_state.vectorstore = None

with st.sidebar:
    st.header("Upload Project")
    uploaded_file = st.file_uploader("Upload Codebase (.zip)", type='zip')
    
    if uploaded_file and st.button("Process Zip"):
        with st.spinner("Analyzing Code..."):
            docs = process_zip_file(uploaded_file)
            st.write(f'Found {len(docs)} files.')
            print(f'Found {len(docs)} files.')
            
            py_splitter = RecursiveCharacterTextSplitter.from_language(
                language='python', chunk_size=2000, chunk_overlap=200
            )
            js_splitter = RecursiveCharacterTextSplitter.from_language(
                language='js', chunk_size=2000, chunk_overlap=200
            )
            generic_splitter = RecursiveCharacterTextSplitter(
                chunk_size=2000, chunk_overlap=200
            )
            
            final_splits = []
            
            for doc in docs:
                file_name = doc.metadata['file_name']
                
                if file_name.endswith('.py'):
                    splits = py_splitter.split_documents([doc])
                    print('py')
                elif file_name.endswith('.js'):
                    splits = js_splitter.split_documents([doc])
                    print('js')
                else:
                    splits = generic_splitter.split_documents([doc])
                    print('generic')
                
                final_splits.extend(splits)
            
            embeddings = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')
            st.session_state.vectorstore = FAISS.from_documents(
                documents=final_splits,
                embedding=embeddings
            )
            
            st.success(f"Processed {len(final_splits)} code chuncks.")

user_input = st.chat_input("Ask a question about the codebase...")

if user_input:
    if not st.session_state.vectorstore:
        st.warning('Please upload a .zip file first.')
    else:
        llm = ChatGroq(api_key=st.secrets['groq_api_key'], model_name='llama-3.3-70b-versatile')
        
        prompt = ChatPromptTemplate.from_template("""
        Answer the question based only on the provided context.
        If the answer isn't in the code say you don't know.
        
        <context>
        {context}
        </context>
        
        Question: {input}
        """)
        
        chain = create_stuff_documents_chain(llm, prompt)
        retriever = st.session_state.vectorstore.as_retriever()
        retrieval_chain = create_retrieval_chain(retriever, chain)
        
        with st.spinner("Thinking..."):
            response = retrieval_chain.invoke({'input': user_input})
            st.write(response['answer'])