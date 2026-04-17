'use client'

import { TopBar } from '@/components/frameforge/top-bar'
import { Sidebar } from '@/components/frameforge/sidebar'
import { StoryboardGrid } from '@/components/frameforge/storyboard-grid'
import { PanelEditorDrawer } from '@/components/frameforge/panel-editor-drawer'

export default function FrameForgePage() {
  return (
    <div className="h-screen flex flex-col bg-black overflow-hidden">
      {/* Top Bar */}
      <TopBar />

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar - Write Flow */}
        <Sidebar />

        {/* Main Canvas - Review Flow */}
        <StoryboardGrid />
      </div>

      {/* Right Drawer - Edit Flow */}
      <PanelEditorDrawer />
    </div>
  )
}
