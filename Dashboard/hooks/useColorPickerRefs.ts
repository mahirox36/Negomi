import { useRef, useMemo } from 'react';

export function useColorPickerRefs() {
  const refs = useRef(new Map<string, React.RefObject<HTMLDivElement>>());

  const getRef = (settingName: string) => {
    if (!refs.current.has(settingName)) {
      refs.current.set(settingName, { current: null });
    }
    return refs.current.get(settingName)!;
  };

  return { getRef };
}
