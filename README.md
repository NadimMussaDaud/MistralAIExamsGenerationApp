# MistralAIExamsGenerationApp
Instead of creating questions by yourself for an Exam let the App do this for you!



## App workflow

```mermaid
flowchart TD
    A[User Uploads Past Tests PDFs] --> B[Text Extraction & Chunking]
    C[Public Question Bank Web Scraper] --> D[Storage & Processing Layer]
    B --> D

    subgraph D [Storage & Processing Layer]
        D1[Vector Database<br>ChromaDB/FAISS]
        D2[Processed Questions<br>PostgreSQL]
    end

    D1 --> E[Retrieval & Synthesis]
    D2 --> E

    subgraph E [Retrieval & Synthesis]
        E1[Retrieve Similar Questions]
        E2[Mistral AI<br>Generate New Questions]
        E3[Format to JSON]
    end

    E3 --> F{LaTeX Templating Engine}
    F --> G[PDF Test Generation]
    G --> H[Output for User]
```
