'use client'

import { useState } from 'react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { sample_response as sample_response_object} from '@/utils/sample_response'
import { cn } from '@/lib/utils'
import { Loader2, ArrowUpRight, Video } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import clsx from 'clsx'

const PROGRESS_STEPS = [
  'Creating sub-queries...',
  'Scraping the web...',
  'Batch-Scraping the selected websites',
  'Summarizing'
]

function ChatPage() {
  const [query, setQuery] = useState('')
  const [history, setHistory] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [progressStep, setProgressStep] = useState<number | null>(null)

  // const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
  //   e.preventDefault();
  
  //   if (!query.trim()) return;
  
  //   setHistory((prev) => [...prev, { role: 'user', content: query }]);
  //   setQuery('');
  //   setLoading(true);
  //   setProgressStep(0);
  
  //   let finalAnswer = '';
  
  //   try {
  //     await streamAgentResponse(query, (msg: string) => {
  //       if (msg.startsWith("Error:")) {
  //         setHistory((prev) => [
  //           ...prev,
  //           { role: 'agent', content: msg }
  //         ]);
  //         return;
  //       }
  
  //       if (msg.startsWith("FINAL_RESPONSE::")) {
  //         finalAnswer = msg.replace("FINAL_RESPONSE::", "");
  //         setHistory((prev) => [
  //           ...prev,
  //           { role: 'agent', content: finalAnswer }
  //         ]);
  //         return;
  //       }
  
  //       // Handle progress messages
  //       const index = PROGRESS_STEPS.findIndex(
  //         (step) => msg.toLowerCase().includes(step.toLowerCase())
  //       );
  
  //       if (index !== -1) {
  //         setProgressStep(index + 1);
  //       }
  
  //       // Optionally show agent thinking messages
  //       setHistory((prev) => [
  //         ...prev.filter((m) => m.role !== 'agent' || !m.ephemeral),
  //         { role: 'agent', content: msg, ephemeral: true },
  //       ]);
  //     });
  //   } catch (error) {
  //     setHistory((prev) => [
  //       ...prev,
  //       { role: 'agent', content: sample_response_object },
  //     ]);
  //   } finally {
  //     setProgressStep(null);
  //     setLoading(false);
  
  //     // Clean up ephemeral updates
  //     setHistory((prev) => prev.filter((m) => !m.ephemeral));
  //   }
  // };
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
  
    if (!query.trim()) return;
  
    setHistory((prev) => [...prev, { role: 'user', content: query }]);
    setQuery('');
    setLoading(true);
    setProgressStep(0);
  
    // mimic progress bar
    for (let i = 0; i < PROGRESS_STEPS.length; i++) {
      await new Promise((res) => setTimeout(res, 1000));
      setProgressStep(i + 1);
    }
  
    try {
      console.log("asking agent")
      const response = await fetch(`http://localhost:8000/api/ask?query=${encodeURIComponent(query)}`, {
        method: 'GET',
        keepalive: true,
        headers: {
          'Content-Type': 'application/json',
          'api-key': process.env.NEXT_PUBLIC_API_KEY || '', // Must match backend header name
        },
      });
  
      if (!response.ok) {
        console.error("hello")
        return sample_response_object
      }
  
      const data: { answer: string } = await response.json();
      const agentResponse = { role: 'agent', content: data.answer };
      console.log(data.answer)
      setHistory((prev) => [...prev, agentResponse]);
    } catch (error) {
      const agentResponse = { role: 'agent', content: sample_response_object };
      setHistory((prev) => [...prev, agentResponse]);
      // console.error(error);
      // setHistory((prev) => [
      //   ...prev,
      //   { role: 'agent', content: 'Something went wrong. Please try again.' },
      // ]);
    } finally {
      setProgressStep(null);
      setLoading(false);
    }
  };
  console.log(history)
  return (
    <div className="flex flex-col min-h-screen bg-muted relative pb-30">
      <div className="flex-grow overflow-y-auto space-y-4 p-4">
        {history.map((msg, idx) => (
          <div key={idx} className={clsx('w-full flex', msg.role === 'user' ? 'justify-end' : 'justify-start')}>
            <Card className="max-w-2xl p-0">
                {msg.role === 'user' ? (
                  <CardContent className='p-0 py-2 pl-4 text-left'>
                    <p className="text-left text-sm text-foreground p-0 w-40">{msg.content}</p>
                  </CardContent>
                ) : (
                  <CardContent className="">
                  <AgentResponse content={msg.content} />
                  </CardContent>
                )}

            </Card>
          </div>
        ))}
        {loading && <ProgressComponent step={progressStep} />}
      </div>
      <div className="fixed bottom-10 p-4 w-full">
        <div className='w-full p-4'>
          <form onSubmit={handleSubmit} className="mb-8 flex gap-2">
            <Input
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder="Ask me anything..."
              className="flex-grow border-1 border-black text-white bg-black"
            />
            <Button type="submit" disabled={loading}>Send</Button>
          </form>
        </div>
      </div>
    </div>
  )
}

