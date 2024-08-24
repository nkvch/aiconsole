#
# MIT License
#
# Copyright (c) 2023 Killian Lucas
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#     ____                      ____      __                            __
#    / __ \____  ___  ____     /  _/___  / /____  _________  ________  / /____  _____
#   / / / / __ \/ _ \/ __ \    / // __ \/ __/ _ \/ ___/ __ \/ ___/ _ \/ __/ _ \/ ___/
#  / /_/ / /_/ /  __/ / / /  _/ // / / / /_/  __/ /  / /_/ / /  /  __/ /_/  __/ /
#  \____/ .___/\___/_/ /_/  /___/_/ /_/\__/\___/_/  / .___/_/   \___/\__/\___/_/
#      /_/                                         /_/
#
# This file has been taken from the wonderful project "open-interpreter" by Killian Lucas
# https://github.com/KillianLucas/open-interpreter
#

import ast
import asyncio
import logging
import queue
import re
import threading
import traceback
from typing import Any, AsyncGenerator

from jupyter_client.asynchronous.client import AsyncKernelClient
from jupyter_client.manager import AsyncKernelManager

from aiconsole.core.assets.materials.material import Material
from aiconsole.core.code_running.code_interpreters.base_code_interpreter import (
    BaseCodeInterpreter,
)
from aiconsole_toolkit.env import get_current_project_venv_python_path

_log = logging.getLogger(__name__)


async def start_new_async_kernel(
    startup_timeout: float = 60, kernel_name: str = "python", **kwargs: Any
) -> tuple[AsyncKernelManager, AsyncKernelClient]:
    """Start a new kernel, and return its Manager and Client"""
    km = AsyncKernelManager(kernel_name=kernel_name)
    if km.kernel_spec is not None:
        km.kernel_spec.argv = [
            str(get_current_project_venv_python_path()),
            "-m",
            "ipykernel_launcher",
            "-f",
            "{connection_file}",
        ]
    await km.start_kernel(**kwargs)
    kc = km.client()
    kc.start_channels()
    try:
        await kc.wait_for_ready(timeout=startup_timeout)
    except RuntimeError:
        kc.stop_channels()
        await km.shutdown_kernel()
        raise

    return (km, kc)


