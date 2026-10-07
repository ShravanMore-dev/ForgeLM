import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

DOCS_DIR = "data/docs"
DB_DIR = "data/vector_db"

def main():
    print(f"--- 1. Scanning for documents in {DOCS_DIR} ---")
    if not os.path.exists(DOCS_DIR) or not os.listdir(DOCS_DIR):
        print("No documents found. Please add files to data/docs/")
        return

    documents = []

    # 1. Load Text files
    txt_loader = DirectoryLoader(DOCS_DIR, glob="**/*.txt", loader_cls=TextLoader)
    documents.extend(txt_loader.load())

    # 2. Load Markdown files
    md_loader = DirectoryLoader(DOCS_DIR, glob="**/*.md", loader_cls=TextLoader)
    documents.extend(md_loader.load())

    # 3. Load PDF files
    pdf_loader = DirectoryLoader(DOCS_DIR, glob="**/*.pdf", loader_cls=PyPDFLoader)
    documents.extend(pdf_loader.load())

    print(f"Loaded {len(documents)} document(s) across all formats.")

    if not documents:
        print("No valid txt, md, or pdf files found.")
        return

    print("\n--- 2. Chunking documentation ---")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} searchable chunks.")

    print("\n--- 3. Generating Embeddings ---")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    print("\n--- 4. Building FAISS Vector Database ---")
    vector_db = FAISS.from_documents(chunks, embeddings)
    
    vector_db.save_local(DB_DIR)
    print(f"Vector database saved to {DB_DIR}/ successfully!")

if __name__ == "__main__":
    main()