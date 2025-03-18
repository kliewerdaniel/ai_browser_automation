import { NextRequest } from 'next/server';
import { Agent } from '@/lib/agent';

// POST /api/run-agent - Runs the AI agent and streams the results back to the client
export async function POST(request: NextRequest) {
  // Create a TransformStream for streaming the response
  const encoder = new TextEncoder();
  const stream = new TransformStream();
  const writer = stream.writable.getWriter();

  // Parse the request body
  let requestData;
  try {
    requestData = await request.json();
  } catch (error) {
    await writer.write(encoder.encode(JSON.stringify({
      type: 'log',
      message: 'Error parsing request: Invalid JSON'
    }) + '\n'));
    await writer.close();
    return new Response(stream.readable, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    });
  }

  const { goal, model = 'mistral', maxSteps = 5 } = requestData;

  if (!goal) {
    await writer.write(encoder.encode(JSON.stringify({
      type: 'log',
      message: 'Error: No goal specified'
    }) + '\n'));
    await writer.close();
    return new Response(stream.readable, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    });
  }

  // Log that we're starting the agent
  await writer.write(encoder.encode(JSON.stringify({
    type: 'log',
    message: `Starting agent with model: ${model}, goal: ${goal.substring(0, 100)}${goal.length > 100 ? '...' : ''}`
  }) + '\n'));

  // Function to send log messages to the client
  const logStep = async (step: any) => {
    // Log the reasoning
    if (step.reasoning) {
      await writer.write(encoder.encode(JSON.stringify({
        type: 'log',
        message: `🤔 Reasoning: ${step.reasoning}`
      }) + '\n'));
    }

    // Log the step description and number
    await writer.write(encoder.encode(JSON.stringify({
      type: 'log',
      message: `📝 Step ${step.number}: ${step.description}`
    }) + '\n'));

    // Log the output if available
    if (step.output) {
      await writer.write(encoder.encode(JSON.stringify({
        type: 'log',
        message: `✅ Output: ${step.output.substring(0, 100)}${step.output.length > 100 ? '...' : ''}`
      }) + '\n'));
    }
  };

  try {
    // Create and run the agent
    const agent = new Agent({
      goal,
      maxSteps,
      model,
      onStepComplete: logStep
    });

    // Execute the agent
    const result = await agent.execute();

    // Send the final result
    await writer.write(encoder.encode(JSON.stringify({
      type: 'result',
      content: result.output
    }) + '\n'));

  } catch (error) {
    console.error('Error executing agent:', error);
    await writer.write(encoder.encode(JSON.stringify({
      type: 'log',
      message: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`
    }) + '\n'));
  } finally {
    // Close the writer when done
    await writer.close();
  }

  // Return the response stream
  return new Response(stream.readable, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  });
}
