:: Local-First Smart Knowledge Assistant (RAG Pipeline)

An offline, privacy-first Retrieval-Augmented Generation (RAG) system built directly on top of the **Endee C++ Vector Engine**. 

This project was developed as a submission for the AI/ML Internship role. It demonstrates end-to-end pipeline engineering, from compiling C++ database engines to deploying highly optimized edge LLMs on resource-constrained hardware.


:: Architecture & Tech Stack

* **Vector Database:** [Endee](https://github.com/endee-io/endee) (Compiled from source with AVX2/SIMD acceleration).
* **Embeddings:** `sentence-transformers` (`all-MiniLM-L6-v2`) generating 384-dimensional dense vectors locally.
* **LLM Generation:** Qwen 2.5 (0.5B parameters) served via Ollama.
* **Orchestration:** Python (Requests, Regex, JSON).

-------------------------

::Engineering Challenges & Solutions

To build this system on a highly constrained Linux environment (< 3GB available disk space and CPU-only processing no GPU) several architectural pivots and low-level optimizations were required:

1. Hardware-Constrained LLM Deployment
Standard local models (like Mistral 7B) requires more than 4gb of storage and high VRAM so to respect system limits while maintaining RAG capabilities i pivoted to **Qwen 2.5: 0.5B** and with thhis 500MB edge model provides fast inference on a CPU while remaining coherent enough to extract answers from highly specific retrieved context

2. C++ API Reverse-Engineering & Integration
Instead of relying on high level Python wrappers i integrated directly with Endee's C++ HTTP API and by analyzing the Endee source code (`src/main.cpp`) of few tenth of lines I mapped the exact JSON schemas required by the engine by first identiftyinh mandatory index parameters (`dim: 384`, `space_type: "cosine"`) and handling stringified metadata payloads (`"meta": json.dumps(...)`) to prevent C++ strict-type crashes then bypassed authorization middleware blocks by identifying open-mode configurations

3. Binary sream passing regex
for fast retrieval endee search endpoint returns a custom binary wrapped text stream rather than standard HTTP JSON for which the sandard py decoders (`requests.json()`) crashed immediately upon hitting the binary characters
so what i did was create a custom regex extraction layer (`re.findall(r'\{"text":\s*".*?"\}', res.text)`) to safely extract the metadata JSON blocks from the raw binary stream bypassing the decode failures

---------------------------------

:: To Run on local setup


### you need ###
* linux environment
* [Ollama](https://ollama.com/) installed (took hella time on my device and also dtried mistral and which also wasted significant time coz my ram wasnt able to contain it anyways)
* C++ build tools (CMake, libssl-dev)


1. Start the Database Engine
Navigate to the root `endee` directory then ensure its built and start the listener:
```bash
bash run.sh

(runs on http://localhost:8080)

2. start the LLM Engine
In a new terminal ensure the Ollama service is running and pull the lightweight model:
Bash

ollama run qwen2:0.5b   (or if you are going to run mistral or any other on hardware constrain you can do pull isolated and then do run)

(Runs on http://localhost:11434)
3.launch the RAG Application

in a third terminal you haveto activate your python environment and start the conversational loop:
Bash

cd rag_app
source venv/bin/activate
pip install -r requirements.txt  # (sentence-transformers, requests)
python test_pipeline.py

Example Usage :
Plaintext

 STARTING RAG PIPELINE TEST

Creating index 'my_docs_v2' in Endee...
 Index ready.

--- Ingesting Documents ---
Inserted chunk 1 into Endee
Inserted chunk 2 into Endee
Inserted chunk 3 into Endee

==================================================
TERMINAL RAG BOT INITIALIZED
Type 'exit' or 'quit' to stop.
==================================================

You: What is the internship stipend?
Searching Endee for context
Found Context
asking local LLM

AI: The internship requires building a RAG system and pays a stipend of ₹20,000 for the first 3 months

might make good UI if i got time