class Python(BaseCodeInterpreter):
    async def initialize(self):
        self.km, self.kc = await start_new_async_kernel(
            env=self.get_environment_variables(),
            # executable=str(get_current_project_venv_python_path()),
            # argv=[f"{get_current_project_venv_python_path()}", "-m", "ipykernel_launcher", "-f", "{connection_file}"],
        )
        self.listener_thread = None
        self.finish_flag = False

        # DISABLED because sometimes this bypasses sending it up to us for some reason!
        # Give it our same matplotlib backend
        # backend = matplotlib.get_backend()

        # Use Agg, which bubbles everything up as an image.
        # Not perfect (I want interactive!) but it works.
        backend = "Agg"

        code = f"""
import matplotlib
matplotlib.use('{backend}')
        """.strip()
        async for _ in self.run(code, []):
            pass

    async def terminate(self):
        self.kc.stop_channels()
        await self.km.shutdown_kernel()

    async def run(self, code: str, materials: list[Material]) -> AsyncGenerator[str, None]:
        self.finish_flag = False
        try:
            preprocessed_code = preprocess_python(code, materials)
            message_queue: queue.Queue[Any] = queue.Queue()
            self._execute_code(preprocessed_code, message_queue)
            async for output in self._capture_output(message_queue):
                yield output
        except GeneratorExit:
            raise  # gotta pass this up!
        except Exception:
            content = traceback.format_exc()
            yield content

    def _execute_code(self, code, message_queue):
        async def iopub_message_listener():
            while True:
                # If self.finish_flag = True, and we didn't set it (we do below), we need to stop. That's our "stop"
                if self.finish_flag:
                    _log.debug("Interrupting kernel.")
                    await self.km.interrupt_kernel()
                    return
                try:
                    msg = await self.kc.iopub_channel.get_msg(timeout=0.05)
                except queue.Empty:
                    continue

                _log.debug("Received message: %s", msg["content"])

                if msg["header"]["msg_type"] == "status" and msg["content"]["execution_state"] == "idle":
                    # Set finish_flag and return when the kernel becomes idle
                    _log.debug("Kernel is idle, setting finish_flag to True.")
                    self.finish_flag = True
                    return

                content = msg["content"]

                if msg["msg_type"] == "stream":
                    line = content["text"]
                    message_queue.put({"type": "console", "format": "output", "content": line})
                elif msg["msg_type"] == "error":
                    content = "\n".join(content["traceback"])
                    # Remove color codes
                    ansi_escape = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
                    content = ansi_escape.sub("", content)
                    message_queue.put(
                        {
                            "type": "console",
                            "format": "output",
                            "content": content,
                        }
                    )
                elif msg["msg_type"] in ["display_data", "execute_result"]:
                    data = content["data"]
                    if "image/png" in data:
                        message_queue.put(
                            {
                                "type": "image",
                                "format": "base64.png",
                                "content": data["image/png"],
                            }
                        )
                    elif "image/jpeg" in data:
                        message_queue.put(
                            {
                                "type": "image",
                                "format": "base64.jpeg",
                                "content": data["image/jpeg"],
                            }
                        )
                    elif "text/html" in data:
                        message_queue.put(
                            {
                                "type": "code",
                                "format": "html",
                                "content": data["text/html"],
                            }
                        )
                    elif "text/plain" in data:
                        message_queue.put(
                            {
                                "type": "console",
                                "format": "output",
                                "content": data["text/plain"],
                            }
                        )
                    elif "application/javascript" in data:
                        message_queue.put(
                            {
                                "type": "code",
                                "format": "javascript",
                                "content": data["application/javascript"],
                            }
                        )

        def start_async_loop(async_func):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(async_func())
            finally:
                loop.close()

        self.listener_thread = threading.Thread(target=start_async_loop, args=(iopub_message_listener,))
        # self.listener_thread.daemon = True
        self.listener_thread.start()

        _log.debug("Listener thread is alive: %s", self.listener_thread.is_alive())

        self.kc.execute(code)  # execute_interactive

    async def _capture_output(self, message_queue):
        while True:
            if self.listener_thread:
                try:
                    output = message_queue.get(timeout=0.1)
                    _log.debug("Output from queue: %s", output)
                    if content := output.get("content", None):
                        yield content
                except queue.Empty:
                    if self.finish_flag:
                        _log.debug("Finish flag is set, stopping output capture.")
                        break

            await asyncio.sleep(0.1)

    def stop(self):
        self.finish_flag = True


def preprocess_python(code: str, materials: list[Material]):
    # If a line starts with "!" then it's a shell command, we need to wrap it appropriately
    code = "\n".join(
        [
            (
                f"import subprocess; out = subprocess.check_output({line[1:]!r}, shell=True); print(out.decode('utf-8'))"
                if line.startswith("!")
                else line
            )
            for line in code.split("\n")
        ]
    )

    # Check for syntax errors in user's code
    try:
        ast.parse(code)
    except SyntaxError as e:
        # If there's a syntax error, return the error message directly
        newline = "\n"
        # msg_for_user = f"SyntaxError on line {e.lineno}, column {e.offset}: {e.msg} ({e.text})"

        msg_for_user = (
            f""
            f'File "{e.filename}", line {e.lineno}, column {e.offset}\n '
            f"  {(e.text or '').replace(newline, '')}\n"
            f"  {(e.offset or 0) * ' '}^\n"
            f"SyntaxError: {e.msg}\n"
        )

        return f"print(f'''{msg_for_user}''')"

    api_materials = [material for material in materials if material.content_type == "api"]
    apis = [material.inlined_content for material in api_materials]

    parsed_code = ast.parse("\n\n\n".join(apis))
    parsed_code.body = [b for b in parsed_code.body if not isinstance(b, ast.Expr) or not isinstance(b.value, ast.Str)]
    apis_str = ast.unparse(parsed_code)

    newline = "\n"
    api_lines = [line for line in apis_str.split(newline) if line.strip()]
    code_lines = [line for line in code.split(newline) if line.strip()]

    # Indentation error windows, https://github.com/10clouds/aiconsole/issues/753
    insert_code = newline.join((line) for line in [*api_lines, *code_lines])
    insert_code = "\n".join(filter(bool, insert_code.split("\n")))

    if not insert_code.strip():
        insert_code = "'No input received'"

    code = f"""
{insert_code}
""".strip()
    _log.info("Preprocessed code: %s", code)
    return code
