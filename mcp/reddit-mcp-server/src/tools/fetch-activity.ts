import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { CallToolRequestSchema, ErrorCode, McpError } from '@modelcontextprotocol/sdk/types.js';
import { callRedditService } from '../reddit-bridge.js';

export interface FetchActivityParams {
  username?: string;
  limit?: number;
  include_posts?: boolean;
  include_comments?: boolean;
}

/**
 * Register the fetch activity tool handler with the MCP server
 */
export function registerFetchActivityTool(server: Server): void {
  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    if (request.params.name !== 'get_reddit_activity') {
      return; // Let other handlers process this request
    }
    
    try {
      const params: FetchActivityParams = request.params.arguments || {};
      
      // Validate parameters
      if (params.limit !== undefined && (typeof params.limit !== 'number' || params.limit <= 0)) {
        throw new McpError(
          ErrorCode.InvalidParams,
          'limit must be a positive number'
        );
      }
      
      // Set defaults for include_posts and include_comments
      if (params.include_posts === undefined) params.include_posts = true;
      if (params.include_comments === undefined) params.include_comments = true;
      
      // Call the Reddit service
      const result = await callRedditService('fetch_activity', params);
      
      // Check for errors from the Python service
      if (result.error) {
        throw new McpError(
          ErrorCode.InternalError,
          result.error
        );
      }
      
      // Format the result for better readability
      const formattedActivity = result.map((item: any) => {
        if (item.type === 'post') {
          return {
            type: 'post',
            title: item.title,
            content: item.selftext ? `${item.selftext.substring(0, 200)}${item.selftext.length > 200 ? '...' : ''}` : '[No content]',
            url: item.url,
            created: new Date(item.created_utc * 1000).toISOString()
          };
        } else if (item.type === 'comment') {
          return {
            type: 'comment',
            content: item.body ? `${item.body.substring(0, 200)}${item.body.length > 200 ? '...' : ''}` : '[No content]',
            created: new Date(item.created_utc * 1000).toISOString(),
            link_id: item.link_id
          };
        }
        return item;
      });
      
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(formattedActivity, null, 2),
          },
        ],
      };
    } catch (error) {
      console.error('Error in get_reddit_activity:', error);
      
      return {
        content: [
          {
            type: 'text',
            text: `Error fetching Reddit activity: ${error instanceof Error ? error.message : String(error)}`,
          },
        ],
        isError: true,
      };
    }
  });
}
