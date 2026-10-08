# ForgeLM 🛠️

### AI-Powered Incident Response & Troubleshooting Assistant for DevOps and SRE

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit)](https://streamlit.io/)
[![PyTorch](https://img.shields.io/badge/PyTorch-ROCm-ee4c2c?logo=pytorch)](https://pytorch.org/)
[![AMD ROCm](https://img.shields.io/badge/AMD-ROCm-red?logo=amd)](https://rocm.docs.amd.com/)
[![FAISS](https://img.shields.io/badge/Vector_Store-FAISS-orange)](https://github.com/facebookresearch/faiss)
[![LangChain](https://img.shields.io/badge/Agent-LangChain-green)](https://www.langchain.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/license/mit/)

ForgeLM is an AI-driven incident response and troubleshooting assistant designed for DevOps and Site Reliability Engineering (SRE) teams.

It combines a custom fine-tuned **Qwen 2.5 1.5B** model with **FAISS-based Retrieval-Augmented Generation (RAG)** and **LangChain ReAct agent logic** to provide context-aware, company-specific troubleshooting assistance.

ForgeLM is designed to run locally, allowing sensitive infrastructure information, SOPs, runbooks, and incident context to remain within the organization's environment.

---

## 🚀 Key Features

### 🤖 Fine-Tuned Language Model

ForgeLM uses a custom-tuned **Qwen 2.5 1.5B** model optimized for SRE and incident-response use cases.

The relatively small model size makes local deployment more practical while still providing a capable natural-language interface for troubleshooting workflows.

### 🧠 Retrieval-Augmented Generation

ForgeLM uses **FAISS** as a local vector database for retrieving relevant organizational knowledge.

Supported knowledge sources include:

- Standard Operating Procedures (SOPs)
- Infrastructure runbooks
- Troubleshooting documentation
- Incident-response procedures
- Company-specific operational knowledge

The retrieved context is supplied to the language model to produce more relevant and grounded responses.

### 🔄 ReAct Agent Logic

ForgeLM uses **LangChain** to implement agent-based reasoning.

The agent can:

1. Understand an incident
2. Retrieve relevant runbook information
3. Reason through possible causes
4. Select diagnostic steps
5. Execute simulated backend tools
6. Analyze tool results
7. Continue the investigation
8. Provide remediation-oriented guidance

### ⚡ AMD ROCm Optimized Inference

ForgeLM is designed to use the **AMD ROCm** runtime instead of relying exclusively on CUDA.

The project is pre-configured with modern AMD hardware such as the **AMD Radeon RX 9060 XT** in mind.

The inference stack uses a ROCm-enabled PyTorch build and can be adapted for NVIDIA CUDA environments.

> On the first AMD deployment, MIOpen/Triton may JIT-compile GPU kernels. This initial compilation can take approximately 5–15 minutes.

### 🧩 Microservices Architecture

ForgeLM separates the application into independent services:

- **Backend:** FastAPI inference engine
- **Frontend:** Streamlit user interface
- **Model:** Fine-tuned Qwen 2.5 1.5B
- **RAG:** FAISS vector database
- **Agent:** LangChain ReAct architecture
- **Deployment:** Docker and Docker Compose

---

## 🏗️ Architecture

```text
                    ┌─────────────────────┐
                    │    Streamlit UI     │
                    │  Chat + Tool Logs   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      FastAPI        │
                    │   Inference API     │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
        ┌──────────┐     ┌───────────┐    ┌────────────┐
        │ Qwen 2.5 │     │    RAG    │    │ LangChain │
        │   1.5B   │     │  Engine   │    │ ReAct Agent│
        └────┬─────┘     └─────┬─────┘    └──────┬─────┘
             │                 │                  │
             │                 ▼                  ▼
             │           ┌───────────┐      ┌─────────────┐
             │           │   FAISS   │      │   Backend   │
             │           │  Vector   │      │    Tools    │
             │           │  Database │      │ (Simulated) │
             │           └───────────┘      └─────────────┘
             │
             ▼
       ┌──────────────┐
       │ AMD ROCm /   │
       │    PyTorch   │
       └──────────────┘
```

---

## 🧠 RAG Pipeline

```text
Runbooks / SOPs
       |
       v
Document Ingestion
       |
       v
Embedding Generation
       |
       v
FAISS Vector Database
       |
       v
Relevant Context Retrieval
       |
       v
Qwen 2.5 1.5B
       |
       v
Incident Response
```

---

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Language Model | Qwen 2.5 1.5B |
| ML Framework | PyTorch |
| GPU Runtime | AMD ROCm |
| Model Framework | HuggingFace Transformers |
| Agent Framework | LangChain |
| Agent Pattern | ReAct |
| RAG | Retrieval-Augmented Generation |
| Vector Store | FAISS |
| Backend | FastAPI |
| Server | Uvicorn |
| Frontend | Streamlit |
| Containerization | Docker |
| Orchestration | Docker Compose |
| GPU Acceleration | AMD ROCm |

---

## ⚙️ Prerequisites

- Docker
- Docker Compose v1.29+
- Compatible GPU
- Minimum 8 GB VRAM
- Minimum 16 GB system RAM

### GPU Support

ForgeLM is primarily configured for **AMD ROCm** and modern AMD GPUs such as the Radeon RX 9060 XT.

The architecture can also be adapted for NVIDIA CUDA.

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/ShravanMore-dev/ForgeLM.git
cd ForgeLM
```

### 2. Add Model Weights

Place the fine-tuned Qwen model weights inside:

```text
models/
```

Model weights are intentionally excluded from version control.

### 3. Add Runbooks and SOPs

Place your runbook and SOP documents inside:

```text
data/
```

Example:

```text
data/
├── runbooks/
├── sops/
└── troubleshooting/
```

Do not commit confidential infrastructure documentation, credentials, API keys, or other sensitive information.

### 4. Start the Stack

```bash
docker-compose up -d
```

---

## 🔥 AMD First-Run Compilation

When ForgeLM is launched for the first time on an AMD GPU, the MIOpen/Triton runtime may need to compile GPU kernels.

This is expected behavior.

The initial compilation may take approximately:

```text
5–15 minutes
```

Monitor the API container:

```bash
docker logs -f forgelm-api
```

Wait until you see:

```text
Application startup complete.
```

---

## 🌐 Access the Application

Once the services are running, open:

```text
http://localhost:8501
```

The Streamlit interface provides the main ForgeLM user experience.

---

## 📂 Project Structure

```text
ForgeLM/
├── api/
│   ├── agent.py          # FastAPI backend and LangChain ReAct engine
│   └── tools.py          # Custom SRE tool execution scripts
├── ui/
│   └── app.py            # Streamlit frontend application
├── data/                 # FAISS vector database and text runbooks
├── models/               # Local LLM weights and LoRA configurations
├── scripts/              # Utility and deployment scripts
├── .env                  # Environment variables and secrets
├── .gitignore            # Git exclusion definitions
├── docker-compose.yml    # Local multi-container orchestration
├── Dockerfile.api        # Backend container configuration
├── Dockerfile.ui         # Frontend container configuration
└── README.md             # Project documentation


The internal source structure may evolve as the project develops.

---

## 🔐 Privacy & Local Deployment

ForgeLM follows a **local-first architecture**.

The intended deployment keeps the following within the organization's environment:

- Infrastructure information
- Internal SOPs
- Runbooks
- Incident context
- Retrieved knowledge
- Model inference

This makes ForgeLM suitable for environments where sensitive operational information should not be sent to external AI APIs.

```text
┌──────────────────────────────────────────┐
│              ORGANIZATION                │
│                                          │
│  Runbooks → FAISS → ForgeLM → User      │
│                │                         │
│                └── Local Inference       │
│                                          │
│       No external AI API required        │
└──────────────────────────────────────────┘
```

---

## 🧪 Example Incident Workflow

Example incident:

```text
Database service is experiencing repeated
connection failures.
```

ForgeLM can process the incident through the following workflow:

```text
Incident
   |
   v
Understand Problem
   |
   v
Retrieve Relevant Runbooks
   |
   v
Reason Through Possible Causes
   |
   v
Execute Diagnostic Tools
   |
   v
Analyze Results
   |
   v
Recommend Remediation
```

The resulting response is grounded in the organization's available operational documentation.

---

## 🎯 Design Goals

### 1. Local-First AI

Run the AI stack locally without requiring external inference APIs.

### 2. Infrastructure-Aware Responses

Use organization-specific documentation through RAG rather than relying exclusively on general model knowledge.

### 3. Lightweight Deployment

Use a 1.5B parameter model to make local deployment more practical.

### 4. Hardware Flexibility

Support AMD ROCm while maintaining an architecture that can be adapted to NVIDIA CUDA.

### 5. Modular Architecture

Separate the user interface, API, model, RAG system, agent, and tooling.

### 6. Agentic Troubleshooting

Move beyond simple text generation toward multi-step incident investigation using ReAct-style agent logic and tool interaction.

---

## 🔭 Future Development

Potential future improvements include:

- Additional infrastructure diagnostic tools
- Production monitoring integrations
- Expanded runbook ingestion pipelines
- Improved document retrieval and ranking
- Automated incident classification
- Kubernetes diagnostics
- Container diagnostics
- Observability integrations
- Automated remediation workflows
- Additional GPU backend support
- Evaluation and benchmarking
- Production authentication and authorization
- Enterprise deployment configurations
- Audit logging and safety controls

---

## ⚠️ Important Notes

### Model Weights

Model weights are not included in the repository and must be provided separately.

### Runbook Data

Do not commit confidential company information, infrastructure credentials, API keys, secrets, or sensitive operational documentation.

### AMD Runtime

The first AMD deployment may take longer because of MIOpen/Triton JIT compilation.

### Simulated Tools

The current ReAct architecture includes simulated backend tool execution.

Before connecting ForgeLM to real infrastructure, production deployments should implement appropriate:

- Authentication
- Authorization
- Audit logging
- Permission controls
- Safety checks
- Human approval mechanisms

---

## 🤝 Contributing

Contributions, bug reports, improvements, and suggestions are welcome.

```bash
git clone https://github.com/ShravanMore-dev/ForgeLM.git
cd ForgeLM

git checkout -b feature/your-feature

# Make your changes

git add .
git commit -m "Add your feature"

git push origin feature/your-feature
```

Open a pull request with:

- Description of the change
- Reason for the change
- Testing performed
- Compatibility considerations

---

## 📜 License

ForgeLM is released under the **MIT License**.

Copyright (c) 2026 **Shravan More**

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

## 👤 Author

**Shravan More**

AI/ML • Robotics • Autonomous Systems • Local AI Infrastructure

GitHub: https://github.com/ShravanMore-dev

---

<p align="center">
  <strong>ForgeLM 🛠️</strong><br>
  <em>Forge reliable incident response with local AI.</em>
</p>
