# AI Browser Automation: MCP-Based Reddit Integration Guidelines

This document outlines the plan for integrating Reddit functionality into the AI Browser Automation Tool using the Model Context Protocol (MCP). By implementing the existing `RedditMonitor` class as an MCP server, we can provide the AI with direct access to Reddit data without requiring browser automation, creating a more efficient and reliable method for Reddit interaction.

---

## 1. MCP Integration Overview

**Objective:**  
Create a dedicated Model Context Protocol (MCP) server that exposes the Reddit API functionality to the AI system, enabling direct access to Reddit data through structured tools and resources rather than browser automation alone.

**Key Integration Components:**
- **Reddit MCP Server:** A TypeScript/Node.js server that implements the MCP protocol and wraps the existing Python-based Reddit functionality.
- **API Bridge Layer:** A communication mechanism between the TypeScript MCP server and the Python-based Reddit monitor.
- **Tool Definitions:** Structured endpoints for the AI to retrieve user posts, comments, and activity.
- **Authentication Management:** Secure handling of Reddit API credentials through environment variables.
- **Response Formatting:** Consistent and structured data formats for Reddit content.

---

## 2. MCP Server Architecture

### Server Structure

The Reddit MCP server will be built using the MCP SDK with the following architecture:

```
reddit-mcp-server/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts           # Main server entry point
│   ├── reddit-bridge.ts   # Communication with Python Reddit functionality
│   ├── tools/             # Tool implementations
│   │   ├── fetch-posts.ts
│   │   ├── fetch-comments.ts
│   │   └── fetch-activity.ts
│   └── resources/         # Resource implementations (optional)
│       └── recent-activity.ts
└── python/                # Python script for Reddit API interaction
    └── reddit_service.py  # Modified from reddit_fetch.py for MCP integration
```

### Tool Interfaces

The MCP server will expose the following tools to the AI system:

```typescript
// Fetch Recent Posts Tool
interface FetchPostsParams {
  limit?: number;           // Optional limit (default: 10)
  subreddit?: string;       // Optional filter by subreddit
  timeframe?: 'hour' | 'day' | 'week' | 'month' | 'year' | 'all';
}

// Fetch Recent Comments Tool  
interface FetchCommentsParams {
  limit?: number;           // Optional limit (default: 10)
  subreddit?: string;       // Optional filter by subreddit
  timeframe?: 'hour' | 'day' | 'week' | 'month' | 'year' | 'all';
}

// Fetch User Activity Tool
interface FetchActivityParams {
  username?: string;        // Optional username (defaults to authenticated user)
  limit?: number;           // Optional limit (default: 20)
  include_posts?: boolean;  // Include posts in results (default: true)
  include_comments?: boolean; // Include comments in results (default: true)
}

// Search Reddit Tool
interface SearchRedditParams {
  query: string;            // Search query
  subreddit?: string;       // Optional subreddit to search within
  sort?: 'relevance' | 'hot' | 'top' | 'new' | 'comments';
  limit?: number;           // Optional limit (default: 25)
}
```

---

## 3. System Prompt Enhancement for Reddit MCP

The following system prompt enhancement should be added to guide the AI when using the Reddit MCP tools:

```
You now have access to direct Reddit functionality through MCP tools that allow you to retrieve posts, comments, and user activity without browser automation. When working with Reddit data:

1. DATA RETRIEVAL: You can access Reddit content using these specific tools:
   - get_reddit_posts: Retrieve recent posts with optional filters
   - get_reddit_comments: Retrieve recent comments with optional filters  
   - get_reddit_activity: Retrieve combined user activity
   - search_reddit: Search across Reddit for specific content

2. DATA PROCESSING: When handling Reddit data:
   - Extract key information relevant to the user's request
   - Organize content chronologically or by relevance
   - Identify important themes, topics, or patterns
   - Format content appropriately for presentation

3. PRIVACY CONSIDERATIONS: When working with Reddit data:
   - Focus on publicly available information
   - Avoid exposing potentially sensitive user activity
   - Provide summaries rather than verbatim content when appropriate
   - Handle controversial content thoughtfully

4. INTEGRATION WITH BROWSER AUTOMATION: Consider when to use:
   - MCP tools for direct data access (faster, more reliable)
   - Browser automation for interactive Reddit tasks (posting, voting, etc.)
   - Combined approaches for complex workflows

Use these tools to efficiently access Reddit content without the overhead of browser automation when direct data access is sufficient for the task.
```

