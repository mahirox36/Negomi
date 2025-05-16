"use client";

import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from "framer-motion";

interface MessageOption {
  id: string;
  name: string;
  content: string;
  channel_id?: string;
  embeds?: EmbedData[];
  created_at?: string;
  message_id?: string;
  color?: string; // For custom display color
}

interface EmbedData {
  title?: string;
  description?: string;
  color?: string;
}

export interface MessageSelectProps {
  guildId: string;
  value: string | string[];
  onChange: (value: string | string[]) => void;
  className?: string;
  placeholder?: string;
  multiple?: boolean;
  searchable?: boolean;
  theme?: 'purple' | 'indigo' | 'blue' | 'emerald' | 'default';
  showPreview?: boolean;
  showEmbedCount?: boolean;
  showChannelId?: boolean;
  showContent?: boolean;
  maxContentLength?: number;
  filterByChannel?: string;
  customFilter?: (message: MessageOption) => boolean;
  customSort?: (a: MessageOption, b: MessageOption) => number;
  onMessageClick?: (message: MessageOption) => void;
  emptyMessage?: string;
  loadingMessage?: string;
  renderCustomOption?: (message: MessageOption, isSelected: boolean) => React.ReactNode;
  disabled?: boolean;
}

const defaultThemeColors = {
  purple: {
    container: "bg-purple-500/10 border-purple-500/30 hover:bg-purple-500/15 focus-within:border-purple-400",
    focusRing: "ring-purple-400/30 ring-offset-gray-900",
    dropdown: "bg-gray-900/95 border-purple-500/20",
    hoverItem: "hover:bg-purple-500/10",
    spinner: "text-purple-400",
    placeholder: "text-purple-300/50",
    loading: "text-purple-300/70",
    accent: "text-purple-300"
  },
  indigo: {
    container: "bg-indigo-500/10 border-indigo-500/30 hover:bg-indigo-500/15 focus-within:border-indigo-400",
    focusRing: "ring-indigo-400/30 ring-offset-gray-900",
    dropdown: "bg-gray-900/95 border-indigo-500/20",
    hoverItem: "hover:bg-indigo-500/10",
    spinner: "text-indigo-400",
    placeholder: "text-indigo-300/50",
    loading: "text-indigo-300/70",
    accent: "text-indigo-300"
  },
  blue: {
    container: "bg-blue-500/10 border-blue-500/30 hover:bg-blue-500/15 focus-within:border-blue-400",
    focusRing: "ring-blue-400/30 ring-offset-gray-900",
    dropdown: "bg-gray-900/95 border-blue-500/20",
    hoverItem: "hover:bg-blue-500/10",
    spinner: "text-blue-400",
    placeholder: "text-blue-300/50",
    loading: "text-blue-300/70",
    accent: "text-blue-300"
  },
  emerald: {
    container: "bg-emerald-500/10 border-emerald-500/30 hover:bg-emerald-500/15 focus-within:border-emerald-400",
    focusRing: "ring-emerald-400/30 ring-offset-gray-900",
    dropdown: "bg-gray-900/95 border-emerald-500/20",
    hoverItem: "hover:bg-emerald-500/10",
    spinner: "text-emerald-400",
    placeholder: "text-emerald-300/50",
    loading: "text-emerald-300/70",
    accent: "text-emerald-300"
  },
  default: {
    container: "bg-white/10 border-white/20 hover:bg-white/[0.12] focus-within:border-white/40",
    focusRing: "ring-white/20 ring-offset-[#1a1b1e]",
    dropdown: "bg-[#1a1b1e]/95 border-white/10",
    hoverItem: "hover:bg-white/10",
    spinner: "text-white/70",
    placeholder: "text-white/50",
    loading: "text-white/50",
    accent: "text-white/80"
  }
};

