# Demo
link to video : [here](https://www.youtube.com/watch?v=kAivqquT7ro)

<p align="center">
  <img src="https://github.com/user-attachments/assets/583160e3-4dbb-491f-b633-be575da07378" alt="image" style="max-width: 100%; height: auto;" />
</p>

# Setup Instructions
```bash
:'
FRONTEND_ENV:
NEXT_PUBLIC_API_KEY // api key shared between backend and frontend

BACKEND_ENV:
FIRECRAWL_API_KEY
GOOGLE_API_KEY
SERPAI_API_KEY
AGENT_API_KEY  // api key shared between backend and frontend
'
cp ./frontend/env.example ./frontend/.env
cp ./backend/env.example ./backend/.env

:'
RUN FRONTEND
'
cd frontend
bun run dev

:'
RUN BACKEND
'
cd backend
python3 -m venv ./env
source ./env/bin/activate
pip3 install -r requirements.txt
fastapi dev main.py
```
# Planning
### High Level Design

> Implemented
```bash
[await api] -> [generate_subqueries_with_llm] -> [seed_url_generation with serp ai] -> [filtering_urls for crawling] -> [scraping_of_urls (firecrawler)] -> [summarize_result_with_llm] -> [await relased api returned]
```

> Suggested

<img width="864" height="707" alt="image" src="https://github.com/user-attachments/assets/95fdcc22-f91d-4568-adc9-017145cba6a7" />

### Auth
> #### **API_KEY** is passed in header from frontend to backend for now.

# Results


### Agent Log (used in demo video):
```python
      INFO   127.0.0.1:63353 - "OPTIONS                                                       
             /api/ask/?query=what%20are%20the%20trends%20of%20indian%20stock%20market%20indice
             s%3F HTTP/1.1" 200
2025-07-21 21:53:11,467 - agent - INFO - [AGENT] Starting task 347888ea-3a0b-41af-8f68-af34b1406fa3 for user query: 'what are the trends of indian stock market indices?'
2025-07-21 21:53:11,467 - agent - INFO - [GEMINI-AGENT] Attempt 1: Generating search queries from user query.
2025-07-21 21:53:18,908 - agent - INFO - [GEMINI-AGENT] Successfully parsed 6 sub-queries.
2025-07-21 21:53:18,909 - agent - INFO - [SUBTASK] Processing sub-query: 'Indian stock market index trends'
2025-07-21 21:53:18,909 - agent - INFO - [SEARCH] Initiating search for query: 'Indian stock market index trends'
2025-07-21 21:53:30,177 - agent - INFO - [SEARCH] Retrieved 5 organic results.
2025-07-21 21:53:30,178 - agent - INFO - [SAVE] SERP results for query 'Indian stock market index trends' saved to: serpai_folder/search_result_2076bba2-0c3a-472d-b6e4-3e0272663074.json
2025-07-21 21:53:30,183 - agent - INFO - [SUBTASK] Processing sub-query: 'NIFTY 50 trend analysis'
2025-07-21 21:53:30,184 - agent - INFO - [SEARCH] Initiating search for query: 'NIFTY 50 trend analysis'
2025-07-21 21:53:30,765 - watchfiles.main - INFO - 1 change detected
2025-07-21 21:53:37,612 - agent - INFO - [SEARCH] Retrieved 5 organic results.
2025-07-21 21:53:37,613 - agent - INFO - [SAVE] SERP results for query 'NIFTY 50 trend analysis' saved to: serpai_folder/search_result_f8e5f169-8fb5-4f93-a2b2-89284294d3a6.json
2025-07-21 21:53:37,613 - agent - INFO - [SUBTASK] Processing sub-query: 'BSE Sensex recent performance'
2025-07-21 21:53:37,613 - agent - INFO - [SEARCH] Initiating search for query: 'BSE Sensex recent performance'
2025-07-21 21:53:37,688 - watchfiles.main - INFO - 1 change detected
2025-07-21 21:53:43,894 - agent - INFO - [SEARCH] Retrieved 5 organic results.
2025-07-21 21:53:43,895 - agent - INFO - [SAVE] SERP results for query 'BSE Sensex recent performance' saved to: serpai_folder/search_result_a482cfc1-3d0a-4723-96e2-86ad017d157a.json
2025-07-21 21:53:43,897 - agent - INFO - [SAVE] SERP results for query 'BSE Sensex recent performance' saved to: precrawl_results/precrawl_result_6dfb5ee0-fb43-415c-87a3-a92bea28f129.json
2025-07-21 21:53:43,897 - agent - INFO - [SUMMARY] Total URLs collected for scraping: 6
2025-07-21 21:53:43,897 - agent - INFO - [SCRAPER] Starting batch scrape for 6 URLs...
['https://www.nseindia.com/market-data/live-market-indices', 'https://www.moneycontrol.com/stocksmarketsindia/', 'https://www.moneycontrol.com/technical-analysis/indian-indices/nifty-50-9', 'https://in.investing.com/indices/s-p-cnx-nifty-technical', 'https://www.bseindia.com/sensex/code/16/', 'https://groww.in/indices/sp-bse-sensex']
2025-07-21 21:53:43,897 - agent - INFO - [BATCH ASYNC] Submitting async batch job for 6 URLs...
2025-07-21 21:53:43,983 - watchfiles.main - INFO - 2 changes detected
2025-07-21 21:53:44,609 - agent - INFO - [BATCH ASYNC] Job submitted with ID: fdbeb04a-5081-4c5c-b721-3caad178dc21
2025-07-21 21:54:03,269 - agent - INFO - [BATCH ASYNC] Job fdbeb04a-5081-4c5c-b721-3caad178dc21 completed successfully.
2025-07-21 21:54:03,269 - agent - INFO - [SCRAPER] Batch scrape completed successfully.
2025-07-21 21:54:03,269 - agent - INFO - [POSTPROCESS] Extracting markdown and appending to scrape targets...
2025-07-21 21:54:03,269 - agent - INFO - [POSTPROCESS] Extracted markdown for 6 documents.
2025-07-21 21:54:03,273 - agent - INFO - [SAVE] Final enriched scrape targets saved to: final_results/final_result_3c6795e1-071a-4878-8ad3-669af254910d.json
2025-07-21 21:54:03,273 - agent - INFO - [SUMMARY] Enriched scrape target count: 6
2025-07-21 21:54:03,276 - agent - WARNING - [DATAPOINT VALIDATION] Skipped invalid item due to error: 1 validation error for Metadata
snippet_highlighted_words
  Field required [type=missing, input_value={'position': 1, 'title': ...source': 'Moneycontrol'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.11/v/missing
2025-07-21 21:54:03,276 - agent - WARNING - [DATAPOINT VALIDATION] Skipped invalid item due to error: 3 validation errors for Metadata
favicon
  Field required [type=missing, input_value={'position': 1, 'title': ... code', 'source': 'BSE'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.11/v/missing
snippet
  Field required [type=missing, input_value={'position': 1, 'title': ... code', 'source': 'BSE'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.11/v/missing
snippet_highlighted_words
  Field required [type=missing, input_value={'position': 1, 'title': ... code', 'source': 'BSE'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.11/v/missing
2025-07-21 21:54:03,276 - agent - INFO - [GEMINI-SUMMARIZER-AGENT] Sending prompt to LLM...
2025-07-21 21:54:03,348 - watchfiles.main - INFO - 1 change detected
2025-07-21 21:54:15,994 - agent - INFO - [GEMINI-SUMMARIZER-AGENT] Response received.
2025-07-21 21:54:15,994 - agent - INFO - [PARSE] Successfully parsed JSON with json.loads.
2025-07-21 21:54:15,995 - agent - INFO - [SAVE] Output saved to user_response/user_response_result_57ba36b4-ab85-42a9-961a-5910df0891d6.json
2025-07-21 21:54:15,996 - agent - INFO - [AGENT] Query finished , response sent to user.
      INFO   127.0.0.1:63355 - "GET                                                           
             /api/ask/?query=what%20are%20the%20trends%20of%20indian%20stock%20market%20indice
             s%3F HTTP/1.1" 200
```
