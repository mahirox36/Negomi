import { HexColorPicker } from "react-colorful";
import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useRef, forwardRef } from "react";
import { createPortal } from "react-dom";

interface ColorPickerProps {
  color: string;
  onChange: (color: string) => void;
  isOpen: boolean;
  onToggle: () => void;
}

const ColorPicker = forwardRef<HTMLDivElement, ColorPickerProps>(
  ({ color, onChange, isOpen, onToggle }, ref) => {
    const pickerRef = useRef<HTMLDivElement>(null);
    const triggerRef = ref as React.RefObject<HTMLDivElement>;

    useEffect(() => {
      if (!isOpen) return;

      const handleClickOutside = (e: MouseEvent) => {
        if (
          !pickerRef.current?.contains(e.target as Node) &&
          !triggerRef.current?.contains(e.target as Node)
        ) {
          onToggle();
        }
      };

      const handleKeyDown = (e: KeyboardEvent) => {
        if (e.key === "Escape") onToggle();
      };

      document.addEventListener("mousedown", handleClickOutside);
      document.addEventListener("keydown", handleKeyDown);

      return () => {
        document.removeEventListener("mousedown", handleClickOutside);
        document.removeEventListener("keydown", handleKeyDown);
      };
    }, [isOpen, onToggle]);

    return (
      <>
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={color}
            onChange={(e) => onChange(e.target.value)}
            className="w-24 bg-gray-900/50 border border-white/10 rounded-lg px-2 py-1 text-sm text-white/90"
            placeholder="#000000"
          />
          <div
            ref={triggerRef}
            className="w-10 h-10 rounded-lg border-2 border-white/10 cursor-pointer hover:border-white/20 transition-colors shadow-lg"
            style={{ backgroundColor: color }}
            onClick={onToggle}
          />
        </div>
        {typeof window !== "undefined" &&
          createPortal(
            <AnimatePresence>
              {isOpen && (
                <motion.div
                  ref={pickerRef}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ duration: 0.1 }}
                  style={{
                    position: "fixed",
                    zIndex: 1000,
                    ...getPickerPosition(triggerRef.current),
                  }}
                  className="color-picker-root"
                >
                  <div className="bg-gray-900/95 p-3 rounded-lg border border-white/10 shadow-xl backdrop-blur-lg">
                    <HexColorPicker
                      color={color}
                      onChange={onChange}
                      className="custom-picker !w-[200px] !h-[200px]"
                    />
                  </div>
                </motion.div>
              )}
            </AnimatePresence>,
            document.body
          )}
      </>
    );
  }
);

ColorPicker.displayName = "ColorPicker";

export default ColorPicker;

function getPickerPosition(triggerElement: HTMLDivElement | null) {
  if (!triggerElement) return { top: 0, left: 0 };

  const rect = triggerElement.getBoundingClientRect();
  const spaceBelow = window.innerHeight - rect.bottom;
  const spaceRight = window.innerWidth - rect.left;

  return {
    top: spaceBelow < 300 ? rect.top - 265 : rect.bottom + 10,
    left: spaceRight < 250 ? rect.right - 225 : rect.left,
  };
}
