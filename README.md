# Unit2-capstone

## System Architecture 


 
```text
User Query (CLI)
 
      │
 
      ▼
 
┌─────────────────┐
 
│  Manager Agent  │  ── classifies query ──► qualitative / quantitative / both
 
└─────────────────┘
 
      │                          │
 
      ▼                          ▼
 
┌──────────────────┐    ┌───────────────────┐
 
│ Qualitative Agent│    │ Quantitative Agent │
 
│                  │    │                   │
 
│ • Vector DB      │    │ • SQLite DB        │
 
│   (ChromaDB)     │    │ • NL → SQL         │
 
│ • Semantic search│    │ • Query execution  │
 
│ • Claude for     │    │ • Claude for       │
 
│   generation     │    │   interpretation   │
 
└──────────────────┘    └───────────────────┘
 
      │                          │
 
      └──────────┬───────────────┘
 
                 ▼
 
      ┌─────────────────────┐
 
      │  Validation Layer   │  ── checks grounding, flags issues
 
      └─────────────────────┘
 
                 │
 
                 ▼
 
      ┌─────────────────────┐
 
      │  Tokenomics Logger  │  ── logs token usage and cost per query
 
      └─────────────────────┘
 
                 │
 
                 ▼
 
        Response to User
```


## Project Structure

```
unit2-capstone/
├── agents/
│   ├── manager.py
│   ├── qualitative.py
│   └── quantitative.py
├── data/
│   ├── chroma/
│   │   ├── 565e0b7b-1025-4cd7-8312-a3726304a367/
│   │   │   ├── data_level0.bin
│   │   │   ├── header.bin
│   │   │   ├── length.bin
│   │   │   └── link_lists.bin
│   │   └── chroma.sqlite3
│   └── documents/
│       ├── analytics_data_dictionary.txt
│       ├── code_review_process.txt
│       ├── customer_complaints.txt
│       ├── employee_experience_policy.txt
│       ├── sales_customer_success_strategy.txt
│       ├── security_policy.txt
│       ├── database.sqlite
│       ├── query_examples.sql
│       ├── setup_mock_data.py
│       └── data/
│           └── documents/
│               ├── analytics_data_dictionary.txt
│               ├── code_review_process.txt
│               ├── customer_complaints.txt
│               ├── employee_experience_policy.txt
│               ├── sales_customer_success_strategy.txt
│               └── security_policy.txt
├── ingest.py
├── main.py
├── README.md
├── requirements.txt
├── smoketest.py
├── test_retrival.py
├── tokenomics/
│   └── logger.py
├── tokenomics_log.jsonl
└── validation/
    ├── __init__.py
    └── validator.py
```



## Trust But Verify
QUERY 1
1. “What is our security policy for remote work?"
2. Answer: * Remote employees are required to utilize secure access methods and approved networks [Source 1].
* Company-issued laptops and mobile devices need to be equipped with full-disk encryption (where technically feasible), supported operating systems, endpoint protection, automatic screen locking, and security updates [Source 2].
* Multi-factor authentication is mandatory when accessing resources remotely [Source 7].
3. The validation did not flag anything.Validation: PASSED
4. After reviewing my security policy document, I confirmed that the agent provided all the necessary details to answer the question. I accepted the response and made no changes. 

QUERY 2
1. Show me our company's monthly revenue trends?
2. Answer: Here are the monthly revenue trends for 2025:
* **January:** $1,460,000.00
* **February:** $1,503,800.00
* **March:** $1,547,600.00
* **April:** $1,591,400.00
* **May:** $1,635,200.00
* **June:** $1,679,000.00
* **July:** $1,722,800.00
* **August:** $1,766,600.00
* **September:** $1,810,400.00
* **October:** $1,854,200.00
* **November:** $1,898,000.00
* **December:** $1,941,800.00

SQL:
SELECT month, SUM(revenue_usd) AS total_revenue
FROM regional_revenue
GROUP BY month
ORDER BY month

3. Nothing was flagged. Validation: PASSED.

4. I did not change anything because the agent properly calculated revenue trends and showed the SQL calculation behind the numbers. I accepted the answer and left it unchanged.


QUERY 3
1. What is our resolution for customer complaints?
2. Answer:
[TOKENOMICS] Agent: manager-classifier | Input: 86 | Output: 2 | Cost: $0.000147
Route: qualitative

[TOKENOMICS] Agent: qualitative | Input: 612 | Output: 59 | Cost: $0.001449

[Qualitative]
- Standard complaints should be provided with a proposed resolution within five business days [Source 9].
- Responses regarding complaints should outline what information is known, actions taken, remaining unresolved items, anticipated timing, and options for the customer to request additional review [Source 5, Source 6].
3. Nothing was flagged. Validation: PASSED.
4. I accepted and did not change anything because the agent extracted the correct information to address the question queried. The answer is kind of vague but that is because my document does not specifically list resolution items, only action steps.

# Example of when I didn't trust Gemini
I queried and asked "what our security policy is?"
Gemini responded and recited all the information in my security policy document. This raised concerns about whether it was properly applying confidentiality and safeguard measures. I reviewed and updated the code to make sure it limited responses to relevant information and redacted sensitive content to prevent any unrestrictured disclosure of information. After updating the code I asked the same question "what is our security policy" and it returned a much better consolidated answer. 