"""CrewAI hierarchical crew of 9 agents. Manager LLM = Opus 4.7."""
from __future__ import annotations
from typing import Any, Dict, List
from crewai import Agent, Crew, Process, Task
from crewai.llm import LLM

from .config import INSFORGE_GATEWAY_BASE, MODEL_BY_AGENT, MODEL_MANAGER, RuntimeConfig
from .tools import shell, files, git as git_tool, browser, vscode_bridge


def _llm(model: str, api_key: str) -> LLM:
    # CrewAI uses LiteLLM under the hood; openai/ prefix routes through OpenAI-compat endpoint.
    return LLM(
        model=f"openai/{model}",
        api_base=INSFORGE_GATEWAY_BASE,
        api_key=api_key,
        temperature=0.2,
    )


AGENT_BLUEPRINT = [
    ("architect",   "Architect",   "Design overall system structure, file layout, module boundaries."),
    ("planner",     "Planner",     "Decompose user goal into ordered actionable tasks."),
    ("researcher",  "Researcher",  "Look up docs, APIs, web for facts the crew needs."),
    ("implementer", "Implementer", "Translate plan into concrete code-synthesis directives."),
    ("coder",       "Coder",       "Make precise file-level edits and additions."),
    ("builder",     "Builder",     "Compile, bundle, install deps, run the project."),
    ("reviewer",    "Reviewer",    "Critique code: bugs, security, style, dead paths."),
    ("tester",      "Tester",      "Write and run tests; report failures."),
    ("verifier",    "Verifier",    "End-to-end verify in browser/CLI; confirm user goal met."),
]


def build_crew(cfg: RuntimeConfig, bridge_send) -> Crew:
    """bridge_send: callable(method:str, params:dict) -> Any — IPC to VS Code extension."""
    tool_set = [
        shell.make_tool(cfg),
        files.make_read_tool(cfg),
        files.make_write_tool(cfg),
        files.make_list_tool(cfg),
        git_tool.make_tool(cfg),
        browser.make_tool(cfg),
        vscode_bridge.make_tool(bridge_send),
    ]

    agents: List[Agent] = []
    for role_key, role_name, goal in AGENT_BLUEPRINT:
        model = MODEL_BY_AGENT[role_key]
        agents.append(Agent(
            role=role_name,
            goal=goal,
            backstory=f"You are the {role_name} of the Surya AI crew. Stay in your role.",
            llm=_llm(model, cfg.api_key),
            tools=tool_set,
            allow_delegation=False,
            verbose=False,
        ))

    manager = Agent(
        role="Manager",
        goal="Orchestrate the 9 specialists to fulfil the user's request end to end.",
        backstory="Hierarchical lead. Delegate, integrate, finish.",
        llm=_llm(MODEL_MANAGER, cfg.api_key),
        allow_delegation=True,
        verbose=False,
    )

    return Crew(
        agents=agents,
        manager_agent=manager,
        process=Process.hierarchical,
        verbose=False,
    )


def run_task(cfg: RuntimeConfig, bridge_send, user_goal: str) -> Dict[str, Any]:
    crew = build_crew(cfg, bridge_send)
    task = Task(
        description=user_goal,
        expected_output="Working result that satisfies the user's goal, with files written "
                        "and a brief summary of what was done and how to run it.",
        agent=crew.manager_agent,
    )
    crew.tasks = [task]
    result = crew.kickoff()
    return {"output": str(result), "tasks_completed": len(crew.tasks)}
