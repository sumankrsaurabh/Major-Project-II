import { CheckCircle, AlertCircle, Loader2 } from 'lucide-react';

export default function ServerStatus({ status }) {
  const statusConfig = {
    ok: { icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-50', label: 'Connected' },
    checking: { icon: Loader2, color: 'text-blue-600', bg: 'bg-blue-50', label: 'Checking' },
    error: { icon: AlertCircle, color: 'text-red-600', bg: 'bg-red-50', label: 'Error' },
    offline: { icon: AlertCircle, color: 'text-yellow-600', bg: 'bg-yellow-50', label: 'Offline' },
  };

  const config = statusConfig[status] || statusConfig.checking;
  const Icon = config.icon;

  return (
    <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-medium ${config.bg} ${config.color.replace('text-', 'border-')}/30`}>
      <Icon className={`w-4 h-4 ${status === 'checking' ? 'animate-spin' : ''}`} />
      <span>{config.label}</span>
    </div>
  );
}
