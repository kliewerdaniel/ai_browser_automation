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
