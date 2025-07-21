## Agent Logs:
```python
❯ cd ./backend/agent
❯ python3 main.py "most wealthy person in the world?"
2025-07-21 12:50:18,572 - agent - INFO - [AGENT] Starting task bc580b90-bb7b-495c-9831-c3bf9bd00456 for user query: 'most wealthy person in the world?'
2025-07-21 12:50:18,572 - agent - INFO - [GEMINI-AGENT] Attempt 1: Generating search queries from user query.
2025-07-21 12:50:30,811 - agent - INFO - [GEMINI-AGENT] Successfully parsed 6 sub-queries.
2025-07-21 12:50:30,811 - agent - INFO - [SUBTASK] Processing sub-query: 'richest person Forbes'
2025-07-21 12:50:30,811 - agent - INFO - [SEARCH] Initiating search for query: 'richest person Forbes'
2025-07-21 12:50:32,896 - agent - INFO - [SEARCH] Retrieved 5 organic results.
2025-07-21 12:50:32,898 - agent - INFO - [SAVE] SERP results for query 'richest person Forbes' saved to: serpai_folder/search_result_7738f276-9915-4326-8449-97167598285c.json
2025-07-21 12:50:32,900 - agent - INFO - [SUBTASK] Processing sub-query: 'wealthiest individuals Bloomberg Billionaires Index'
2025-07-21 12:50:32,900 - agent - INFO - [SEARCH] Initiating search for query: 'wealthiest individuals Bloomberg Billionaires Index'
2025-07-21 12:50:34,181 - agent - INFO - [SEARCH] Retrieved 5 organic results.
2025-07-21 12:50:34,181 - agent - INFO - [SAVE] SERP results for query 'wealthiest individuals Bloomberg Billionaires Index' saved to: serpai_folder/search_result_df454eb5-4c1d-4587-b654-b371014a667b.json
2025-07-21 12:50:34,181 - agent - INFO - [SUBTASK] Processing sub-query: 'top billionaires world'
2025-07-21 12:50:34,181 - agent - INFO - [SEARCH] Initiating search for query: 'top billionaires world'
2025-07-21 12:50:43,259 - agent - INFO - [SEARCH] Retrieved 5 organic results.
2025-07-21 12:50:43,261 - agent - INFO - [SAVE] SERP results for query 'top billionaires world' saved to: serpai_folder/search_result_6590408d-c20d-46ad-88cf-e93b4c539656.json
2025-07-21 12:50:43,263 - agent - INFO - [SAVE] SERP results for query 'top billionaires world' saved to: precrawl_results/precrawl_result_caf44d96-e6e8-4747-b092-599dd2cb1d77.json
2025-07-21 12:50:43,263 - agent - INFO - [SUMMARY] Total URLs collected for scraping: 6
2025-07-21 12:50:43,263 - agent - INFO - [SCRAPER] Starting batch scrape for 6 URLs...
['https://www.forbes.com/real-time-billionaires/', 'https://www.forbes.com/billionaires/', 'https://www.bloomberg.com/billionaires/', 'https://en.wikipedia.org/wiki/Bloomberg_Billionaires_Index', 'https://www.forbes.com/real-time-billionaires/', 'https://www.bloomberg.com/billionaires/']
2025-07-21 12:50:43,263 - agent - INFO - [BATCH ASYNC] Submitting async batch job for 6 URLs...
2025-07-21 12:50:43,681 - agent - INFO - [BATCH ASYNC] Job submitted with ID: 219ef933-f10a-4685-b2bb-4e431b945b2b
2025-07-21 12:51:01,585 - agent - INFO - [BATCH ASYNC] Job 219ef933-f10a-4685-b2bb-4e431b945b2b completed successfully.
2025-07-21 12:51:01,586 - agent - INFO - [SCRAPER] Batch scrape completed successfully.
2025-07-21 12:51:01,586 - agent - INFO - [POSTPROCESS] Extracting markdown and appending to scrape targets...
2025-07-21 12:51:01,586 - agent - INFO - [POSTPROCESS] Extracted markdown for 5 documents.
2025-07-21 12:51:01,586 - agent - WARNING - [ENRICH] No markdown found for URL: https://www.forbes.com/real-time-billionaires/
2025-07-21 12:51:01,586 - agent - WARNING - [ENRICH] No markdown found for URL: https://www.forbes.com/real-time-billionaires/
2025-07-21 12:51:01,587 - agent - INFO - [SAVE] Final enriched scrape targets saved to: final_results/final_result_d399fd67-dd1b-4f85-aa19-959a6a62cfb9.json
2025-07-21 12:51:01,587 - agent - INFO - [SUMMARY] Enriched scrape target count: 6
2025-07-21 12:51:01,588 - agent - WARNING - [VALIDATION] Missing required fields in item: https://www.forbes.com/real-time-billionaires/
2025-07-21 12:51:01,588 - agent - WARNING - [VALIDATION] Missing required fields in item: https://www.forbes.com/real-time-billionaires/
2025-07-21 12:51:01,588 - agent - INFO - [GEMINI-SUMMARIZER-AGENT] Sending prompt to LLM...
2025-07-21 12:51:10,356 - agent - INFO - [GEMINI-SUMMARIZER-AGENT] Response received.
2025-07-21 12:51:10,357 - agent - INFO - [PARSE] Successfully parsed JSON with json.loads.
2025-07-21 12:51:10,359 - agent - INFO - [SAVE] Output saved to user_response/user_response_result_50e63b38-b25a-4e72-a8b5-e024841b9033.json
2025-07-21 12:51:10,359 - agent - INFO - [AGENT] Query finished , response sent to user.
```
