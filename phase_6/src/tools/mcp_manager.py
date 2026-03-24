import asyncio
import os
import json
import subprocess
import time
from phase_6.src.logger import logger

class MCPManager:
    """Robust Stdio MCP Client for Python 3.9 (Manual Handshake)."""
    
    async def _call_stdio_tool(self, command, args, tool_name, tool_args, env_ext=None):
        env = {**os.environ}
        if env_ext: env.update(env_ext)
            
        proc = subprocess.Popen(
            [command] + args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            bufsize=1 # Line buffered
        )
        
        def send(msg):
            proc.stdin.write(json.dumps(msg) + "\n")
            proc.stdin.flush()

        def receive(target_id=None, method_name=None):
            # Simple synchronous read loop for this tool call
            start_time = time.time()
            while time.time() - start_time < 15: # 15s timeout
                line = proc.stdout.readline()
                if not line: break
                try:
                    data = json.loads(line)
                    if target_id and data.get("id") == target_id:
                        return data
                    if method_name and data.get("method") == method_name:
                        return data
                except: continue
            return None

        try:
            # 1. Initialize
            send({
                "jsonrpc": "2.0", "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "MarketAnalyst", "version": "1.0.0"}
                }
            })
            receive(target_id=1)
            
            # 2. Initialized Notification
            send({ "jsonrpc": "2.0", "method": "notifications/initialized" })
            
            # 3. Call Tool
            send({
                "jsonrpc": "2.0", "id": 2,
                "method": "tools/call",
                "params": { "name": tool_name, "arguments": tool_args }
            })
            
            res = receive(target_id=2)
            proc.terminate()
            
            if res and "result" in res:
                content = res["result"].get("content", [])
                # Handle different content formats (DuckDuckGo returns text usually)
                return content
            return None
            
        except Exception as e:
            logger.error(f"MCP Tool Call Error: {str(e)}")
            proc.kill()
            return None

    async def call_duckduckgo_search(self, query: str):
        return await self._call_stdio_tool(
            "npx", ["-y", "@modelcontextprotocol/server-duckduckgo"],
            "duckduckgo_search", {"query": query}
        )

    async def call_sequential_thinking(self, thought: str, context: str = ""):
        return await self._call_stdio_tool(
            "npx", ["-y", "@modelcontextprotocol/server-sequential-thinking"],
            "sequentialthinking", {"thought": thought, "context": context}
        )

mcp_mgr = MCPManager()