---

## 4. Technical Implementation Details

### Python-TypeScript Bridge

The MCP server will communicate with the Python Reddit functionality using a child process approach:

```typescript
// src/reddit-bridge.ts
import { spawn } from 'child_process';
import { promisify } from 'util';

export async function callRedditService(method: string, params: any): Promise<any> {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python', [
      './python/reddit_service.py',
      method,
      JSON.stringify(params)
    ]);
    
    let dataString = '';
    let errorString = '';
    
    pythonProcess.stdout.on('data', (data) => {
      dataString += data.toString();
    });
    
    pythonProcess.stderr.on('data', (data) => {
      errorString += data.toString();
    });
    
    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Process exited with code ${code}: ${errorString}`));
        return;
      }
      
      try {
        const result = JSON.parse(dataString);
        resolve(result);
      } catch (e) {
        reject(new Error(`Failed to parse Python output: ${e.message}`));
      }
    });
  });
}
```

### Python Service Adaptation

The `reddit_fetch.py` file will be adapted into `reddit_service.py` to work as a service for the MCP bridge:

```python
#!/usr/bin/env python3
import json
import sys
from reddit_fetch import RedditMonitor

def main():
    if len(sys.argv) != 3:
        print(json.dumps({"error": "Invalid arguments"}))
        sys.exit(1)
    
    method = sys.argv[1]
    params = json.loads(sys.argv[2])
    
    monitor = RedditMonitor()
    
    if method == "fetch_posts":
        limit = params.get("limit", 10)
        result = monitor.fetch_recent_posts(limit=limit)
        print(json.dumps(result))
    elif method == "fetch_comments":
        limit = params.get("limit", 10)
        result = monitor.fetch_recent_comments(limit=limit)
        print(json.dumps(result))
    elif method == "fetch_activity":
        limit = params.get("limit", 20)
        result = monitor.fetch_all_recent_activity(limit=limit)
        print(json.dumps(result))
    else:
        print(json.dumps({"error": f"Unknown method: {method}"}))
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### MCP Tool Implementation

The tool implementations will use the bridge to call the Python functions:

