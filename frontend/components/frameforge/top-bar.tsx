'use client'

import { FileDown } from 'lucide-react'
import { useStoryboardStore } from '@/lib/storyboard-store'
import { exportStoryboardToPDF } from '@/lib/pdf-export'

export function TopBar() {
  const { panels, appState } = useStoryboardStore()

  const handleExport = async () => {
    if (panels.length === 0) {
      console.warn('No storyboard to export')
      return
    }
    
    try {
      await exportStoryboardToPDF(panels, 'Storyboard')
    } catch (error) {
      console.error('Failed to export PDF:', error)
    }
  }

  return (
    <header className="h-[60px] border-b-2 border-[#000000] bg-[#F0F0F0] flex items-center justify-between px-[20px]">
      {/* Logo and Title */}
      <div className="flex items-center gap-[20px]">
        {/* Bauhaus geometric logo */}
        <div className="flex items-center gap-[10px]">
          <div className="w-[40px] h-[40px] bg-[#E30613] border-2 border-[#000000]" />
          <div className="w-[40px] h-[40px] bg-[#00509A] border-2 border-[#000000] -ml-[20px] -mt-[10px]" />
          <div className="w-[40px] h-[40px] bg-[#F7D117] border-2 border-[#000000] -ml-[20px] mt-[10px]" />
        </div>
        <h1 
          className="text-[24px] font-bold uppercase tracking-[-0.03em] text-[#1A1A1A]"
          style={{ fontFamily: 'var(--font-futura), Century Gothic, sans-serif', lineHeight: 1.1 }}
        >
          FrameForge
        </h1>
      </div>

      {/* Export Button */}
      <button
        onClick={handleExport}
        disabled={appState !== 'generated' || panels.length === 0}
        className="
          flex items-center gap-[10px] px-[20px] py-[10px]
          bg-[#F0F0F0] text-[#1A1A1A] border-2 border-[#000000]
          text-[12px] font-bold uppercase tracking-[0.02em]
          min-h-[44px] min-w-[44px]
          hover:bg-[#E30613] hover:text-[#F0F0F0] hover:border-4 hover:px-[18px] hover:py-[8px]
          active:bg-[#990000]
          focus:outline-3 focus:outline-[#000000] focus:outline-offset-0
          disabled:bg-[#D0D0D0] disabled:text-[#808080] disabled:border-[#808080] disabled:cursor-not-allowed
        "
        style={{ fontFamily: 'var(--font-futura), Century Gothic, sans-serif' }}
      >
        <FileDown className="w-[20px] h-[20px]" strokeWidth={2} />
        <span>Export PDF</span>
      </button>
    </header>
  )
}
