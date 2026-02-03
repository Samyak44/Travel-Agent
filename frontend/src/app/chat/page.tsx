'use client'

import { useState, useEffect, useRef } from 'react'
import { FaPaperPlane, FaPlus, FaComments, FaBars, FaTimes } from 'react-icons/fa'
import { api } from '@/lib/api'
import { useAuthGuard } from '@/hooks/useAuthGuard'
import Navbar from '@/components/Navbar'
import LoadingSpinner from '@/components/LoadingSpinner'
import { ChatResponse } from '@/types'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

interface Conversation {
  conversation_id: string
  title?: string
  updated_at?: string
}

export default function ChatPage() {
  const { user, isLoading: authLoading } = useAuthGuard()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [sending, setSending] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [suggestions, setSuggestions] = useState<string[]>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (user) {
      loadConversations()
    }
  }, [user])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, sending])

  const loadConversations = async () => {
    if (!user) return
    try {
      const data = await api.getUserConversations(user.id)
      setConversations(data.conversations || data || [])
    } catch {
      // conversations may not exist yet
    }
  }

  const loadConversation = async (convId: string) => {
    try {
      const data = await api.getConversationHistory(convId)
      const history: Message[] = (data.messages || data || []).map((m: any) => ({
        role: m.role,
        content: m.content,
      }))
      setMessages(history)
      setConversationId(convId)
      setSuggestions([])
      setSidebarOpen(false)
    } catch {
      // handle error silently
    }
  }

  const startNewChat = () => {
    setMessages([])
    setConversationId(null)
    setSuggestions([])
    setSidebarOpen(false)
  }

  const sendMessage = async (text?: string) => {
    const messageText = text || input.trim()
    if (!messageText || sending || !user) return

    const userMessage: Message = { role: 'user', content: messageText }
    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setSuggestions([])
    setSending(true)

    try {
      const data: ChatResponse = await api.sendMessage(
        messageText,
        conversationId || undefined,
        user.id
      )
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.message,
      }
      setMessages((prev) => [...prev, assistantMessage])

      if (data.conversation_id) {
        setConversationId(data.conversation_id)
      }
      if (data.suggestions?.length) {
        setSuggestions(data.suggestions)
      }

      loadConversations()
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Sorry, something went wrong. Please try again.' },
      ])
    } finally {
      setSending(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  if (authLoading) {
    return <LoadingSpinner message="Loading..." />
  }

  if (!user) return null

  return (
    <div className="h-screen flex flex-col bg-gray-100">
      <Navbar />
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar overlay for mobile */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 bg-black/30 z-20 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Sidebar */}
        <aside
          className={`
            fixed lg:static inset-y-0 left-0 z-30 w-72 bg-white border-r border-gray-200
            transform transition-transform lg:translate-x-0
            ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
            flex flex-col pt-16 lg:pt-0
          `}
        >
          <div className="p-4 border-b border-gray-200">
            <button
              onClick={startNewChat}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 flex items-center justify-center space-x-2"
            >
              <FaPlus />
              <span>New Chat</span>
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-2">
            {conversations.length === 0 ? (
              <p className="text-gray-400 text-sm text-center mt-4">No conversations yet</p>
            ) : (
              conversations.map((conv) => (
                <button
                  key={conv.conversation_id}
                  onClick={() => loadConversation(conv.conversation_id)}
                  className={`w-full text-left p-3 rounded-lg mb-1 hover:bg-gray-100 transition-colors flex items-center space-x-2 ${
                    conversationId === conv.conversation_id ? 'bg-blue-50 text-blue-700' : 'text-gray-700'
                  }`}
                >
                  <FaComments className="flex-shrink-0 text-gray-400" />
                  <span className="truncate text-sm">
                    {conv.title || conv.conversation_id.slice(0, 8) + '...'}
                  </span>
                </button>
              ))
            )}
          </div>
        </aside>

        {/* Main chat area */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Mobile sidebar toggle */}
          <div className="lg:hidden p-2 border-b border-gray-200 bg-white">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 text-gray-600 hover:text-gray-900"
            >
              {sidebarOpen ? <FaTimes /> : <FaBars />}
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 && (
              <div className="flex items-center justify-center h-full">
                <div className="text-center max-w-md">
                  <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <FaComments className="text-blue-600 text-2xl" />
                  </div>
                  <h2 className="text-xl font-semibold text-gray-900 mb-2">
                    Welcome, {user.full_name}!
                  </h2>
                  <p className="text-gray-500">
                    Ask me anything about travel planning. I can help you search flights,
                    find hotels, check weather, and more!
                  </p>
                </div>
              </div>
            )}

            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[75%] px-4 py-3 rounded-2xl whitespace-pre-wrap ${
                    msg.role === 'user'
                      ? 'bg-blue-600 text-white rounded-br-md'
                      : 'bg-white text-gray-900 shadow-sm border border-gray-100 rounded-bl-md'
                  }`}
                >
                  {msg.content}
                </div>
              </div>
            ))}

            {sending && (
              <div className="flex justify-start">
                <div className="bg-white px-4 py-3 rounded-2xl rounded-bl-md shadow-sm border border-gray-100">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Suggestion chips */}
          {suggestions.length > 0 && (
            <div className="px-4 pb-2 flex flex-wrap gap-2">
              {suggestions.map((s, idx) => (
                <button
                  key={idx}
                  onClick={() => sendMessage(s)}
                  className="bg-white border border-blue-200 text-blue-700 px-3 py-1 rounded-full text-sm hover:bg-blue-50 transition-colors"
                >
                  {s}
                </button>
              ))}
            </div>
          )}

          {/* Input area */}
          <div className="p-4 bg-white border-t border-gray-200">
            <div className="max-w-3xl mx-auto flex space-x-2">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Type your message..."
                rows={1}
                className="flex-1 resize-none border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
              />
              <button
                onClick={() => sendMessage()}
                disabled={!input.trim() || sending}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <FaPaperPlane />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
