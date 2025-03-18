import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { CallToolRequestSchema, ErrorCode, McpError } from '@modelcontextprotocol/sdk/types.js';
import { callRedditService } from '../reddit-bridge.js';

export interface FetchPostsParams {
  limit?: number;
  subreddit?: string;
  timeframe?: 'hour' | 'day' | 'week' | 'month' | 'year' | 'all';
}

/**
 * Register the fetch posts tool handler with the MCP server
 */
export function registerFetchPostsTool(server: Server): void {
  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    if (request.params.name !== 'get_reddit_posts') {
      return; // Let other handlers process this request
    }
    
    try {
      const params: FetchPostsParams = request.params.arguments || {};
      
      // Validate parameters
      if (params.limit !== undefined && (typeof params.limit !== 'number' || params.limit <= 0)) {
        throw new McpError(
          ErrorCode.InvalidParams,
          'limit must be a positive number'
        );
      }
      
      // Call the Reddit service
      const result = await callRedditService('fetch_posts', params);
      
      // Check for errors from the Python service
      if (result.error) {
        throw new McpError(
          ErrorCode.InternalError,
          result.error
        );
      }
      
      // Format the result for better readability
      const formattedPosts = result.map((post: any) => ({
        title: post.title,
        content: post.selftext ? `${post.selftext.substring(0, 200)}${post.selftext.length > 200 ? '...' : ''}` : '[No content]',
        url: post.url,
        created: new Date(post.created_utc * 1000).toISOString(),
        type: post.type
      }));
      
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(formattedPosts, null, 2),
          },
        ],
      };
    } catch (error) {
      console.error('Error in get_reddit_posts:', error);
      
      return {
        content: [
          {
            type: 'text',
            text: `Error fetching Reddit posts: ${error instanceof Error ? error.message : String(error)}`,
          },
        ],
        isError: true,
      };
    }
  });
}
