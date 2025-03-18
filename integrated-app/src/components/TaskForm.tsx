"use client";

import { useState, FormEvent } from "react";
import { FaSpinner } from "react-icons/fa";
import axios from "axios";

type TaskFormProps = {
  onTaskCreated: (taskId: string) => void;
};

export default function TaskForm({ onTaskCreated }: TaskFormProps) {
  const [url, setUrl] = useState("");
  const [description, setDescription] = useState("");
  const [taskType, setTaskType] = useState("web_scrape");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    // Reset error state
    setError(null);
    
    // Validation
    if (!url.trim()) {
      setError("URL is required");
      return;
    }
    
    if (!description.trim()) {
      setError("Description is required");
      return;
    }
    
    // Set loading state
    setIsLoading(true);
    
    try {
      const response = await axios.post("/api/flask/task", {
        url,
        description,
        task_type: taskType
      });
      
      if (response.data && response.data.status === "success") {
        // Clear form
        setUrl("");
        setDescription("");
        setTaskType("web_scrape");
        
        // Notify parent component
        onTaskCreated(response.data.task.id);
      } else {
        setError(response.data.message || "An error occurred while creating the task");
      }
    } catch (err) {
      console.error("Error creating task:", err);
      setError(err instanceof Error ? err.message : "An error occurred while creating the task");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-900/50 border border-red-500 p-3 rounded-md text-sm text-red-200">
          {error}
        </div>
      )}
      
      <div className="space-y-2">
        <label htmlFor="url" className="block text-sm font-medium text-gray-300">
          Target URL
        </label>
        <input
          type="url"
          id="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://example.com"
          className="w-full p-2 rounded-md bg-gray-700 border border-gray-600 text-white focus:ring-2 focus:ring-primary focus:border-transparent"
          required
        />
      </div>
      
      <div className="space-y-2">
        <label htmlFor="description" className="block text-sm font-medium text-gray-300">
          Task Description
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Describe what you want to automate, e.g., 'Gather news headlines and summarize them'"
          rows={4}
          className="w-full p-2 rounded-md bg-gray-700 border border-gray-600 text-white focus:ring-2 focus:ring-primary focus:border-transparent"
          required
        />
      </div>
      
      <div className="space-y-2">
        <label htmlFor="taskType" className="block text-sm font-medium text-gray-300">
          Task Type
        </label>
        <select
          id="taskType"
          value={taskType}
          onChange={(e) => setTaskType(e.target.value)}
          className="w-full p-2 rounded-md bg-gray-700 border border-gray-600 text-white focus:ring-2 focus:ring-primary focus:border-transparent"
        >
          <option value="web_scrape">Web Scraping</option>
          <option value="form_fill">Form Filling</option>
          <option value="data_extraction">Data Extraction</option>
        </select>
      </div>
      
      <div className="pt-2">
        <button
          type="submit"
          disabled={isLoading}
          className="w-full py-2 px-4 bg-primary hover:bg-primary-dark text-gray-900 font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isLoading ? (
            <>
              <FaSpinner className="inline-block mr-2 animate-spin" />
              Processing...
            </>
          ) : (
            "Start Task"
          )}
        </button>
      </div>
    </form>
  );
}
