import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { CallToolRequestSchema, ErrorCode, McpError } from '@modelcontextprotocol/sdk/types.js';
import { callRedditService } from '../reddit-bridge.js';

export interface SearchRedditParams {
  query: string;
  subreddit?: string;
  sort?: 'relevance' | 'hot' | 'top' | 'new' | 'comments';
  limit?: number;
}

/**
 * Register the search Reddit tool handler with the MCP server
 * Note: This is a placeholder for future implementation, as the current
 * RedditMonitor class doesn't directly support search
 */
export function registerSearchRedditTool(server: Server): void {
  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    if (request.params.name !== 'search_reddit') {
      return; // Let other handlers process this request
    }
    
    try {
      const params: SearchRedditParams = request.params.arguments || {};
      
      // Validate parameters
      if (!params.query || typeof params.query !== 'string') {
        throw new McpError(
          ErrorCode.InvalidParams,
          'query parameter is required and must be a string'
        );
      }
      
      if (params.limit !== undefined && (typeof params.limit !== 'number' || params.limit <= 0)) {
        throw new McpError(
          ErrorCode.InvalidParams,
          'limit must be a positive number'
        );
      }
      
      // Since this is just a placeholder, we'll return a "not implemented" error
      // In the future, this would call the actual Reddit service search method
      return {
        content: [
          {
            type: 'text',
            text: `The Reddit search functionality is not yet implemented. This tool is a placeholder for future development.

Requested search:
- Query: ${params.query}
- Subreddit: ${params.subreddit || 'all'}
- Sort: ${params.sort || 'relevance'}
- Limit: ${params.limit || 25}`,
          },
        ],
      };
    } catch (error) {
      console.error('Error in search_reddit:', error);
      
      return {
        content: [
          {
            type: 'text',
            text: `Error searching Reddit: ${error instanceof Error ? error.message : String(error)}`,
          },
        ],
        isError: true,
      };
    }
  });
}
