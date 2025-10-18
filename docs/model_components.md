# Model Components

This document describes the key model components used in the Doc Assist system.

## Retriever

The retriever component is responsible for finding relevant documentation based on the user's query. It uses dense vector embeddings and efficient similarity search to identify the most relevant documents.

### Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  User Query  │────▶│   Encoder    │────▶│ Vector Search │
└──────────────┘     └──────────────┘     └──────────────┘
                                                  │
                                                  ▼
                                          ┌──────────────┐
                                          │   Ranking    │
                                          └──────────────┘
                                                  │
                                                  ▼
                                          ┌──────────────┐
                                          │  Top-K Docs  │
                                          └──────────────┘
```

### Components

#### 1. Encoder

The encoder converts text into dense vector embeddings using the Sentence Transformers library:

```python
self.encoder = SentenceTransformer(model_name, device=device)
```

We use the "all-MiniLM-L6-v2" model, which is a lightweight but powerful model that produces 384-dimensional embeddings. This model has been trained on a diverse set of tasks and performs well on semantic similarity tasks.

#### 2. Vector Search

For efficient similarity search, we use FAISS (Facebook AI Similarity Search):

```python
self.index = faiss.read_index(faiss_path)
```

FAISS provides highly optimized algorithms for similarity search in high-dimensional spaces. We use either a flat index (for exact search) or an IVFPQ index (for approximate search) depending on the size of the corpus.

#### 3. Hybrid Ranking

To improve the quality of retrieved documents, we use a hybrid ranking approach that combines semantic similarity with lexical overlap:

```python
def _lexical_boost(self, query: str, doc_text: str) -> float:
    # Crude lexical overlap for hybrid weighting
    q_terms = set(query.lower().split())
    d_terms = set(doc_text.lower().split())
    inter = len(q_terms & d_terms)
    return 1.0 + 0.02 * inter  # Tiny boost per term
```

This gives a small boost to documents that share common terms with the query, which helps to balance semantic similarity with lexical matching.

### Implementation Details

The retriever is implemented in `src/retriever/retriever.py`. Key methods include:

- `__init__`: Initializes the retriever with a FAISS index and document mapping
- `search`: Searches for relevant documents given a query
- `_lexical_boost`: Calculates a lexical overlap boost for hybrid ranking

## Generator

The generator component takes the retrieved context and the original query to generate a coherent and accurate answer. It uses a pre-trained language model fine-tuned for code-related tasks.

### Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  User Query  │     │   Context    │     │   Prompt     │
└──────────────┘     └──────────────┘     │  Template    │
        │                   │             └──────────────┘
        └───────────┬───────┘                    │
                    ▼                            │
            ┌──────────────┐                     │
            │ Format Prompt │◀────────────────────┘
            └──────────────┘
                    │
                    ▼
            ┌──────────────┐
            │   Tokenizer  │
            └──────────────┘
                    │
                    ▼
            ┌──────────────┐
            │ CodeT5 Model │
            └──────────────┘
                    │
                    ▼
            ┌──────────────┐
            │   Decoder    │
            └──────────────┘
                    │
                    ▼
            ┌──────────────┐
            │   Answer     │
            └──────────────┘
```

### Components

#### 1. Prompt Template

We use a structured prompt template to guide the model's generation:

```python
def format_prompt(self, query: str, contexts: list[str]) -> str:
    preface = "You are a technical assistant. Use only the given context.\n"
    ctx = "\n".join([f"[{i+1}] {c}" for i, c in enumerate(contexts)])
    return f"{preface}\nQuestion: {query}\nContext:\n{ctx}\n\nAnswer:"
```

This template:
- Sets the role of the model as a technical assistant
- Instructs it to use only the provided context
- Includes the user's query
- Provides numbered context documents
- Prompts for an answer

#### 2. Tokenizer and Model

We use the RobertaTokenizer and T5ForConditionalGeneration from the Hugging Face Transformers library:

