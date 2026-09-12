# Context Lens

> **The page becomes the prompt.**

Context Lens is a browser-native AI agent designed to bring intelligence directly into the environment where work happens.

Knowledge workers constantly leave their workflow to search for information, ask an AI assistant, and manually copy answers back into forms and applications.

Context Lens removes that context switching.

Instead of opening a separate chatbot and explaining what you're looking at, the agent uses the webpage itself as context. It can understand the surrounding record, identify missing information, research it on the web, provide evidence, and return the answer directly into the workflow.

## The Problem

Modern knowledge work often looks like this:

1. Open a CRM or business application.
2. Discover a missing piece of information.
3. Open a search engine or AI assistant.
4. Explain the context.
5. Research the answer.
6. Verify the information.
7. Copy the result.
8. Return to the original application.
9. Paste it into the correct field.

The information is rarely the hard part.

**The context switching is.**

## The Idea

Context Lens changes the interaction model.

Instead of:

**Work → Open AI → Explain context → Research → Copy → Return → Paste**

we want:

**Work → Context Lens understands → Research → Evidence → Action**

The environment becomes part of the agent's prompt.

## Demo

The current prototype demonstrates an AI-powered CRM workflow using an NVIDIA account record.

A user can research missing account fields such as:

- CEO
- Founded
- Headquarters
- Revenue

The agent researches the missing information and enriches the record while preserving the evidence behind each result.

### Evidence, not guesses

Every researched value can be inspected through its evidence panel, showing the source and reasoning behind the returned information.

## Architecture

Context Lens combines several components:

- **OpenAI** for agent reasoning and contextual understanding
- **Exa** for live web research
- **OpenRouter** for model access and routing
- **Python** backend for research orchestration
- **HTML / CSS / JavaScript** for the browser-native interface

The architecture is intentionally lightweight so the agent can remain close to the user's workflow.

## Why Context Matters

A standalone chatbot starts with very little context.

The user has to explain:

> "I'm looking at an NVIDIA account in my CRM. The CEO field is empty. Find the current CEO and tell me where you found it."

Context Lens starts from the environment itself.

The agent can already see:

- The account being viewed
- The field being researched
- The surrounding company information
- The user's current workflow

That makes the interaction shorter, more natural, and less error-prone.

## Example

A CRM record contains:

```text
Company: NVIDIA
CEO: [missing]
Founded: 1993
Headquarters: Santa Clara, California
The user invokes Context Lens on the missing CEO field.
The agent:
Understands the field and surrounding account context.
Searches the web using Exa.
Extracts the relevant information.
Associates the answer with its source.
Writes the result back into the workflow.
Makes the evidence available for inspection.
Result:
CEO: Jensen Huang
✓ Researched
What Makes It Different
Context Lens is not simply another browser automation tool.
The central idea is where the agent lives.
Traditional AI assistants require users to leave their workflow and provide context.
Context Lens embeds intelligence into the workflow itself.
The page becomes the prompt.
Project Status
This repository contains the hackathon prototype for Context Lens.
The prototype focuses on demonstrating the interaction model, contextual research workflow, evidence-backed enrichment, and browser-native experience.
Built For
Agents, Everywhere: Bots, Channels, & More
Global Hackathon
AI Tinkerers × OpenAI
Author
Built by Sakshi Borkar
Team: OUT OF CONTEXT
