import { useState, useEffect, useRef } from 'react';

interface SearchInputProps {
  onSearch: (value: string) => void;
  suggestions?: string[];
  placeholder?: string;
  className?: string;
}

export default function SearchInput({
  onSearch,
  suggestions = [],
  placeholder = 'Search...',
  className = ''
}: SearchInputProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [value, setValue] = useState('');
  const [filteredSuggestions, setFilteredSuggestions] = useState<string[]>([]);
  const inputRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const filtered = suggestions.filter(item =>
      item.toLowerCase().includes(value.toLowerCase())
    ).slice(0, 5);
    setFilteredSuggestions(filtered);
  }, [value, suggestions]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (inputRef.current && !inputRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div ref={inputRef} className={`relative ${className}`}>
      <div className="relative">
        <i className="fas fa-search absolute left-3 top-1/2 -translate-y-1/2 text-white/50"></i>
        <input
          type="text"
          value={value}
          onChange={(e) => {
            setValue(e.target.value);
            setIsOpen(true);
            onSearch(e.target.value);
          }}
          onFocus={() => setIsOpen(true)}
          placeholder={placeholder}
          className="w-full pl-10 pr-4 py-2.5 rounded-lg bg-white/10 border border-white/20
            text-white transition-all duration-200 outline-none
            focus:border-white/40 focus:ring-2 focus:ring-white/20
            ring-offset-2 ring-offset-[#1a1b1e]"
        />
      </div>
      {isOpen && filteredSuggestions.length > 0 && (
        <div className="absolute w-full mt-1 py-2 bg-[#1a1b1e]/95 border border-white/10
          rounded-lg backdrop-blur-lg shadow-xl z-50">
          {filteredSuggestions.map((suggestion, index) => (
            <div
              key={index}
              className="px-4 py-2 hover:bg-white/10 cursor-pointer text-white/90
                transition-colors"
              onClick={() => {
                setValue(suggestion);
                onSearch(suggestion);
                setIsOpen(false);
              }}
            >
              {suggestion}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
