export default function LoadingSpinner({ message }: { message?: string }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
      <div className="text-center">
        <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mx-auto mb-4" />
        {message && <p className="text-gray-600">{message}</p>}
      </div>
    </div>
  )
}
