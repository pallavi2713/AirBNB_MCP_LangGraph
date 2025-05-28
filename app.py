import asyncio
from typing import Dict, TypedDict
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import END, Graph
from mcp_use import MCPAgent, MCPClient
import os

class AgentState(TypedDict):
    input: str
    response: str
    summary: str
    is_valid: bool

async def safe_close_client(client):
    if client:
        try:
            await asyncio.wait_for(client.close_all_sessions(), timeout=5.0)
        except Exception:
            pass  

async def generate_response(state: AgentState) -> Dict:
    try:
        prompt = (
            f"Provide exactly 3 listings for {state['input']} with:\n"
            f"1. Property name\n2. Price per night in INR\n"
            f"3. Exact location\n4. 3 key amenities\n"
            f"Format each listing clearly with bullet points"
        )
        response = await agent.run(prompt)
        return {
            **state,
            "response": response,
            "is_valid": True
        }
    except Exception:
        return {
            **state,
            "response": "Error: Could not retrieve listings. Please try again.",
            "is_valid": False
        }

async def summarize_response(state: AgentState) -> Dict:
    if not state.get("is_valid", False):
        return {**state, "summary": ""}

    try:
        summary = await llm.ainvoke(
            f"Create a brief summary of these listings to choose best option: {state['response']}"
        )
        return {**state, "summary": summary.content}
    except Exception:
        return {**state, "summary": ""}

async def process_query():
    load_dotenv()
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        print("Missing GROQ_API_KEY")
        return

    client = None
    try:
        client = MCPClient.from_config_file("browser_mcp.json")

        global llm, agent
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.5,
            api_key=groq_key,
            max_retries=5
        )

        agent = MCPAgent(
            llm=llm,
            client=client,
            max_steps=15,
            memory_enabled=True,
            system_prompt="""
            You are a travel assistant. When asked for listings:
            1. Provide exactly 3 options
            2. Format each with:
               • Property Name
               • Price/night (INR)
               • Location
               • 2 amenities
            3. Be factual and concise
            """
        )

        query = input("\nEnter location for listings (or 'quit'): ").strip()
        if not query or query.lower() == 'quit':
            return

        workflow = Graph()
        workflow.add_node("generate", generate_response)
        workflow.add_node("summarize", summarize_response)
        workflow.add_conditional_edges("generate", lambda x: "summarize" if x["is_valid"] else END)
        workflow.add_edge("summarize", END)
        workflow.set_entry_point("generate")

        app = workflow.compile()
        result = await app.ainvoke({
            "input": query,
            "response": "",
            "summary": "",
            "is_valid": False
        })

        print(f"\n=== Here are the listings for: {result["input"]} ===")
        for k, v in result.items():
            print(f"{k}: {v}\n")

        print("\n=== LISTINGS ===")
        print(result.get("response", "No listings could be generated"))

        if result.get("summary"):
            print("\n=== SUMMARY ===")
            print(result["summary"])

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        await safe_close_client(client)

async def main():
    try:
        await process_query()
    except KeyboardInterrupt:
        print("\nOperation cancelled")
    finally:
        print("\nCleanup complete")

if __name__ == "__main__":
    asyncio.run(main())
