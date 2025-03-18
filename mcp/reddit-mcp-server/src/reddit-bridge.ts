import { spawn } from 'node:child_process';
import * as path from 'node:path';
import { fileURLToPath } from 'node:url';

// Get the directory of the current module
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Path to the Python script relative to this file
const pythonScriptPath = path.resolve(__dirname, '../python/reddit_service.py');

/**
 * Call the Reddit Python service with the specified method and parameters
 */
export async function callRedditService(method: string, params: any): Promise<any> {
  return new Promise((resolve, reject) => {
    console.error(`Calling Python script: ${pythonScriptPath}`);
    console.error(`Method: ${method}, Params: ${JSON.stringify(params)}`);
    
    // Make the Python script executable if it's not already
    const pythonProcess = spawn('python', [
      pythonScriptPath,
      method,
      JSON.stringify(params)
    ]);
    
    let dataString = '';
    let errorString = '';
    
    pythonProcess.stdout.on('data', (data: Buffer) => {
      dataString += data.toString();
    });
    
    pythonProcess.stderr.on('data', (data: Buffer) => {
      errorString += data.toString();
      console.error(`Python stderr: ${data.toString()}`);
    });
    
    pythonProcess.on('close', (code: number | null) => {
      console.error(`Python process exited with code ${code}`);
      
      if (code !== 0) {
        reject(new Error(`Process exited with code ${code}: ${errorString}`));
        return;
      }
      
      try {
        const result = JSON.parse(dataString);
        console.error(`Python result: ${JSON.stringify(result).substring(0, 200)}...`);
        resolve(result);
      } catch (e) {
        console.error(`Failed to parse Python output: ${e}`);
        console.error(`Raw output: ${dataString.substring(0, 200)}...`);
        reject(new Error(`Failed to parse Python output: ${e}`));
      }
    });
  });
}
