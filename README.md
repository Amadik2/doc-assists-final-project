# Doc Assist

A domain-specific question-answering system for software documentation using Retrieval-Augmented Generation (RAG).

## Features

- **Domain-Specific Retrieval**: Optimized for technical documentation with technical term weighting
- **Code-Aware Generation**: Uses CodeT5 for high-quality code generation
- **Hybrid Ranking**: Combines semantic and lexical search for better results
- **Fact Verification**: Checks generated content against retrieved context
- **Fast Response**: Sub-500ms response times for most queries
- **Web UI**: Streamlit-based interface for easy interaction
- **REST API**: FastAPI-based API for programmatic access

## Architecture

Doc Assist uses a Retrieval-Augmented Generation (RAG) architecture:

1. **Retriever**: Uses FAISS with Sentence Transformers embeddings to find relevant documentation
2. **Generator**: Uses CodeT5 to generate answers based on retrieved context
3. **Verifier**: Ensures generated content is supported by the retrieved context

## Setup

### Prerequisites

- Python 3.9+
- PyTorch 2.0+
- CUDA (optional, for GPU acceleration)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/doc-assist.git
cd doc-assist

# Install dependencies
make setup
```

### Building the Index

Before using Doc Assist, you need to build the search index:

```bash
# Configure data sources in src/config/build_index.yaml
# Then build the index
make index
```

### Running the API

```bash
make serve
```

The API will be available at http://localhost:8080.

### Running the UI

```bash
make ui
```

The UI will be available at http://localhost:8501.

## Usage

### API

```bash
curl -X POST http://localhost:8080/answer \
  -H "Content-Type: application/json" \
  -d '{"question": "How to groupby and sum in pandas?", "top_k": 5}'
```

### Python Client

```python
import requests

response = requests.post(
    "http://localhost:8080/answer",
    json={"question": "How to read CSV with pandas?", "top_k": 5}
)

print(response.json()["answer"])
```

## Development

### Running Tests

```bash
make test
```

### Docker Build

```bash
docker build -f docker/Dockerfile -t doc-assist .
docker run -p 8080:8080 doc-assist
```

## License

MIT

## Acknowledgments

- [Hugging Face Transformers](https://github.com/huggingface/transformers)
- [Sentence Transformers](https://github.com/UKPLab/sentence-transformers)
- [FAISS](https://github.com/facebookresearch/faiss)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Streamlit](https://streamlit.io/)
