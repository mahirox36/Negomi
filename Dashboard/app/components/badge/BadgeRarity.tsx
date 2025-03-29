import { FaCrown, FaStar, FaGem } from 'react-icons/fa';
import clsx from 'clsx';

interface BadgeRarityProps {
  value: number;
  onChange: (value: number) => void;
}

const rarityLevels = [
  { value: 1, label: 'Common', color: 'text-gray-400', bg: 'bg-gray-500/20', border: 'border-gray-500', icon: FaStar },
  { value: 2, label: 'Uncommon', color: 'text-green-400', bg: 'bg-green-500/20', border: 'border-green-500', icon: FaStar },
  { value: 3, label: 'Rare', color: 'text-blue-400', bg: 'bg-blue-500/20', border: 'border-blue-500', icon: FaGem },
  { value: 4, label: 'Epic', color: 'text-purple-400', bg: 'bg-purple-500/20', border: 'border-purple-500', icon: FaGem },
  { value: 5, label: 'Legendary', color: 'text-yellow-400', bg: 'bg-yellow-500/20', border: 'border-yellow-500', icon: FaCrown },
];

export function BadgeRarity({ value, onChange }: BadgeRarityProps) {
  return (
    <div className="space-y-2">
      <label className="text-sm font-medium text-slate-300">Rarity</label>
      <div className="grid grid-cols-5 gap-2">
        {rarityLevels.map((rarity) => (
          <button
            key={rarity.value}
            type="button"
            onClick={() => onChange(rarity.value)}
            className={clsx(
              'p-2 rounded-lg flex flex-col items-center justify-center gap-1 transition-all',
              value === rarity.value ? `${rarity.bg} border-2 ${rarity.border}` : 'bg-slate-800/50 border border-slate-700/50 hover:bg-slate-700/50'
            )}
          >
            <rarity.icon className={rarity.color} />
            <span className={`text-xs font-medium ${rarity.color}`}>
              {rarity.label}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
