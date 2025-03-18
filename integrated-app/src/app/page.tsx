"use client";

import { useState } from "react";
import HeaderNav from "@/components/HeaderNav";
import ChatInterface from "@/components/ChatInterface";
import TaskForm from "@/components/TaskForm";
import TaskResults from "@/components/TaskResults";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"automation" | "chat">("automation");
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null);
  const [taskUpdated, setTaskUpdated] = useState<boolean>(false);

  return (
    <main className="min-h-screen retro-scanlines">
      <HeaderNav />
      
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center mb-6">
          <div className="inline-flex rounded-md shadow-sm" role="group">
            <button
              type="button"
              className={`px-6 py-2 text-sm font-medium rounded-l-lg ${
                activeTab === "automation"
                  ? "bg-primary text-gray-900 hover:bg-primary-dark"
                  : "bg-gray-800 text-gray-300 hover:bg-gray-700"
              }`}
              onClick={() => setActiveTab("automation")}
            >
              Browser Automation
            </button>
            <button
              type="button"
              className={`px-6 py-2 text-sm font-medium rounded-r-lg ${
                activeTab === "chat"
                  ? "bg-primary text-gray-900 hover:bg-primary-dark"
                  : "bg-gray-800 text-gray-300 hover:bg-gray-700"
              }`}
              onClick={() => setActiveTab("chat")}
            >
              AI Assistant
            </button>
          </div>
        </div>

        {activeTab === "automation" ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-gray-800 rounded-xl p-6 shadow-lg">
              <h2 className="text-2xl font-bold mb-4 text-primary">Create Automation Task</h2>
              <TaskForm 
                onTaskCreated={(taskId) => {
                  setCurrentTaskId(taskId);
                  setTaskUpdated(true);
                }}
              />
            </div>
            
            <div className="bg-gray-800 rounded-xl p-6 shadow-lg">
              <h2 className="text-2xl font-bold mb-4 text-primary">Task Results</h2>
              <TaskResults 
                taskId={currentTaskId} 
                taskUpdated={taskUpdated}
                onTaskLoaded={() => setTaskUpdated(false)}
              />
            </div>
          </div>
        ) : (
          <div className="bg-gray-800 rounded-xl shadow-lg h-[700px]">
            <ChatInterface />
          </div>
        )}
      </div>
    </main>
  );
}
