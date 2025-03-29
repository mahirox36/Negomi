"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import LoadingScreen from "../components/LoadingScreen";
import { motion } from "framer-motion";

export default function PrivacyPolicy() {
  const [content, setContent] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchContent = async () => {
      try {
        const response = await axios.get("/api/v1/bot/privacy-policy", {withCredentials: true});
        setContent(response.data);
      } catch (err) {
        setError("Failed to load Privacy Policy");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchContent();
  }, []);

  if (loading) return <LoadingScreen message="Loading Privacy Policy..." />;
  if (error) return <div className="text-red-500 p-4">{error}</div>;

  return (
    <main className="min-h-screen bg-gradient-to-br from-pink-600 to-purple-800">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="container mx-auto px-4 pt-24 pb-12"
      >
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ 
            duration: 0.8,
            ease: [0.21, 0.47, 0.32, 0.98] 
          }}
          className="max-w-4xl mx-auto"
        >
          <div className="bg-black/20 backdrop-blur-xl rounded-2xl p-8 shadow-2xl border border-white/10">
            <motion.h1 
              initial={{ y: 10, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-white to-purple-200 mb-8"
            >
              Privacy Policy
            </motion.h1>
            <motion.div 
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.4 }}
              className="prose prose-invert max-w-none prose-h1:text-white prose-h2:text-purple-200 prose-h3:text-indigo-200 prose-p:text-gray-200 prose-a:text-indigo-400 prose-strong:text-white/90 prose-code:text-pink-300 prose-blockquote:border-l-purple-500"
            >
              <ReactMarkdown
                components={{
                  h1: ({node, ...props}) => <h1 className="text-3xl font-bold mb-6 mt-8 text-white" {...props} />,
                  h2: ({node, ...props}) => <h2 className="text-2xl font-semibold mb-4 mt-6 text-purple-200" {...props} />,
                  h3: ({node, ...props}) => <h3 className="text-xl font-medium mb-3 mt-4 text-indigo-200" {...props} />,
                  p: ({node, ...props}) => <p className="mb-4 text-gray-200 leading-relaxed" {...props} />,
                  ul: ({node, ...props}) => <ul className="list-disc pl-6 mb-4 text-gray-200 space-y-2" {...props} />,
                  ol: ({node, ...props}) => <ol className="list-decimal pl-6 mb-4 text-gray-200 space-y-2" {...props} />,
                  li: ({node, ...props}) => <li className="mb-1" {...props} />,
                  a: ({node, ...props}) => (
                    <a 
                      className="text-indigo-400 hover:text-indigo-300 underline decoration-2 underline-offset-2 transition-colors" 
                      {...props}
                    />
                  ),
                  blockquote: ({node, ...props}) => (
                    <blockquote 
                      className="border-l-4 border-purple-500 pl-4 italic text-gray-300 my-4" 
                      {...props}
                    />
                  ),
                }}
              >
                {content}
              </ReactMarkdown>
            </motion.div>
          </div>
        </motion.div>
      </motion.div>
    </main>
  );
}
