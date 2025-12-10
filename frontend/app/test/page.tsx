"use client";

import { useState, useEffect } from "react";
import { dashboardAPI } from "@/lib/api";

export default function TestPage() {
    const [result, setResult] = useState<string>("Not tested yet");
    const [loading, setLoading] = useState(false);

    const testAPI = async () => {
        setLoading(true);
        try {
            console.log("Starting API test...");
            const stats = await dashboardAPI.getStats();
            console.log("API test success:", stats);
            setResult(`Success: ${JSON.stringify(stats, null, 2)}`);
        } catch (error) {
            console.error("API test error:", error);
            setResult(`Error: ${error}`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-8">
            <h1 className="text-2xl font-bold mb-4">API Test Page</h1>
            
            <button 
                onClick={testAPI}
                disabled={loading}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
            >
                {loading ? "Testing..." : "Test Dashboard API"}
            </button>
            
            <div className="mt-4">
                <h2 className="font-semibold">Result:</h2>
                <pre className="bg-gray-100 p-4 rounded mt-2 whitespace-pre-wrap text-sm">
                    {result}
                </pre>
            </div>
            
            <div className="mt-4">
                <p className="text-sm text-gray-600">
                    Check the browser console for detailed logs.
                </p>
            </div>
        </div>
    );
}