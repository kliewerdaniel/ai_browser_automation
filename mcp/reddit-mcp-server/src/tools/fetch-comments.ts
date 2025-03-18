import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { CallToolRequestSchema, ErrorCode, McpError } from '@modelcontextprotocol/sdk/types.js';
import { callRedditService } from '../reddit-bridge.js';

export interface FetchCommentsParams {
  limit?: number;
  subreddit?: string;
  timeframe?: 'hour' | 'day' | 'week' | 'month' | 'year' | 'all';
}

/**
 * Register the fetch comments tool handler with the MCP server
 */
export function registerFetchCommentsTool(server: Server): void {
  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    if (request.params.name !== 'get_reddit_comments') {
      return; // Let other handlers process this request
    }
    
    try {
      const params: FetchCommentsParams = request.params.arguments || {};
      
      // Validate parameters
      if (params.limit !== undefined && (typeof params.limit !== 'number' || params.limit <= 0)) {
        throw new McpError(
          ErrorCode.InvalidParams,
          'limit must be a positive number'
        );
      }
      
      // Call the Reddit service
      const result = await callRedditService('fetch_comments', params);
      
      // Check for errors from the Python service
      if (result.error) {
        throw new McpError(
          ErrorCode.InternalError,
          result.error
        );
      }
      
      // Format the result for better readability
      const formattedComments = result.map((comment: any) => ({
        content: comment.body ? `${comment.body.substring(0, 200)}${comment.body.length > 200 ? '...' : ''}` : '[No content]',
        created: new Date(comment.created_utc * 1000).toISOString(),
        link_id: comment.link_id,
        type: comment.type
      }));
      
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(formattedComments, null, 2),
          },
        ],
      };
    } catch (error) {
      console.error('Error in get_reddit_comments:', error);
      
      return {
        content: [
          {
            type: 'text',
            text: `Error fetching Reddit comments: ${error instanceof Error ? error.message : String(error)}`,
          },
        ],
        isError: true,
      };
    }
  });
}
