import { TextareaHTMLAttributes, useEffect, useRef } from 'react';

interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  autoResize?: boolean;
  maxHeight?: number;
}

export default function Textarea({
  label,
  error,
  autoResize = true,
  maxHeight = 400,
  className = '',
  ...props
}: TextareaProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (autoResize && textareaRef.current) {
      const textarea = textareaRef.current;
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, maxHeight)}px`;
    }
  }, [props.value, autoResize, maxHeight]);

  return (
    <div className="space-y-1">
      {label && (
        <label className="block text-sm font-medium text-white/70">
          {label}
        </label>
      )}
      <textarea
        ref={textareaRef}
        {...props}
        className={`w-full px-4 py-2.5 rounded-lg bg-white/10 border border-white/20
          text-white transition-all duration-200 outline-none resize-none
          focus:border-white/40 focus:ring-2 focus:ring-white/20
          ring-offset-2 ring-offset-[#1a1b1e] ${className}`}
        style={{
          minHeight: '80px',
          maxHeight: `${maxHeight}px`
        }}
      />
      {error && (
        <p className="text-sm text-red-400">{error}</p>
      )}
    </div>
  );
}
