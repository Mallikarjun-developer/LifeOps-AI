# Devpost submission draft — customize after testing

## Project name
LifeOps AI — Voice-first Autonomous Day Planner

## Tagline
An Alexa+-style voice assistant that turns everyday requests into real tasks, plans your day, and replans when priorities change.

## Project description
LifeOps AI addresses the gap between talking about productivity and actually organizing work. Users speak or type natural-language commands, and the application invokes task-management tools over the Model Context Protocol (MCP), persists changes to SQLite, and visualizes an updated daily plan. The schedule engine prioritizes deadlines, respects configurable working hours, and explicitly identifies tasks that cannot fit. A responsive dashboard and spoken responses make each action visible and understandable.

The experience is a **simulated Alexa+ web application**, not a deployed Alexa+ add-on. It demonstrates the interaction pattern through browser speech recognition, an MCP client, and a self-hosted MCP Streamable HTTP server.

## Primary track
Alexa+ — simulated Alexa+ experience with a real MCP backend and web client.

## Mini challenge
Do not select AWS Builder unless an actual qualifying AWS service/tool has been used and documented. Do not select Open Source solely because this primary project is public; that challenge requires a separate qualifying contribution or project.

## Tools and product feedback — adapt to actual experience

- **MCP Python SDK / FastMCP:** Used for Streamable HTTP tool server and client sessions. [Fill in: what worked well, friction, onboarding, would use again and why.]
- **FastAPI:** Used for REST endpoints and web hosting. [Fill in actual feedback.]
- **Browser Web Speech API:** Used for push-to-talk recognition and spoken replies. [Fill in actual compatibility and usability feedback.]
- **SQLite:** Used for persistent task storage. [Fill in actual feedback.]
- **Optional OpenAI API:** Include only if configured and tested; explain purpose and feedback.

## Honest limitations
No official Alexa+ device or account integration, no always-on wake word, no third-party calendar integration, no authentication, no external notifications. Complex natural-language time changes require the optional model integration or manual entry.

## 2:35 demo video script

**0:00–0:18 — Problem:** “Planning isn't the hard part; keeping plans up to date is. LifeOps turns voice requests into actions.”

**0:18–0:40 — Architecture:** “This is a simulated Alexa+-style experience, using browser voice input, a real MCP Streamable HTTP tool server, and persistent task storage.”

**0:40–1:10 — Create:** Press the microphone and say “Add prepare interview high priority.” Show the new task appear.

**1:10–1:32 — Add:** Say “Add finish hackathon submission.” Show both tasks.

**1:32–1:58 — Plan:** Say “Plan my day.” Show the schedule populate. Explain conflicts if any.

**1:58–2:18 — Adapt:** Say “Complete task 1.” Replan and show the completed task removed from the schedule.

**2:18–2:35 — Closing:** Show the MCP server running and briefly describe the user value.

Do not record a claim about a feature you haven't verified. Ensure public video URL, repository access, English-language submission, and deadline compliance.

## Friction log template (fill with real events only)

- Task attempted:
- Steps taken:
- Expected result:
- Actual result:
- Severity:
- Workaround:
- Suggested improvement:
