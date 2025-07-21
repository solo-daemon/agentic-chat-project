import re
import ast
import os
import logging
import uuid
import json
import asyncio
from dotenv import load_dotenv, find_dotenv
from firecrawl import FirecrawlApp
from serpapi import GoogleSearch
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, HttpUrl, ValidationError
from typing import List, Optional
from pathlib import Path
# Load environment variables
load_dotenv(find_dotenv())
SERPAPI_API_KEY = os.getenv("SERPAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("agent")

# === Initialize Firecrawl Client === #
crawler = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
# === Initialize LLM === #
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GOOGLE_API_KEY)
# === Asynchronous SERP Search === #
async def serp_search(query: str, num_results: int = 5) -> list:
    """
    Performs a Google search using SerpAPI and returns the top organic results.

    Parameters:
        query (str): The search query to be executed.
        num_results (int): Number of results to fetch. (NOTE: Actual filtering must be handled manually after retrieval.)

    Returns:
        List[dict]: A list of organic search result dictionaries.

    Production Considerations:
    - Ensure API limits are handled and usage is monitored.
    - Avoid making too many concurrent calls to stay within SerpAPI's rate limits.
    - Log all search activity for debugging and analytics.
    """
    logger.info(f"[SEARCH] Initiating search for query: '{query}'")
    
    try:
        search = GoogleSearch({
            "q": query,
            "location": "Delhi, India",
            "google_domain": "google.co.in",
            "engine": "google",
            "gl": "in",
            "hl": "en",
            "api_key": SERPAPI_API_KEY,
            # 'num' is ignored here; we manually truncate below
        })

        result = search.get_dict()
        organic_results = result.get("organic_results", [])[:num_results]

        logger.info(f"[SEARCH] Retrieved {len(organic_results)} organic results.")
        return organic_results

    except Exception as e:
        logger.exception(f"[ERROR] Failed to perform SERP search: {e}")
        return []

# === Crawl a Single URL (Async) === #
async def crawl_url(url: str) -> str:
    """
    Crawls the given URL using Firecrawl and extracts the main textual content.

    Args:
        url (str): The target URL.

    Returns:
        str: The extracted plain text, or empty string on failure.
    """
    try:
        logger.info(f"[CRAWL] Initiating crawl for URL: {url}")
        result = await crawler.extract(url)

        if not result or "text" not in result:
            logger.warning(f"[CRAWL] Missing 'text' in response for URL: {url}")
            return ""

        logger.info(f"[CRAWL] Successfully extracted {len(result['text'])} characters from {url}")
        return result["text"]

    except Exception as e:
        logger.error(f"[CRAWL] Error crawling URL: {url} — {e}", exc_info=True)
        return ""

# === Batch Crawl === #
async def batch_scrape_async(urls: List[str], formats: List[str] = ["markdown"]) -> dict:
    """
    Perform an asynchronous batch scrape and poll until completion.

    Args:
        urls (List[str]): URLs to scrape.
        formats (List[str]): Output formats.

    Returns:
        dict: Final result of the job.
    """
    try:
        print(urls)
        logger.info(f"[BATCH ASYNC] Submitting async batch job for {len(urls)} URLs...")
        job = crawler.async_batch_scrape_urls(urls, formats=formats)
        job_id = job.id
        logger.info(f"[BATCH ASYNC] Job submitted with ID: {job_id}")
        while True:
            job_status = crawler.check_batch_scrape_status(job_id)
            logger.debug(f"[BATCH ASYNC] Job status: {job_status}")

            if job_status.status == "completed":
                logger.info(f"[BATCH ASYNC] Job {job_id} completed successfully.")
                return job_status
            elif job_status.status == "failed":
                logger.error(f"[BATCH ASYNC] Job {job_id} failed.")
                return job_status
            elif job_status.status == "cancelled":
                logger.warning(f"[BATCH ASYNC] Job {job_id} was cancelled.")
                return job_status

            await asyncio.sleep(2)


    except Exception as e:
        logger.error(f"[BATCH ASYNC] Exception during async batch scrape: {e}", exc_info=True)
        return {}

