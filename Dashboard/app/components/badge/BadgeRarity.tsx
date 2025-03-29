import { FaCrown, FaStar, FaGem } from 'react-icons/fa';

interface BadgeRarityProps {
  value: number;
  onChange: (value: number) => void;
}

const rarityLevels = [
  { value: 1, label: 'Common', color: 'gray', icon: FaStar },
  { value: 2, label: 'Uncommon', color: 'green', icon: FaStar },
  { value: 3, label: 'Rare', color: 'blue', icon: FaGem },
  { value: 4, label: 'Epic', color: 'purple', icon: FaGem },
  { value: 5, label: 'Legendary', color: 'yellow', icon: FaCrown },
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
            className={`p-2 rounded-lg flex flex-col items-center justify-center gap-1 transition-all ${
              value === rarity.value
                ? `bg-${rarity.color}-500/20 border-2 border-${rarity.color}-500`
                : 'bg-slate-800/50 border border-slate-700/50 hover:bg-slate-700/50'
            }`}
          >
            <rarity.icon className={`text-${rarity.color}-400`} />
            <span className={`text-xs font-medium text-${rarity.color}-400`}>
              {rarity.label}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
