# Travel Assistant using LangGraph, MCP, Groq & Airbnb MCP Server
This project is a command-line-based travel assistant that takes a location as input and returns exactly 3 Airbnb-style listings with details like property name, price per night, location, and key amenities. It also generates a short summary to help users choose the best stay.

🔍 What Is This Project About?
This app is built using the Model Context Protocol (MCP), which allows Large Language Models (LLMs) to interact intelligently with tools like APIs, browsers, and other services.

## We use:

LangChain + LangGraph: For managing multi-step, stateful workflows

Groq + LLaMA-3: For ultra-fast and accurate LLM inference

MCP + @openbnb/mcp-server-airbnb: To allow the LLM to browse and fetch listings

Playwright (optional): For browser-based MCP interactions (can be expanded)

## What Is MCP?
Model Context Protocol (MCP) is a new standard that allows LLMs to:

Open real browser sessions

Access custom API wrappers

Interact with real-world data/tools safely

Run sandboxed, repeatable tool-based workflows

With MCP, your agent doesn't just generate text—it acts.

In this project, MCP powers the connection to an Airbnb-style listing tool, allowing the LLM to "see" real listings data via a virtualized browser/API interface.

## Tools & Components Used
1. @openbnb/mcp-server-airbnb
This is an MCP server plugin that simulates fetching Airbnb-like listings.

It bypasses robot.txt rules with --ignore-robots-txt to allow scraping or mock browsing.
MCPAgent uses this server to retrieve listings for your input query (like “Goa” or “Delhi”).

2. playwright (optional server)
While not used in this run, @playwright/mcp is an MCP browser tool that enables general web browsing via a headless browser session.
You can add it to your config to allow the agent to browse real websites through controlled and secure interactions.

3. MCPAgent & MCPClient
MCPClient launches the defined servers (like Airbnb).
MCPAgent wraps around LangChain’s agent to enable LLM → MCP tool interaction.

4. LangGraph
A graph-based orchestration system from LangChain.
Allows modeling of agent steps using nodes and conditional flows.

In this project:

Node 1: Generate listings via MCP
Node 2: Summarize the listings via Groq

Flow: If listings are valid → summarize → end

5. Groq + LLaMA-3
We use ChatGroq as the LLM provider.
Groq supports blazing-fast LLaMA-3 models.
It performs both listing formatting and summary generation.

## ⚙️ How It Works (Step-by-Step)
User Input: You’re asked for a location (e.g., “Goa”).

Graph Workflow Begins:
generate_response node runs:
Constructs a structured prompt asking for 3 listings
MCPAgent queries @openbnb/mcp-server-airbnb to get listings
If response is valid, graph continues

Summarization:

A short description of the listings is generated via Groq (LLaMA-3)

## Output:

Listings are printed
Summary is printed (optional)

