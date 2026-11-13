/**
 * Turn an API error into a message a person can read.
 *
 * The backend answers validation failures in a few shapes:
 *   { detail: "..." } | { error: "..." } | { field: ["...", ...], ... }
 * This flattens whichever one arrives; `fallback` is used when there is nothing
 * useful (e.g. the server could not be reached).
 */
export const getErrorMessage = (err: any, fallback = 'Something went wrong. Please try again.'): string => {
  const data = err?.response?.data;
  if (!data) {
    return err?.response ? fallback : 'Could not reach the server. Check your connection and try again.';
  }
  if (typeof data === 'string') {
    // Avoid dumping an HTML error page into the UI
    return data.length < 300 && !data.trim().startsWith('<') ? data : fallback;
  }
  if (typeof data.detail === 'string') return data.detail;
  if (typeof data.error === 'string') return data.error;
  if (typeof data.message === 'string') return data.message;

  const parts: string[] = [];
  for (const [field, value] of Object.entries(data)) {
    const text = Array.isArray(value) ? value.join(' ') : typeof value === 'string' ? value : '';
    if (!text) continue;
    const label = field === 'non_field_errors' ? '' : `${field.replace(/_/g, ' ')}: `;
    parts.push(`${label}${text}`);
  }
  return parts.length ? parts.join('\n') : fallback;
};

export default getErrorMessage;
