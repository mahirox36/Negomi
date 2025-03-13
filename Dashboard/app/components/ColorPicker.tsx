import { HexColorPicker } from "react-colorful";
import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useRef } from "react";
import { createPortal } from "react-dom";

interface ColorPickerProps {
  color: string;
  onChange: (color: string) => void;
  onClose: () => void;
  isOpen: boolean;
  triggerRef: React.RefObject<HTMLDivElement>;
}

export default function ColorPicker({ color, onChange, onClose, isOpen, triggerRef }: ColorPickerProps) {
  const pickerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isOpen) return;

    const handleClickOutside = (e: MouseEvent) => {
      if (!pickerRef.current?.contains(e.target as Node) && 
          !triggerRef.current?.contains(e.target as Node)) {
        onClose();
      }
    };

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleKeyDown);
    
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen || typeof window === 'undefined') return null;

  return createPortal(
    <AnimatePresence>
      {isOpen && (
        <motion.div
          ref={pickerRef}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          transition={{ duration: 0.1 }}
          style={{
            position: 'fixed',
            zIndex: 1000,
            ...getPickerPosition(triggerRef.current),
          }}
          className="color-picker-root"
        >
          <div className="bg-gray-900/95 p-3 rounded-lg border border-white/10 shadow-xl backdrop-blur-lg">
            <HexColorPicker 
              color={color} 
              onChange={onChange}
              className="custom-picker"
            />
          </div>
        </motion.div>
      )}
    </AnimatePresence>,
    document.body
  );
}

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
