import requests
import aiohttp
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()
TAVILY_KEY = os.getenv("TAVILY_KEY")


class AiSearch:
    def __init__(self, query: str):
        self.query = query

    def search(self):
        response = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": TAVILY_KEY,
                "query": self.query,
                "max_results": 5,
                "include_raw_content": True,
            },
        )
        results = response.json().get("results", [])
        return results

    def build_context(self, results):
        all_text = ""
        for i, item in enumerate(results, 1):
            title = item.get("title", "No Title")
            content = item.get("raw_content") or item.get("content", "")
            all_text += f"[{i}] {title}\n{content[:300]}\n\n"
        return all_text

    async def fetch_answer(self, context=""):
        try:
            short_context = context[:3000]

            prompt = self.query
            if context:
                prompt = f"Context:\n{short_context}\n\nQuestion: {self.query}\nAnswer concisely."

            payload = {
                "prompt": prompt,
                "network": True,
                "stream": False,
                "system": {
                    "userId": "#/chat/1722576084617",
                    "withoutContext": False,
                },
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.binjie.fun/api/generateStream",
                    headers={"Content-Type": "application/json"},
                    json=payload,
                ) as response:
                    return await response.text()

        except Exception as e:
            return f"Error: {e}"


# usage
async def main():
    query = input("Enter your question: ").strip()
    if not query:
        return

    ai = AiSearch(query)

    results = ai.search()
    if not results:
        print("No results found")
        return

    context = ai.build_context(results)
    answer = await ai.fetch_answer(context)

    print(answer)


asyncio.run(main())
#done its work
