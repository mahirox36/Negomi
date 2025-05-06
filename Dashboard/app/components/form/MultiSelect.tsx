import { useState, useRef, useEffect } from 'react';

interface Option {
  value: string;
  label: string;
}

interface MultiSelectProps {
  options: Option[];
  value: string[];
  onChange: (value: string[]) => void;
  label?: string;
  placeholder?: string;
  className?: string;
}

export default function MultiSelect({
  options,
  value,
  onChange,
  label,
  placeholder = 'Select options...',
  className = ''
}: MultiSelectProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const containerRef = useRef<HTMLDivElement>(null);

  const filteredOptions = options.filter(
    option => !value.includes(option.value) &&
    option.label.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const selectedOptions = options.filter(
    option => value.includes(option.value)
  );

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="space-y-1">
      {label && (
        <label className="block text-sm font-medium text-white/70">
          {label}
        </label>
      )}
      <div ref={containerRef} className={`relative ${className}`}>
        <div
          className="min-h-[42px] px-3 py-1.5 rounded-lg bg-white/10 border border-white/20
            text-white cursor-pointer transition-all duration-200
            focus-within:border-white/40 focus-within:ring-2 focus-within:ring-white/20
            ring-offset-2 ring-offset-[#1a1b1e]"
          onClick={() => setIsOpen(true)}
        >
          <div className="flex flex-wrap gap-2">
            {selectedOptions.map((option) => (
              <div
                key={option.value}
                className="inline-flex items-center gap-1 px-2 py-1 bg-white/20
                  rounded-md text-sm"
              >
                {option.label}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onChange(value.filter(v => v !== option.value));
                  }}
                  className="hover:text-red-400 transition-colors"
                >
                  <i className="fas fa-times"></i>
                </button>
              </div>
            ))}
            <input
              type="text"
              className="flex-1 min-w-[120px] bg-transparent outline-none"
              placeholder={selectedOptions.length === 0 ? placeholder : ''}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onFocus={() => setIsOpen(true)}
            />
          </div>
        </div>
        {isOpen && filteredOptions.length > 0 && (
          <div className="absolute w-full mt-1 py-2 bg-[#1a1b1e]/95 border border-white/10
            rounded-lg backdrop-blur-lg shadow-xl z-50 max-h-60 overflow-auto">
            {filteredOptions.map((option) => (
              <div
                key={option.value}
                className="px-4 py-2 hover:bg-white/10 cursor-pointer text-white/90
                  transition-colors"
                onClick={() => {
                  onChange([...value, option.value]);
                  setSearchTerm('');
                }}
              >
                {option.label}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
