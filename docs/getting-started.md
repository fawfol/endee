# Endee: High-Performance Open Source Vector Database

**Endee** is a specialized, high-performance vector database built for speed and efficiency — engineered for production AI systems that need to process data at scale.

Never heard of a vector database? No worries — check out our blog where we explain what it is and what you can build with it: [endee.io/blog](https://endee.io/blog)

---

## Let's Get Started

To use Endee, the first step is to start the server. There are 4 ways to do this:

1. **Docker** — pull and run the pre-built image from Docker Hub 
2. **Docker build from source** — build the Docker image yourself from the source code(recommended)
3. **install.sh script** — automated build script for Linux and macOS
4. **Manual CMake build** — full manual control over the build

> **Windows users:** Methods 3 and 4 are not supported on Windows. Docker (Methods 1 or 2) is the only way to run Endee on Windows.

---

## Method 1: Docker

### Prerequisite: Install Docker

That's the only thing you need. Go to [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/) and install Docker Desktop for your OS (Windows, Mac, or Linux).

Once installed, open a terminal and verify it works:

```bash
docker --version
```

---

### Run Endee

```bash
docker run \
  --ulimit nofile=100000:100000 \
  -p 8080:8080 \
  -v ./endee-data:/data \
  --name endee-server \
  --restart unless-stopped \
  endeeio/endee-server:latest
```

That's it. Docker pulls the image automatically if not already present, and Endee starts.

**What each flag means:**

| Flag | Meaning |
|---|---|
| `--ulimit nofile=100000:100000` | Allows the container to open up to 100,000 files simultaneously — databases need this |
| `-p 8080:8080` | Port mapping (`your_machine:container`). Makes the server reachable at `localhost:8080` |
| `-v ./endee-data:/data` | Stores Endee's database files in an `endee-data/` folder in your current directory |
| `--name endee-server` | Names the container so you can reference it easily (e.g. `docker stop endee-server`) |
| `--restart unless-stopped` | Auto-restarts if the container crashes, but not if you manually stop it |
| `-e NDD_AUTH_TOKEN=your_token` | Optional. Protects the server with a token — every client request must include it, otherwise the server rejects it. Omit to run with no authentication. |
| `endeeio/endee-server:latest` | The official pre-built Endee image from Docker Hub |

**Want to store the data in a different folder?** Replace `./endee-data` with any path:

```bash
-v ./endee-data:/data                      # default: stores in an 'endee-data/' folder in the current directory
-v ~/endee-data:/data                      # example: stores in your home directory
-v C:/Users/YourName/endee-data:/data      # example: Windows local drive
-v /Volumes/MyDrive/endee-data:/data       # example: macOS local drive
```

Only change the left side of the `:` — the right side (`/data`) is fixed.

---

### Verify it's running

Open your browser and go to **[http://localhost:8080](http://localhost:8080)** — you should see the Endee dashboard.

---

### Stop the server

```bash
docker stop endee-server
```

Your data stays safe in the folder you configured.

---

### Next steps: Using Endee

Once your server is running, head over to [docs.endee.io/quick-start](https://docs.endee.io/quick-start) to learn how to create indexes, store vectors, and run your first similarity search.

---

## Method 2: Docker Build from Source(Recommended)

Use this if you want to build the image yourself from the source code instead of pulling from Docker Hub.

### Prerequisites

- Docker installed (same as Method 1)
- The repo cloned on your machine

```bash
git clone https://github.com/endee-io/endee.git
cd endee
```

---

### Step 1: Figure out your CPU type

Endee uses special CPU instructions called **SIMD** to run vector searches extremely fast. Different CPUs support different instruction sets, so you need to pick the right one when building.

> Think of it like this: your CPU has built-in shortcuts for doing math on large amounts of data at once. SIMD lets Endee use those shortcuts. Picking the right flag tells the compiler which shortcuts your CPU has.

| Your hardware | Flag to use |
|---|---|
| Mac with M1 / M2 / M3 / M4 chip | `neon` |
| Linux or Windows with Intel or AMD CPU | `avx2` |
| Server-grade Intel Xeon / AMD EPYC | `avx512` |
| ARM server (ARMv9) | `sve2` |

Not sure on Linux? Run this to check:
```bash
lscpu | grep -o 'avx2\|avx512'
```

---

### Step 2: Build the image

**For Intel/AMD (x86_64):**
```bash
docker build \
  --ulimit nofile=100000:100000 \
  --build-arg BUILD_ARCH=avx2 \
  -t endee-oss:latest \
  -f ./infra/Dockerfile \
  .
```

**For Apple Silicon Mac:**
```bash
docker build \
  --ulimit nofile=100000:100000 \
  --build-arg BUILD_ARCH=neon \
  -t endee-oss:latest \
  -f ./infra/Dockerfile \
  .
```

**What each flag means:**

| Flag | Meaning |
|---|---|
| `--ulimit nofile=100000:100000` | Allows the build process to open up to 100,000 files at once. The compiler opens many files during a large C++ build — without this it can fail. |
| `--build-arg BUILD_ARCH=avx2` | Passes a build argument into the Dockerfile. This tells it which CPU instruction set to compile for (`avx2`, `avx512`, `neon`, or `sve2`). |
| `-t endee-oss:latest` | Tags (names) the resulting image as `endee-oss:latest` so you can refer to it by name when running it. |
| `-f ./infra/Dockerfile` | Points Docker to the Dockerfile — the recipe file that describes how to build the image. |
| `.` | The build context — Docker copies all files in the current directory into the build environment so the Dockerfile can access them. |

This will take a few minutes the first time.

---

### Step 3: Run with Docker Compose

```bash
docker compose up -d
```

Docker Compose reads the `docker-compose.yml` in the repo and starts the container using the image you just built.

**What the `docker-compose.yml` configures by default:**


To enable token authentication, open `docker-compose.yml` and set `NDD_AUTH_TOKEN`:
```yaml
environment:
  NDD_AUTH_TOKEN: "your_token"
```

| Setting | Default | What it means |
|---|---|---|
| `image` | `endee-oss:latest` | Uses the image you built in Step 2 |
| `ports: "8080:8080"` | Your machine : container | Makes the server reachable at `localhost:8080` |
| `ulimits: nofile: 100000` | File limit | Allows Endee to open up to 100,000 files at once |
| `NDD_NUM_THREADS: 0` | Thread count | `0` = use all available CPU threads automatically |
| `NDD_AUTH_TOKEN: ""` | Auth token | Empty = no authentication. Set a value to protect the server with a token. |
| `volumes: endee-data:/data` | Persistent storage | Uses a named Docker volume (`endee-data`) to store database files. Docker manages the storage location automatically. |
| `restart: unless-stopped` | Restart policy | Auto-restarts on crash, but not on manual stop |
| `logging max-size: 200m` | Log file size | Each log file capped at 200MB |
| `logging max-file: 5` | Log file count | Keeps at most 5 log files (1GB total) |

---

### Stop the container

```bash
docker compose down
```

---

## Method 3: install.sh Script (Linux / macOS)

This script handles OS detection, dependency installation, and the full build automatically. One command does everything.

### Prerequisites

- Linux or macOS (not supported on Windows)
- Git installed

Clone the repo:

```bash
git clone https://github.com/endee-io/endee.git
cd endee
```

Make the script executable:

```bash
chmod +x ./install.sh
```

### Pick your flags

Before running, you need two things:

**1. Build mode** — what kind of binary to produce:

| Flag | What it does |
|---|---|
| `--release` | Optimized build for production. Use this by default. |
| `--debug_all` | Adds full debug symbols and enables internal logging. Use when debugging crashes or tracing behavior. |
| `--debug_nd` | Enables only Endee's internal logging/timing without slowing down the binary with full debug symbols. |

**2. CPU flag** — same as Method 2, pick the one matching your hardware:

| Your hardware | Flag |
|---|---|
| Mac M1 / M2 / M3 / M4 | `--neon` |
| Linux Intel / AMD | `--avx2` |
| Server-grade Xeon / EPYC | `--avx512` |
| ARMv9 server | `--sve2` |

### Run it

```bash
# Production build on Intel/AMD Linux
./install.sh --release --avx2

# Production build on Apple Silicon Mac
./install.sh --release --neon
```

The script will install all dependencies, compile the binary, and download the frontend automatically.

### Start the server

```bash
chmod +x ./run.sh
./run.sh
```

The server starts at **[http://localhost:8080](http://localhost:8080)**.

You can also pass options:

```bash
./run.sh ndd_data_dir=./my_data          # use a custom data folder
./run.sh ndd_auth_token=your_token       # enable token authentication — every client request must include this token
```

> When `ndd_auth_token` is set, all requests your client makes to the server must include that token in the request header — otherwise the server will reject them. For how to pass the token in your client code, see [docs.endee.io/quick-start](https://docs.endee.io/quick-start).

---

## Method 4: Manual CMake Build

Use this when you want full control over the build — useful if you are integrating Endee into an existing build pipeline or want to run tests.

### Prerequisites

- Linux or macOS
- Clang 19 or newer
- `cmake`, `build-essential`, `libssl-dev`, `libcurl4-openssl-dev`

Clone the repo:

```bash
git clone https://github.com/endee-io/endee.git
cd endee
```

### Step 1: Create the build directory

Make sure you are inside the cloned repo folder (the one that contains `CMakeLists.txt`) before running these:

Then create and enter the build directory:

```bash
mkdir build && cd build
```

### Step 2: Configure with CMake

Pick your SIMD flag (same table as above) and run:

```bash
# Release build for Intel/AMD
cmake -DCMAKE_BUILD_TYPE=Release -DUSE_AVX2=ON ..

# Release build for Apple Silicon
cmake -DCMAKE_BUILD_TYPE=Release -DUSE_NEON=ON ..
```

**Optional debug flags you can add:**

| Flag | What it does |
|---|---|
| `-DDEBUG=ON` | Adds full debug symbols, disables optimizations (`-g3 -O0`) |
| `-DND_DEBUG=ON` | Enables Endee's internal logging and timing output |

Example with debug enabled:

```bash
cmake -DUSE_NEON=ON -DND_DEBUG=ON ..
```

**All compile-time flags reference:**

| Flag | Default | Default behaviour | What passing `-DFLAG=ON` changes |
|---|---|---|---|
| `-DDEBUG=ON` | `OFF` | Release build compiled with `-O3 -ffast-math` for maximum performance | Switches to debug build: disables all optimisations (`-O0`), adds full debug symbols (`-g3`). Use when debugging crashes or stepping through code with a debugger. |
| `-DND_DEBUG=ON` | `OFF` | No internal logging — Endee runs silently | Enables Endee's internal debug logging and operation timing output to stdout. Useful for tracing what the server is doing without a full debug build. |
| `-DND_SPARSE_INSTRUMENT=ON` | `OFF` | No timing data collected for sparse index operations | Adds fine-grained timing instrumentation around sparse index operations. Use to profile and diagnose sparse search performance. |
| `-DND_MDBX_INSTRUMENT=ON` | `OFF` | No timing data collected for MDBX (the embedded key-value store) | Adds timing instrumentation around MDBX read/write calls. Use to profile storage layer bottlenecks. |
| `-DNDD_INV_IDX_STORE_FLOATS=ON` | `OFF` | Sparse index stores values as quantized `fp16` — smaller memory footprint | Stores raw `float32` values in the sparse index instead. Higher numerical precision but doubles the memory used by the sparse index. |
| `-DUSE_AVX2=ON` | `OFF` | Must pick exactly one SIMD flag or the build fails | Compiles with AVX2, FMA, F16C instructions. Target: modern Intel/AMD x86_64 desktops and servers. |
| `-DUSE_AVX512=ON` | `OFF` | Must pick exactly one SIMD flag or the build fails | Compiles with AVX512F, BW, VNNI, FP16, VPOPCNTDQ instructions. Target: server-grade Intel Xeon / AMD EPYC. The binary exits at startup if the CPU does not support all required extensions. |
| `-DUSE_NEON=ON` | `OFF` | Must pick exactly one SIMD flag or the build fails | Compiles with NEON, FP16, DotProd. On Apple Silicon uses `-mcpu=native`; on other ARM uses `-march=armv8.2-a+fp16+dotprod`. |
| `-DUSE_SVE2=ON` | `OFF` | Must pick exactly one SIMD flag or the build fails | Compiles with SVE2, FP16, DotProd (`-march=armv8.6-a+sve2+fp16+dotprod`). Target: ARMv9 servers. |

> **Note:** Exactly one SIMD flag must be set — the build fails if none is provided.

### Step 3: Compile

```bash
make -j$(nproc)
```

`-j$(nproc)` tells make to use all available CPU cores in parallel, speeding up the build.

### Step 4: Run the binary

The compiled binary lands in the `build/` folder. Its name depends on the SIMD flag you used:

| SIMD flag | Binary name |
|---|---|
| `USE_AVX2` | `ndd-avx2` |
| `USE_AVX512` | `ndd-avx512` |
| `USE_NEON` on Linux ARM | `ndd-neon` |
| `USE_NEON` on Mac | `ndd-neon-darwin` |
| `USE_SVE2` | `ndd-sve2` |

A symlink named `ndd` is also created pointing to whichever binary you built.

After `make` finishes, go back to the repo root first:

```bash
cd ..
```

Then run:

```bash
mkdir -p ./data
NDD_DATA_DIR=./data ./build/ndd
```

**What these two lines do:**

`mkdir -p ./data` — creates a folder called `data` inside your repo directory. This is where Endee will store all its database and index files. The `-p` flag means "create it only if it doesn't already exist" — it won't fail if the folder is already there.

`NDD_DATA_DIR=./data ./build/ndd` — this is two things combined into one line:

| Part | What it is |
|---|---|
| `NDD_DATA_DIR=./data` | An environment variable telling Endee where to store its data. `./data` means the `data/` folder in your current directory (the repo root). |
| `./build/ndd` | The compiled server binary. After `make` finishes, the binary lands inside the `build/` folder. `./build/ndd` is a shortcut (symlink) that points to whichever SIMD binary you just built. |


### Enable token authentication (optional)

By default the server runs with no password — anyone who can reach `localhost:8080` can use it. If you want to protect your server with a token, pass `NDD_AUTH_TOKEN` the same way:

```bash
NDD_DATA_DIR=./data NDD_AUTH_TOKEN=your_token ./build/ndd
```

> When `NDD_AUTH_TOKEN` is set, every request your client makes to the server must include that token in the `Authorization` header — otherwise the server will reject it. See [docs.endee.io/quick-start](https://docs.endee.io/quick-start) for how to pass the token in your client code.

The server starts at **[http://localhost:8080](http://localhost:8080)**.

---

### Check server health

```bash
curl http://localhost:8080/api/v1/health
```

### List all indexes

**Without authentication:**
```bash
curl http://localhost:8080/api/v1/index/list
```

**With a token:**
```bash
curl -H "Authorization: your_token" http://localhost:8080/api/v1/index/list
```