export default function MessageSelect({
  guildId,
  value,
  onChange,
  className = '',
  placeholder = 'Select a message...',
  multiple = false,
  searchable = true,
  theme = 'purple',
  showPreview = true,
  showEmbedCount = true,
  showChannelId = true,
  showContent = true,
  maxContentLength = 60,
  filterByChannel = '',
  customFilter,
  customSort,
  onMessageClick,
  emptyMessage = 'No messages available',
  loadingMessage = 'Loading messages...',
  renderCustomOption,
  disabled = false
}: MessageSelectProps) {
  const [options, setOptions] = useState<MessageOption[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [channels, setChannels] = useState<Record<string, string>>({});
  
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Normalize value to array for consistent handling
  const selectedIds = Array.isArray(value) ? value : value ? [value] : [];
  
  // Memoize selected and filtered options
  const selectedOptions = options.filter(opt => selectedIds.includes(opt.id));
  
  const filteredOptions = options.filter(opt => {
    // First check if it's already selected
    if (selectedIds.includes(opt.id)) return false;
    
    // Apply search filter if there's a search term
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      if (!opt.name.toLowerCase().includes(term) && 
          !opt.content.toLowerCase().includes(term) &&
          !(opt.embeds?.some(embed => 
            (embed.title?.toLowerCase() || '').includes(term) ||
            (embed.description?.toLowerCase() || '').includes(term)
          ))
      ) {
        return false;
      }
    }
    
    // Filter by channel if specified
    if (filterByChannel && opt.channel_id !== filterByChannel) {
      return false;
    }
    
    // Apply custom filter if provided
    if (customFilter && !customFilter(opt)) {
      return false;
    }
    
    return true;
  });

  // Sort options based on custom sort or default to newest first
  const sortedOptions = [...filteredOptions].sort((a, b) => {
    if (customSort) {
      return customSort(a, b);
    }
    
    // Default sort by creation date (newest first)
    const dateA = a.created_at ? new Date(a.created_at).getTime() : 0;
    const dateB = b.created_at ? new Date(b.created_at).getTime() : 0;
    return dateB - dateA;
  });

  // Fetch channels to display channel names
  useEffect(() => {
    const fetchChannels = async () => {
      if (!guildId) return;
      
      try {
        const response = await axios.get(`/api/v1/guilds/${guildId}/channels`);
        const channelMap: Record<string, string> = {};
        
        if (Array.isArray(response.data)) {
          response.data.forEach((channel: any) => {
            if (channel?.id && channel?.name) {
              channelMap[channel.id] = channel.name;
            }
          });
        }
        
        setChannels(channelMap);
      } catch (error) {
        console.error("Failed to fetch channels:", error);
      }
    };
    
    fetchChannels();
  }, [guildId]);

  // Fetch messages
  useEffect(() => {
    const fetchMessages = async () => {
      if (!guildId) return;
      
      setIsLoading(true);
      setError(null);
      
      try {
        const response = await axios.get(`/api/v1/guilds/${guildId}/messages`, {
          withCredentials: true,
        });
        
        if (Array.isArray(response.data)) {
          setOptions(response.data);
          
          // Validate that selected values exist in options
          validateSelections(response.data);
        } else {
          setOptions([]);
          setError("Invalid data format received from API");
        }
      } catch (error) {
        console.error("Failed to fetch messages:", error);
        setError("Failed to load messages");
        setOptions([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchMessages();
  }, [guildId]);

  // Validate that selected values exist in options
  const validateSelections = (availableOptions: MessageOption[]) => {
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
      
      // If dropdown would overflow bottom of viewport
      if (dropdownRect.height > spaceBelow) {
        // If more space above than below and enough space above
        if (spaceAbove > spaceBelow && dropdownRect.height <= spaceAbove) {
          dropdownRef.current.style.bottom = `${containerRect.height}px`;
          dropdownRef.current.style.top = 'auto';
        } else {
          // Limit height if not enough space above or below
          dropdownRef.current.style.maxHeight = `${Math.max(100, spaceBelow - 20)}px`;
          dropdownRef.current.style.top = `${containerRect.height + 8}px`;
          dropdownRef.current.style.bottom = 'auto';
        }
      } else {
        // Default position (below input)
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
  }, [isOpen, options.length]);

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
    if (!isOpen) return;
    
    const handleKeyDown = (e: KeyboardEvent) => {
      switch (e.key) {
        case 'Escape':
          setIsOpen(false);
          setSearchTerm('');
          break;
          
        case 'ArrowDown':
        case 'ArrowUp':
          e.preventDefault();
          // We could implement focus navigation here
          break;
          
        case 'Enter':
          // We could implement selecting the focused option
          break;
      }
    };
    
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen]);

  const handleSelect = (messageId: string) => {
    if (multiple) {
      const newValue = [...selectedIds, messageId];
      onChange(newValue);
    } else {
      onChange(messageId);
      setIsOpen(false);
    }
    
    setSearchTerm('');
    
    // Call the onClick handler if provided
    if (onMessageClick) {
      const selectedMessage = options.find(m => m.id === messageId);
      if (selectedMessage) {
        onMessageClick(selectedMessage);
      }
    }
    
    if (searchable && inputRef.current) {
      inputRef.current.focus();
    }
  };

  const handleRemove = (messageId: string, event: React.MouseEvent) => {
    event.stopPropagation();
    
    if (multiple) {
      onChange(selectedIds.filter(id => id !== messageId));
    } else {
      onChange('');
    }
    
    if (searchable && inputRef.current) {
      inputRef.current.focus();
    }
  };

  // Format the date
  const formatDate = (dateString?: string): string => {
    if (!dateString) return '';
    
    try {
      const date = new Date(dateString);
      
      if (isNaN(date.getTime())) {
        return '';
      }
      
      return new Intl.DateTimeFormat('en-US', {
        month: 'short',
        day: 'numeric'
      }).format(date);
    } catch {
      return '';
    }
  };

  // Truncate text helper
  const truncateText = (text: string, maxLength: number): string => {
    if (!text) return '';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
  };

  // Get embed color or use default
  const getEmbedColor = (message: MessageOption): string => {
    // Use custom color if provided
    if (message.color) return message.color;
    
    // Use color from first embed if available
    if (message.embeds && message.embeds.length > 0 && message.embeds[0].color) {
      return message.embeds[0].color;
    }
    
    // Default color based on theme
    switch (theme) {
      case 'purple': return '#9333ea';  // purple-600
      case 'indigo': return '#4f46e5';  // indigo-600
      case 'blue': return '#2563eb';    // blue-600
      case 'emerald': return '#059669'; // emerald-600
      default: return '#6366f1';        // indigo-500
    }
  };

  // Get embed count
  const getEmbedCount = (message: MessageOption): number => {
    return message.embeds?.length || 0;
  };

  // Get channel name from ID
  const getChannelName = (channelId?: string): string => {
    if (!channelId) return 'No channel';
    return channels[channelId] ? `#${channels[channelId]}` : `#${channelId}`;
  };

  // Choose theme colors
  const themeStyles = defaultThemeColors[theme];

  // Animation variants for message items
  const itemVariants = {
    hidden: { opacity: 0, y: 5 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.15 } },
    exit: { opacity: 0, scale: 0.96, transition: { duration: 0.1 } }
  };

  // Message option rendering
  const renderMessageOption = (message: MessageOption, isSelected = false) => {
    // Use custom renderer if provided
    if (renderCustomOption) {
      return renderCustomOption(message, isSelected);
    }

    const embedColor = getEmbedColor(message);
    const embedCount = getEmbedCount(message);
    const formattedDate = formatDate(message.created_at);
    
    return (
      <div className={`relative flex flex-col gap-1 ${showPreview ? 'py-3' : 'py-2'}`}>
        {/* Color indicator on the left */}
        <div 
          className="absolute left-0 top-0 bottom-0 w-1 rounded-full"
          style={{ backgroundColor: embedColor }}
        ></div>
        
        {/* Content container */}
        <div className="pl-3">
          <div className="flex justify-between items-start">
            {/* Message name */}
            <div className="font-medium text-white truncate max-w-[70%]">
              {message.name || "Unnamed Message"}
            </div>
            
            {/* Badges */}
            <div className="flex gap-2">
              {showEmbedCount && embedCount > 0 && (
                <span 
                  className="text-xs px-1.5 py-0.5 rounded-full flex items-center gap-1"
                  style={{ 
                    backgroundColor: `${embedColor}30`,
                    color: embedColor 
                  }}
                >
                  <i className="fas fa-layer-group text-xs"></i>
                  <span>{embedCount}</span>
                </span>
              )}
              
              {formattedDate && (
                <span className="text-xs text-white/50 flex items-center gap-1">
                  <i className="fas fa-calendar-alt text-xs"></i>
                  {formattedDate}
                </span>
              )}
            </div>
          </div>
          
          {/* Channel info */}
          {showChannelId && message.channel_id && (
            <div className="text-xs text-white/60 mt-0.5 flex items-center gap-1">
              <i className="fas fa-hashtag text-xs"></i>
              {getChannelName(message.channel_id)}
            </div>
          )}
          
          {/* Content preview */}
          {showContent && message.content && (
            <div className="text-sm text-white/70 mt-1 truncate">
              {truncateText(message.content, maxContentLength)}
            </div>
          )}
          
          {/* Preview if enabled */}
          {showPreview && message.embeds && message.embeds.length > 0 && (
            <div className="flex mt-2 gap-2 overflow-x-auto scrollbar-thin scrollbar-thumb-white/10 py-1">
              {message.embeds.map((embed, idx) => (
                <div 
                  key={idx}
                  className="flex-shrink-0 h-4 rounded-sm border-l-2 px-1 text-xs text-white/60 flex items-center"
                  style={{ 
                    backgroundColor: 'rgba(47, 49, 54, 0.3)',
                    borderLeftColor: embed.color || embedColor
                  }}
                >
                  {embed.title ? truncateText(embed.title, 15) : `Embed ${idx + 1}`}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div ref={containerRef} className={`relative ${className}`}>
      {/* Selection display area */}
      <div
        className={`min-h-[42px] px-3 py-2 rounded-lg border transition-all duration-200
          ${themeStyles.container}
          ${isOpen ? `ring-2 ${themeStyles.focusRing} ring-offset-2` : ''}
          ${isLoading ? 'opacity-75' : ''}
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
        onClick={() => !disabled && !isLoading && setIsOpen(!isOpen)}
        tabIndex={disabled ? -1 : 0}
        role="combobox"
        aria-expanded={isOpen}
        aria-disabled={disabled}
        aria-haspopup="listbox"
      >
        <div className="flex flex-wrap gap-2">
          {/* Selected messages */}
          {selectedOptions.length > 0 ? selectedOptions.map((message) => (
            <div key={message.id} className="flex items-center gap-1 pl-2 pr-1 py-1 bg-white/10 rounded-md border border-white/10">
              <span className="text-white truncate max-w-[150px]">
                {message.name || "Unnamed Message"}
              </span>
              {!disabled && (
                <button
                  onClick={(e) => handleRemove(message.id, e)}
                  className="ml-1 text-pink-300 hover:text-pink-400 transition-colors p-1 rounded-full hover:bg-white/5"
                  aria-label="Remove"
                >
                  <i className="fas fa-times text-xs" />
                </button>
              )}
            </div>
          )) : (
            /* Show placeholder if nothing selected */
            <span className={`${themeStyles.placeholder}`}>
              {placeholder}
            </span>
          )}
          
          {/* Search input */}
          {searchable && isOpen && (
            <input
              ref={inputRef}
              type="text"
              className={`flex-1 min-w-[120px] bg-transparent outline-none text-white placeholder:${themeStyles.placeholder}`}
              placeholder="Type to search..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onClick={(e) => {
                e.stopPropagation();
                if (!disabled) setIsOpen(true);
              }}
              disabled={disabled}
              aria-autocomplete="list"
            />
          )}
        </div>
      </div>
      
      {/* Dropdown menu */}
      <AnimatePresence>
        {isOpen && !disabled && (
          <motion.div 
            ref={dropdownRef}
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -5 }}
            transition={{ duration: 0.15 }}
            className={`absolute w-full py-2 border rounded-lg shadow-xl z-50 overflow-auto
              max-h-[350px] scrollbar-thin scrollbar-thumb-white/20 scrollbar-track-transparent
              backdrop-blur-lg ${themeStyles.dropdown}`}
            role="listbox"
          >
            {isLoading ? (
              <div className={`px-4 py-3 flex items-center gap-2 ${themeStyles.loading}`}>
                <i className={`fas fa-spinner-third animate-spin ${themeStyles.spinner}`}></i>
                {loadingMessage}
              </div>
            ) : error ? (
              <div className="px-4 py-3 text-red-400">
                <i className="fas fa-exclamation-triangle mr-2"></i>
                {error}
              </div>
            ) : sortedOptions.length > 0 ? (
              <AnimatePresence>
                {sortedOptions.map((message) => (
                  <motion.div
                    key={message.id}
                    variants={itemVariants}
                    initial="hidden"
                    animate="visible"
                    exit="exit"
                    className={`px-4 py-0.5 ${themeStyles.hoverItem} cursor-pointer
                      transition-colors relative border-b border-white/5 last:border-b-0`}
                    onClick={() => handleSelect(message.id)}
                    role="option"
                    aria-selected={selectedIds.includes(message.id)}
                  >
                    {renderMessageOption(message)}
                  </motion.div>
                ))}
              </AnimatePresence>
            ) : (
              <div className={`px-4 py-3 text-center ${themeStyles.loading}`}>
                {searchTerm ? `No messages matching "${searchTerm}"` : emptyMessage}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}