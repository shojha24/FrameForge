'use client'

import { FileDown, Film } from 'lucide-react'

export function TopBar() {
  const handleExport = () => {
    console.log('[v0] Export to PDF triggered')
  }

  return (
    <header className="h-[56px] border-b-2 border-white bg-[#0A0A0A] flex items-center justify-between px-6">
      {/* Logo and Title */}
      <div className="flex items-center gap-4">
        <div className="w-10 h-10 bg-white flex items-center justify-center sharp-shadow">
          <Film className="w-6 h-6 text-[#0A0A0A]" strokeWidth={2.5} />
        </div>
        <h1 
          className="text-2xl font-bold uppercase tracking-tight text-white"
          style={{ fontFamily: 'var(--font-cooper-black), Georgia, serif' }}
        >
          FrameForge
        </h1>
      </div>

      {/* Export Button */}
      <button
        onClick={handleExport}
        className="
          flex items-center gap-3 px-5 py-2.5
          bg-[#0A0A0A] text-white border-2 border-white
          font-mono text-xs font-bold uppercase tracking-wider
          sharp-shadow
          hover:bg-white hover:text-[#0A0A0A]
          transition-colors duration-100
        "
      >
        <FileDown className="w-4 h-4" strokeWidth={2.5} />
        <span>Export PDF</span>
      </button>
    </header>
  )
}
