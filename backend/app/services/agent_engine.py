
from ddgs import DDGS
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode


# ==========================================
# 1. RESEARCH PLANNING
# ==========================================

def create_research_plan(goal: str) -> dict:

    if not isinstance(goal, str) or not goal.strip():
        return {
            "status": "invalid_goal",
            "message": "Research goal cannot be empty."
        }

    goal = goal.strip()

    research_tasks = [
        {
            "task_id": 1,
            "action": "identify_topics",
            "description": "Identify the main topics and concepts related to the research goal."
        },
        {
            "task_id": 2,
            "action": "collect_information",
            "description": "Collect information from relevant sources."
        },
        {
            "task_id": 3,
            "action": "compare_findings",
            "description": "Compare findings and identify similarities and differences."
        },
        {
            "task_id": 4,
            "action": "connect_knowledge",
            "description": "Connect new findings with existing memories."
        },
        {
            "task_id": 5,
            "action": "generate_report",
            "description": "Prepare a research report with evidence and source references."
        }
    ]

    return {
        "status": "plan_created",
        "research_goal": goal,
        "total_tasks": len(research_tasks),
        "research_plan": research_tasks
    }


# ==========================================
# 2. URL CLEANING
# ==========================================

def clean_url(url: str) -> str:

    try:
        parsed = urlparse(url)

        if parsed.scheme.lower() not in ("http", "https"):
            return ""

        host = (parsed.hostname or "").lower()

        if not host:
            return ""

        if (
            (host == "bing.com" or host.endswith(".bing.com"))
            and parsed.path.startswith("/aclick")
        ):
            return ""

        blocked_hosts = [
            "doubleclick.net",
            "googleadservices.com",
            "googlesyndication.com"
        ]

        if any(
            host == blocked or host.endswith("." + blocked)
            for blocked in blocked_hosts
        ):
            return ""

        tracking_parameters = {
            "utm_source",
            "utm_medium",
            "utm_campaign",
            "utm_term",
            "utm_content",
            "gclid",
            "fbclid",
            "msclkid"
        }

        clean_query = [
            (key, value)
            for key, value in parse_qsl(parsed.query)
            if key.lower() not in tracking_parameters
        ]

        clean_path = parsed.path.rstrip("/") or "/"

        return urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            clean_path,
            "",
            urlencode(clean_query),
            ""
        ))

    except Exception:
        return ""


# ==========================================
# 3. SEARCH RESULT PROCESSING
# ==========================================

def process_search_results(search_results, max_results):

    results = []
    seen_urls = set()
    domain_counts = {}

    for item in search_results:

        original_url = item.get("href", "")
        cleaned_url = clean_url(original_url)

        if not cleaned_url or cleaned_url in seen_urls:
            continue

        domain = urlparse(cleaned_url).hostname

        if domain_counts.get(domain, 0) >= 2:
            continue

        title = (item.get("title") or "").strip()
        snippet = (item.get("body") or "").strip()

        if not title or not snippet:
            continue

        seen_urls.add(cleaned_url)
        domain_counts[domain] = domain_counts.get(domain, 0) + 1

        results.append({
            "title": title,
            "url": cleaned_url,
            "source_domain": domain,
            "snippet": snippet
        })

        if len(results) >= max_results:
            break

    return results


# ==========================================
# 4. INFORMATION COLLECTION
# ==========================================

def collect_information(
    query: str,
    max_results: int = 5
) -> dict:

    if not isinstance(query, str) or not query.strip():
        return {
            "status": "invalid_query",
            "results": []
        }

    if (
        not isinstance(max_results, int)
        or isinstance(max_results, bool)
        or max_results < 1
        or max_results > 20
    ):
        return {
            "status": "invalid_max_results",
            "message": "max_results must be between 1 and 20.",
            "results": []
        }

    original_query = query.strip()

    # Prepare fallback queries
    search_queries = [original_query]

    simplified_query = " ".join(
        word for word in original_query.split()
        if word.lower() not in {
            "recent", "latest", "developments",
            "development", "in", "the", "of",
            "about", "and", "for"
        }
    )

    if simplified_query and simplified_query.lower() != original_query.lower():
        search_queries.append(simplified_query)

    all_results = []
    searched_queries = []

    try:

        with DDGS(timeout=20) as search:

            for search_query in search_queries:

                searched_queries.append(search_query)

                try:
                    search_results = search.text(
                        search_query,
                        max_results=max_results * 3,
                        backend="bing"
                    )

                    results = process_search_results(
                        search_results,
                        max_results
                    )

                    for result in results:
                        if result["url"] not in {
                            item["url"] for item in all_results
                        }:
                            all_results.append(result)

                    if len(all_results) >= max_results:
                        break

                except Exception:
                    continue

        if all_results:
            return {
                "status": "success",
                "query": original_query,
                "searched_queries": searched_queries,
                "total_results": len(all_results[:max_results]),
                "results": all_results[:max_results]
            }

        return {
            "status": "no_results",
            "query": original_query,
            "searched_queries": searched_queries,
            "message": "No suitable search results were found.",
            "results": []
        }

    except Exception as error:

        return {
            "status": "search_failed",
            "query": original_query,
            "message": str(error),
            "results": []
        }


# ==========================================
# 5. LOCAL TESTING
# ==========================================

if __name__ == "__main__":

    print("\n--- RESEARCH PLANNING TEST ---")

    print(create_research_plan(
        "Research recent developments in Generative AI"
    ))

    print("\n--- INFORMATION COLLECTION TEST ---")

    print(collect_information(
        "Recent developments in Generative AI",
        max_results=5
    ))
