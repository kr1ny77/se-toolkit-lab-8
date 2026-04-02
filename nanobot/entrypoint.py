#!/usr/bin/env python3
"""
Nanobot gateway entrypoint.

Resolves environment variables into config.json at runtime, then execs nanobot gateway.
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def install_mcp_deps():
    """Install MCP dependencies from mounted volumes."""
    import shutil
    import tempfile
    
    mcp_lms = Path("/app/mcp/mcp-lms")
    mcp_webchat = Path("/app/nanobot-websocket-channel/mcp-webchat")
    nanobot_webchat = Path("/app/nanobot-websocket-channel/nanobot-webchat")
    nanobot_channel_protocol = Path("/app/nanobot-websocket-channel/nanobot-channel-protocol")
    
    # Copy to temp directory to avoid timestamp issues with mounted volumes
    tmpdir = Path(tempfile.mkdtemp())
    
    # Install in dependency order
    if nanobot_channel_protocol.exists():
        dst = tmpdir / "nanobot-channel-protocol"
        shutil.copytree(nanobot_channel_protocol, dst)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-cache-dir", str(dst)])
    if mcp_lms.exists():
        dst = tmpdir / "mcp-lms"
        shutil.copytree(mcp_lms, dst)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-cache-dir", str(dst)])
    if nanobot_webchat.exists():
        dst = tmpdir / "nanobot-webchat"
        shutil.copytree(nanobot_webchat, dst)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-cache-dir", str(dst)])
    if mcp_webchat.exists():
        # Install with --no-deps since nanobot-channel-protocol is already installed
        dst = tmpdir / "mcp-webchat"
        shutil.copytree(mcp_webchat, dst)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-cache-dir", "--no-deps", str(dst)])
    
    # Cleanup
    shutil.rmtree(tmpdir)


def main():
    # Install MCP dependencies first
    install_mcp_deps()
    config_dir = Path(__file__).parent
    config_file = config_dir / "config.json"
    resolved_file = Path("/tmp/config.resolved.json")
    workspace_dir = config_dir / "workspace"

    # Read base config
    with open(config_file) as f:
        config = json.load(f)

    # Override provider API key and base URL from env vars
    if "LLM_API_KEY" in os.environ:
        config["providers"]["custom"]["apiKey"] = os.environ["LLM_API_KEY"]
    if "LLM_API_BASE_URL" in os.environ:
        config["providers"]["custom"]["apiBase"] = os.environ["LLM_API_BASE_URL"]

    # Override agent model from env var
    if "LLM_API_MODEL" in os.environ:
        config["agents"]["defaults"]["model"] = os.environ["LLM_API_MODEL"]

    # Override gateway host/port from env vars
    if "NANOBOT_GATEWAY_CONTAINER_ADDRESS" in os.environ:
        config["gateway"]["host"] = os.environ["NANOBOT_GATEWAY_CONTAINER_ADDRESS"]
    if "NANOBOT_GATEWAY_CONTAINER_PORT" in os.environ:
        config["gateway"]["port"] = int(os.environ["NANOBOT_GATEWAY_CONTAINER_PORT"])

    # Configure webchat channel from env vars
    if "NANOBOT_WEBCHAT_CONTAINER_ADDRESS" in os.environ:
        if "webchat" not in config["channels"]:
            config["channels"]["webchat"] = {}
        config["channels"]["webchat"]["enabled"] = True
        config["channels"]["webchat"]["host"] = os.environ["NANOBOT_WEBCHAT_CONTAINER_ADDRESS"]
    if "NANOBOT_WEBCHAT_CONTAINER_PORT" in os.environ:
        if "webchat" not in config["channels"]:
            config["channels"]["webchat"] = {}
        config["channels"]["webchat"]["enabled"] = True
        config["channels"]["webchat"]["port"] = int(os.environ["NANOBOT_WEBCHAT_CONTAINER_PORT"])
    if "NANOBOT_ACCESS_KEY" in os.environ:
        if "webchat" not in config["channels"]:
            config["channels"]["webchat"] = {}
        config["channels"]["webchat"]["enabled"] = True
        config["channels"]["webchat"]["accessKey"] = os.environ["NANOBOT_ACCESS_KEY"]

    # Configure MCP servers from env vars
    if "tools" not in config:
        config["tools"] = {}
    if "mcpServers" not in config["tools"]:
        config["tools"]["mcpServers"] = {}

    # LMS MCP server
    if "NANOBOT_LMS_BACKEND_URL" in os.environ or "NANOBOT_LMS_API_KEY" in os.environ:
        config["tools"]["mcpServers"]["lms"] = {
            "command": "python",
            "args": ["-m", "mcp_lms"],
        }
        env = {}
        if "NANOBOT_LMS_BACKEND_URL" in os.environ:
            env["NANOBOT_LMS_BACKEND_URL"] = os.environ["NANOBOT_LMS_BACKEND_URL"]
        if "NANOBOT_LMS_API_KEY" in os.environ:
            env["NANOBOT_LMS_API_KEY"] = os.environ["NANOBOT_LMS_API_KEY"]
        if env:
            config["tools"]["mcpServers"]["lms"]["env"] = env

    # Webchat MCP server
    if "NANOBOT_WEBCHAT_UI_RELAY_URL" in os.environ or "NANOBOT_WEBCHAT_MCP_TOKEN" in os.environ:
        config["tools"]["mcpServers"]["webchat"] = {
            "command": "python",
            "args": ["-m", "mcp_webchat"],
        }
        env = {}
        if "NANOBOT_WEBCHAT_UI_RELAY_URL" in os.environ:
            env["NANOBOT_WEBCHAT_UI_RELAY_URL"] = os.environ["NANOBOT_WEBCHAT_UI_RELAY_URL"]
        if "NANOBOT_WEBCHAT_MCP_TOKEN" in os.environ:
            env["NANOBOT_WEBCHAT_MCP_TOKEN"] = os.environ["NANOBOT_WEBCHAT_MCP_TOKEN"]
        if env:
            config["tools"]["mcpServers"]["webchat"]["env"] = env

    # Write resolved config
    with open(resolved_file, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Using config: {resolved_file}", file=sys.stderr)

    # Exec nanobot gateway
    os.execvp("nanobot", ["nanobot", "gateway", "--config", str(resolved_file), "--workspace", str(workspace_dir)])


if __name__ == "__main__":
    main()
