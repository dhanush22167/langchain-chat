from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import tempfile, os, shutil

router = APIRouter()

vector_store = None
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": False},
    cache_folder="/tmp/embeddings"
)

PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are a helpful assistant. Answer the question using ONLY the context below.
If the answer is not in the context, say "I don't have that information in the uploaded document."

Context:
{context}

Question: {question}

Answer:"""
)


class QuestionRequest(BaseModel):
    question: str


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    global vector_store

    if not file.filename.endswith((".pdf", ".txt")):
        raise HTTPException(400, "Only PDF or TXT files supported")

    suffix = ".pdf" if file.filename.endswith(".pdf") else ".txt"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        if suffix == ".pdf":
            loader = PyPDFLoader(tmp_path)
        else:
            loader = TextLoader(tmp_path, encoding="utf-8")

        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(docs)

        if not chunks:
            raise HTTPException(400, "No text could be extracted from the file")

        vector_store = FAISS.from_documents(chunks, embeddings)

        return {
            "status": "success",
            "filename": file.filename,
            "chunks": len(chunks),
            "pages": len(docs)
        }
    finally:
        os.unlink(tmp_path)


@router.post("/ask")
async def ask_question(body: QuestionRequest):
    global vector_store

    if vector_store is None:
        raise HTTPException(400, "Please upload a document first")

    if not body.question.strip():
        raise HTTPException(400, "Question cannot be empty")

    groq_key = os.environ.get("GROQ_API_KEY")
    if not groq_key:
        raise HTTPException(500, "GROQ_API_KEY not configured")

    llm = ChatGroq(
        api_key=groq_key,
        model_name="llama-3.1-8b-instant",
        temperature=0.2,
    )

    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | PROMPT
        | llm
        | StrOutputParser()
    )

    answer = chain.invoke(body.question)

    return {
        "answer": answer,
        "question": body.question,
    }


@router.delete("/reset")
async def reset():
    global vector_store
    vector_store = None
    return {"status": "reset", "message": "Document cleared"}