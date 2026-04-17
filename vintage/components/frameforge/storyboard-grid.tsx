'use client'

import { GripVertical, Clapperboard } from 'lucide-react'
import { useStoryboardStore } from '@/lib/storyboard-store'

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center h-full p-10">
      <div className="max-w-[400px] text-center">
        {/* Vintage film reel icon */}
        <div className="w-24 h-24 mx-auto mb-8 bg-[#1A1A1A] border-2 border-[#333333] flex items-center justify-center sharp-shadow">
          <Clapperboard className="w-12 h-12 text-[#444444]" strokeWidth={1.5} />
        </div>

        <h2 
          className="text-3xl font-bold uppercase tracking-tight text-white mb-4"
          style={{ fontFamily: 'var(--font-cooper-black), Georgia, serif' }}
        >
          No storyboard yet
        </h2>
        <p className="text-base text-[#888888] leading-relaxed font-serif">
          Describe your scene in the panel on the left, then generate your storyboard frames.
        </p>
      </div>
    </div>
  )
}

function LoadingState() {
  const { panelCount } = useStoryboardStore()
  
  return (
    <div className="p-8 h-full overflow-y-auto">
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {[...Array(panelCount)].map((_, i) => (
          <div 
            key={i} 
            className="bg-[#111111] border-2 border-[#333333] sharp-shadow projector-flicker"
            style={{ animationDelay: `${i * 0.05}s` }}
          >
            {/* Image skeleton */}
            <div className="aspect-video panel-skeleton" />
            {/* Caption skeleton */}
            <div className="p-3 border-t border-[#333333]">
              <div className="h-4 panel-skeleton w-3/4" />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function PanelCard({ panel, index }: { panel: ReturnType<typeof useStoryboardStore>['panels'][0], index: number }) {
  const { selectPanel, updatePanelCaption } = useStoryboardStore()

  return (
    <div 
      className="
        bg-[#111111] border-2 border-white
        sharp-shadow
        hover:shadow-[6px_6px_0px_0px_rgba(245,166,35,0.4)]
        transition-shadow duration-100
        group
      "
    >
      {/* Image with shot type badge */}
      <button
        onClick={() => selectPanel(panel.id)}
        className="
          relative aspect-video w-full overflow-hidden
          cursor-pointer
          border-b-2 border-[#333333]
        "
      >
        {/* Placeholder image with film grain */}
        <div className="absolute inset-0 bg-[#1A1A1A] film-grain flex items-center justify-center">
          <div className="w-16 h-16 border-2 border-[#333333] flex items-center justify-center z-10">
            <span className="text-2xl font-bold text-[#444444] font-mono">{index + 1}</span>
          </div>
        </div>
        
        {/* Shot type badge */}
        <div className="
          absolute top-3 left-3 z-10
          px-3 py-1.5
          bg-white text-[#0A0A0A]
          font-mono text-xs font-bold uppercase
        ">
          {panel.shotType}
        </div>

        {/* Hover overlay */}
        <div className="
          absolute inset-0 z-20
          flex items-center justify-center
          bg-[#0A0A0A]/80
          opacity-0 group-hover:opacity-100
          transition-opacity duration-100
        ">
          <span className="
            font-mono text-xs font-bold uppercase text-[#0A0A0A]
            bg-[#F5A623] px-4 py-2
          ">
            Click to edit
          </span>
        </div>
      </button>

      {/* Caption input */}
      <div className="p-3 flex items-center gap-3">
        <GripVertical 
          className="w-4 h-4 text-[#444444] cursor-grab flex-shrink-0" 
          strokeWidth={2}
        />
        <input
          type="text"
          value={panel.caption}
          onChange={(e) => updatePanelCaption(panel.id, e.target.value)}
          placeholder="Add caption..."
          className="
            flex-1 bg-transparent border-0
            font-mono text-xs text-[#F5F5F0]
            placeholder:text-[#444444]
            focus:outline-none
          "
        />
      </div>
    </div>
  )
}

function GeneratedState() {
  const { panels } = useStoryboardStore()

  return (
    <div className="p-8 h-full overflow-y-auto">
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-6">
        {panels.map((panel, index) => (
          <PanelCard key={panel.id} panel={panel} index={index} />
        ))}
      </div>
    </div>
  )
}

export function StoryboardGrid() {
  const { appState } = useStoryboardStore()

  return (
    <main className="flex-1 bg-[#0A0A0A] overflow-hidden relative film-grain">
      {appState === 'empty' && <EmptyState />}
      {appState === 'loading' && <LoadingState />}
      {appState === 'generated' && <GeneratedState />}
    </main>
  )
}
