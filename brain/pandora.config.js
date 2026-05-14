module.exports = {
  apps: [
    {
      name: "pandora-mcp",
      script: "server.py",
      interpreter: "/Users/pan/Pandora/brain/venv/bin/python",
      cwd: "/Users/pan/Pandora/brain",
      interpreter_args: "-u",
      autorestart: true,
      watch: false,
      max_memory_restart: "500M",
      error_file: "/tmp/pandora-mcp-error.log",
      out_file: "/tmp/pandora-mcp.log",
      env: {
        PYTHONPATH: "/Users/pan/Pandora/brain",
        VAULT_PATH: "/Users/pan/Pandora/vault"
      }
    },
    {
      name: "pandora-daemon",
      script: "daemon.py",
      interpreter: "/Users/pan/Pandora/brain/venv/bin/python",
      cwd: "/Users/pan/Pandora/brain",
      interpreter_args: "-u",
      autorestart: true,
      watch: false,
      max_memory_restart: "500M",
      error_file: "/tmp/pandora-daemon-error.log",
      out_file: "/tmp/pandora-daemon.log",
      env: {
        PYTHONPATH: "/Users/pan/Pandora/brain",
        VAULT_PATH: "/Users/pan/Pandora/vault"
      }
    },
    {
      name: "pandora-agents",
      script: "agents/agent_server.py",
      interpreter: "/Users/pan/Pandora/brain/venv/bin/python",
      cwd: "/Users/pan/Pandora/brain",
      interpreter_args: "-u",
      autorestart: true,
      watch: false,
      max_memory_restart: "500M",
      error_file: "/tmp/pandora-agents-error.log",
      out_file: "/tmp/pandora-agents.log",
      env: {
        PYTHONPATH: "/Users/pan/Pandora/brain",
        VAULT_PATH: "/Users/pan/Pandora/vault"
      }
    }
  ]
}
