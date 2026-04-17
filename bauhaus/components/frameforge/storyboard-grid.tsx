'use client'

import { GripVertical } from 'lucide-react'
import { useStoryboardStore } from '@/lib/storyboard-store'

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center h-full p-[40px]">
      <div className="max-w-[400px] text-center">
        {/* Bauhaus geometric illustration */}
        <div className="relative mb-[40px] flex items-center justify-center">
          <div className="w-[100px] h-[100px] bg-[#E30613] border-2 border-[#000000]" />
          <div className="w-[100px] h-[100px] bg-[#00509A] border-2 border-[#000000] -ml-[50px] mt-[50px]" />
          <div className="w-[100px] h-[100px] bg-[#F7D117] border-2 border-[#000000] -ml-[50px] -mt-[50px]" />
        </div>

        <h2 
          className="text-[32px] font-bold uppercase tracking-[-0.03em] text-[#1A1A1A] mb-[20px]"
          style={{ fontFamily: 'var(--font-futura), Century Gothic, sans-serif', lineHeight: 1.1 }}
        >
          No storyboard
        </h2>
        <p className="text-[16px] text-[#606060] leading-[1.4]">
          Describe your scene in the panel on the left, then generate your storyboard frames.
        </p>
      </div>
    </div>
  )
}

function LoadingState() {
  return (
    <div className="p-[40px] h-full overflow-y-auto">
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-[20px]">
        {[...Array(6)].map((_, i) => (
          <div 
            key={i} 
            className="bg-[#F0F0F0] border-2 border-[#000000]"
          >
            {/* Image skeleton - concrete textured */}
            <div className="aspect-video skeleton-block relative flex items-center justify-center">
              <div 
                className="block-spinner"
                style={{ animationDelay: `${i * 0.1}s` }}
              />
            </div>
            {/* Caption skeleton */}
            <div className="p-[10px] border-t-2 border-[#000000]">
              <div className="h-[20px] skeleton-block" />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function PanelCard({ panel, index }: { panel: ReturnType<typeof useStoryboardStore>['panels'][0], index: number }) {
  const { selectPanel, updatePanelCaption } = useStoryboardStore()
  
  // Cycle through Bauhaus colors for badges
  const badgeColors = ['#E30613', '#00509A', '#F7D117', '#009E60']
  const badgeColor = badgeColors[index % badgeColors.length]
  const badgeTextColor = badgeColor === '#F7D117' ? '#1A1A1A' : '#F0F0F0'

  return (
    <div 
      className="
        bg-[#F0F0F0] border-2 border-[#000000]
        hover:border-4 hover:bg-[#F7D117]
        group
      "
    >
      {/* Image with shot type badge */}
      <button
        onClick={() => selectPanel(panel.id)}
        className="
          relative aspect-video w-full overflow-hidden
          cursor-pointer
          border-b-2 border-[#000000]
        "
      >
        {/* Placeholder image - concrete textured */}
        <div className="absolute inset-0 skeleton-block flex items-center justify-center">
          <div className="w-[60px] h-[60px] border-2 border-[#808080] flex items-center justify-center">
            <span className="text-[24px] font-bold text-[#808080] font-mono">{index + 1}</span>
          </div>
        </div>
        
        {/* Shot type badge */}
        <div 
          className="
            absolute top-[10px] left-[10px]
            px-[10px] py-[10px]
            border-2 border-[#000000]
            font-mono text-[12px] font-bold
          "
          style={{ backgroundColor: badgeColor, color: badgeTextColor }}
        >
          {panel.shotType}
        </div>

        {/* Hover overlay */}
        <div className="
          absolute inset-0
          flex items-center justify-center
          opacity-0 group-hover:opacity-100
          bg-[#000000]/50
        ">
          <span 
            className="
              font-bold text-[12px] uppercase text-[#F0F0F0]
              bg-[#000000] px-[20px] py-[10px] border-2 border-[#F0F0F0]
            "
            style={{ fontFamily: 'var(--font-futura), Century Gothic, sans-serif' }}
          >
            Click to edit
          </span>
        </div>
      </button>

      {/* Caption input */}
      <div className="p-[10px] flex items-center gap-[10px]">
        <GripVertical 
          className="w-[20px] h-[20px] text-[#808080] cursor-grab flex-shrink-0" 
          strokeWidth={2}
        />
        <input
          type="text"
          value={panel.caption}
          onChange={(e) => updatePanelCaption(panel.id, e.target.value)}
          placeholder="Add caption..."
          className="
            flex-1 bg-transparent border-0
            font-mono text-[12px] text-[#1A1A1A]
            placeholder:text-[#808080]
            focus:outline-none
            p-[5px]
            hover:bg-[#E0E0E0]
          "
        />
      </div>
    </div>
  )
}

function GeneratedState() {
  const { panels } = useStoryboardStore()

  return (
    <div className="p-[40px] h-full overflow-y-auto">
      {/* Yellow accent bar */}
      <div className="h-[10px] bg-[#F7D117] -mx-[40px] -mt-[40px] mb-[30px]" />
      
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-[20px]">
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
    <main className="flex-1 bg-[#E0E0E0] overflow-hidden relative concrete-texture">
      {appState === 'empty' && <EmptyState />}
      {appState === 'loading' && <LoadingState />}
      {appState === 'generated' && <GeneratedState />}
    </main>
  )
}
