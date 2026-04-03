##local first smart Knowledge Assistant with RAG PIPILINE

An offline(bigger llm obviously better) Retrieval-Augmented Generation system built directly on top of the **Endee C++ Vector Engine**. 

This project is to demonstrates end to end pipeline coding from compiling cpp database engines to deploying highly optimized edge LLMs on my resource contstarint hardware all wrapped in a custom fullstack web interface

##techstack
* **Vector Database:** [Endee](https://github.com/endee-io/endee) (Compiled from source with AVX2/SIMD acceleration).
* **Embeddings:** `sentence-transformers` (`all-MiniLM-L6-v2`) generating 384-dimensional dense vectors locally.
* **LLM Generation:** Qwen 2.5 (0.5B parameters) served via Ollama.
* **Backend Orchestration:** Python (FastAPI, Requests, Regex).
* **Frontend UI:** Vanilla HTML/CSS/JS.

-----

##Challenges and solution i came up with

To build this system on a highly constrained Linux environment (< 3GB available disk space and CPU-only processing with no GPU), several architectural pivots and low-level optimizations were required:

###1-hardware constrained llm dev
even standard lightweight local models like Mistral 7B require mopre than 4 gb of storage and high RAM overhead so to respect this system limits without crashing my machine while maintaining RAG capabilities what i did was to use **Qwen 2.5: 0.5B**. probably like 500MB edge model that provides fast inference on a CPU while remaining coherent enough to extract accurate answers from highly specific retrieved context

###2-cpp api 
instead of relying on highlevel py wrapper i integrated directly with Endee's Cpp HTTP API and by analyzing the Endee source code (`src/main.cpp`) for few 60s line depth i mapped the exact JSON schemas required by the engine coded bookish lol and identified mandatory index parameters (`dim: 384`, `space_type: "cosine"`) and handled stringified metadata payloads (`"meta": json.dumps(...)`) to prevent cpp strict-type crashes and also successfully bypassed authorization middleware blocks by identifying open mode configurations

### 3.regex i build
for fast retrieval the Endee search endpoint returns a custom binary wrapped text stream rather than standard HTTP JSOn which crashes the standard python decoders (`requests.json()`) upon hitting the binary characters.so to solve this i created a custom Regex extraction layer (`re.findall(r'\{"text":\s*".*?"\}', res.text)`) to extract the metadata JSON blocks from the raw binary to prevent the decode failures

-----

##how to run on local setup

### requirements
* Linux
* [Ollama](https://ollama.com/) installed or anyother.. this process took the longest to wasting my time
* cpp build tools CMake and libssl-dev
```bash
1.start db engine
Navigate to the root `endee` directory, ensure it is built, and start the listener: bash run.sh

(Runs on http://localhost:8080)
2.Start the LLM Engine

In a new terminal, ensure the Ollama service is running and pull the lightweight model:
Bash

ollama run qwen2:0.5b

(Runs on http://localhost:11434)
3.Launch the Full-Stack RAG Application

In a third terminal, activate your Python environment, install the web server dependencies, and start the API:
Bash

cd rag_app
source venv/bin/activate
pip install fastapi uvicorn pydantic sentence-transformers requests
python server.py

4.Open the Web Interface

Once the server indicates the database is loaded, open your web browser and navigate to:
http://localhost:3000

You can now chat directly with the offline RAG pipeline via UI

