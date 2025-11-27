```
bose-rag-system/
│
├── config/
│   ├── __init__.py
│   ├── settings.py              # Global configuration
│   └── constants.py             # Content types, chunk sizes
│
├── src/
│   ├── __init__.py
│   │
│   ├── content_detection/
│   │   ├── __init__.py
│   │   └── detector.py          # Detect text/table/image
│   │
│   ├── document_processing/
│   │   ├── __init__.py
│   │   ├── base_processor.py    # Abstract base class
│   │   ├── text_processor.py    # Text processing
│   │   ├── table_processor.py   # Table extraction
│   │   ├── image_processor.py   # Image handling
│   │   └── router.py            # Route to processor
│   │
│   ├── embeddings/
│   │   ├── __init__.py
│   │   └── embedder.py          # Sentence Transformers
│   │
│   ├── vector_store/
│   │   ├── __init__.py
│   │   └── chromadb_manager.py  # ChromaDB with metadata
│   │
│   ├── retrieval/
│   │   ├── __init__.py
│   │   └── content_aware_retriever.py  # Smart retrieval
│   │
│   ├── generation/
│   │   ├── __init__.py
│   │   ├── llm_handler_phi.py   # Phi-2 handler
│   │   ├── prompt_builder.py    # Context-aware prompts
│   │   └── response_formatter.py # Format answers
│   │
│   ├── error_handling/
│   │   ├── __init__.py
│   │   ├── handlers.py          # Error handlers
│   │   └── logger.py            # Logging
│   │
│   └── interfaces/
│       ├── __init__.py
│       ├── rag_phi.py           # Main RAG class
│       ├── gradio_app.py        # Web interface
│       └── cli.py               # CLI interface
│
├── data/
│   ├── documents/               # Raw PDFs
│   ├── processed/               # Processed chunks
│   └── vector_db/               # ChromaDB storage
│
├── tests/
│   ├── __init__.py
│   ├── test_detection.py
│   ├── test_processing.py
│   ├── test_retrieval.py
│   └── test_integration.py
│
├── scripts/
│   ├── demo.py                  # Quick demo
│   └── evaluate.py              # Evaluation metrics
│
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```