# === BREAKDOWN QUERY === #
async def breakdown_query(user_query):
    """
    Breaks down the user's main query into multiple efficient and precise sub-queries 
    suitable for use as Google search queries.

    Parameters:
        user_query (str): The original query input provided by the user.

    Returns:
        List[str]: A list of at least 3 (or more) search-optimized sub-queries.
                   If the agent fails to return valid sub-queries after a retry, 
                   it returns a hardcoded error message.

    Raises:
        Logs error if both attempts fail.
    """

    prompt_template = f"""
You are a professional-grade research assistant designed to generate **efficient, Google-searchable queries** 
from a user's question. Your task is to break down the user query into **3 to 6 concise and highly specific search queries**, 
prioritized from **most relevant to least**, formatted exactly as shown.

### Format Rules:
- Only output a plain bullet list of keyword-style search queries
- Each bullet must start with a dash and a space (`- `)
- No quotes, no numbering, no headings
- No sentences or explanations—use **compact, high-impact keyword phrases**
- Return **at least 3**, preferably 4–6 if the query is broad

### Each query MUST:
- Be self-contained and independently Google-searchable
- Be specific, scoped, and use **relevant keywords**
- Avoid vague or speculative language (no “how can I”, “is it possible”, “could it be…”)
- Target different useful angles of the original query
- Reflect **descending order of relevance**, most useful ones first

### Example:

User Query:
\"\"\"can you tell me about the top trending actors?\"\"\"

Sub-Queries:
- most popular actors 2024
- trending actors IMDb
- highest grossing actors this year
- actors with most social media followers

---

Now respond to the following user query:

User Query:
\"\"\"{user_query}\"\"\"

Sub-Queries:
""".strip()

    for attempt in range(2):
        try:
            logger.info(f"[GEMINI-AGENT] Attempt {attempt + 1}: Generating search queries from user query.")

            response = await llm.ainvoke([HumanMessage(content=prompt_template)])
            raw_lines = response.content.strip().splitlines()

            sub_qs = [
                line.strip("-• ").strip()
                for line in raw_lines
                if line.strip().startswith(("-", "•")) and len(line.strip("-• ").strip().split()) >= 3
            ]

            if len(sub_qs) >= 3:
                logger.info(f"[GEMINI-AGENT] Successfully parsed {len(sub_qs)} sub-queries.")
                return sub_qs[:3]
            else:
                logger.warning(f"[GEMINI-AGENT] Invalid or insufficient sub-queries on attempt {attempt + 1}. Raw output:\n{response.content}")

        except Exception as e:
            logger.error(f"[GEMINI-AGENT] Exception while generating sub-queries: {str(e)}")

    logger.error("[GEMINI-AGENT] Failed to generate valid sub-queries after 2 attempts.")
    return ["[GEMINI-ERROR] Failed to generate sub-queries for the given user query."]

# === DATA MODELS === #
class Metadata(BaseModel):
    position: Optional[int]
    title: str
    link: HttpUrl
    redirect_link: Optional[HttpUrl]
    displayed_link: Optional[str]
    favicon: Optional[HttpUrl]
    snippet: Optional[str]
    snippet_highlighted_words: Optional[List[str]]
    source: Optional[str]

class ScrapeDataPoint(BaseModel):
    link: HttpUrl
    metadata: Metadata
    markdown: str

# === PREPARE AND VALIDATE ENRICHED SCRAPE TARGETS === #
def convert_to_datapoints(raw_items: List[dict]) -> List[ScrapeDataPoint]:
    valid_datapoints = []
    for item in raw_items:
        try:
            # Validate necessary keys exist
            if "link" not in item or "metadata" not in item or "markdown" not in item:
                logger.warning(f"[VALIDATION] Missing required fields in item: {item.get('link', '[no-link]')}")
                continue

            # Parse metadata using Pydantic model
            metadata = Metadata(**item["metadata"])
            dp = ScrapeDataPoint(link=item["link"], metadata=metadata, markdown=item["markdown"])
            valid_datapoints.append(dp)
        except Exception as e:
            logger.warning(f"[DATAPOINT VALIDATION] Skipped invalid item due to error: {e}")
    return valid_datapoints