```typescript
// src/tools/fetch-posts.ts
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { CallToolRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import { callRedditService } from '../reddit-bridge.js';

export function registerFetchPostsTool(server: Server) {
  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    if (request.params.name !== 'get_reddit_posts') {
      return; // Let other handlers process this
    }
    
    try {
      const result = await callRedditService('fetch_posts', request.params.arguments);
      
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(result, null, 2),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `Error fetching Reddit posts: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  });
}
```

---

## 5. Iterative Implementation Plan

### Phase 1: MCP Server Setup
- **Project Structure:**
  - Create directory structure for the Reddit MCP server
  - Set up package.json and TypeScript configuration
  - Install MCP SDK and necessary dependencies
- **Python Adaptation:**
  - Convert reddit_fetch.py to a service-oriented script
  - Add command-line interface for method calls
  - Ensure proper JSON serialization of all Reddit data

### Phase 2: Bridge Implementation
- **Communication Layer:**
  - Implement the TypeScript-Python bridge
  - Create robust error handling for process communication
  - Test data serialization/deserialization across languages
- **Environment Management:**
  - Configure environment variable handling for Reddit credentials
  - Implement startup validation for required credentials
  - Create documentation for credential setup

### Phase 3: Tool Definition and Implementation
- **Tool Interfaces:**
  - Define the core tool interfaces (posts, comments, activity)
  - Implement handlers for each tool
  - Create input validation for tool parameters
- **Response Formatting:**
  - Design consistent response formats for Reddit data
  - Implement data cleaning and formatting
  - Add rich text support for Reddit markdown content

### Phase 4: MCP Integration and Testing
- **Server Registration:**
  - Add the Reddit MCP server to the MCP settings
  - Implement server lifecycle management
  - Test connection and tool discovery
- **Tool Testing:**
  - Create test scenarios for each Reddit tool
  - Validate error handling and edge cases
  - Measure performance and optimize as needed

### Phase 5: AI Integration and Documentation
- **System Prompt Updates:**
  - Enhance the system prompt with Reddit capabilities
  - Add example tool usage for common scenarios
  - Document best practices for Reddit data handling
- **User Guide:**
  - Create user documentation for Reddit integration
  - Provide examples of tasks that leverage Reddit tools
  - Include troubleshooting guidance

---

## 6. MCP Server Implementation

### Main Server File

```typescript
// src/index.ts
#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { registerFetchPostsTool } from './tools/fetch-posts.js';
import { registerFetchCommentsTool } from './tools/fetch-comments.js';
import { registerFetchActivityTool } from './tools/fetch-activity.js';
import { registerSearchRedditTool } from './tools/search-reddit.js';

class RedditMcpServer {
  private server: Server;

  constructor() {
    this.server = new Server(
      {
        name: 'reddit-mcp-server',
        version: '0.1.0',
      },
      {
        capabilities: {
          resources: {},
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
    
    // Error handling
    this.server.onerror = (error) => console.error('[MCP Error]', error);
    process.on('SIGINT', async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  private setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'get_reddit_posts',
          description: 'Get recent posts from Reddit',
          inputSchema: {
            type: 'object',
            properties: {
              limit: {
                type: 'number',
                description: 'Number of posts to retrieve (default: 10)',
              },
              subreddit: {
                type: 'string',
                description: 'Optional subreddit to filter by',
              },
              timeframe: {
                type: 'string',
                enum: ['hour', 'day', 'week', 'month', 'year', 'all'],
                description: 'Time period to fetch posts from',
              },
            },
          },
        },
        {
          name: 'get_reddit_comments',
          description: 'Get recent comments from Reddit',
          inputSchema: {
            type: 'object',
            properties: {
              limit: {
                type: 'number',
                description: 'Number of comments to retrieve (default: 10)',
              },
              subreddit: {
                type: 'string',
                description: 'Optional subreddit to filter by',
              },
              timeframe: {
                type: 'string',
                enum: ['hour', 'day', 'week', 'month', 'year', 'all'],
                description: 'Time period to fetch comments from',
              },
            },
          },
        },
        {
          name: 'get_reddit_activity',
          description: 'Get combined user activity from Reddit',
          inputSchema: {
            type: 'object',
            properties: {
              username: {
                type: 'string',
                description: 'Username to fetch activity for (defaults to authenticated user)',
              },
              limit: {
                type: 'number',
                description: 'Number of activities to retrieve (default: 20)',
              },
              include_posts: {
                type: 'boolean',
                description: 'Include posts in results (default: true)',
              },
              include_comments: {
                type: 'boolean',
                description: 'Include comments in results (default: true)',
              },
            },
          },
        },
        {
          name: 'search_reddit',
          description: 'Search Reddit for specific content',
          inputSchema: {
            type: 'object',
            properties: {
              query: {
                type: 'string',
                description: 'Search query',
              },
              subreddit: {
                type: 'string',
                description: 'Optional subreddit to search within',
              },
              sort: {
                type: 'string',
                enum: ['relevance', 'hot', 'top', 'new', 'comments'],
                description: 'Sort method for results',
              },
              limit: {
                type: 'number',
                description: 'Number of results to retrieve (default: 25)',
              },
            },
            required: ['query'],
          },
        },
      ],
    }));

