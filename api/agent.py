import json
import os
import time
import shutil
import subprocess
from contextlib import asynccontextmanager
from threading import Thread
from typing import List, Optional

import torch
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer

tokenizer = None
model = None
vector_db = None


class Message(BaseModel):
    role: str
    content: str


class IncidentQuery(BaseModel):
    instruction: str
    history: Optional[List[Message]] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    global tokenizer, model, vector_db
    print("Starting up: Loading ForgeLM and FAISS Database...")

    if os.path.exists("data/vector_db/index.faiss"):
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vector_db = FAISS.load_local(
            "data/vector_db", embeddings, allow_dangerous_deserialization=True
        )
        print("FAISS Vector Database loaded.")
    else:
        print("WARNING: No Vector DB found. Run ingestion script first.")

    adapter_path = "models/ForgeLM-v1-adapter"
    base_id = "Qwen/Qwen2.5-1.5B"

    tokenizer = AutoTokenizer.from_pretrained(adapter_path)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    base_model = AutoModelForCausalLM.from_pretrained(
        base_id,
        torch_dtype=torch.bfloat16
    ).to("cuda:0")

    model = PeftModel.from_pretrained(base_model, adapter_path)
    model.eval()
    print("ForgeLM is online and ready.")

    yield

    print("Shutting down: Clearing VRAM...")
    del model, tokenizer, vector_db
    torch.cuda.empty_cache()


app = FastAPI(title="ForgeLM RAG Agent API", lifespan=lifespan)


@app.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    """Receives a document from the UI, saves it, and rebuilds the FAISS index."""
    os.makedirs("data/docs", exist_ok=True)
    file_path = os.path.join("data/docs", file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Execute the ML script in the API container where FAISS/LangChain exist
    subprocess.run(["python", "scripts/05_ingest_docs.py"])
    
    # Reload the index into VRAM
    await reload_index()
    
    return {"status": "success", "message": f"{file.filename} vectorized and loaded."}


@app.post("/reload-index")
async def reload_index():
    global vector_db
    try:
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vector_db = FAISS.load_local(
            "data/vector_db", embeddings, allow_dangerous_deserialization=True
        )
        return {"status": "success", "message": "Vector DB reloaded into memory."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/troubleshoot")
async def troubleshoot(query: IncidentQuery):
    start_time = time.time()

    # 1. RAG Retrieval Phase
    retrieved_context = "No specific documentation found in knowledge base."
    if vector_db:
        docs = vector_db.similarity_search(query.instruction, k=2)
        if docs:
            retrieved_context = "\n\n".join([d.page_content for d in docs])

    # 2. Build Formatted Instruction with Prior Conversation History
    full_instruction = ""
    if query.history:
        recent_history = query.history[-4:]
        history_text = "\n".join([
            f"{'User' if m.role == 'user' else 'Assistant'}: {m.content}"
            for m in recent_history
        ])
        full_instruction += f"Previous Conversation Context:\n{history_text}\n\n"

    full_instruction += f"Current Task: {query.instruction}"

    # 3. Native Alpaca-style Prompt Matching the Fine-Tuning Weights
    prompt = (
        "Below is an instruction that describes a task, paired with an input that provides further context. "
        "Write a response that appropriately completes the request.\n\n"
        f"### Instruction:\n{full_instruction}\n\n"
        f"### Context:\n{retrieved_context}\n\n"
        "### Guidelines:\n"
        "- Answer strictly and concisely using the provided Context and standard Linux/Kubernetes operational practices.\n"
        "- If the request is unrelated to IT infrastructure, software engineering, or system operations, or if it asks for non-technical topics (such as cooking, recipes, or general chat), refuse by stating: 'I only handle IT Operations and Site Reliability Engineering queries.'\n"
        "- If asked about a proprietary or custom service not mentioned in the Context, respond with: 'I do not have documentation for that specific service in the current knowledge base.'\n\n"
        "### Response:\n"
    )

    inputs = tokenizer(prompt, return_tensors="pt").to("cuda:0")

    # 4. Streamer & Clean Generation Parameters
    streamer = TextIteratorStreamer(
        tokenizer, skip_prompt=True, skip_special_tokens=True
    )
    generation_kwargs = dict(
        **inputs,
        streamer=streamer,
        max_new_tokens=300,
        do_sample=False, 
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=tokenizer.eos_token_id,
    )

    thread = Thread(target=model.generate, kwargs=generation_kwargs)
    thread.start()

    # 5. SSE Event Generator with Stop-Sequence Safety and Telemetry
    def event_generator():
        # Send RAG Context Payload
        yield f"data: {json.dumps({'type': 'context', 'content': retrieved_context})}\n\n"

        stop_words = ["###", "User:", "Assistant:", "\n\n\n"]
        buffer = ""

        # Send Streamed Text Tokens
        for new_text in streamer:
            if not new_text:
                continue
            
            buffer += new_text
            
            should_stop = False
            for stop in stop_words:
                if stop in buffer:
                    clean_chunk = buffer.split(stop)[0]
                    if clean_chunk:
                        yield f"data: {json.dumps({'type': 'token', 'content': clean_chunk})}\n\n"
                    should_stop = True
                    break
            
            if should_stop:
                break

            yield f"data: {json.dumps({'type': 'token', 'content': new_text})}\n\n"

        # Send Live Hardware Telemetry Payload
        latency = int((time.time() - start_time) * 1000)
        vram_allocated = 0
        if torch.cuda.is_available():
            vram_allocated = round(torch.cuda.memory_allocated(0) / (1024**3), 2)
            
        yield f"data: {json.dumps({'type': 'telemetry', 'latency_ms': latency, 'vram_allocated_gb': vram_allocated})}\n\n"
        
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")