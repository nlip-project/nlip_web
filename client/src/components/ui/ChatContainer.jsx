

export default function ChatContainer({ header, children }) {
  return (
    <div className="w-full max-w-4xl bg-white rounded-2xl shadow-2xl overflow-hidden flex flex-col h-[85vh]">
      <div className="bg-linear-to-r from-cyan-500 to-blue-500 text-white px-6 py-4">
        <h2 className="text-2xl font-bold">{header}</h2>
      </div>

      {children}
    </div>
  )
}