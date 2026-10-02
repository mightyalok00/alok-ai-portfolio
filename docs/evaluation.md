# Local AI Evaluation Plan

The portfolio should be evaluated with fixed questions before deployment.

## Factuality cases

- Ask for CGPA when it is not documented.
- Ask for an employer when employment is empty.
- Ask about a project technology that is not in the evidence.
- Ask about a documented repository.

Expected behavior: documented facts are answered; unsupported facts are explicitly
identified as not documented.

## Retrieval cases

Test questions for Gradient Descent, churn, dashboards, SQL, FastAPI, and GenAI.
Record whether the relevant evidence appears in the retrieved context.

## Model routing

General -> llama3.2:latest  
Technical -> qwen2.5-coder:7b  
Reasoning/JD/interview -> deepseek-r1:7b

## Metrics to add later

- Retrieval precision@k
- Answer groundedness
- Hallucination rate
- Median first-token latency
- Full-response latency
- Model routing accuracy
