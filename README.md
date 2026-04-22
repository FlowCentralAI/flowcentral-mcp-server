![FlowCentral](/central.jpg)

# FlowCentral MCP Server
Create an account at [flowcentral.ai](https://flowcentral.ai) and the bot will walk you through setup.

Basically we have a distributed linux-style system that provides tool infra for bots. Tools are arranged in folders for easy management across functions and teams. Teams can call each other's functions directly or of course the bots can just do things themselves. Under the covers is an MCP-compliant system but we support hotloading etc. without some of the clunky overhead of constantly updating MCP tools.

To get started, clone the repo, do the Python env stuff, set up your API keys as environment variables (OPENROUTER_API_KEY, ANTHROPIC_API_KEY, etc.) and connect this local Python server to the main server (see runServer). We give you all the source code to build your own tool-calling chatbot just like Claude or whatever. See `Games/FlowCentral/Bots/Atlas/` for the bot persona configuration and `Home/chat.py` for the shared chat loop — the bot discovers tools dynamically via search/dir rather than pre-loading them.

*note that `game_set("FlowCentral")` locks the server to a game, then `character_bot()` assigns bots to roles and `game_move_bot()`/`game_move_human()` handles movement between locations


## FlowCentral Network

Each MCP server is part of a collaborative network of AI agents and developers. Using the Model Context Protocol, the platform creates an ecosystem where agents can discover and use each other's capabilities across the network. Tools and functions can be shared, discovered, and coordinated between agents—whether for enterprise automation, workflow orchestration, or any other application. The network architecture enables agents to find and leverage tools from other users, creating a decentralized ecosystem of shared capabilities.

The centerpiece of this project is a Python MCP host (referred to as a 'remote') that lets you install functions and 3rd party MCP tools on the fly

## Quick Start

1. Prerequisites - need to install Python for the server and Node for Lobster (the MCP client); you should also install uv/uvx and node/npx since it seems that MCP needs both


2. Python 3.13 seems to be most stable right now because of async support

3. Set up your Python virtual environment and install dependencies:

```bash
cd python-server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. Set up your API keys. Create a script in `python-server/` to export your keys (these are gitignored so your keys won't be committed). For example, create `set_OPENROUTER.bat`:

```bash
#!/bin/bash
# Usage: source set_OPENROUTER.bat

export OPENROUTER_API_KEY="sk-or-v1-your-key-here"

echo "OPENROUTER_API_KEY has been set"
```

Create one per provider you need (`set_ANTHROPIC.bat`, `set_GOOGLE.bat`, etc.) following the same pattern. Source them after activating your venv:

```bash
source venv/bin/activate
source set_OPENROUTER.bat
source set_ANTHROPIC.bat      # if using Anthropic models
source set_GOOGLE.bat         # if using Google APIs
```

You only need the keys for the providers you plan to use. At minimum, `OPENROUTER_API_KEY` is required for the default bot (Atlas).

6. Edit the runServer script in the `python-server` folder and set the email and service name (it's actually best practice to create a copy "runServerFoo" that you can replace the runServer file with when we do updates):

```bash
python server.py  \
  --email=youremail@gmail.com  \             # email you use for flowcentral
  --api-key=foobar \                         # should change online
  --host=localhost \                         # npx MCP will be looking here to connect to remote (assumes there is at least one running locally)
  --port=8000  \
  --cloud-host=wss://flowcentral.ai  \   # points to cloud
  --cloud-port=443  \
  --service-name=home                        # remote name, can be anything but must be unique across all machines
```
7. The MCP client is now called **Lobster**. To use this as a regular standalone MCP server, add the following config to Windsurf or Cursor or whatever:

```json
   "mcpServers": {
      "atlantis": {
         "command": "npx",
         "args": [
            "atlantis-mcp",
            "--port",
            "8000"
            ]
      }
   }
```

To add Atlantis to Claude Code:

```claude mcp add atlantis -- npx atlantis-mcp --port 8000```

To connect to Codex:

```codex mcp add atlantis -- npx atlantis-mcp --port 8000```

To add Atlantis Open Weather for testing:

```claude mcp add --transport stdio weather_forecast --env OPENWEATHER_API_KEY=mykey123 -- uvx --from atlantis-open-weather-mcp start-weather-server```

8. To connect to FlowCentral, sign into https://www.flowcentral.ai under the same email

9. Your remote(s) should autoconnect using email and default api key = 'foobar' (see 'api' command to generate a new key later). The first server to connect will be assigned your 'default' unless you manually change it later

10. Initially the functions and servers folders will be empty except for some examples

11. You can run this standalone MCP or accessed from the cloud or both

### Architecture

Caveat: MCP terminology is already terrible and calling things 'servers' or 'hosts' just makes it more confusing because MCP is inherently p2p

Pieces of the system:

- **Cloud**: the FlowCentral cloud server; a place to share tools and let users bang on them
- **Remote**: the Python server process found in this repo, officially referred to as an MCP 'host' (you can run >1 either on same box or on different one, just specify different service names)
- **Dynamic Function**: a simple Python function that you write, acts as a tool
- **Dynamic MCP Server**: any 3rd party MCP, stored as a JSON config file

![design](/design.png)

Note that MCP auth and security are still being worked out so using the cloud for auth is easier right now

### Directories

1. **Python Remote (MCP P2P server)** (`python-server/`)
   - Location of our 'remote'. Runs locally but can be controlled remotely

2. **Lobster (MCP Client)** (`client/`)
   - lets Claude Code or Codex run Atlantis commands or chat via MCP
   - uses npx (easy to install into Claude Code or Codex)
   - cloud connection not needed - although it may complain
   - only supports a subset of the spec
   - can only see tools on the local box (at least right now) or shared
     tools set to 'public'

### Python Server Layout

If you are trying to understand the Python source, start in `python-server/server.py` and then branch out from there:

- **`server.py`** - main entry point and protocol host. It starts the Starlette app, owns the `DynamicAdditionServer` class, manages WebSocket and cloud Socket.IO connections, and wires together the function/server managers. If you are tracing a tool invocation, the consolidated MCP `tools/call` handler lives here in `DynamicAdditionServer._handle_tools_call()`, which then delegates to `_execute_tool()`.
- **`DynamicFunctionManager.py`** - owns the dynamic Python tool system under `dynamic_functions/`. This is where function decorators are defined (`@visible`, `@public`, `@protected`, `@exclude`, etc.), files are scanned and validated, Python modules are loaded/reloaded, and tool calls are dispatched into user code.
- **`DynamicServerManager.py`** - manages third-party MCP server configs under `dynamic_servers/`. It saves/loads JSON configs, starts stdio MCP servers, keeps sessions alive, and fetches their tool lists.
- **`atlantis.py`** - the dynamic function harness/runtime API injected into dynamic functions. This is the bridge that tool code uses for `client_log`, streaming, HTML/image/video responses, click/upload callbacks, request context, and persistent shared state. See the [Dynamic Functions Documentation](python-server/README.dynamic_functions.md) for the function-authoring side of this API.
- **`lobster.py`** - compatibility layer for the local Atlantis MCP client. It defines the `readme` / `command` / `chat` tools and translates those local calls into the cloud-backed command flow.
- **`state.py`** - central configuration and process-wide state. It sets up logging, defines `FUNCTIONS_DIR` and `SERVERS_DIR`, and stores base server constants like host/port and request timeout.
- **`utils.py`** - low-level helpers shared across the server and dynamic functions. It contains search-term parsing, JSON/log formatting, the global server-instance bridge, and client command/log plumbing used by `atlantis.py`.
- **`PIDManager.py`** - single-instance guard for the Python server process via PID files.
- **`ColoredFormatter.py`** - logging formatter and request-context filter used by `state.py`.

The runtime split is basically:

1. `server.py` receives MCP traffic.
2. `server.py` routes MCP `tools/call` through `DynamicAdditionServer._handle_tools_call()`.
3. `_handle_tools_call()` delegates Python tool execution to `DynamicFunctionManager.py` and proxied MCP tool execution to `DynamicServerManager.py`.
4. Dynamic functions call back into the host through `atlantis.py` and `utils.py`.

For dynamic function authoring details, see [Dynamic Functions Documentation](python-server/README.dynamic_functions.md).

## Features

#### Dynamic Functions

Dynamic functions give users the ability to create and maintain custom functions-as-tools, which are kept in the `dynamic_functions/` folder. Functions are loaded on start and automatically reloaded when modified.

For detailed information about creating and using dynamic functions, see the [Dynamic Functions Documentation](python-server/README.dynamic_functions.md).

#### Dynamic MCP Servers

- gives users the ability to install and manage third-party MCP server tools; JSON config files are kept in the `dynamic_servers/` folder
- each MCP server will need to be 'started' first to fetch the list of tools
- each server config follows the usual JSON structure that contains an 'mcpServers' element; for example, this installs an openweather MCP server:

   ```json
   {
      "mcpServers": {
         "openweather": {
            "command": "uvx",
            "args": [
            "--from",
            "atlantis-open-weather-mcp",
            "start-weather-server",
            "--api-key",
            "<your openweather api key>"
            ]
         }
      }
   }
   ```

The weather MCP service is just an existing one ported to uvx. See [here](https://github.com/ProjectAtlantis-dev/atlantis-open-weather-mcp)


## Cloud

The cloud service at https://www.flowcentral.ai provides a centralized hub for managing your remote servers and sharing tools across machines.

### App Organization

Dynamic functions are organized into apps using **folder structure**. Simply place your `.py` files in subdirectories:

```
dynamic_functions/
├── Home/                    # App: "Home"
│   └── atlas.py
├── Accounting/              # App: "Accounting"
│   ├── accounting.py
│   └── foo.py
└── FilmFromImage/          # App: "FilmFromImage"
    └── qwen_image_edit_local.py
```

**The folder name IS the app name.** Functions in `Home` folder are assigned accordingly.

#### Nested Apps (Subfolders)

Create nested app structures using subfolders:

```
dynamic_functions/
└── MyApp/
    └── SubModule/
        └── Feature/
            └── my_function.py
```

This creates the app name: `MyApp/SubModule/Feature`

**Best Practices:**
- Keep it simple - one level of folders is usually enough
- Use descriptive folder names (e.g., `Chat`, `Admin`, `Tools`)
- Group related functions together in the same folder
- The folder structure keeps your code organized and clear

### Tool Calling with Search Terms

When calling tools, you can use **compound tool names** to disambiguate functions. **Only include as much of the path as needed to uniquely identify the function.**

**Format:** `remote_owner*remote_name*app*location*function`

**Key Principle: Use the simplest form that resolves uniquely**

```python
# If you have these functions:
# - dynamic_functions/Chat/send_message.py
# - dynamic_functions/Email/send_message.py
# - dynamic_functions/SMS/send_message.py

send_message              ❌ Ambiguous! Which one?
**Chat**send_message      ✅ Clear! The one in Chat
**Email**send_message     ✅ Clear! The one in Email
```

**Examples:**

```
update_image                          → Simple call (only works if unique)
**MyApp**update_image                 → Specify app to disambiguate
**MyApp/SubModule**process_data       → Nested app path
alice*prod*Admin**restart             → Full routing: owner + remote + app + function
***office*print                       → Just location context
```

**How it works:**
- Fields: `remote_owner*remote_name*app*location*function`
- Separate fields with `*` (asterisk)
- **Omit fields you don't need** (use empty strings: `**App**func`)
- The app field supports slash notation for nested apps (`MyApp/SubModule`)
- The last field is always the function name
- No asterisks = treat entire name as function name

**When to use compound names:**
- **Name conflicts**: Multiple apps have functions with the same name
- **Remote targeting**: Call functions on specific remotes from the cloud
- **Location routing**: Target functions at specific physical locations
- **Multi-user setups**: Specify owner and remote in shared environments

**Best practice:** Start simple (`update_image`) and add context only when needed to resolve ambiguity (`**ImageTools**update_image`).

**Example:**
```python
# File: dynamic_functions/ImageTools/process.py
@visible
async def update_image(image_path: str):
    """Update an image."""
    return "updated"

# If this is the ONLY update_image:
update_image                          ✅ Works fine!

# If Chat app ALSO has update_image:
**ImageTools**update_image            ✅ Now we need to specify the app
```

## Bot: Atlas

Atlas is the front-desk chatbot for FlowCentral. Bot personas now live inside each game folder, and the shared runtime lives in `Home/`:

```
Games/FlowCentral/                   # Game definition
├── Bots/                            # Bot personas for this game
│   ├── Atlas/
│   │   ├── config.json              # Model, provider, greeting, handler references
│   │   ├── system_prompt.md         # Base system prompt (markdown)
│   │   ├── prompt.py                # System prompt builder with context injection
│   │   ├── main.py                  # Index placeholder
│   │   └── atlas_face.jpg           # Bot avatar
│   └── Celeste/                     # Executive concierge
│       ├── config.json
│       ├── system_prompt.md
│       ├── prompt.py
│       ├── main.py
│       └── celeste_face.jpg
├── Locations/                       # Rooms players can move between
│   ├── Lobby.json                   # Location metadata + adjacency
│   ├── Lobby.jpg                    # Background image
│   ├── Lounge.json
│   └── Lounge.jpg
└── Roles/                           # NPC role definitions
    ├── Greeter/                     # Atlas's role
    │   ├── system_prompt.md         # Role-specific system prompt
    │   └── prompt.py
    └── Concierge/                   # Celeste's role
        ├── system_prompt.md
        └── prompt.py

Home/                                # Shared bot + game runtime
├── chat.py                          # OpenRouter chat completions handler
├── chat_callback.py                 # Routes chat to correct bot via transcript detection
├── turn.py                          # Multi-turn LLM conversation loop with tool calls
├── bot_common.py                    # Shared utils: transcript fetch, tool discovery
├── game_common.py                   # Character system, movement, bot spawning
├── main.py                          # game_set(), game_show(), bot_list(), game_move_bot/human()
├── GAME.md                          # ER diagram of the game data model
├── MULTIX.md                        # User-facing CLI documentation
└── README.py                        # Serves MULTIX.md and GAME.md via MCP
```

### Game system

Games manage bot assignments, character roles, locations, and movement. Everything is scoped per-game:

- **`game_set(name)`** — Locks the server to a game (e.g. `"FlowCentral"`)
- **`character_bot(sid, role)`** — Assigns a bot to a role (e.g. `character_bot("atlas", "Greeter")`)
- **`character_human(role, name)`** — Assigns a human player to a role
- **`game_move_bot(sid, location)`** / **`game_move_human(sid, location)`** — Moves characters between locations
- **`game_show()`** — Renders a live ER diagram of the game state

Locations are defined as JSON files in `Games/<game>/Locations/` with adjacency graphs (`connects_to`). Movement is only allowed along connected edges. New players start at the default location (marked with `"default": true`).

### Player data

All game state is scoped under `Data/{game_id}/`:

```
Data/
├── main.py                          # Game-scoped data helpers
├── todo.py                          # Todo/task management per session
└── {game_id}/                       # Per-game data (created at runtime)
    ├── characters.json              # Bot and human role assignments
    ├── positions.json               # Current location of each character
    ├── profiles.json                # Player profiles
    └── interactions.json            # Per-bot interaction history (timestamps, counts)
```

### Key files

- **`python-server/dynamic_functions/Home/MULTIX.md`** — User-facing documentation for the FlowCentral MCP tools (commands, search terms, tool prefixes, etc.). This is the file served by the `readme` MCP tool.
- **`Games/FlowCentral/Bots/Atlas/config.json`** — Bot configuration: model (minimax-m2.7), provider (OpenRouter), greeting message, and references for the chat handler and system prompt.
- **`Home/main.py`** — Game lifecycle tools: `game_set()`, `game_show()`, `bot_list()`, `location_list()`, `game_move_bot()`, `game_move_human()`.
- **`Home/game_common.py`** — Character system (`character_bot()`, `character_human()`, `character_list()`), movement logic, bot spawning.
- **`Home/chat_callback.py`** — Chat routing: detects which bot is in the room from the transcript and dispatches to its chat handler.
- **`Data/main.py`** — Game-scoped data system: positions, profiles, interactions, all under `Data/{game_id}/`.

### Troubleshooting

If MCP tools aren't working (e.g. returning `Unknown tool` errors), **check the server log first**. The Python server writes detailed logs to **`python-server/runServer.log`** — this file shows exactly what's happening with tool calls, cloud auth, and client connections. It can get large, so tail the last ~1000 lines:

```bash
tail -1000 python-server/runServer.log
```

**Common issues visible in the log:**
- `⚠️ Unexpected tool call from local client` — the server received a tool call but didn't recognize it; check that your tools are registered
- `❌ Authentication failed` — cloud credentials are wrong or the account doesn't exist; check your email/api-key
- `🏠 Local MCP tool call intercepted` — confirms the server is receiving tool calls from the MCP client

Visitor-related log lines include `"Visitor:"`, `"New conversation for"`, and `"Injected time-gap message"`.

### How to build a new bot

To create a new bot, you need: a persona folder in `Games/<game>/Bots/`, a role in `Games/<game>/Roles/`, and optionally a new location.

**Step 1: Create the persona folder** (`Games/FlowCentral/Bots/YourBot/`)

You need 4-5 files:

**`config.json`** — Model and identity:
```json
{
  "sid": "yourbot",
  "displayName": "YourBot",
  "image": "yourbot_face.jpg",
  "provider": "openrouter",
  "model": "minimax/minimax-m2.7",
  "baseUrl": "https://openrouter.ai/api/v1",
  "apiKeyEnv": "OPENROUTER_API_KEY",
  "chatHandler": "dynamic_functions.Home.chat.handle_chat_completions",
  "systemPrompt": "system_prompt.md",
  "greeting": "Hi, I'm YourBot."
}
```

- `sid` — unique bot identifier, used in transcripts and character system
- `chatHandler` — always `dynamic_functions.Home.chat.handle_chat_completions` (shared runtime)
- `systemPrompt` — markdown file in the bot's folder containing the base system prompt
- `image` — avatar image filename in the bot's folder
- `apiKeyEnv` — environment variable holding the API key
- `greeting` — what the bot says when it first appears

**`system_prompt.md`** — The bot's personality in plain markdown:
```markdown
You are YourBot, a [description of role and personality].

[Instructions for behavior, tone, tools, etc.]
```

**`prompt.py`** — Builds interaction context (time awareness, returning visitor detection). Copy from `Games/FlowCentral/Bots/Atlas/prompt.py` and adjust as needed.

**`main.py`** — Index placeholder so the bot shows up in tool discovery:
```python
import atlantis
import logging

logger = logging.getLogger("mcp_server")

@visible
async def index():
    """YourBot — [role description]."""
    pass
```

**`yourbot_face.jpg`** — Avatar image. Shown when the bot spawns.

**Step 2: Create the role** (`Games/FlowCentral/Roles/YourRole/`)

**`system_prompt.md`** — Role-specific system prompt additions:
```markdown
You are stationed at [location]. Your job is to [role description].
```

**`prompt.py`** — Optional role-specific prompt builder. Copy from an existing role if needed.

**`main.py`** — Index placeholder:
```python
import atlantis
import logging

logger = logging.getLogger("mcp_server")

@visible
async def index():
    """YourRole — [description]."""
    pass
```

**Step 3: Add a location** (optional)

If your bot needs its own room, create a location JSON file in `Games/FlowCentral/Locations/`:

**`YourLocation.json`**:
```json
{
  "name": "YourLocation",
  "description": "A brief description of this location.",
  "image": "YourLocation.jpg",
  "connects_to": ["Lobby"]
}
```

Add a background image (`YourLocation.jpg`) to the same `Locations/` folder. Then update the Lobby's `connects_to` array to include `"YourLocation"` so players can travel between the two.

**Step 4: Assign your bot to its role**

Once the game is locked to FlowCentral (via `game_set`), register your bot as a character and assign it to the role you created:

```python
character_bot("yourbot", "YourRole")
```

This links the bot's `sid` to the role folder so the system knows which system prompt and behavior to use. If a character with this `sid` already exists, it updates the role instead of creating a duplicate.

**Step 5: Move your bot to its location**

Place your bot in the room where it should greet visitors:

```python
await game_move_bot("yourbot", "YourLocation")
```

New bots must enter the default location (the Lobby) first before moving elsewhere — this mirrors how players enter the game. If your bot's location is the Lobby itself, you can omit the location argument.

**Step 6: Spawn the bot**

Show the bot's avatar and have it introduce itself with its configured greeting message:

```python
await spawn_bot("yourbot")
```

This displays the bot's face image to the client and sends the greeting as a chat message so the bot appears in the conversation transcript. After this, the chat callback will automatically route incoming messages to your bot based on who's present in the room.

**Putting it all together:**

Here's the full sequence you'd run to bring a new bot online in a session:

```python
await game_set("FlowCentral")           # Lock server to the game (once per server)
character_bot("yourbot", "YourRole")     # Assign bot to role
await game_move_bot("yourbot")           # Enter the default lobby
await spawn_bot("yourbot")               # Show face + greeting
```
