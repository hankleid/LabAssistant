import asyncio
import json
import re
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage, UserMessage, ToolResultBlock
import time

prompts_dir, tools_dir = "prompts", "tools"
system_prompt = open(f'{prompts_dir}/system_prompt.txt', 'r').read()
make_plan_prompt = open(f'{prompts_dir}/make_plan_prompt.txt', 'r').read()
revise_plan_prompt = open(f'{prompts_dir}/revise_plan_prompt.txt', 'r').read()
gen_tools_prompt = open(f'{prompts_dir}/generate_tools_prompt.txt', 'r').read()
revise_tools_prompt = open(f'{prompts_dir}/revise_tools_prompt.txt', 'r').read()
gen_exec_checkpoints_prompt = open(f'{prompts_dir}/generate_execution_checkpoints_prompt.txt', 'r').read()
execute_phase_prompt = open(f'{prompts_dir}/execute_plan_prompt.txt').read()
interpret_results_prompt = open(f'{prompts_dir}/interpret_results_prompt.txt').read()

full_planning_prompt = f"You are measuring unknown physics in a known experimental system.\n\n{make_plan_prompt}"
full_revise_plan_prompt = f"Read PLAN.md carefully in its entirety. Your task is to critically audit it on three axes and then revise it in-place. Do not summarize — edit PLAN.md directly to fix every problem you identify.\n\n---\n\n{revise_plan_prompt}"
full_gen_tools_prompt = f"{gen_tools_prompt}\n\nSuggested Python modules: numpy, qutip, scipy.\n\nUse `conda activate 3p12` to use the right environment.\n\nAll your tools should go in LabAssistant/tools/."

def log(txt, path='log.txt'):
    with open(path, "a+") as f:
        f.write(txt)

def fmt_tool_call(name, inp):
    """Format a tool invocation line."""
    primary = {
        "Bash": "command", "Read": "file_path", "Edit": "file_path",
        "Write": "file_path", "Glob": "pattern", "Grep": "pattern",
        "WebSearch": "query", "WebFetch": "url",
    }
    if name == "Skill":
        skill_name = inp.get("skill", "")
        args = inp.get("args", "")
        return f"  [Skill] {skill_name}" + (f' "{args}"' if args else "")
    key = primary.get(name)
    value = inp.get(key, "") if key else ""
    return f"  [{name}] {value}" if value else f"  [{name}] {inp}"

def to_text(content):
    """Normalise tool result content to a plain string."""
    if content is None:
        return ""
    if isinstance(content, list):
        text = "\n".join(
            item.get("text", str(item)) if isinstance(item, dict) else str(item)
            for item in content
        )
    else:
        text = str(content)
    # Strip injected system instructions from tool results
    lines = [l for l in text.splitlines() if not l.strip().startswith("REMINDER:")]
    return "\n".join(lines)

def fmt_tool_result(name, content, is_error):
    """Format a tool result block."""
    prefix = "  !!" if is_error else "  ->"
    text = to_text(content)

    if not text.strip():
        return f"{prefix} (empty)"

    if name == "WebSearch":
        return fmt_websearch_result(prefix, text)

    if name in ("Read", "Skill"):
        return ""

    indented = "\n".join(f"       {l}" for l in text.splitlines())
    return f"{prefix} [{name}]:\n{indented}"

def fmt_websearch_result(prefix, text):
    """Parse and pretty-print web search results."""
    results = []

    # 1. Try JSON array (most common format from the tool)
    try:
        data = json.loads(text)
        if isinstance(data, list):
            for item in data:
                title   = item.get("title", "").strip()
                url     = item.get("url", item.get("link", "")).strip()
                snippet = item.get("snippet", item.get("description", "")).strip()
                if url:
                    results.append((title, url, snippet))
    except (json.JSONDecodeError, AttributeError):
        pass

    # 2. Markdown links: [Title](URL)
    if not results:
        for title, url in re.findall(r'\[([^\]]+)\]\((https?://[^)]+)\)', text):
            results.append((title.strip(), url.strip(), ""))

    # 3. Numbered blocks with a URL line
    if not results:
        for block in re.split(r'\n(?=\d+[\.\)])', text.strip()):
            url_match = re.search(r'https?://[^\s"\'}>]+', block)
            if not url_match:
                continue
            url = url_match.group(0).rstrip('.,)')
            first_line = re.sub(r'^\d+[\.\)]\s*', '', block.splitlines()[0]).strip()
            snippet_lines = [
                l.strip() for l in block.splitlines()[1:]
                if l.strip() and url not in l
            ]
            results.append((first_line, url, " ".join(snippet_lines)))

    if results:
        lines = [f"{prefix} {len(results)} result(s):"]
        for i, (title, url, snippet) in enumerate(results, 1):
            lines.append(f"       {i}. {title}")
            lines.append(f"          {url}")
            if snippet:
                lines.append(f"          {snippet}")
        return "\n".join(lines)

    # Fallback: plain indented text
    indented = "\n".join(f"       {l}" for l in text.splitlines())
    return f"{prefix} search result:\n{indented}"


async def start_agent(user_prompt):
    tool_names: dict[str, str] = {}  # tool_use_id -> tool name

    log("\n\n-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-\n\n")

    # Agentic loop: streams messages as Claude works
    async for message in query(
        prompt= user_prompt,
        options=ClaudeAgentOptions(
            model='claude-sonnet-4-6',
            system_prompt=system_prompt,
            setting_sources=["user", "project"],
            allowed_tools=["Skill", "Read", "Edit", "Bash", "Glob", "Grep", "WebSearch", "WebFetch"],
            permission_mode="acceptEdits",
        ),
    ):
        # print("message")
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text") and block.text:
                    log(">> " + block.text.replace("\n", "\n   "))
                elif hasattr(block, "name"):
                    tool_names[block.id] = block.name
                    log(fmt_tool_call(block.name, block.input))

        elif isinstance(message, UserMessage):
            if isinstance(message.content, list):
                for block in message.content:
                    if isinstance(block, ToolResultBlock):
                        name = tool_names.get(block.tool_use_id, "Tool")
                        result = fmt_tool_result(name, block.content, block.is_error)
                        if result:
                            log(result)

        elif isinstance(message, ResultMessage):
            cost = f"  ${message.total_cost_usd:.4f}" if message.total_cost_usd else ""
            log(f"\nDone ({message.subtype}){cost}")


print("starting...")
# asyncio.run(start_agent(full_planning_prompt))
# asyncio.run(start_agent(full_revise_plan_prompt))
# asyncio.run(start_agent(full_gen_tools_prompt))
# asyncio.run(start_agent(revise_tools_prompt))
# asyncio.run(start_agent(gen_exec_checkpoints_prompt))
# asyncio.run(start_agent(execute_phase_prompt))
asyncio.run(start_agent(interpret_results_prompt))

