import { Play, Pause, Settings } from 'lucide-react';
import { useState } from 'react';

interface ControlsProps {
  status: 'running' | 'stopped';
  onStatusChange: (status: 'running' | 'stopped') => void;
}

export default function Controls({ status, onStatusChange }: ControlsProps) {
  const [showSettings, setShowSettings] = useState(false);

  const toggleAgent = () => {
    onStatusChange(status === 'running' ? 'stopped' : 'running');
  };

  return (
    <div className="flex items-center gap-3">
      <div className="flex items-center gap-2 px-4 py-2 bg-gray-800/50 rounded-lg border border-gray-700">
        <div
          className={`w-2 h-2 rounded-full ${
            status === 'running' ? 'bg-green-400 animate-pulse' : 'bg-gray-500'
          }`}
        />
        <span className="text-sm font-medium">
          {status === 'running' ? 'Active' : 'Inactive'}
        </span>
      </div>

      <button
        onClick={toggleAgent}
        className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
          status === 'running'
            ? 'bg-red-500/20 text-red-400 hover:bg-red-500/30 border border-red-500/50'
            : 'bg-green-500/20 text-green-400 hover:bg-green-500/30 border border-green-500/50'
        }`}
      >
        {status === 'running' ? (
          <>
            <Pause className="w-4 h-4" />
            Stop
          </>
        ) : (
          <>
            <Play className="w-4 h-4" />
            Start
          </>
        )}
      </button>

      <button
        onClick={() => setShowSettings(!showSettings)}
        className="p-2 bg-gray-800/50 hover:bg-gray-700/50 rounded-lg border border-gray-700 transition-colors"
      >
        <Settings className="w-5 h-5" />
      </button>
    </div>
  );
}
