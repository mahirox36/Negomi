interface Embed {
  title?: string;
  description?: string;
  color?: string;
  fields?: Array<{
    name: string;
    value: string;
    inline?: boolean;
  }>;
}

interface ReactionRole {
  emoji: string;
  role_id: string;
}

interface MessagePreviewProps {
  content: string;
  embeds?: Embed[];
  reactions?: ReactionRole[];
}

export default function MessagePreview({ content, embeds = [], reactions = [] }: MessagePreviewProps) {
  return (
    <div className="mt-4 rounded-lg border border-white/10 bg-[#313338] p-4">
      {/* Content */}
      <div className="text-white/90 whitespace-pre-wrap break-words">{content}</div>

      {/* Embeds */}
      {embeds.map((embed, index) => (
        <div
          key={index}
          className="mt-2 rounded border-l-4"
          style={{
            borderLeftColor: embed.color || '#000000',
            backgroundColor: 'rgba(255, 255, 255, 0.05)',
          }}
        >
          <div className="p-3">
            {embed.title && (
              <div className="font-semibold text-white">{embed.title}</div>
            )}
            {embed.description && (
              <div className="text-white/80 mt-1">{embed.description}</div>
            )}
            {embed.fields && embed.fields.length > 0 && (
              <div className="mt-2 grid gap-2">
                {embed.fields.map((field, fieldIndex) => (
                  <div key={fieldIndex} className={field.inline ? 'inline-block mr-4' : 'block'}>
                    <div className="font-medium text-white">{field.name}</div>
                    <div className="text-white/80">{field.value}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      ))}

      {/* Reactions */}
      {reactions.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-2 pt-2 border-t border-white/10">
          {reactions.map((reaction, index) => (
            <div
              key={index}
              className="flex items-center gap-1 px-2 py-1 rounded bg-white/5 text-white/80"
            >
              <span>{reaction.emoji}</span>
              <span className="text-xs">1</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}