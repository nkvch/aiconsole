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
import os
import asyncio
import logging
import platform
import queue
import subprocess
import threading
import time
import traceback
from typing import AsyncGenerator, Optional

from aiconsole.core.assets.materials.material import Material

from .base_code_interpreter import BaseCodeInterpreter
from .languages.mcp_python import MCPPythonCodeInterpreter

_log = logging.getLogger(__name__)


class SubprocessCodeInterpreter(BaseCodeInterpreter):
    def __init__(self):
        super().__init__()
        self.start_cmd = ""
        self.process = None
        self.output_queue: queue.Queue[str] = queue.Queue()
        self.done = threading.Event()
        self.mcp_interpreter: Optional[MCPPythonCodeInterpreter] = None

    async def initialize(self, use_mcp: bool = False):
        # This line checks the environment variable
        if os.environ.get("DISABLE_MCP", "").lower() == "true":
            use_mcp = False  # Force-disable MCP regardless of other settings
        
        if use_mcp:
            self.mcp_interpreter = MCPPythonCodeInterpreter()
            await self.mcp_interpreter.initialize(use_mcp=True)

    def detect_end_of_execution(self, line):
        return None

    def line_postprocessor(self, line):
        return line

    def preprocess_code(self, code, materials: list[Material]):
        """
        This needs to insert an end_of_execution marker of some kind,
        which can be detected by detect_end_of_execution.
        """
        return code

    def terminate(self):
        if self.process:
            self.process.terminate()
        if self.mcp_interpreter:
            self.mcp_interpreter.terminate()
        self.done.set()

    def start_process(self):
        if self.process:
            self.terminate()

        self.process = subprocess.Popen(
            self.start_cmd.split(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self.get_environment_variables(),
            shell=platform.system() == "Windows",
            text=True,
            bufsize=0,
            universal_newlines=True,
        )
        threading.Thread(
            target=self.handle_stream_output,
            args=(self.process.stdout, False),
            daemon=True,
        ).start()
        threading.Thread(
            target=self.handle_stream_output,
            args=(self.process.stderr, True),
            daemon=True,
        ).start()

    async def run(self, code: str, materials: list[Material]) -> AsyncGenerator[str, None]:
        # Try MCP execution first if enabled
        if self.mcp_interpreter:
            try:
                async for output in self.mcp_interpreter.run(code, materials):
                    yield output
                return
            except Exception as e:
                yield f"MCP Error: {str(e)}"
                # Fall through to subprocess execution

        # Original subprocess implementation
        retry_count = 0
        max_retries = 3

        try:
            await self.wait_for_path()
            code = self.preprocess_code(code, materials)
            _log.info(f"Running code:\n{code}\n---")
            if not self.process:
                self.start_process()
        except:  # noqa E722
            yield traceback.format_exc()
            return

        while retry_count <= max_retries:
            self.done.clear()

            try:
                if not self.process or not self.process.stdin:
                    raise Exception("Process not started")

                self.process.stdin.write(code + "\n")
                self.process.stdin.flush()
                break
            except:  # noqa E722
                if retry_count != 0:
                    yield traceback.format_exc()
                    yield f"Retrying... ({retry_count}/{max_retries})"
                    yield "Restarting process."

                self.start_process()
                retry_count += 1
                if retry_count > max_retries:
                    yield "Maximum retries reached. Could not execute code."
                    return

        while True:
            if not self.output_queue.empty():
                yield self.output_queue.get()
            else:
                await asyncio.sleep(0.1)
            try:
                output = self.output_queue.get(timeout=0.3)
                yield output
            except queue.Empty:
                if self.done.is_set() or (self.process and self.process.poll() is not None):
                    for _ in range(3):
                        if not self.output_queue.empty():
                            yield self.output_queue.get()
                        await asyncio.sleep(0.2)
                    break

    def handle_stream_output(self, stream, is_error_stream):
        for line in iter(stream.readline, ""):
            _log.debug(f"Received output line:\n{line}\n---")

            line = self.line_postprocessor(line)

            if line is None:
                continue

            if self.detect_end_of_execution(line):
                self.done.set()
            elif is_error_stream and "KeyboardInterrupt" in line:
                self.output_queue.put("KeyboardInterrupt")
                time.sleep(0.1)
                self.done.set()
            else:
                self.output_queue.put(line)