# === PROMPT TEMPLATE === #
def build_llm_prompt(user_query: str, datapoints: List[ScrapeDataPoint]) -> str:
    blocks = [f"## USER QUERY\n\n{user_query}\n\n"]
    for idx, dp in enumerate(datapoints):
        meta = dp.metadata
        blocks.append(f"""
### DATAPOINT #{idx + 1}
**Title:** {meta.title}
**Link:** {meta.link}
**Redirect Link:** {meta.redirect_link or 'N/A'}
**Displayed Link:** {meta.displayed_link or 'N/A'}
**Source:** {meta.source or 'N/A'}
**Snippet:** {meta.snippet or 'N/A'}
**Position:** {meta.position or 'N/A'}
**Favicon:** {meta.favicon or 'N/A'}
**Highlighted Words:** {", ".join(meta.snippet_highlighted_words or [])}

### MARKDOWN CONTENT
{dp.markdown.strip()}
        """)
    # Add formatting expectations for the agent
    blocks.append("""
---


### INSTRUCTIONS FOR LLM

You are a precise, factual assistant. Analyze the provided markdowns and generate a structured summary strictly based on the information within them.

## OUTPUT FORMAT (Markdown-wrapped JSON) ##

```json
{
  "detailed_analysis": "## Overview\\n...\\n## Comparison\\n...",
  "websites": [
    {
      "favicon_url": "https://...",
      "link": "https://...",
      "snippet": "..."
    }
  ],
  "videos": [
    "https://example.com/video1",
    "https://example.com/video2"
  ]
}

                  
### FIELD DESCRIPTORS ###
	-   detailed_analysis: A concise (200–600 words) analysis in markdown format. Should explain the key insights and do comparisons/review/suggest if applicable. Ensure that it is never empty and includes highly realavant for the user query.
	-   websites: An array of useful links with:
	-   favicon_url: Taken from each datapoint’s favicon field.
	-   link: The main link from the datapoint.
	-   snippet: A helpful short description based on the markdown or snippet—must reflect actual content, not hallucinated.
	-   videos: If URLs in the content suggest YouTube or video platforms, return a list of such links.

### STRICT RULES ###
    -   Use only the content from the markdowns. DO NOT hallucinate.
	-   Ensure returned JSON is well-formed, Markdown-wrapped, and fully parseable.
	-   Do not include anything outside the code block.         
""")
    return "\n".join(blocks)

# === AGENT INVOCATION === #
async def summarize_for_user(user_query: str, datapoints: List[ScrapeDataPoint]):
        # === Build Prompt === #
    prompt_template = build_llm_prompt(user_query, datapoints)

        # === Invoke LLM === #
    logger.info("[GEMINI-SUMMARIZER-AGENT] Sending prompt to LLM...")
    response = await llm.ainvoke([HumanMessage(content=prompt_template)])
    logger.info("[GEMINI-SUMMARIZER-AGENT] Response received.")

    # === Extract JSON Block from Markdown === #
    json_block_match = re.search(r"```json\s*(\{.*?\})\s*```", response.content, re.DOTALL)
    if not json_block_match:
        logger.error("[GEMINI-SUMMARIZER-AGENT] Failed to extract JSON from model output.")
        raise ValueError("Failed to extract JSON from model output.")

    json_str = json_block_match.group(1)

    # === Try Parsing JSON === #
    try:
        parsed_response = json.loads(json_str)
        logger.info("[PARSE] Successfully parsed JSON with json.loads.")
    except Exception as e:
        logger.warning(f"[PARSE] json.loads failed: {e}, trying ast.literal_eval...")
        try:
            parsed_response = ast.literal_eval(json_str)
        except Exception as e:
            logger.error(f"[PARSE] Failed to parse JSON via ast.literal_eval: {e}")
            raise

    # === Final Schema Validation (safe access with defaults) === #
    final_output = {
        "detailed_analysis": parsed_response.get("detailed_analysis", "").strip(),
        "websites": parsed_response.get("websites", []),
        "videos": parsed_response.get("videos", []),
    }

    # === Save Output to Disk === #
    output_dir = Path("user_response")
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"user_response_result_{uuid.uuid4()}.json"
    output_path = output_dir / filename

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(final_output, f, ensure_ascii=False, indent=2)
        logger.info(f"[SAVE] Output saved to {output_path}")
    except Exception as e:
        logger.error(f"[SAVE ERROR] Failed to save output: {e}")
        raise

    return final_output



# === Define the schema for a single scraped target === #
class ScrapeTarget(BaseModel):
    link: HttpUrl
    metadata: dict


