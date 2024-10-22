from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma

from .config import RQA_ST_Liyi_Chroma_Config

if __name__ == "__main__":
    persist_directory = RQA_ST_Liyi_Chroma_Config.PERSIST_DIRECTORY
    data_directory = RQA_ST_Liyi_Chroma_Config.ORIGIN_DATA
    loader = DirectoryLoader(data_directory, glob="*.txt", loader_cls=lambda p: TextLoader(p, encoding="utf-8"))

    # Load documentscls
    documents = loader.load()
    print(f"Loaded {len(documents)} documents from {data_directory}")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    split_docs = text_splitter.split_documents(documents)
    print(f"Split into {len(split_docs)} document chunks")

    # Check if split_docs is not empty
    if not split_docs:
        raise ValueError("No documents to embed after splitting. Please check your input data.")

    # Use a valid model identifier from Hugging Face Model Hub
    model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    print(f"Using HuggingFace model: {model_name}")
    embeddings = HuggingFaceEmbeddings(model_name=model_name)

    # Check if embedding model is loaded correctly
    try:
        vectordb = Chroma.from_documents(
            documents=split_docs, embedding=embeddings, persist_directory=persist_directory
        )
    except Exception as e:
        print(f"Error occurred while creating Chroma vector store: {e}")
        raise

    # Persist the vector database
    try:
        vectordb.persist()
        print("Vector database persisted successfully.")
    except Exception as e:
        print(f"Error occurred while persisting vector database: {e}")
