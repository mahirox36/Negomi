import { useState, useRef, useEffect } from 'react';
import axios from 'axios';

interface DiscordOption {
  id: string;
  name: string;
  type?: string;
  color?: string;
  icon?: string;
}

interface DiscordSelectProps {
  type: 'channel' | 'role';
  guildId: string;
  value: string | string[];
  onChange: (value: string | string[]) => void;
  className?: string;
  placeholder?: string;
  multiple?: boolean;
  searchable?: boolean;
}

export default function DiscordSelect({
  type,
  guildId,
  value,
  onChange,
  className = '',
  placeholder = 'Select...',
  multiple = false,
  searchable = false
}: DiscordSelectProps) {
  const [options, setOptions] = useState<DiscordOption[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const containerRef = useRef<HTMLDivElement>(null);

  // Convert value to array for consistent handling
  const selectedValues = Array.isArray(value) ? value : [value];

  const selectedOptions = options.filter(opt => selectedValues.includes(opt.id));
  const filteredOptions = options.filter(opt => 
    !selectedValues.includes(opt.id) &&
    opt.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  useEffect(() => {
    const fetchOptions = async () => {
      setIsLoading(true);
      try {
        const response = await axios.get(`/api/v1/guilds/${guildId}/${type}s`);
        setOptions(response.data);
      } catch (error) {
        console.error(`Failed to fetch ${type}s:`, error);
      }
      setIsLoading(false);
    };

    fetchOptions();
  }, [guildId, type]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (optionId: string) => {
    if (multiple) {
      const newValue = selectedValues.includes(optionId)
        ? selectedValues.filter(v => v !== optionId)
        : [...selectedValues, optionId];
      onChange(newValue);
    } else {
      onChange(optionId);
      setIsOpen(false);
    }
    setSearchTerm('');
  };

  const handleRemove = (optionId: string, event: React.MouseEvent) => {
    event.stopPropagation();
    if (multiple) {
      onChange(selectedValues.filter(v => v !== optionId));
    }
  };

  const getDefaultIcon = (type: 'channel' | 'role') => {
    if (type === 'channel') return 'fa-solid fa-hashtag';
    // Role icons based on name patterns
    return {
      admin: 'fa-solid fa-crown',
      admins: 'fa-solid fa-crown',
      mod: 'fa-solid fa-shield',
      mods: 'fa-solid fa-shield',
      bot: 'fa-solid fa-robot',
      bots: 'fa-solid fa-robot',
      mute: 'fa-solid fa-volume-xmark',
      default: 'fa-solid fa-circle'
    };
  };

  const getRoleIcon = (option: DiscordOption) => {
    if (type !== 'role') return getDefaultIcon('channel');
    const name = option.name.toLowerCase();
    const roleIcons = getDefaultIcon('role') as Record<string, string>;
    
    for (const [key, icon] of Object.entries(roleIcons)) {
      if (name.includes(key)) return icon;
    }
    return roleIcons.default;
  };

  const isValidColor = (color?: string) => {
    return color && color !== '#000000';
  };

  const renderOptionContent = (option: DiscordOption, onClick?: (e: React.MouseEvent) => void) => {
    const validColor = isValidColor(option.color);
    const style = validColor ? {
      backgroundColor: `${option.color}15`,
      borderColor: option.color,
      color: option.color
    } : undefined;

    return (
      <div
        className={`inline-flex items-center gap-2 px-2.5 py-1.5 rounded-md text-sm
          transition-all duration-200
          ${validColor ? 'border-2' : 'bg-white/15 border border-white/20'}`}
        style={style}
      >
        {option.icon ? (
          <img
            src={option.icon}
            alt=""
            className="w-4 h-4 rounded-full object-cover flex-shrink-0"
            onError={(e) => {
              const target = e.target as HTMLImageElement;
              target.style.display = 'none';
              target.parentElement?.querySelector('.default-icon')?.classList.remove('hidden');
            }}
          />
        ) : (
          <i className={`${getRoleIcon(option)} text-sm opacity-70 flex-shrink-0 default-icon`} />
        )}
        <span>{option.name}</span>
        {multiple && onClick && (
          <button
            onClick={onClick}
            className="ml-1 hover:text-red-400 transition-colors focus:outline-none"
            aria-label="Remove"
          >
            <i className="fas fa-times text-xs" />
          </button>
        )}
      </div>
    );
  };

  return (
    <div ref={containerRef} className={`relative ${className}`}>
      <div
        className={`min-h-[42px] px-3 py-2 rounded-lg bg-white/10 border border-white/20
          text-white cursor-pointer transition-all duration-200
          hover:bg-white/[0.12] focus-within:border-white/40 
          ${isOpen ? 'ring-2 ring-white/20 ring-offset-2 ring-offset-[#1a1b1e]' : ''}
          ${isLoading ? 'opacity-75 cursor-wait' : ''}`}
        onClick={() => !isLoading && setIsOpen(!isOpen)}
      >
        <div className="flex flex-wrap gap-2">
          {selectedOptions.map((option) => (
            <div key={option.id}>
              {renderOptionContent(option, (e) => handleRemove(option.id, e))}
            </div>
          ))}
          {(searchable || selectedOptions.length === 0) && (
            <input
              type="text"
              className="flex-1 min-w-[120px] bg-transparent outline-none placeholder-white/50"
              placeholder={selectedOptions.length === 0 ? placeholder : 'Type to search...'}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onClick={(e) => {
                e.stopPropagation();
                setIsOpen(true);
              }}
            />
          )}
        </div>
      </div>
      {isOpen && (
        <div className="absolute w-full mt-2 py-2 bg-[#1a1b1e]/95 border border-white/10
          rounded-lg backdrop-blur-lg shadow-xl z-50 max-h-60 overflow-auto
          scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
          {isLoading ? (
            <div className="px-4 py-3 text-white/50 flex items-center gap-2">
              <i className="fas fa-spinner-third animate-spin"></i>
              Loading...
            </div>
          ) : filteredOptions.length > 0 ? (
            filteredOptions.map((option) => (
              <div
                key={option.id}
                className="px-4 py-2.5 hover:bg-white/10 cursor-pointer
                  transition-colors flex items-center gap-3 group"
                onClick={() => handleSelect(option.id)}
              >
                {renderOptionContent(option)}
                {multiple && (
                  <i className="fas fa-plus ml-auto opacity-0 group-hover:opacity-70 transition-opacity" />
                )}
              </div>
            ))
          ) : (
            <div className="px-4 py-3 text-white/50">
              {searchTerm ? 'No matches found' : 'No options available'}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
