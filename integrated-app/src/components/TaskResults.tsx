"use client";

import { useState, useEffect } from "react";
import { FaSpinner } from "react-icons/fa";
import axios from "axios";
import { marked } from "marked";

type TaskResultsProps = {
  taskId: string | null;
  taskUpdated: boolean;
  onTaskLoaded: () => void;
};

type Task = {
  id: string;
  url: string;
  description: string;
  task_type: string;
  status: string;
  created_at: number;
  updated_at: number;
  result: any;
  error: string | null;
};

export default function TaskResults({ taskId, taskUpdated, onTaskLoaded }: TaskResultsProps) {
  const [task, setTask] = useState<Task | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pollingIntervalId, setPollingIntervalId] = useState<NodeJS.Timeout | null>(null);

  useEffect(() => {
    // Clear polling interval when component unmounts
    return () => {
      if (pollingIntervalId) {
        clearInterval(pollingIntervalId);
      }
    };
  }, [pollingIntervalId]);

  useEffect(() => {
    if (taskId && taskUpdated) {
      fetchTask(taskId);
      onTaskLoaded();
    }
  }, [taskId, taskUpdated, onTaskLoaded]);

  const fetchTask = async (id: string) => {
    // Clear any existing polling
    if (pollingIntervalId) {
      clearInterval(pollingIntervalId);
      setPollingIntervalId(null);
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`/api/flask/task/${id}`);
      
      if (response.data && response.data.status === "success") {
        setTask(response.data.task);
        
        // If task is still running, start polling
        if (response.data.task.status === "running" || response.data.task.status === "pending") {
          const intervalId = setInterval(() => fetchTask(id), 2000);
          setPollingIntervalId(intervalId);
        }
      } else {
        setError(response.data.message || "Failed to fetch task details");
      }
    } catch (err) {
      console.error("Error fetching task:", err);
      setError(err instanceof Error ? err.message : "An error occurred while fetching the task");
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading && !task) {
    return (
      <div className="flex flex-col items-center justify-center p-8">
        <FaSpinner className="text-primary text-4xl animate-spin mb-4" />
        <p className="text-gray-300">Loading task details...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-900/50 border border-red-500 p-4 rounded-md">
        <h3 className="text-lg font-semibold text-red-200 mb-2">Error</h3>
        <p className="text-red-200">{error}</p>
      </div>
    );
  }

  if (!task) {
    return (
      <div className="bg-gray-700 rounded-md p-6 text-center">
        <p className="text-gray-300">No task selected. Create a new task to see results here.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="bg-gray-700 rounded-md p-4">
        <h3 className="font-semibold text-primary mb-1">Task Details</h3>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div className="text-gray-400">URL:</div>
          <div className="text-white truncate">{task.url}</div>
          <div className="text-gray-400">Type:</div>
          <div className="text-white capitalize">{task.task_type.replace('_', ' ')}</div>
          <div className="text-gray-400">Status:</div>
          <div>
            <span 
              className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${
                task.status === "completed" 
                  ? "bg-green-900/50 text-green-300" 
                  : task.status === "failed"
                  ? "bg-red-900/50 text-red-300"
                  : task.status === "running"
                  ? "bg-blue-900/50 text-blue-300"
                  : "bg-gray-900/50 text-gray-300"
              }`}
            >
              {task.status}
              {(task.status === "running" || task.status === "pending") && (
                <FaSpinner className="inline-block ml-1 animate-spin" size={10} />
              )}
            </span>
          </div>
        </div>
      </div>

      {task.status === "completed" && task.result && (
        <div className="bg-gray-700 rounded-md p-4">
          <h3 className="font-semibold text-primary mb-3">Results</h3>
          
          {task.result.title && (
            <div className="mb-3">
              <h4 className="text-white font-medium text-lg">{task.result.title}</h4>
            </div>
          )}
          
          {task.result.summary && (
            <div className="prose prose-sm prose-invert max-w-none">
              <div 
                dangerouslySetInnerHTML={{ 
                  __html: marked(task.result.summary) as string 
                }}
              />
            </div>
          )}
          
          {!task.result.summary && !task.result.title && (
            <pre className="bg-gray-800 p-3 rounded-md overflow-auto text-xs text-gray-300">
              {JSON.stringify(task.result, null, 2)}
            </pre>
          )}
        </div>
      )}

      {task.status === "failed" && task.error && (
        <div className="bg-red-900/30 border border-red-900 rounded-md p-4">
          <h3 className="font-semibold text-red-300 mb-2">Error</h3>
          <p className="text-red-200">{task.error}</p>
        </div>
      )}

      {(task.status === "running" || task.status === "pending") && (
        <div className="bg-blue-900/30 border border-blue-900 rounded-md p-4 flex items-center space-x-3">
          <FaSpinner className="text-blue-300 animate-spin" />
          <p className="text-blue-200">
            {task.status === "running" 
              ? "Task is currently running. Results will appear here when complete." 
              : "Task is queued and will start shortly..."}
          </p>
        </div>
      )}
    </div>
  );
}
