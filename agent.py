import logging_

from claude_code_sdk import ClaudeCodeOptions, query, AssistantMessage, UserMessage, TextBlock, ToolUseBlock, \
    ToolResultBlock, ResultMessage


class Agent:
    def __init__(self, name, sys_prompt, cwd, model):
        self._logger = logging_.get_logger("agent " + name)

        self._options = ClaudeCodeOptions(
            system_prompt=sys_prompt,
            cwd=cwd, model=model,
            allowed_tools=["Edit", "Glob", "Grep", "LS", "Read", "Write"],
            disallowed_tools=["Bash", "MultiEdit", "NotebookEdit", "NotebookRead", "Task", "TodoWrite", "WebFetch",
                              "WebSearch"],
            permission_mode='acceptEdits'
        )
        self._logger.debug(self._options)

    async def query(self, prompt):
        self._logger.info(f"Starting new query with prompt: {prompt}")
        last_tool_read = False
        last_tool_grep = False

        async for message in query(prompt=prompt, options=self._options):
            if isinstance(message, AssistantMessage):
                content = message.content[0]
                if isinstance(content, TextBlock):
                    self._logger.debug(f"Text message received: '{content.text}'")
                elif isinstance(content, ToolUseBlock):
                    last_tool_read = content.name in "Read"
                    last_tool_grep = content.name in "Grep"
                    if content.name in ["Read", "Write"]:
                        self._logger.debug(f"Tool use requested: {content.name} (File: {content.input['file_path']})")
                    elif content.name == "LS":
                        self._logger.debug(f"Tool use requested: {content.name} (Path: {content.input['path']})")
                    elif content.name == "TodoWrite":
                        todos = [(f"[{'x' if todo['status'] == 'completed' else ' '}]  " + todo["content"]) for todo in
                                 content.input["todos"]]
                        self._logger.debug("Tool use requested: ToDo update\n" + "\n  ".join(todos[::-1]))
                    else:
                        self._logger.debug(f"Tool use requested: {content.name} (input: {content.input})")
                else:
                    self._logger.debug(f"Message received: {message}")

            elif isinstance(message, UserMessage):
                content = message.content[0]
                if isinstance(content, ToolResultBlock):
                    if last_tool_read:
                        self._logger.debug(f"Tool use responded: Read with {'' if content.is_error else 'no '}errors")
                    elif last_tool_grep:
                        self._logger.debug(f"Tool use responded: Grep with {'' if content.is_error else 'no '}errors")
                    else:
                        self._logger.debug(f"Tool use responded: {content.content}")

            elif isinstance(message, ResultMessage):
                successful = "successful" if message.subtype == "success" else "not successful"
                self._logger.debug(f"Result {successful}: '{message.result}'")
                return message.result

            else:
                self._logger.debug(f"Message received: {message}")

        return None
