import React, { useEffect, useRef, useState } from 'react';
import { AlertTriangle, CheckCircle2, Info, X, XCircle } from 'lucide-react';

/**
 * App-wide feedback: toast notifications and a confirmation dialog.
 *
 * These replace the browser's native alert()/confirm(), which block the page,
 * cannot be styled and look out of place. Usage from anywhere (no hook needed):
 *
 *   notify.success('Saved');
 *   notify.error('Something went wrong');
 *   if (await confirmDialog({ message: 'Delete this contact?', danger: true })) { ... }
 *
 * <FeedbackHost /> must be rendered once near the root of the app.
 */

type ToastKind = 'success' | 'error' | 'info';

interface Toast {
  id: number;
  kind: ToastKind;
  message: string;
}

export interface ConfirmOptions {
  title?: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  danger?: boolean;
}

interface PendingConfirm extends ConfirmOptions {
  resolve: (confirmed: boolean) => void;
}

type Listener = {
  toast: (toast: Toast) => void;
  confirm: (pending: PendingConfirm) => void;
};

let listener: Listener | null = null;
let nextId = 1;

const push = (kind: ToastKind, message: string): void => {
  if (listener) {
    listener.toast({ id: nextId++, kind, message });
  } else {
    // Host not mounted (should not happen) - never lose the message silently
    console.warn(`[${kind}] ${message}`);
  }
};

export const notify = {
  success: (message: string) => push('success', message),
  error: (message: string) => push('error', message),
  info: (message: string) => push('info', message),
};

export const confirmDialog = (options: ConfirmOptions | string): Promise<boolean> => {
  const base: ConfirmOptions = typeof options === 'string' ? { message: options } : options;
  // Destructive prompts get the warning styling unless the caller says otherwise
  const opts: ConfirmOptions = {
    danger: /delete|overwrite|cannot be undone/i.test(base.message),
    ...base,
  };
  return new Promise((resolve) => {
    if (listener) {
      listener.confirm({ ...opts, resolve });
    } else {
      resolve(window.confirm(opts.message));
    }
  });
};

const ICONS: Record<ToastKind, React.ReactNode> = {
  success: <CheckCircle2 className="h-5 w-5 text-emerald-500 shrink-0" />,
  error: <XCircle className="h-5 w-5 text-red-500 shrink-0" />,
  info: <Info className="h-5 w-5 text-blue-500 shrink-0" />,
};

export const FeedbackHost: React.FC = () => {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [pending, setPending] = useState<PendingConfirm | null>(null);
  const confirmButtonRef = useRef<HTMLButtonElement>(null);

  const dismiss = (id: number) => setToasts((current) => current.filter((t) => t.id !== id));

  useEffect(() => {
    listener = {
      toast: (toast) => {
        setToasts((current) => [...current, toast]);
        // Errors stay longer so they can be read
        window.setTimeout(() => dismiss(toast.id), toast.kind === 'error' ? 8000 : 4000);
      },
      confirm: (next) => setPending(next),
    };
    return () => {
      listener = null;
    };
  }, []);

  const settle = (confirmed: boolean) => {
    if (pending) {
      pending.resolve(confirmed);
      setPending(null);
    }
  };

  useEffect(() => {
    if (!pending) return;
    confirmButtonRef.current?.focus();
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') settle(false);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pending]);

  return (
    <>
      <div
        className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 w-[min(24rem,calc(100vw-2rem))]"
        role="status"
        aria-live="polite"
      >
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className="flex items-start gap-3 rounded-lg border border-border bg-card text-card-foreground shadow-lg p-4"
          >
            {ICONS[toast.kind]}
            <p className="flex-1 text-sm whitespace-pre-line break-words">{toast.message}</p>
            <button
              type="button"
              onClick={() => dismiss(toast.id)}
              className="text-muted-foreground hover:text-foreground"
              aria-label="Dismiss notification"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        ))}
      </div>

      {pending && (
        <div
          className="fixed inset-0 z-[110] flex items-center justify-center bg-black/50 p-4"
          onClick={() => settle(false)}
        >
          <div
            role="alertdialog"
            aria-modal="true"
            aria-labelledby="confirm-dialog-title"
            aria-describedby="confirm-dialog-message"
            className="w-full max-w-md rounded-lg border border-border bg-card text-card-foreground shadow-xl p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start gap-3">
              {pending.danger && <AlertTriangle className="h-6 w-6 text-red-500 shrink-0" />}
              <div>
                <h2 id="confirm-dialog-title" className="text-lg font-semibold">
                  {pending.title || 'Please confirm'}
                </h2>
                <p id="confirm-dialog-message" className="mt-2 text-sm text-muted-foreground whitespace-pre-line">
                  {pending.message}
                </p>
              </div>
            </div>
            <div className="mt-6 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => settle(false)}
                className="px-4 py-2 rounded-md border border-border text-sm hover:bg-muted"
              >
                {pending.cancelLabel || 'Cancel'}
              </button>
              <button
                ref={confirmButtonRef}
                type="button"
                onClick={() => settle(true)}
                className={`px-4 py-2 rounded-md text-sm text-white ${
                  pending.danger ? 'bg-red-600 hover:bg-red-700' : 'bg-blue-600 hover:bg-blue-700'
                }`}
              >
                {pending.confirmLabel || (pending.danger ? 'Delete' : 'Confirm')}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default FeedbackHost;