function ProgressComponent({ step }: { step: number | null }) {
  if (step === null) return null

  return (
    <div className="flex flex-col gap-2 px-4 py-2 animate-pulse text-sm">
      {PROGRESS_STEPS.map((s, i) => (
        <div key={s} className="flex items-center gap-2">
          <div className={clsx(
            'h-4 w-4 rounded-full border-2 flex items-center justify-center',
            i < step ? 'border-green-500 bg-green-500' : 'border-gray-500'
          )}>
            {i < step ? <div className="h-2 w-2 bg-white rounded-full" /> : null}
          </div>
          <p className={clsx(i < step ? 'text-foreground' : 'text-muted-foreground')}>{s}</p>
        </div>
      ))}
    </div>
  )
}

function AgentResponse({ content }: { content: any }) {
  return (
    <div className="space-y-4 w-full pr-8 p-4">
      {/* Links with favicon */}
      <div className="grid grid-cols-2 gap-4">
      {content['websites']?.slice(0, 4).map((item: any, i: number) => (
        <a
          key={i}
          href={item.link}
          target="_blank"
          rel="noopener noreferrer"
          className="group flex items-start gap-2 p-2 rounded-lg border-l-2 border-transparent hover:border-l-primary hover:bg-muted transition-all duration-200"
        >
          <img src={item.favicon_url} alt="favicon" className="w-6 h-6 mt-1" />
          <div className="flex justify-between items-start w-full">
            <span className="text-sm line-clamp-2 text-left">{item.snippet}</span>
            <ArrowUpRight
              size={14}
              className="mt-1 opacity-0 group-hover:opacity-100 transition-transform duration-200 transform group-hover:scale-125 text-muted-foreground"
            />
          </div>
        </a>
      ))}
      </div>

      {/* Markdown analysis */}
      <div className="prose prose-sm max-w-none">
        <ReactMarkdown>{content.detailed_analysis}</ReactMarkdown>
      </div>

      {/* Buttons with link */}
      <h4 className="font-semibold text-sm">References</h4>
      <div className="flex flex-wrap gap-2">
      {content['websites']?.map((item: any, i: number) => (
        <Button
          key={i}
          variant="outline"
          size="sm"
          onClick={() => window.open(item.link, '_blank')}
          className="group flex items-center gap-1 border transition-all duration-200 hover:border-primary"
        >
          <span className="truncate max-w-xs text-xs">{item.snippet}</span>
          <ArrowUpRight
            size={14}
            className="transition-transform duration-200 group-hover:scale-125"
          />
        </Button>
      ))}
      </div>

      {/* Videos */}
      {content['videos']?.length > 0 && (
        <div className="space-y-2">
          <h4 className="font-semibold text-sm">Related Videos</h4>
          {content['videos'].map((url: string, i: number) => (
            <a
            key={i}
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className={cn(
              'group flex items-center space-x-3 rounded-xl border border-gray-200 p-3 shadow-sm transition hover:shadow-md hover:border-blue-500 bg-white'
            )}
          >
            <div className="flex-shrink-0">
              <Button
                size="icon"
                variant="outline"
                className="rounded-full group-hover:bg-blue-500 group-hover:text-white transition"
              >
                <Video className="h-4 w-4" />
              </Button>
            </div>
            <div className="truncate text-sm text-blue-700 group-hover:underline max-w-[calc(100%-2rem)]">
              {truncateUrl(url)}
            </div>
          </a>
          ))}
        </div>
      )}
    </div>
  )
}

function truncateUrl(url: string, maxLength = 50) {
  try {
    const u = new URL(url)
    const pretty = u.hostname + u.pathname
    return pretty.length > maxLength ? pretty.slice(0, maxLength) + '…' : pretty
  } catch {
    return url.length > maxLength ? url.slice(0, maxLength) + '…' : url
  }
}

export default ChatPage

export async function streamAgentResponse(query: string, onMessage: (msg: string) => void) {
  const response = await fetch("/api/ask", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": process.env.NEXT_PUBLIC_API_KEY || "",
    },
    body: JSON.stringify({ query }),
  });

  if (!response.ok || !response.body) {
    throw new Error("Network response was not ok");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // Break into messages
    const lines = buffer.split("\n\n");
    buffer = lines.pop() || ""; // save last incomplete line

    for (const line of lines) {
      const trimmed = line.replace(/^data:\s*/, "").trim();

      // Final response marker (custom tag)
      if (trimmed.startsWith("FINAL_RESPONSE::")) {
        const final = trimmed.replace("FINAL_RESPONSE::", "");
        onMessage(final);
      } else if (trimmed.startsWith("ERROR::")) {
        onMessage("Error: " + trimmed.replace("ERROR::", ""));
      } else {
        onMessage(trimmed); // status updates
      }
    }
  }
}