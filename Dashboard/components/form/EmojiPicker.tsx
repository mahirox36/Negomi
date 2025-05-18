import { useState, useRef, useEffect } from 'react';
import data from '@emoji-mart/data';
import Picker from '@emoji-mart/react';

interface EmojiPickerProps {
  value: string;
  onChange: (emoji: string) => void;
  placeholder?: string;
  theme?: 'purple' | 'default';
}

export default function EmojiPicker({ value, onChange, placeholder = 'Select an emoji...', theme = 'purple' }: EmojiPickerProps) {
  const [showPicker, setShowPicker] = useState(false);
  const pickerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (pickerRef.current && !pickerRef.current.contains(event.target as Node)) {
        setShowPicker(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleEmojiSelect = (emoji: any) => {
    onChange(emoji.native);
    setShowPicker(false);
  };

  return (
    <div className="relative" ref={pickerRef}>
      <button
        onClick={() => setShowPicker(!showPicker)}
        className={`w-full px-4 py-2 rounded-lg border ${
          theme === 'purple'
            ? 'border-purple-500/20 bg-purple-500/10 hover:bg-purple-500/20'
            : 'border-white/10 bg-white/5 hover:bg-white/10'
        } transition-all flex items-center justify-between`}
      >
        <span className="text-white/70">{value || placeholder}</span>
        <i className="fas fa-smile text-white/50"></i>
      </button>

      {showPicker && (
        <div className="absolute z-50 mt-2">
          <Picker
            data={data}
            onEmojiSelect={handleEmojiSelect}
            theme="dark"
            set="native"
          />
        </div>
      )}
    </div>
  );
}