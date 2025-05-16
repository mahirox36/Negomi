"use client";

import { useState, useRef, useEffect } from 'react';
import axios from 'axios';

interface DiscordOption {
  id: string;
  name: string;
  type?: string;
  color?: string;
  icon?: string;
  is_assignable?: boolean;
  position?: number;
}

interface DiscordSelectProps {
  type: 'channel' | 'role' | 'category';
  guildId: string;
  value: string | string[];
  onChange: (value: string | string[]) => void;
  className?: string;
  placeholder?: string;
  multiple?: boolean;
  searchable?: boolean;
  theme?: 'purple' | 'default';
  permissionRestrictions?: boolean;
}

export default function DiscordSelect({
  type,
  guildId,
  value,
  onChange,
  className = '',
  placeholder = 'Select...',
  multiple = false,
  searchable = true,
  theme = 'purple',
  permissionRestrictions = true,
}: DiscordSelectProps) {
  const [options, setOptions] = useState<DiscordOption[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Normalize value to array for consistent handling
  const selectedIds = Array.isArray(value) ? value : value ? [value] : [];
  
  // Memoize selected and filtered options
  const selectedOptions = options.filter(opt => selectedIds.includes(opt.id));
  const filteredOptions = options.filter(opt => 
    !selectedIds.includes(opt.id) &&
    opt.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Sort roles by position if applicable
  useEffect(() => {
    if (type === 'role' && selectedOptions.length > 0) {
      const sortedIds = [...selectedOptions]
        .sort((a, b) => (b.position || 0) - (a.position || 0))
        .map(opt => opt.id);
      
      if (multiple && JSON.stringify(sortedIds) !== JSON.stringify(selectedIds)) {
        onChange(sortedIds);
      }
    }
  }, [selectedOptions, type, multiple, onChange, selectedIds]);

  // Fetch options from API
  useEffect(() => {
    const fetchOptions = async () => {
      if (!guildId) return;
      
      setIsLoading(true);
      try {
        const endpoint = type === 'category' ? 'categories' : `${type}s`;
        const response = await axios.get(`/api/v1/guilds/${guildId}/${endpoint}`);
        const items = response.data?.filter((item: any) => item?.id && item?.name) || [];
        setOptions(items);
        
        // Validate selections against available options
        validateSelections(items);
      } catch (error) {
        console.error(`Failed to fetch ${type}s:`, error);
        setOptions([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchOptions();
  }, [guildId, type]);

  // Validate that selected values exist in options
  const validateSelections = (availableOptions: DiscordOption[]) => {
    const availableIds = new Set(availableOptions.map(item => item.id));
    
    if (multiple) {
      const validValues = selectedIds.filter(id => availableIds.has(id));
      if (validValues.length !== selectedIds.length) {
        onChange(validValues);
      }
    } else if (value && !availableIds.has(value as string)) {
      onChange('');
    }
  };

  // Handle dropdown position
  useEffect(() => {
    if (!isOpen || !dropdownRef.current || !containerRef.current) return;

    const updateDropdownPosition = () => {
      if (!dropdownRef.current || !containerRef.current) return;
      
      const containerRect = containerRef.current.getBoundingClientRect();
      const dropdownRect = dropdownRef.current.getBoundingClientRect();
      const viewportHeight = window.innerHeight;
      const spaceBelow = viewportHeight - containerRect.bottom;
      const spaceAbove = containerRect.top;
      
      // Check if dropdown would overflow the bottom of the viewport
      if (dropdownRect.height > spaceBelow) {
        // Check if there's more space above than below
        if (spaceAbove > spaceBelow && dropdownRect.height <= spaceAbove) {
          dropdownRef.current.style.bottom = `${containerRect.height}px`;
          dropdownRef.current.style.top = 'auto';
        } else {
          // Limit the height if there's not enough space above or below
          dropdownRef.current.style.maxHeight = `${Math.max(100, spaceBelow - 20)}px`;
          dropdownRef.current.style.top = `${containerRect.height + 8}px`;
          dropdownRef.current.style.bottom = 'auto';
        }
      } else {
        // Default positioning (below input)
        dropdownRef.current.style.top = `${containerRect.height + 8}px`;
        dropdownRef.current.style.bottom = 'auto';
      }
    };

    updateDropdownPosition();
    window.addEventListener('resize', updateDropdownPosition);
    window.addEventListener('scroll', updateDropdownPosition);

    return () => {
      window.removeEventListener('resize', updateDropdownPosition);
      window.removeEventListener('scroll', updateDropdownPosition);
    };
  }, [isOpen]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setSearchTerm('');
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Focus input when dropdown opens
  useEffect(() => {
    if (isOpen && searchable && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen, searchable]);

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;
      
      switch (e.key) {
        case 'Escape':
          setIsOpen(false);
          setSearchTerm('');
          break;
        case 'ArrowDown':
        case 'ArrowUp':
          e.preventDefault();
          // Could implement focus navigation for keyboard users
          break;
        case 'Enter':
          // Could implement selecting the focused option
          break;
      }
    };
    
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen]);

  const handleSelect = (optionId: string) => {
    if (multiple) {
      const newValue = selectedIds.includes(optionId)
        ? selectedIds.filter(id => id !== optionId)
        : [...selectedIds, optionId];
      onChange(newValue);
    } else {
      onChange(optionId);
      setIsOpen(false);
    }
    setSearchTerm('');
    if (searchable && inputRef.current) {
      inputRef.current.focus();
    }
  };

  const handleRemove = (optionId: string, event: React.MouseEvent) => {
    event.stopPropagation();
    if (multiple) {
      onChange(selectedIds.filter(id => id !== optionId));
    } else {
      onChange('');
    }
    
    if (searchable && inputRef.current) {
      inputRef.current.focus();
    }
  };

  // Get appropriate icon based on option type and name
  const getOptionIcon = (option: DiscordOption): string => {
    if (type === 'channel') return 'fa-solid fa-hashtag';
    if (type === 'category') return 'fa-solid fa-folder';
    
    // For roles, match name patterns
    const name = option.name.toLowerCase();
    if (name.includes('admin')) return 'fa-solid fa-crown';
    if (name.includes('mod')) return 'fa-solid fa-shield';
    if (name.includes('bot')) return 'fa-solid fa-robot';
    if (name.includes('mute')) return 'fa-solid fa-volume-xmark';
    return 'fa-solid fa-circle';
  };

  // Check if color is valid and ensure readability
  const getOptionStyles = (option: DiscordOption, isDropdownItem = false): React.CSSProperties => {
    const color = option.color;
    
    // If no color or default black, use theme colors
    if (!color || color === '#000000') {
      return isDropdownItem ? {} : {
        backgroundColor: 'rgba(168, 85, 247, 0.1)', // purple-500 with low opacity
        borderColor: 'rgb(168, 85, 247)',  // purple-500
        color: 'white'
      };
    }

    // Calculate luminance to determine text color
    const r = parseInt(color.slice(1, 3), 16) / 255;
    const g = parseInt(color.slice(3, 5), 16) / 255;
    const b = parseInt(color.slice(5, 7), 16) / 255;
    const luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b;
    
    // For dropdown items, we don't need background
    if (isDropdownItem) {
      return {
        color: luminance > 0.5 ? color : 'white',
      };
    }
    
    // For selected items, add background and ensure text contrast
    return {
      backgroundColor: `${color}25`, // 15% opacity
      borderColor: color,
      color: luminance > 0.5 ? '#000' : '#fff',
    };
  };

  // Render an individual option with proper styling
  const OptionItem = ({ 
    option, 
    isSelected = false, 
    onClick,
    isDropdownItem = false
  }: { 
    option: DiscordOption, 
    isSelected?: boolean, 
    onClick?: (e: React.MouseEvent) => void,
    isDropdownItem?: boolean
  }) => {
    const isDisabled = type === 'role' && option.is_assignable === false && permissionRestrictions;
    const style = getOptionStyles(option, isDropdownItem);
    
    return (
      <div
        className={`inline-flex items-center gap-2 px-2.5 py-1.5 rounded-md text-sm
          transition-all duration-200 relative group
          ${!isDropdownItem ? 'border-2' : ''}
          ${isDisabled ? 'opacity-50' : ''}
          ${isSelected ? 'bg-opacity-20' : ''}`}
        style={style}
      >
        {option.icon ? (
          <img
            src={option.icon}
            alt=""
            className="w-4 h-4 rounded-full object-cover flex-shrink-0"
            onError={(e) => {
              (e.target as HTMLImageElement).style.display = 'none';
              e.currentTarget.parentElement?.querySelector('.default-icon')?.classList.remove('hidden');
            }}
          />
        ) : (
          <i className={`${getOptionIcon(option)} text-sm opacity-70 flex-shrink-0 default-icon`} />
        )}
        <span className="truncate max-w-[200px]">{option.name}</span>
        {isSelected && onClick && (
          <button
            onClick={onClick}
            className="ml-1 text-pink-300 hover:text-pink-400 transition-colors focus:outline-none"
            aria-label="Remove"
            tabIndex={0}
          >
            <i className="fas fa-times text-xs" />
          </button>
        )}
      </div>
    );
  };

  // Theme-based styles
  const getThemeStyles = () => {
    if (theme === 'purple') {
      return {
        container: "bg-purple-500/10 border-purple-500/30 hover:bg-purple-500/15 focus-within:border-indigo-400",
        focusRing: "ring-indigo-400/30 ring-offset-gray-900",
        dropdown: "bg-gray-900/95 border-purple-500/20",
        hoverItem: "hover:bg-purple-500/10",
        spinner: "text-purple-400",
        placeholder: "text-purple-300/50",
        loading: "text-purple-300/70"
      };
    }
    return {
      container: "bg-white/10 border-white/20 hover:bg-white/[0.12] focus-within:border-white/40",
      focusRing: "ring-white/20 ring-offset-[#1a1b1e]",
      dropdown: "bg-[#1a1b1e]/95 border-white/10",
      hoverItem: "hover:bg-white/10",
      spinner: "text-white/70",
      placeholder: "placeholder-white/50",
      loading: "text-white/50"
    };
  };

  const themeStyles = getThemeStyles();

  return (
    <div ref={containerRef} className={`relative ${className}`}>
      {/* Selection display area */}
      <div
        className={`min-h-[42px] px-3 py-2 rounded-lg border transition-all duration-200
          ${themeStyles.container}
          ${isOpen ? `ring-2 ${themeStyles.focusRing} ring-offset-2` : ''}
          ${isLoading ? 'opacity-75 cursor-wait' : 'cursor-pointer'}`}
        onClick={() => !isLoading && setIsOpen(!isOpen)}
        tabIndex={0}
        role="combobox"
        aria-expanded={isOpen}
        aria-haspopup="listbox"
        aria-controls="options-list"
      >
        <div className="flex flex-wrap gap-2">
          {/* Selected options */}
          {selectedOptions.length > 0 && selectedOptions.map((option) => (
            <div key={option.id}>
              <OptionItem 
                option={option} 
                isSelected={true}
                onClick={(e) => handleRemove(option.id, e)} 
              />
            </div>
          ))}
          
          {/* Search input */}
          {(searchable || selectedOptions.length === 0) && (
            <input
              ref={inputRef}
              type="text"
              className={`flex-1 min-w-[120px] bg-transparent outline-none text-white ${themeStyles.placeholder}`}
              placeholder={selectedOptions.length === 0 ? placeholder : 'Type to search...'}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onClick={(e) => {
                e.stopPropagation();
                setIsOpen(true);
              }}
              aria-autocomplete="list"
            />
          )}
        </div>
      </div>
      
      {/* Dropdown menu */}
      {isOpen && (
        <div 
          ref={dropdownRef}
          id="options-list"
          className={`absolute w-full py-2 border rounded-lg backdrop-blur-lg shadow-xl z-50 overflow-auto
            scrollbar-thin scrollbar-thumb-purple-500/20 scrollbar-track-transparent
            ${themeStyles.dropdown}`}
          role="listbox"
        >
          {isLoading ? (
            <div className={`px-4 py-3 flex items-center gap-2 ${themeStyles.loading}`}>
              <i className={`fas fa-spinner-third animate-spin ${themeStyles.spinner}`}></i>
              Loading...
            </div>
          ) : filteredOptions.length > 0 ? (
            filteredOptions.map((option) => {
              const isDisabled = type === 'role' && option.is_assignable === false && permissionRestrictions;
              return (
          <div
            key={option.id}
            className={`px-4 py-2.5 group ${!isDisabled ? `${themeStyles.hoverItem} cursor-pointer text-sky-100` : 'cursor-not-allowed'}
              transition-colors flex items-center gap-3 relative`}
            onClick={() => !isDisabled && handleSelect(option.id)}
            role="option"
            aria-selected={selectedIds.includes(option.id)}
            tabIndex={isDisabled ? -1 : 0}
          >
            <OptionItem option={option} isDropdownItem={true} />
            
            {multiple && !isDisabled && (
              <i className="fas fa-plus ml-auto text-purple-400 opacity-0 group-hover:opacity-70 transition-opacity" />
            )}
            
            {isDisabled && permissionRestrictions && (
              <div className="tooltip absolute z-50 whitespace-nowrap p-2 rounded-md bg-gray-900 text-white text-xs
                transform -translate-x-1/2 right-4 pointer-events-none transition-opacity opacity-0 group-hover:opacity-100
                border border-gray-700 shadow-lg"
                style={{top: '-10px'}}
              >
                This role cannot be assigned due to permission restrictions
              </div>
            )}
          </div>
              );
            })
          ) : (
            <div className={`px-4 py-3 ${themeStyles.loading}`}>
              {searchTerm ? 'No matches found' : 'No options available'}
            </div>
          )}
        </div>
      )}
    </div>
  );
}