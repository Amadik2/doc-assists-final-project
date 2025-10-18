# Setup and Installation

This document provides detailed instructions for setting up and running the Doc Assist system.

## Prerequisites

- Python 3.9+
- PyTorch 2.0+
- CUDA (optional, for GPU acceleration)
- Git

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/doc-assist.git
cd doc-assist
```

### 2. Create a Virtual Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows
.\venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Download required models
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('stopwords')"
```

## Building the Index

Before using Doc Assist, you need to build the search index:

```bash
# Configure data sources in configs/build_index.yaml
# Then build the index
python run.py index --config configs/build_index.yaml
```

This will:
1. Load the data from the specified sources
2. Generate embeddings using the specified model
3. Build a FAISS index for efficient similarity search
4. Save the index and mapping files to the specified location

## Running the System

### API Server

```bash
# Start the API server
python run.py serve --host 127.0.0.1 --port 8080
```

The API will be available at http://localhost:8080.

### UI Server

```bash
# Start the UI server
python run.py ui --host 127.0.0.1 --port 8501 --api-url http://127.0.0.1:8080
```

The UI will be available at http://localhost:8501.

### Running Both Services

```bash
# Start both API and UI servers
python run.py start
```

## Using the System

### Via the UI

1. Open a web browser and navigate to http://localhost:8501
2. Enter your question in the text box
3. Click the "Answer" button
4. View the generated answer and the retrieved context

### Via the API

```bash
# Example API request
curl -X POST http://localhost:8080/answer \
  -H "Content-Type: application/json" \
  -d '{"question": "How to groupby and sum in pandas?", "top_k": 5}'
```

### Via the Command Line

```bash
# Run a single query
python run.py query "How to read CSV with pandas?"
```

## Troubleshooting

### Common Issues

1. **Port already in use**: If you see an error like "Port 8080 is already in use", try using a different port:
   ```bash
   python run.py serve --port 8081
   ```

2. **Missing dependencies**: If you encounter missing dependencies, try reinstalling them:
   ```bash
   pip install -r requirements.txt
   ```

3. **Index not found**: If the system can't find the index, make sure you've built it:
   ```bash
   python run.py index --config configs/build_index.yaml
   ```

4. **Model loading errors**: If you encounter errors loading the models, check that you have enough disk space and that the models are downloaded correctly.

### Getting Help

If you encounter any issues not covered here, please open an issue on the GitHub repository or contact the project maintainers.
