/**
 * Format a number of hours as a readable string.
 */
export const formatHours = (hours: number): string => {
  const h = Math.floor(hours);
  const m = Math.round((hours - h) * 60);
  return `${h}h ${m}m`;
};

/**
 * Format a date string to a locale-friendly display.
 */
export const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr + 'T00:00:00');
  return date.toLocaleDateString('en-US', {
    weekday: 'short',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

/**
 * Get the Monday of the current week.
 */
export const getWeekStart = (date: Date = new Date()): Date => {
  const d = new Date(date);
  const day = d.getDay();
  const diff = d.getDate() - day + (day === 0 ? -6 : 1);
  d.setDate(diff);
  d.setHours(0, 0, 0, 0);
  return d;
};

/**
 * Format a date as YYYY-MM-DD for API calls.
 */
export const toISODate = (date: Date): string => {
  return date.toISOString().split('T')[0];
};

/**
 * Get status badge color class.
 */
export const getStatusColor = (status: string): string => {
  const colors: Record<string, string> = {
    draft: '#6b7280',
    submitted: '#f59e0b',
    approved: '#10b981',
    rejected: '#ef4444',
    active: '#10b981',
    completed: '#3b82f6',
    on_hold: '#f59e0b',
    cancelled: '#6b7280',
  };
  return colors[status] || '#6b7280';
};
