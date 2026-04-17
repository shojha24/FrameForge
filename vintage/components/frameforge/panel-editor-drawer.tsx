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
      const timer = setTimeout(() => {
        setIsVisible(false)
      }, 150)
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

  return (
    <>
      {/* Scrim */}
      <div 
        className={`
          fixed inset-0 bg-black/80 z-[100]
          transition-opacity duration-150
          ${isDrawerOpen ? 'opacity-100' : 'opacity-0'}
        `}
        onClick={closeDrawer}
      />

      {/* Drawer */}
      <div 
        className={`
          fixed top-0 right-0 bottom-0 w-full max-w-[480px]
          bg-[#111111] border-l-2 border-white
          z-[100] flex flex-col
          transition-transform duration-150 ease-out
          ${isDrawerOpen ? 'translate-x-0' : 'translate-x-full'}
        `}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b-2 border-[#333333]">
          <h2 
            className="text-2xl font-bold uppercase tracking-tight text-white"
            style={{ fontFamily: 'var(--font-cooper-black), Georgia, serif' }}
          >
            Edit panel {panelIndex + 1}
          </h2>
          <button
            onClick={closeDrawer}
            className="
              w-10 h-10 bg-[#0A0A0A] border-2 border-white
              flex items-center justify-center
              hover:bg-white hover:text-[#0A0A0A]
              transition-colors duration-100
            "
          >
            <X className="w-5 h-5" strokeWidth={2.5} />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-8">
          {/* Large Image Preview */}
          <div className="relative aspect-video w-full border-2 border-white sharp-shadow-lg overflow-hidden film-grain">
            <div className="absolute inset-0 bg-[#1A1A1A] flex items-center justify-center">
              <div className="w-20 h-20 border-2 border-[#333333] flex items-center justify-center z-10">
                <span className="text-3xl font-bold text-[#444444] font-mono">{panelIndex + 1}</span>
              </div>
            </div>
            {/* Shot type badge */}
            <div className="
              absolute top-4 left-4 z-10
              px-3 py-1.5
              bg-white text-[#0A0A0A]
              font-mono text-xs font-bold uppercase
            ">
              {selectedPanel.shotType}
            </div>
          </div>

          {/* Shot Type Selection */}
          <div className="flex flex-col gap-3">
            <label 
              className="text-sm font-bold uppercase tracking-wider text-white"
              style={{ fontFamily: 'var(--font-cooper-black), Georgia, serif' }}
            >
              Shot type
            </label>
            <div className="relative">
              <select
                value={selectedPanel.shotType}
                onChange={(e) => updatePanelShotType(selectedPanelId!, e.target.value as ShotType)}
                className="
                  w-full p-4 pr-12
                  bg-[#1A1A1A] text-white border-2 border-white
                  font-mono text-sm
                  sharp-shadow
                  appearance-none cursor-pointer
                  hover:bg-[#222222]
                  focus:shadow-[4px_4px_0px_0px_rgba(255,255,255,0.4)]
                "
              >
                {SHOT_TYPES.map((st) => (
                  <option key={st.value} value={st.value} className="bg-[#1A1A1A]">
                    {st.label}
                  </option>
                ))}
              </select>
              <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none">
                <ChevronDown className="w-5 h-5 text-white" strokeWidth={2.5} />
              </div>
            </div>
          </div>

          {/* Prompt Editor */}
          <div className="flex flex-col gap-3">
            <label 
              className="text-sm font-bold uppercase tracking-wider text-white"
              style={{ fontFamily: 'var(--font-cooper-black), Georgia, serif' }}
            >
              Auto-generated prompt
            </label>
            <textarea
              value={selectedPanel.prompt}
              onChange={(e) => updatePanelPrompt(selectedPanelId!, e.target.value)}
              className="
                w-full h-[140px] p-4
                bg-[#1A1A1A] text-[#F5F5F0] border-2 border-white
                font-mono text-xs leading-relaxed
                resize-none
                sharp-shadow
                hover:bg-[#222222]
                focus:shadow-[4px_4px_0px_0px_rgba(255,255,255,0.4)]
              "
            />
          </div>
        </div>

        {/* Footer with Regenerate Button */}
        <div className="p-6 border-t-2 border-[#333333]">
          <button
            onClick={handleRegenerate}
            disabled={isRegenerating}
            className={`
              w-full py-4
              border-2 border-white
              font-mono text-sm font-bold uppercase tracking-wider
              flex items-center justify-center gap-3
              sharp-shadow-lg
              transition-colors duration-100
              ${isRegenerating
                ? 'bg-[#333333] text-[#666666] cursor-not-allowed border-[#666666] shadow-none'
                : 'bg-[#F5A623] text-[#0A0A0A] border-[#F5A623] hover:bg-white hover:border-white'
              }
            `}
          >
            <RefreshCw className={`w-5 h-5 ${isRegenerating ? 'animate-spin' : ''}`} strokeWidth={2} />
            <span>{isRegenerating ? 'Regenerating...' : 'Regenerate panel'}</span>
          </button>
        </div>
      </div>
    </>
  )
}
