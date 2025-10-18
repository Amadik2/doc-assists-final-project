# Data Processing

This document describes the data sources, preprocessing steps, and indexing methodology used in the Doc Assist project.

## Data Sources

Doc Assist leverages three key datasets:

### 1. StaQC (Stack Overflow Question–Code Pairs)

StaQC is the largest systematically mined dataset of question–code pairs, comprising approximately 148K Python and 120K SQL examples (Yao et al., 2018). It is derived from Stack Overflow through a Bi-View Hierarchical Neural Network that extracts high-quality code snippets from multi-code and single-code answer posts.

In our implementation, we use a small sample of the StaQC dataset for demonstration purposes:

```python
sample_staqc = [
    (1, "def example():\n    return 'Hello'", "How to create a simple function?"),
    (2, "import numpy as np\n\narr = np.array([1, 2, 3])", "How to create a numpy array?"),
    (3, "for i in range(10):\n    print(i)", "How to loop through numbers?"),
    (4, "import pandas as pd\n\ndf = pd.read_csv('file.csv')", "How to read a CSV file with pandas?"),
    (5, "import pandas as pd\n\ndf = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})\ndf.groupby('A').sum()", "How to groupby and sum in pandas?")
]
```

### 2. CoNaLa (Code–Natural Language Dataset)

CoNaLa is a benchmark dataset containing natural-language intents paired with corresponding code snippets (Yin et al., 2018). It includes a large automatically mined set and a high-quality, human-annotated test set.

In our implementation, we use a small sample of the CoNaLa dataset for demonstration purposes:

```python
sample_conala = [
    {
        "rewritten_intent": "create a list of integers from 1 to 10",
        "snippet": "list(range(1, 11))"
    },
    {
        "rewritten_intent": "get the current date",
        "snippet": "from datetime import date\ntoday = date.today()"
    },
    # ... more examples
]
```

### 3. Custom Documentation (Future Work)

In a production environment, Doc Assist would be expanded to include:
- Official documentation from popular libraries (e.g., NumPy, Pandas, TensorFlow)
- API references
- Tutorials and guides
- Code examples from GitHub repositories

## Data Preprocessing

The data preprocessing pipeline consists of the following steps:

### 1. Loading and Parsing

- **StaQC**: The data is loaded from a pickle file and parsed into a list of (id, code, question) tuples.
- **CoNaLa**: The data is loaded from a JSONL file and parsed into a list of dictionaries with "rewritten_intent" and "snippet" fields.

### 2. Text Normalization

- **Questions/Intents**: 
  - Lowercasing
  - Removing special characters
  - Tokenization
  - Stopword removal
  - Lemmatization

- **Code Snippets**:
  - Standardizing whitespace
  - Removing comments
  - Normalizing variable names (in a full implementation)

### 3. Corpus Building

The preprocessed data is combined into a unified corpus, where each document contains:
- A unique identifier
- The original text (question or intent)
- The associated code snippet
- Metadata (source, tags, etc.)

## Embedding Generation

For efficient retrieval, all documents in the corpus are converted into dense vector embeddings:

1. **Model**: We use the Sentence Transformers model "all-MiniLM-L6-v2" for generating embeddings.
2. **Batching**: Documents are processed in batches to optimize memory usage and computation time.
3. **Normalization**: The embeddings are normalized to unit length for cosine similarity calculations.

## Index Building

The document embeddings are indexed using FAISS (Facebook AI Similarity Search) for efficient similarity search:

1. **Index Type**: We use a flat index for small datasets and an IVFPQ (Inverted File with Product Quantization) index for larger datasets.
2. **Training**: For IVFPQ indices, the index is trained on the document embeddings to optimize clustering.
3. **Adding Vectors**: The document embeddings are added to the index.
4. **Saving**: The index is saved to disk for later use.

## Mapping File

Along with the FAISS index, we save a mapping file that maps from index positions to the original documents:

```json
[
  {
    "id": 1,
    "text": "How to create a simple function?",
    "code": "def example():\n    return 'Hello'",
    "source": "staqc"
  },
  {
    "id": 2,
    "text": "How to create a numpy array?",
    "code": "import numpy as np\n\narr = np.array([1, 2, 3])",
    "source": "staqc"
  },
  // ... more documents
]
```

## Future Enhancements

In future iterations, the data processing pipeline could be enhanced with:

1. **Data Augmentation**: Generating additional question-code pairs through paraphrasing and code transformation.
2. **Quality Filtering**: Implementing more sophisticated filtering to remove low-quality examples.
3. **Incremental Indexing**: Supporting the addition of new documents without rebuilding the entire index.
4. **Multi-modal Indexing**: Incorporating separate indices for code and text with specialized embedding models.

![Data Processing Pipeline](figures/data_processing_pipeline.png)
*Note: This figure is a placeholder and needs to be created*
