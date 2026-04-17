'use client'

import { useEffect, useState } from 'react'
import { X, RefreshCw, ChevronDown } from 'lucide-react'
import { useStoryboardStore, type ShotType } from '@/lib/storyboard-store'

const SHOT_TYPES: { value: ShotType; label: string }[] = [
  { value: 'ECU', label: 'ECU - Extreme close-up' },
  { value: 'CU', label: 'CU - Close-up' },
  { value: 'MS', label: 'MS - Medium shot' },
  { value: 'WS', label: 'WS - Wide shot' },
  { value: 'ELS', label: 'ELS - Extreme long shot' },
  { value: 'OTS', label: 'OTS - Over the shoulder' },
  { value: 'POV', label: 'POV - Point of view' },
]

export function PanelEditorDrawer() {
  const {
    isDrawerOpen,
    selectedPanelId,
    panels,
    closeDrawer,
    updatePanelShotType,
    updatePanelPrompt,
    regeneratePanel,
  } = useStoryboardStore()

  const [isVisible, setIsVisible] = useState(false)
  const [isRegenerating, setIsRegenerating] = useState(false)

  const selectedPanel = panels.find(p => p.id === selectedPanelId)
  const panelIndex = panels.findIndex(p => p.id === selectedPanelId)

  useEffect(() => {
    if (isDrawerOpen) {
      setIsVisible(true)
    } else {
      // Instant close - no animation delay
      const timer = setTimeout(() => {
        setIsVisible(false)
      }, 50)
      return () => clearTimeout(timer)
    }
  }, [isDrawerOpen])

  const handleRegenerate = async () => {
    if (!selectedPanelId) return
    setIsRegenerating(true)
    await regeneratePanel(selectedPanelId)
    setIsRegenerating(false)
  }

  if (!isVisible || !selectedPanel) return null

  // Cycle through Bauhaus colors
  const badgeColors = ['#E30613', '#00509A', '#F7D117', '#009E60']
  const badgeColor = badgeColors[panelIndex % badgeColors.length]
  const badgeTextColor = badgeColor === '#F7D117' ? '#1A1A1A' : '#F0F0F0'

  return (
    <>
      {/* Scrim - concrete textured */}
      <div 
        className={`
          fixed inset-0 scrim z-[100]
          ${isDrawerOpen ? 'opacity-100' : 'opacity-0'}
        `}
        onClick={closeDrawer}
      />

      {/* Drawer - appears instantly from right */}
      <div 
        className={`
          fixed top-0 right-0 bottom-0 w-full max-w-[500px]
          bg-[#F0F0F0] border-l-2 border-[#000000]
          z-[100] flex flex-col
          ${isDrawerOpen ? 'translate-x-0' : 'translate-x-full'}
        `}
      >
        {/* Red accent bar */}
        <div className="h-[10px] bg-[#E30613]" />
        
        {/* Header */}
        <div className="flex items-center justify-between p-[20px] border-b-2 border-[#000000]">
          <h2 
            className="text-[24px] font-bold uppercase tracking-[-0.03em] text-[#1A1A1A]"
            style={{ fontFamily: 'var(--font-futura), Century Gothic, sans-serif', lineHeight: 1.1 }}
          >
            Edit panel
          </h2>
          <button
            onClick={closeDrawer}
            className="
              w-[44px] h-[44px] bg-[#F0F0F0] border-2 border-[#000000]
              flex items-center justify-center
              hover:bg-[#E30613] hover:text-[#F0F0F0] hover:border-4
              active:bg-[#990000]
            "
          >
            <X className="w-[20px] h-[20px]" strokeWidth={2} />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-[20px] flex flex-col gap-[30px]">
          {/* Large Image Preview */}
          <div className="relative aspect-video w-full border-2 border-[#000000] overflow-hidden skeleton-block">
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-[80px] h-[80px] border-2 border-[#808080] flex items-center justify-center">
                <span className="text-[32px] font-bold text-[#808080] font-mono">{panelIndex + 1}</span>
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
              {selectedPanel.shotType}
            </div>
          </div>

          {/* Shot Type Selection */}
          <div className="flex flex-col gap-[10px]">
            <label 
              className="text-[12px] font-bold uppercase tracking-[0.02em] text-[#1A1A1A]"
              style={{ fontFamily: 'var(--font-futura), Century Gothic, sans-serif' }}
            >
              Shot type
            </label>
            <div className="relative">
              <select
                value={selectedPanel.shotType}
                onChange={(e) => updatePanelShotType(selectedPanelId!, e.target.value as ShotType)}
                className="
                  w-full p-[10px] pr-[40px]
                  bg-[#F0F0F0] text-[#1A1A1A] border-2 border-[#000000]
                  font-sans text-[16px]
                  appearance-none cursor-pointer
                  hover:bg-[#F7D117] hover:border-4 hover:p-[8px] hover:pr-[38px]
                  focus:outline-3 focus:outline-[#000000] focus:outline-offset-0
                "
              >
                {SHOT_TYPES.map((st) => (
                  <option key={st.value} value={st.value}>
                    {st.label}
                  </option>
                ))}
              </select>
              <div className="absolute right-[10px] top-1/2 -translate-y-1/2 pointer-events-none">
                <ChevronDown className="w-[20px] h-[20px] text-[#1A1A1A]" strokeWidth={2} />
              </div>
            </div>
          </div>

          {/* Prompt Editor */}
          <div className="flex flex-col gap-[10px]">
            <label 
              className="text-[12px] font-bold uppercase tracking-[0.02em] text-[#1A1A1A]"
              style={{ fontFamily: 'var(--font-futura), Century Gothic, sans-serif' }}
            >
              Auto-generated prompt
            </label>
            <textarea
              value={selectedPanel.prompt}
              onChange={(e) => updatePanelPrompt(selectedPanelId!, e.target.value)}
              className="
                w-full h-[160px] p-[10px]
                bg-[#F0F0F0] text-[#1A1A1A] border-2 border-[#000000]
                font-mono text-[12px] leading-[1.4]
                resize-none
                hover:border-4 hover:p-[8px]
                focus:outline-3 focus:outline-[#000000] focus:outline-offset-0
              "
            />
          </div>
        </div>

        {/* Footer with Regenerate Button */}
        <div className="p-[20px] border-t-2 border-[#000000]">
          {/* Blue accent bar */}
          <div className="h-[10px] bg-[#00509A] -mx-[20px] -mt-[20px] mb-[20px]" />
          <button
            onClick={handleRegenerate}
            disabled={isRegenerating}
            className={`
              w-full py-[15px]
              border-2 border-[#000000]
              text-[14px] font-bold uppercase tracking-[0.02em]
              flex items-center justify-center gap-[10px]
              min-h-[50px]
              ${isRegenerating
                ? 'bg-[#A0A0A0] text-[#606060] cursor-not-allowed disabled-pattern'
                : 'bg-[#00509A] text-[#F0F0F0] hover:bg-[#E30613] hover:border-4 hover:py-[13px] active:bg-[#990000]'
              }
            `}
            style={{ fontFamily: 'var(--font-futura), Century Gothic, sans-serif' }}
          >
            <RefreshCw className={`w-[20px] h-[20px] ${isRegenerating ? 'animate-spin' : ''}`} strokeWidth={2} />
            <span>{isRegenerating ? 'Regenerating...' : 'Regenerate panel'}</span>
          </button>
        </div>
      </div>
    </>
  )
}