```python
self.tokenizer = RobertaTokenizer.from_pretrained(model_name)
self.model = T5ForConditionalGeneration.from_pretrained(model_name)
```

We specifically use the "Salesforce/codet5-base" model, which is a T5 model fine-tuned on code-related tasks. This model has 220 million parameters and has been trained on a diverse set of programming languages.

#### 3. Generation Parameters

We use beam search with carefully tuned parameters for generation:

```python
ids = self.model.generate(
    **inputs,
    max_new_tokens=max_tokens,
    num_beams=4,
    no_repeat_ngram_size=3,
    length_penalty=0.6,
    temperature=0.7,
    early_stopping=True
)
```

These parameters:
- `max_new_tokens`: Limits the length of the generated text
- `num_beams`: Uses beam search with 4 beams for more diverse and high-quality generation
- `no_repeat_ngram_size`: Prevents repetition of 3-grams
- `length_penalty`: Slightly penalizes longer sequences
- `temperature`: Adds some randomness to the generation
- `early_stopping`: Stops generation when all beams have reached the end token

### Implementation Details

The generator is implemented in `src/generator/generator.py`. Key methods include:

- `__init__`: Initializes the generator with a pre-trained model
- `format_prompt`: Formats the prompt for generation
- `generate`: Generates an answer based on the query and contexts

## RAG Pipeline

The RAG (Retrieval-Augmented Generation) pipeline orchestrates the retriever and generator components, ensuring a smooth flow from query to answer.

### Architecture

```
┌──────────────┐
│  User Query  │
└──────────────┘
        │
        ▼
┌──────────────┐
│   Retriever  │
└──────────────┘
        │
        ▼
┌──────────────┐
│  Top-K Docs  │
└──────────────┘
        │
        ▼
┌──────────────┐
│   Generator  │
└──────────────┘
        │
        ▼
┌──────────────┐
│   Answer     │
└──────────────┘
```

### Components

#### 1. Query Processing

The pipeline preprocesses the user's query to optimize retrieval:

- Removing special characters
- Expanding common abbreviations
- Handling code-specific syntax

#### 2. Context Selection

After retrieval, the pipeline selects the most relevant context documents:

- Filtering out irrelevant documents
- Limiting the total context length
- Ensuring diversity of context

#### 3. Answer Generation

The pipeline then generates an answer based on the query and selected context:

```python
def answer(self, query: str, top_k=3):
    # Retrieve relevant documents
    contexts = self.retriever.search(query, top_k=top_k)
    
    # Extract text from contexts
    context_texts = [ctx[0]["text"] for ctx in contexts]
    
    # Generate answer
    answer = self.generator.generate(query, context_texts)
    
    # Return answer and contexts
    return {
        "answer": answer,
        "contexts": contexts,
        "citations": [],
        "flags": []
    }
```

#### 4. Post-processing

In a full implementation, the pipeline would also:

- Verify the factual accuracy of the generated answer
- Add citations to the source documents
- Flag any potential issues with the answer
- Format the answer for presentation

### Implementation Details

The RAG pipeline is implemented in `src/rag/pipeline.py`. Key methods include:

- `__init__`: Initializes the pipeline with retriever and generator components
- `answer`: Processes a query and returns an answer with supporting context

## Future Enhancements

In future iterations, the model components could be enhanced with:

1. **Improved Retriever**:
   - Dense passage retrieval with in-batch negatives
   - Learned sparse retrieval (e.g., SPLADE)
   - Hybrid dense-sparse retrieval

2. **Advanced Generator**:
   - Fine-tuning on domain-specific data
   - Instruction tuning for better following of instructions
   - Parameter-efficient fine-tuning (e.g., LoRA)

3. **Enhanced Pipeline**:
   - Multi-hop reasoning
   - Query rewriting
   - Answer verification
   - Uncertainty estimation

![Model Components](figures/model_components.png)
*Note: This figure is a placeholder and needs to be created*
