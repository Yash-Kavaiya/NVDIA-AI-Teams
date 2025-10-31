export function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center h-screen bg-nvidia-dark">
      <div className="text-center">
        <div className="relative w-24 h-24 mx-auto mb-6">
          <div className="absolute inset-0 border-4 border-nvidia-green/30 rounded-full"></div>
          <div className="absolute inset-0 border-4 border-nvidia-green border-t-transparent rounded-full animate-spin"></div>
        </div>
        <h2 className="text-nvidia-text text-xl font-semibold mb-2">
          Loading NVIDIA AI Agent
        </h2>
        <p className="text-nvidia-gray text-sm">
          Initializing vector database and embeddings...
        </p>
      </div>
    </div>
  );
}

export function EmptyState({ icon, title, description }: { 
  icon: string; 
  title: string; 
  description: string;
}) {
  return (
    <div className="flex items-center justify-center h-full p-8">
      <div className="text-center max-w-md">
        <div className="text-6xl mb-4">{icon}</div>
        <h3 className="text-nvidia-text text-xl font-semibold mb-2">{title}</h3>
        <p className="text-nvidia-gray">{description}</p>
      </div>
    </div>
  );
}
