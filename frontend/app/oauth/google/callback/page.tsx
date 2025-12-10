"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { useAuth } from "../../../context/AuthContext";
import { API_URL } from "@/lib/config";

function GoogleCallbackContent() {
    const [status, setStatus] = useState("processing");
    const [message, setMessage] = useState("Completing your sign-in...");
    const [processed, setProcessed] = useState(false);
    const searchParams = useSearchParams();
    const { login } = useAuth();

    useEffect(() => {
        // Prevent multiple processing
        if (processed) return;

        const handleGoogleCallback = async () => {
            setProcessed(true);
            
            try {
                // Check if we received a token directly (current flow)
                const token = searchParams.get("token");
                const isNewUser = searchParams.get("new_user") === "true";
                
                if (token) {
                    // Token flow - backend already handled OAuth exchange
                    login(token);
                    setStatus("success");
                    setMessage("Sign-in successful! Redirecting...");
                    return;
                }

                // Legacy code flow (fallback)
                const code = searchParams.get("code");
                const error = searchParams.get("error");

                if (error) {
                    setStatus("error");
                    setMessage("Google sign-in was cancelled or failed.");
                    return;
                }

                if (!code) {
                    setStatus("error");
                    setMessage("No authorization code or token received.");
                    return;
                }

                const response = await fetch(`${API_URL}/auth/google/callback?code=${code}`, {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                    },
                });

                if (response.ok) {
                    const data = await response.json();
                    login(data.access_token);
                    setStatus("success");
                    setMessage("Sign-in successful! Redirecting...");
                } else {
                    const errorData = await response.json();
                    setStatus("error");
                    setMessage(errorData.detail || "Failed to complete Google sign-in");
                }
            } catch (err) {
                setStatus("error");
                setMessage("Network error during sign-in");
            }
        };

        handleGoogleCallback();
    }, []); // Empty dependency array since we only want this to run once

    return (
        <div className="flex min-h-screen items-center justify-center bg-gray-100">
            <div className="w-full max-w-md rounded-lg bg-white p-8 shadow-md text-center">
                {status === "processing" && (
                    <>
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                        <h2 className="text-xl font-semibold text-gray-900 mb-2">
                            Completing Sign-In
                        </h2>
                        <p className="text-gray-600">{message}</p>
                    </>
                )}

                {status === "success" && (
                    <>
                        <div className="rounded-full bg-green-100 p-3 mx-auto mb-4 w-16 h-16 flex items-center justify-center">
                            <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                            </svg>
                        </div>
                        <h2 className="text-xl font-semibold text-gray-900 mb-2">
                            Welcome!
                        </h2>
                        <p className="text-gray-600">{message}</p>
                    </>
                )}

                {status === "error" && (
                    <>
                        <div className="rounded-full bg-red-100 p-3 mx-auto mb-4 w-16 h-16 flex items-center justify-center">
                            <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                        </div>
                        <h2 className="text-xl font-semibold text-gray-900 mb-2">
                            Sign-In Failed
                        </h2>
                        <p className="text-gray-600 mb-4">{message}</p>
                        <a
                            href="/login"
                            className="inline-block px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                        >
                            Try Again
                        </a>
                    </>
                )}
            </div>
        </div>
    );
}

function LoadingFallback() {
    return (
        <div className="flex min-h-screen items-center justify-center bg-gray-100">
            <div className="w-full max-w-md rounded-lg bg-white p-8 shadow-md text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                    Loading...
                </h2>
                <p className="text-gray-600">Please wait while we complete your sign-in.</p>
            </div>
        </div>
    );
}

export default function GoogleCallbackPage() {
    return (
        <Suspense fallback={<LoadingFallback />}>
            <GoogleCallbackContent />
        </Suspense>
    );
}