    // Register individual tool handlers
    registerFetchPostsTool(this.server);
    registerFetchCommentsTool(this.server);
    registerFetchActivityTool(this.server);
    registerSearchRedditTool(this.server);
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Reddit MCP server running on stdio');
  }
}

const server = new RedditMcpServer();
server.run().catch(console.error);
```

---

## 7. MCP Configuration

To integrate the Reddit MCP server with the AI system, the following configuration should be added to the MCP settings file:

```json
{
  "mcpServers": {
    "reddit": {
      "command": "node",
      "args": ["/path/to/reddit-mcp-server/build/index.js"],
      "env": {
        "REDDIT_CLIENT_ID": "your-client-id",
        "REDDIT_CLIENT_SECRET": "your-client-secret",
        "REDDIT_USER_AGENT": "your-user-agent",
        "REDDIT_USERNAME": "your-username",
        "REDDIT_PASSWORD": "your-password"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

---

## 8. Best Practices for Reddit MCP Implementation

- **Authentication Management:**  
  - Use environment variables for all Reddit API credentials
  - Implement proper validation of credentials at startup
  - Create helper scripts for users to obtain and configure credentials

- **Error Handling:**  
  - Implement robust error handling for API rate limits
  - Provide clear error messages that help diagnose issues
  - Include fallbacks for common failure scenarios

- **Data Processing:**  
  - Clean and format Reddit data for consistent presentation
  - Parse markdown content appropriately
  - Handle media content and links properly

- **Privacy Considerations:**  
  - Focus on public information and user-owned content
  - Implement filtering for potentially sensitive information
  - Provide sanitization options for returned content

- **Performance Optimization:**  
  - Implement caching for frequently accessed data
  - Use pagination for large result sets
  - Optimize Python-TypeScript communication for speed

- **Extension Points:**  
  - Design the MCP server to be extensible for future Reddit features
  - Use interfaces that can accommodate additional data fields
  - Document extension mechanisms for developers

---

## 9. MCP Server Installation Guide

To install and use the Reddit MCP server, follow these steps:

1. **Create Reddit API Credentials:**
   - Go to https://www.reddit.com/prefs/apps
   - Click "create another app..." at the bottom
   - Select "script"
   - Fill in the name, description, and redirect URI (use http://localhost:8000)
   - Note the client ID and client secret for later use

2. **Install Dependencies:**
   ```bash
   # Install Node.js dependencies
   cd reddit-mcp-server
   npm install
   
   # Install Python dependencies
   pip install praw python-dotenv
   ```

3. **Build the MCP Server:**
   ```bash
   npm run build
   ```

4. **Configure MCP Settings:**
   - Add the Reddit MCP configuration to your MCP settings file
   - Replace the credential placeholders with your actual Reddit API credentials

5. **Test the Server:**
   ```bash
   # Test direct execution
   node build/index.js
   
   # The server should start and await MCP protocol commands on stdin/stdout
   ```

6. **Restart the AI Application:**
   - Restart the AI application to load the new MCP server
   - Verify that the Reddit tools appear in the server capabilities

---

## 10. Next Steps

1. **Create the Reddit MCP Server** project structure
2. **Implement the Python service adapter** for reddit_fetch.py
3. **Build the TypeScript-Python bridge** for communication
4. **Implement the core Reddit tools** for posts, comments, and activity
5. **Add the configuration** to the MCP settings
6. **Test the integration** with various Reddit-related tasks
7. **Document usage patterns** for developers and users
8. **Extend with additional Reddit functionality** as needed

By following these guidelines, the Reddit MCP server can be effectively integrated with the AI Browser Automation Tool, providing direct access to Reddit data through a structured API rather than requiring browser automation for all Reddit interactions. This hybrid approach combines the efficiency of direct API access with the flexibility of browser automation when needed, creating a more powerful and versatile system.
