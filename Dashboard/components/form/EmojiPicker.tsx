import { useState, useRef, useEffect } from "react";
import data from "@emoji-mart/data";
import Picker from "@emoji-mart/react";

interface CustomEmoji {
  id: string;
  name: string;
  url: string;
  animated: boolean;
}

interface EmojiPickerProps {
  value: string;
  onChange: (emoji: string, url?: string) => void;
  placeholder?: string;
  theme?: "purple" | "default";
  guildId?: string;
  animatedOnly?: boolean;
}

export default function EmojiPicker({
  value,
  onChange,
  placeholder = "Select an emoji...",
  theme = "purple",
  guildId,
  animatedOnly = false,
}: EmojiPickerProps) {
  const [showPicker, setShowPicker] = useState(false);
  const [customEmojis, setCustomEmojis] = useState<CustomEmoji[]>([]);
  const [selectedEmoji, setSelectedEmoji] = useState<{
    isCustom: boolean;
    emoji: string;
    url?: string;
    name?: string;
  } | null>(null);
  const pickerRef = useRef<HTMLDivElement>(null);

  // Parse initial value to detect if it's a custom emoji
  useEffect(() => {
    if (!value) {
      setSelectedEmoji(null);
      return;
    }

    // Check if it's a custom emoji in format <a:name:id> or <:name:id>
    const customEmojiRegex = /<(a)?:([^:]+):(\d+)>/;
    const match = value.match(customEmojiRegex);

    if (match) {
      const [, isAnimated, name, id] = match;
      const emojiUrl = `https://cdn.discordapp.com/emojis/${id}.${
        isAnimated ? "gif" : "png"
      }`;
      setSelectedEmoji({
        isCustom: true,
        emoji: value,
        url: emojiUrl,
        name,
      });
    } else {
      setSelectedEmoji({
        isCustom: false,
        emoji: value,
      });
    }
  }, [value]);

  // Close picker when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        pickerRef.current &&
        !pickerRef.current.contains(event.target as Node)
      ) {
        setShowPicker(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Fetch custom emojis from the guild
  useEffect(() => {
    if (guildId) {
      fetch(`/api/v1/guilds/${guildId}/emojis`)
        .then((res) => res.json())
        .then((emojis) => {
          const filtered = animatedOnly
            ? emojis.filter((e: CustomEmoji) => e.animated)
            : emojis;
          setCustomEmojis(filtered);
        })
        .catch((err) => console.error("Error fetching custom emojis:", err));
    }
  }, [guildId, animatedOnly]);

  const handleEmojiSelect = (emoji: any) => {
    // Handle standard emoji
    if (emoji.native) {
      setSelectedEmoji({
        isCustom: false,
        emoji: emoji.native,
      });
      onChange(emoji.native);
    }
    // Handle custom emoji
    else if (emoji.id) {
      const customEmojiFormat = `<${emoji.animated ? "a" : ""}:${emoji.name}:${
        emoji.id
      }>`;
      setSelectedEmoji({
        isCustom: true,
        emoji: customEmojiFormat,
        url: emoji.url,
        name: emoji.name,
      });
      onChange(customEmojiFormat, emoji.url);
    }
    setShowPicker(false);
  };
  return (
    <div className="relative" ref={pickerRef}>
      <button
        onClick={() => setShowPicker(!showPicker)}
        className={`w-full px-3 py-2 rounded-lg border shadow-sm ${
          theme === "purple"
            ? "border-purple-500/30 bg-purple-500/10 hover:bg-purple-500/20 shadow-purple-500/5"
            : "border-white/10 bg-white/5 hover:bg-white/10 shadow-white/5"
        } transition-all flex items-center justify-between group focus:outline-none focus:ring-2 ${
          theme === "purple"
            ? "focus:ring-purple-500/30"
            : "focus:ring-white/20"
        }`}
      >
        <div className="flex items-center gap-3 text-white/70">
          {selectedEmoji ? (
            <>
              {selectedEmoji.isCustom && selectedEmoji.url ? (
                <div
                  className={`h-7 w-7 rounded-md overflow-hidden flex-shrink-0 flex items-center justify-center ${
                    theme === "purple" ? "bg-purple-500/10" : "bg-white/5"
                  } border ${
                    theme === "purple"
                      ? "border-purple-500/20"
                      : "border-white/10"
                  }`}
                >
                  <img
                    src={selectedEmoji.url}
                    alt={selectedEmoji.name || "Custom emoji"}
                    className="h-5 w-5 object-contain"
                  />
                </div>
              ) : (
                <div
                  className={`h-7 w-7 rounded-md overflow-hidden flex-shrink-0 flex items-center justify-center text-xl ${
                    theme === "purple" ? "bg-purple-500/10" : "bg-white/5"
                  } border ${
                    theme === "purple"
                      ? "border-purple-500/20"
                      : "border-white/10"
                  }`}
                >
                  {selectedEmoji.emoji}
                </div>
              )}
              <div className="flex flex-col">
                <span className="truncate max-w-[95px] text-sm font-medium">
                  {selectedEmoji.isCustom
                    ? selectedEmoji.name
                    : ""}
                </span>
              </div>
            </>
          ) : (
            <span className="text-sm">{placeholder}</span>
          )}
        </div>
        <div
          className={`flex items-center justify-center w-9 h-9 rounded-full ${
            theme === "purple"
              ? "bg-purple-500/20 group-hover:bg-purple-500/30"
              : "bg-white/10 group-hover:bg-white/20"
          } transition-all`}
        >
          <i className="fas fa-smile text-white/50 group-hover:text-white/80 transition-all"></i>
        </div>
      </button>

      {showPicker && (
        <div className="absolute z-50 mt-2 bg-[#1e1e1e] rounded-lg shadow-lg border border-white/10 overflow-hidden">
          <div className="p-3 bg-black/40 border-b border-white/5 flex items-center justify-between">
            <h3 className="text-white font-medium">Choose an emoji</h3>
            <button
              onClick={() => setShowPicker(false)}
              className="w-6 h-6 flex items-center justify-center rounded-full bg-white/5 hover:bg-white/10 text-white/50 hover:text-white/80 transition-all"
            >
              <i className="fas fa-times text-xs"></i>
            </button>
          </div>

          <div className="p-2 max-h-[350px] overflow-y-auto custom-scrollbar">
            {customEmojis.length > 0 && (
              <div className="mb-2 bg-black/20 rounded-lg p-3 border border-white/5 backdrop-blur-sm">
                <h3 className="text-white/90 text-sm font-bold mb-3 flex items-center gap-2">
                  <i
                    className={`fas fa-server ${
                      theme === "purple" ? "text-purple-400" : "text-blue-400"
                    }`}
                  ></i>
                  <span>Server Emojis</span>
                  <span
                    className={`text-xs px-2 py-0.5 rounded-full ml-1 ${
                      theme === "purple"
                        ? "bg-purple-500/20 text-purple-300"
                        : "bg-blue-500/20 text-blue-300"
                    }`}
                  >
                    {customEmojis.length}
                  </span>
                </h3>

                <div className="grid grid-cols-6 sm:grid-cols-7 md:grid-cols-8 gap-2">
                  {customEmojis.map((emoji) => (
                    <button
                      key={emoji.id}
                      onClick={() => handleEmojiSelect(emoji)}
                      className={`aspect-square p-1.5 rounded-lg transition-all flex items-center justify-center ${
                        theme === "purple"
                          ? "bg-purple-900/30 hover:bg-purple-800/50 border border-purple-500/20 hover:border-purple-500/50 hover:shadow-lg hover:shadow-purple-500/10"
                          : "bg-gray-800/80 hover:bg-gray-700 border border-white/10 hover:border-white/20 hover:shadow-lg hover:shadow-white/5"
                      }`}
                      title={emoji.name}
                    >
                      <div className="relative w-full h-full group">
                        <img
                          src={emoji.url}
                          alt={emoji.name}
                          className="w-full h-full object-contain transition-transform group-hover:scale-110"
                          loading="lazy"
                        />
                        {emoji.animated && (
                          <div
                            className={`absolute -top-1 -right-1 w-3 h-3 rounded-full ${
                              theme === "purple"
                                ? "bg-purple-400"
                                : "bg-blue-400"
                            } animate-pulse`}
                            title="Animated"
                          ></div>
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}
            <Picker
              data={data}
              onEmojiSelect={handleEmojiSelect}
              theme="dark"
              set="native"
            />{" "}
          </div>
        </div>
      )}

      <style jsx>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.1);
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(255, 255, 255, 0.2);
        }
      `}</style>
    </div>
  );
}
