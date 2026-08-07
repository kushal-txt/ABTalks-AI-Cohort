QUESTIONS_DB = {
    1: {
        "primary": "For Day 1, you set up your VS Code and Python environments. How did you configure your Python virtual environment (.venv), and why is it important to use virtual environments instead of installing packages globally?",
        "follow_up": "If you needed to share this environment setup with a teammate, what files would you commit to Git, and how would they reproduce it?"
    },
    2: {
        "primary": "On Day 2, you set up Ollama and downloaded a local model. Which model did you use, and how did you configure your coding assistant (like Cline or Copilot) to use it locally?",
        "follow_up": "What are the latency and privacy trade-offs of running a local model like Qwen2.5-Coder versus using a cloud LLM API?"
    },
    3: {
        "primary": "For Day 3, you built your first full-stack chatbot with a React frontend and a FastAPI backend. How did you connect the frontend to the backend, and how did you handle CORS issues?",
        "follow_up": "How did your FastAPI backend communicate with the local Ollama instance? Did you use a library or direct HTTP calls?"
    },
    4: {
        "primary": "On Day 4, you worked on processing structured data like CSVs or JSON. How did you clean or validate the data before feeding it into your system?",
        "follow_up": "What library did you use for structured data manipulation, and how did you handle missing values or incorrect data types?"
    },
    5: {
        "primary": "On Day 5, you focused on unstructured data like PDFs and HTML. What libraries did you use to extract text, and how did you split the text into manageable chunks?",
        "follow_up": "Why is chunk size and chunk overlap critical when preparing unstructured documents for an embedding model?"
    },
    6: {
        "primary": "On Day 6, you built a Knowledge Base repository. How did you structure the folder system, and how does the system know when a new file is added and needs to be parsed?",
        "follow_up": "How do you handle updating or deleting files in your knowledge base without duplicating vector database entries?"
    },
    7: {
        "primary": "For Day 7, you explored embeddings. Explain the difference between keyword lexical search (like BM25) and semantic search using vector embeddings. When would you prefer one over the other?",
        "follow_up": "If a user searches for 'cold weather', how does a vector embedding model match it to a document containing 'chilly temperatures'?"
    },
    8: {
        "primary": "On Day 8, you studied Vector Databases. What is a vector database, and why can't we just use a traditional relational database like PostgreSQL for large-scale vector similarity search?",
        "follow_up": "Actually, PostgreSQL does have an extension called pgvector. Under what circumstances would you use pgvector versus a dedicated vector database like Pinecone, Qdrant, or Chroma?"
    },
    9: {
        "primary": "For Day 9, you populated your vector database. How did you handle bulk inserts, and how do you verify that the vector dimensions of your embedding model match the database configuration?",
        "follow_up": "What is indexing in a vector database (e.g., HNSW or IVF), and how does it speed up queries at scale?"
    },
    10: {
        "primary": "On Day 10, you built a Retrieval & Matching Engine. Explain how you calculate similarity (like Cosine Similarity or L2 distance) to retrieve relevant documents. How do you set a similarity threshold?",
        "follow_up": "What is the 'Lost in the Middle' phenomenon in LLM retrieval, and how does your matching engine attempt to solve or mitigate it?"
    },
    11: {
        "primary": "For Day 11, you built an end-to-end RAG system. Walk me through the exact path a user's query takes from the frontend, through the retrieval engine, to the LLM, and back to the user.",
        "follow_up": "If the LLM returns an answer that isn't supported by the retrieved documents, what is that called, and how did you prevent it in your prompt instructions?"
    },
    12: {
        "primary": "On Day 12, you studied Prompt Engineering. What techniques (such as system instructions, few-shot examples, or Chain-of-Thought prompting) did you implement to ensure high-quality and consistent answers?",
        "follow_up": "How did you structure your system instructions to prevent the model from answering questions outside of its retrieved context?"
    },
    13: {
        "primary": "On Day 13, you explored Advanced Prompting: Function Calling & Structured Outputs. How does function calling work? How does the model know which function to call, and who actually executes the function?",
        "follow_up": "If the model outputs invalid arguments or invalid JSON during a function call, how does your backend capture and handle that error?"
    },
    14: {
        "primary": "For Day 14, you learned about Fine-Tuning. When is it appropriate to fine-tune a model versus using Retrieval-Augmented Generation (RAG)? What are the trade-offs in terms of data, cost, and complexity?",
        "follow_up": "Can you combine RAG and Fine-Tuning in the same system? If so, what role does each play?"
    },
    15: {
        "primary": "On Day 15, you did hands-on fine-tuning with LoRA and QLoRA. How do LoRA and QLoRA make fine-tuning consumer-grade models feasible on limited hardware?",
        "follow_up": "What is the difference between LoRA and QLoRA, specifically regarding weight quantization?"
    },
    16: {
        "primary": "On Day 16, you integrated your chatbot backend API. How did you structure your FastAPI routes, and how did you secure sensitive environment variables like API keys?",
        "follow_up": "How did you manage API errors or rate-limiting from the LLM provider to ensure the backend doesn't crash for the user?"
    },
    17: {
        "primary": "On Day 17, you built the chatbot frontend. What framework did you use, and how did you manage conversation state and scroll behaviors in the chat window?",
        "follow_up": "How did you design the user interface to clearly distinguish between user messages, agent responses, and loading states?"
    },
    18: {
        "primary": "For Day 18, you implemented Streaming Responses. How does streaming work under the hood (e.g., Server-Sent Events or WebSockets), and how does the frontend render chunks in real time?",
        "follow_up": "What are the latency benefits of streaming for the end-user compared to waiting for the full response?"
    },
    19: {
        "primary": "On Day 19, you worked on Response Formatting. How does your frontend parse and render rich text elements like markdown tables, bold text, or syntax-highlighted code blocks?",
        "follow_up": "What security considerations (like XSS) did you have to address when rendering raw markdown or HTML in a web page?"
    },
    20: {
        "primary": "For Day 20, you set up Conversation Memory. Which memory strategy did you implement (e.g., sliding window, summarizing memory, or full history)? What are the scaling and token cost trade-offs?",
        "follow_up": "If a user has an extremely long session, how does your memory manager prevent exceeding the LLM's context window limit?"
    },
    21: {
        "primary": "On Day 21, you explored LangChain Agents. What is the fundamental difference between a static LangChain Chain and a LangChain Agent? How does the agent decide which tool to execute?",
        "follow_up": "What is the ReAct (Reason-Action) loop, and how does the agent use it to solve complex tasks step-by-step?"
    },
    22: {
        "primary": "For Day 22, you studied Multi-Agent Orchestration. How do you orchestrate multiple agents to work together? Explain the difference between hierarchical and sequential agent team structures.",
        "follow_up": "What is the risk of infinite loops in multi-agent systems, and how did you implement guardrails to prevent it?"
    },
    23: {
        "primary": "On Day 23, you focused on the Model Context Protocol (MCP). What is MCP, and how does it standardize the way AI agents connect to external tools, databases, or local files?",
        "follow_up": "Explain the difference between an MCP Client and an MCP Server in this architecture."
    },
    24: {
        "primary": "For Day 24, you integrated your agentic chatbot. How did you show the agent's internal thought process or tool executions in the UI so the user understands what is happening under the hood?",
        "follow_up": "How does the UI handle cases where an agent is running a long-running tool execution or fails to execute a tool?"
    },
    25: {
        "primary": "On Day 25, you worked on Chatbot Evaluation & Testing. How did you evaluate the quality of your chatbot's answers? What metrics (like faithfulness, answer relevance, or context recall) did you look at?",
        "follow_up": "How can you automate evaluation to run continuously as part of a CI/CD pipeline?"
    },
    26: {
        "primary": "On Day 26, you optimized performance and costs. What strategies (such as prompt caching, model downgrading, or response caching) did you use to reduce token costs and latency?",
        "follow_up": "How does prompt caching work, and what type of workloads benefit most from it?"
    },
    27: {
        "primary": "For Day 27, you set up Security & Guardrails. What are the common security vulnerabilities of LLM applications, and how did you protect your chatbot from prompt injection attacks?",
        "follow_up": "Did you implement any content moderation filters or PII (Personally Identifiable Information) masking? How did they work?"
    },
    28: {
        "primary": "On Day 28, you deployed your chatbot using Docker and Kubernetes. How did you structure your Dockerfile to optimize image size, and what is the role of a Kubernetes deployment manifest?",
        "follow_up": "How did you manage environment variables and secrets (like API keys) in a Kubernetes deployment?"
    },
    29: {
        "primary": "For Day 29, you set up Monitoring, Logging & Observability. What metrics (e.g. latency, token usage, error rates) did you track, and what tools did you use to view them in production?",
        "follow_up": "How do trace IDs help you debug a slow or incorrect response in a multi-agent or RAG pipeline?"
    },
    30: {
        "primary": "On Day 30, you worked on Production Readiness. What is a load test, and what key thresholds (like requests per second or response latency) did you test before declaring the app ready?",
        "follow_up": "What is a roll-back plan, and how would you execute it in a Kubernetes environment if a new release causes errors?"
    },
    31: {
        "primary": "Finally, let's talk about Day 31: your Capstone Project. What was the core problem it solved, which components were you most proud of, and what was the main engineering challenge you overcame?",
        "follow_up": "If you had another month to work on this capstone, what features or architecture improvements would you prioritize next?"
    }
}
