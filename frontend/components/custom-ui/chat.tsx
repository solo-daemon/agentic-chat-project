// components/custom-ui/chat.tsx
'use client';

import dynamic from 'next/dynamic';

const CopilotChat = dynamic(() => import('@copilotkit/react-ui').then(mod => mod.CopilotChat), {
  ssr: false,
});

export function Chat() {
  return (
    <div className="flex h-full w-80 flex-col border-l bg-background">
      <CopilotChat className="flex-1 min-h-0 py-4" />
    </div>
  );
}