# === Process User Query and Prepare Scraping Targets === #
async def process_query(user_query: str):
    """
    Handles the full processing pipeline for a given user query:
    1. Breaks down the query into optimized sub-queries.
    2. Searches each sub-query using SERP API.
    3. Saves the search results in disk-safe JSON format.
    4. Extracts top URLs to scrape with associated metadata.
    
    Parameters:
        user_query (str): The original user-supplied query string.
    
    Returns:
        dict: {
            "task_id": str,              # UUID for the task
            "sub_queries": List[str],    # All derived sub-queries
            "to_scrape": List[dict]      # Each item contains 'link' and 'metadata'
        }
    """
    task_id = str(uuid.uuid4())
    logger.info(f"[AGENT] Starting task {task_id} for user query: '{user_query}'")
    
    # === Step 1: Break query into sub-queries === #
    sub_questions = await breakdown_query(user_query)

    # === Step 2: Prepare output directory for saving search results === #
    output_dir = "serpai_folder"
    os.makedirs(output_dir, exist_ok=True)

    to_scrape: List[dict] = []
    to_scrape_url_list: List[str] = []
    for sub_q in sub_questions:
        logger.info(f"[SUBTASK] Processing sub-query: '{sub_q}'")
        try:
            # === Step 3: Perform Google Search via SerpAPI === #
            search_results = await serp_search(sub_q)
            top_results = search_results[:2]  # Limit to top 2 results only
            top_urls = [res.get("link") for res in search_results[:2] if res.get("link")]
            to_scrape_url_list.extend(top_urls)
            # === Step 4: Persist search results to JSON for auditability === #
            wrapped_results = [{"query": sub_q, "output": top_results}]
            filename = f"search_result_{uuid.uuid4()}.json"
            filepath = os.path.join(output_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(wrapped_results, f, indent=2, ensure_ascii=False)
            logger.info(f"[SAVE] SERP results for query '{sub_q}' saved to: {filepath}")

            # === Step 5: Extract valid URLs and package with metadata === #
            for res in top_results:
                try:
                    item = ScrapeTarget(link=res["link"], metadata=res)
                    to_scrape.append(item.model_dump(mode="json"))
                except (KeyError, ValidationError) as ve:
                    logger.warning(f"[SKIP] Invalid result skipped: {ve}")

        except Exception as e:
            logger.exception(f"[ERROR] Failed to handle sub-query '{sub_q}': {e}")

    output_dir = "precrawl_results"
    os.makedirs(output_dir, exist_ok=True)

    filename = f"precrawl_result_{uuid.uuid4()}.json"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(to_scrape, f, indent=2, ensure_ascii=False)

    logger.info(f"[SAVE] SERP results for query '{sub_q}' saved to: {filepath}")

    # === Final Summary Logging === #
    logger.info(f"[SUMMARY] Total URLs collected for scraping: {len(to_scrape)}")
    logger.debug(f"[SUMMARY] URLs to scrape: {json.dumps(to_scrape, indent=2)}")

    # # # === Run the batch scrape === # # #
    logger.info(f"[SCRAPER] Starting batch scrape for {len(to_scrape)} URLs...")
    try:
        result = await batch_scrape_async(to_scrape_url_list)
        logger.info(f"[SCRAPER] Batch scrape completed successfully.")
    except Exception as scrape_err:
        logger.exception(f"[SCRAPER] Batch scrape failed: {scrape_err}")
        raise RuntimeError("Batch scrape failed.") from scrape_err

    # === Extract clean markdown + URL per document === #
    logger.info(f"[POSTPROCESS] Extracting markdown and appending to scrape targets...")
    clean_data = []
    url_to_markdown = {}

    try:
        for doc in result.data:
            url = doc.metadata.get("url")
            markdown = doc.markdown
            clean_data.append({
                "url": url,
                "markdown": markdown
            })
            if url:
                url_to_markdown[url] = markdown
        logger.info(f"[POSTPROCESS] Extracted markdown for {len(url_to_markdown)} documents.")
    except Exception as e:
        logger.exception(f"[POSTPROCESS] Failed to extract markdown from scrape result: {e}")
        raise RuntimeError("Failed to extract markdown data.") from e

    # === Append markdown to each ScrapeTarget if matching URL exists === #
    enriched_scrape_targets = []
    for item in to_scrape:
        try:
            url = item["link"]
            markdown = url_to_markdown.get(url, None)
            if markdown is not None:
                item["markdown"] = markdown.strip()
            else:
                logger.warning(f"[ENRICH] No markdown found for URL: {url}")
            enriched_scrape_targets.append(item)
        except Exception as enrich_err:
            logger.warning(f"[ENRICH] Failed to enrich item {item.get('link', '[unknown]')}: {enrich_err}")
            enriched_scrape_targets.append(item)  # Append as-is to avoid data loss

    # === Prepare output path === #
    output_dir = os.path.join("final_results")
    os.makedirs(output_dir, exist_ok=True)

    # === Write enriched result to file === #
    filename = f"final_result_{uuid.uuid4()}.json"
    output_path = os.path.join(output_dir, filename)
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(enriched_scrape_targets, f, indent=2, ensure_ascii=False)
        logger.info(f"[SAVE] Final enriched scrape targets saved to: {output_path}")
    except Exception as save_err:
        logger.exception(f"[SAVE] Failed to save final enriched results: {save_err}")

    # === Final Summary === #
    logger.info(f"[SUMMARY] Enriched scrape target count: {len(enriched_scrape_targets)}")
    logger.debug(f"[SUMMARY] Final enriched to_scrape: {json.dumps(enriched_scrape_targets, indent=2)}")

    # # await asyncio.sleep(8)
    # with open(f"./final_results/{filename}", encoding="utf-8") as f:
    #     sample_data = json.load(f)
    datapoints = convert_to_datapoints(enriched_scrape_targets)
    # logger.info(f"[SUMMARIZER-AGENT] No of datapoints: {len(datapoints)}")
    result = await summarize_for_user(user_query, datapoints=datapoints)
    logger.info(f"[AGENT] Query finished , response sent to user.")
    return result
    return {
        "task_id": task_id,
        "sub_queries": sub_questions,
        "to_scrape": enriched_scrape_targets
    }


if __name__ == "__main__":
    import sys

    # # === for testing user response summarizer === # 
    # sample_data = json.load(open("./final_results/final_result_2cf1bc79-7cac-4030-879f-7dc1dab078e5.json"))
    # datapoints = convert_to_datapoints(sample_data)
    # result = asyncio.run(summarize_for_user("Compare the latest electric vehicle models and give me a summary of their safety features.", datapoints))
    # prompt_template = build_llm_prompt("Compare the latest electric vehicle models and give me a summary of their safety features.", datapoints)
    # output_dir = os.path.join("prompts")
    # os.makedirs(output_dir, exist_ok=True)

    # # === Write enriched result to file === #
    # filename = f"prompt_builder_result_{uuid.uuid4()}.md"
    # output_path = os.path.join(output_dir, filename)
    # try:
    #     with open(output_path, "w", encoding="utf-8") as f:
    #         json.dump(prompt_template, f, indent=2, ensure_ascii=False)
    #     logger.info(f"[SAVE] Final enriched scrape targets saved to: {output_path}")
    # except Exception as save_err:
    #     logger.exception(f"[SAVE] Failed to save final enriched results: {save_err}")

    # === for testing llm === #
    # query = " ".join(sys.argv[1:]) or "Compare the latest electric vehicle models and give me a summary of their safety features."
    # sub_question = asyncio.run(breakdown_query(query))
    # print(sub_question)

    # === For Testing Firecrawl batch urls === #
    # urls = sys.argv[1:] or [
    #     "https://quii.gitbook.io/learn-go-with-tests",
    #     "https://docs.copilotkit.ai/coagents/tutorials/ai-travel-app"
    # ]
    # print("URLs to scrape:", urls)

    # === Run the batch scrape === #
    # result = asyncio.run(batch_scrape_async(to_scrape)
    # === Extract clean markdown + URL per document === #
    # clean_data = []
    # for doc in result.data:
    #     clean_data.append({
    #         "url": doc.metadata.get("url"),
    #         "markdown": doc.markdown
    #     })

    # # === Create unique chat ID === #
    # chat_id = str(uuid.uuid4())[:8]  # or use a fixed value for testing

    # === Prepare output path === #
    # output_dir = os.path.join("firecrawl_results", f"chat_{chat_id}")
    # os.makedirs(output_dir, exist_ok=True)

    # # # === Write result to file === #
    # output_path = os.path.join(output_dir, "results.json")
    # with open(output_path, "w", encoding="utf-8") as f:
    #     json.dump(clean_data, f, indent=2, ensure_ascii=False)

    # logger.info(f"[BATCH ASYNC] Results saved to: {output_path}")
    # # === END of Run the BATCH SCRAPE === #

    # === For Testing Serp AI === #
    # query = " ".join(sys.argv[1:]).strip()

    # if not query:
    #     logger.error("No query provided. Please pass a search term as a command-line argument.")
    #     sys.exit(1)

    # logger.info(f"[MAIN] Received query: {query}")

    # # Run the async search
    # results = asyncio.run(serp_search(query))

    # # Prepare output directory
    # output_dir = "serpai_folder"
    # os.makedirs(output_dir, exist_ok=True)

    # # Create unique filename
    # filename = f"search_result_{uuid.uuid4()}.json"
    # filepath = os.path.join(output_dir, filename)

    # # Save results to file
    # try:
    #     with open(filepath, "w", encoding="utf-8") as f:
    #         json.dump(results, f, indent=2, ensure_ascii=False)
    #     logger.info(f"[SAVE] Search results saved to: {filepath}")
    # except Exception as e:
    #     logger.exception(f"[ERROR] Failed to save search results: {e}")

    # === For Testing the process in full === #
    query = " ".join(sys.argv[1:]) or "Compare the latest electric vehicle models and give me a summary of their safety features."
    asyncio.run(process_query(query))
