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

const CAMERA_ANGLES = [
  'Eye Level',
  'High Angle',
  'Low Angle',
  'Bird\'s-Eye View / Top-Down',
  'Worm\'s-Eye View',
  'Dutch Angle / Canted Angle',
  'Ground Level',
]

// Valid panel field keys
const VALID_PANEL_KEYS = [
  'caption',
  'shot_type',
  'camera_angle',
  'characters',
  'pose_query',
  'lighting_mood',
  'background',
  'action_note',
  'visual_style',
]

interface PanelJsonData {
  caption?: string
  shot_type?: string
  camera_angle?: string
  characters?: Array<{ name: string; position: string }>
  pose_query?: string
  lighting_mood?: string
  background?: string
  action_note?: string
  visual_style?: string
}

export function PanelEditorDrawer() {
  const {
    isDrawerOpen,
    selectedPanelId,
    panels,
    closeDrawer,
    updatePanelShotType,
    regeneratePanel,
  } = useStoryboardStore()

  const [isVisible, setIsVisible] = useState(false)
  const [isRegenerating, setIsRegenerating] = useState(false)
  const [panelData, setPanelData] = useState<PanelJsonData>({})
  const [jsonError, setJsonError] = useState<string>('')

  const selectedPanel = panels.find(p => p.id === selectedPanelId)
  const panelIndex = panels.findIndex(p => p.id === selectedPanelId)

  useEffect(() => {
    if (isDrawerOpen && selectedPanel) {
      setIsVisible(true)
      setJsonError('')
      // Initialize panel data from selected panel
      const data: PanelJsonData = {
        caption: selectedPanel.caption || '',
        shot_type: selectedPanel.shotType,
      }
      setPanelData(data)
    } else {
      const timer = setTimeout(() => {
        setIsVisible(false)
      }, 50)
      return () => clearTimeout(timer)
    }
  }, [isDrawerOpen, selectedPanel])

  const handleFieldChange = (key: keyof PanelJsonData, value: any) => {
    setPanelData(prev => ({
      ...prev,
      [key]: value
    }))
    setJsonError('')
  }

  const handleCharacterChange = (index: number, field: 'name' | 'position', value: string) => {
    setPanelData(prev => {
      const chars = [...(prev.characters || [])]
      if (!chars[index]) {
        chars[index] = { name: '', position: '' }
      }
      chars[index][field] = value
      return { ...prev, characters: chars }
    })
  }

  const validatePanelData = (): boolean => {
    // Check for invalid keys
    const invalidKeys = Object.keys(panelData).filter(
      key => !VALID_PANEL_KEYS.includes(key)
    )
    if (invalidKeys.length > 0) {
      setJsonError(`Invalid keys: ${invalidKeys.join(', ')}. Valid keys are: ${VALID_PANEL_KEYS.join(', ')}`)
      return false
    }

    // Validate enum values
    if (panelData.shot_type && !SHOT_TYPES.some(st => st.value === panelData.shot_type)) {
      setJsonError(`Invalid shot_type: ${panelData.shot_type}. Must be one of: ${SHOT_TYPES.map(st => st.value).join(', ')}`)
      return false
    }

    if (panelData.camera_angle && !CAMERA_ANGLES.includes(panelData.camera_angle)) {
      setJsonError(`Invalid camera_angle: ${panelData.camera_angle}. Must be one of: ${CAMERA_ANGLES.join(', ')}`)
      return false
    }

    return true
  }

  const handleRegenerate = async () => {
    if (!selectedPanelId || !validatePanelData()) return
    
    setIsRegenerating(true)
    try {
      // Convert to snake_case for API
      const apiData: any = {}
      Object.entries(panelData).forEach(([key, value]) => {
        apiData[key] = value
      })
      
      await regeneratePanel(selectedPanelId, apiData)
    } catch (error) {
      console.error('Regeneration failed:', error)
      setJsonError(error instanceof Error ? error.message : 'Panel regeneration failed')
    } finally {
      setIsRegenerating(false)
    }
  }

  if (!isVisible || !selectedPanel) return null

  // Cycle through Bauhaus colors
  const badgeColors = ['#E30613', '#00509A', '#F7D117', '#009E60']
  const badgeColor = badgeColors[panelIndex % badgeColors.length]
  const badgeTextColor = badgeColor === '#F7D117' ? '#1A1A1A' : '#F0F0F0'

  return (
    <>
      {/* Scrim */}
      <div 
        className={`
          fixed inset-0 scrim z-[100]
          ${isDrawerOpen ? 'opacity-100' : 'opacity-0'}
        `}
        onClick={closeDrawer}
      />

      {/* Drawer */}
      <div 
        className={`
          fixed top-0 right-0 bottom-0 w-full max-w-[600px]
          bg-[#F0F0F0] border-l-2 border-[#000000]
          z-[100] flex flex-col overflow-hidden
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
        <div className="flex-1 overflow-y-auto p-[20px] flex flex-col gap-[20px]">
          {/* Large Image Preview */}
          <div className="relative aspect-video w-full border-2 border-[#000000] overflow-hidden bg-[#D0D0D0]">
            {selectedPanel.imageUrl ? (
              <img
                src={selectedPanel.imageUrl}
                alt={`Panel ${panelIndex + 1}`}
                className="absolute inset-0 w-full h-full object-cover"
              />
            ) : (
              <div className="absolute inset-0 skeleton-block flex items-center justify-center">
                <div className="w-[80px] h-[80px] border-2 border-[#808080] flex items-center justify-center">
                  <span className="text-[32px] font-bold text-[#808080] font-mono">{panelIndex + 1}</span>
                </div>
              </div>
            )}
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
              {panelData.shot_type || selectedPanel.shotType}
            </div>
          </div>

          {/* AI-Generated Prompt (Read-Only) */}
          <div className="flex flex-col gap-[10px]">
            <label 
              className="text-[12px] font-bold uppercase tracking-[0.02em] text-[#1A1A1A]"
              style={{ fontFamily: 'var(--font-futura), Century Gothic, sans-serif' }}
            >
              AI-generated prompt (read-only)
            </label>
            <div
              className="
                w-full max-h-[100px] overflow-y-auto p-[10px]
                bg-[#E8E8E8] text-[#1A1A1A] border-2 border-[#000000]
                font-mono text-[10px] leading-[1.3]
              "
            >
              {selectedPanel.prompt || '(prompt will be generated after edits and regeneration)'}
            </div>
          </div>

          {/* Panel JSON Fields Editor */}
          <div className="flex flex-col gap-[15px]">
            <div>
              <label 
                className="text-[12px] font-bold uppercase tracking-[0.02em] text-[#1A1A1A]"
                style={{ fontFamily: 'var(--font-futura), Century Gothic, sans-serif' }}
              >
                Panel metadata (editable)
              </label>
            </div>

            {/* Caption */}
            <div className="flex flex-col gap-[5px]">
              <label className="text-[11px] font-bold text-[#1A1A1A]">Caption</label>
              <input
                type="text"
                value={panelData.caption || ''}
                onChange={(e) => handleFieldChange('caption', e.target.value)}
                className="
                  w-full p-[8px]
                  bg-[#F0F0F0] text-[#1A1A1A] border-2 border-[#000000]
                  font-sans text-[13px]
                  hover:border-4 hover:p-[6px]
                  focus:outline-3 focus:outline-[#000000] focus:outline-offset-0
                "
                placeholder="Panel caption"
              />
            </div>

            {/* Shot Type */}
            <div className="flex flex-col gap-[5px]">
              <label className="text-[11px] font-bold text-[#1A1A1A]">Shot Type</label>
              <div className="relative">
                <select
                  value={panelData.shot_type || ''}
                  onChange={(e) => {
                    handleFieldChange('shot_type', e.target.value)
                    updatePanelShotType(selectedPanelId!, e.target.value as ShotType)
                  }}
                  className="
                    w-full p-[8px] pr-[35px]
                    bg-[#F0F0F0] text-[#1A1A1A] border-2 border-[#000000]
                    font-sans text-[13px]
                    appearance-none cursor-pointer
                    hover:border-4 hover:p-[6px] hover:pr-[33px]
                    focus:outline-3 focus:outline-[#000000] focus:outline-offset-0
                  "
                >
                  <option value="">Select shot type</option>
                  {SHOT_TYPES.map((st) => (
                    <option key={st.value} value={st.value}>
                      {st.label}
                    </option>
                  ))}
                </select>
                <ChevronDown className="absolute right-[8px] top-1/2 -translate-y-1/2 pointer-events-none w-[16px] h-[16px] text-[#1A1A1A]" strokeWidth={2} />
              </div>
            </div>

            {/* Camera Angle */}
            <div className="flex flex-col gap-[5px]">
              <label className="text-[11px] font-bold text-[#1A1A1A]">Camera Angle</label>
              <div className="relative">
                <select
                  value={panelData.camera_angle || ''}
                  onChange={(e) => handleFieldChange('camera_angle', e.target.value)}
                  className="
                    w-full p-[8px] pr-[35px]
                    bg-[#F0F0F0] text-[#1A1A1A] border-2 border-[#000000]
                    font-sans text-[13px]
                    appearance-none cursor-pointer
                    hover:border-4 hover:p-[6px] hover:pr-[33px]
                    focus:outline-3 focus:outline-[#000000] focus:outline-offset-0
                  "
                >
                  <option value="">Select camera angle</option>
                  {CAMERA_ANGLES.map((angle) => (
                    <option key={angle} value={angle}>
                      {angle}
                    </option>
                  ))}
                </select>
                <ChevronDown className="absolute right-[8px] top-1/2 -translate-y-1/2 pointer-events-none w-[16px] h-[16px] text-[#1A1A1A]" strokeWidth={2} />
              </div>
            </div>

            {/* Background */}
            <div className="flex flex-col gap-[5px]">
              <label className="text-[11px] font-bold text-[#1A1A1A]">Background / Setting</label>
              <textarea
                value={panelData.background || ''}
                onChange={(e) => handleFieldChange('background', e.target.value)}
                className="
                  w-full h-[60px] p-[8px]
                  bg-[#F0F0F0] text-[#1A1A1A] border-2 border-[#000000]
                  font-sans text-[12px] leading-[1.3]
                  resize-none
                  hover:border-4 hover:p-[6px]
                  focus:outline-3 focus:outline-[#000000] focus:outline-offset-0
                "
                placeholder="Describe the background or setting"
              />
            </div>

            {/* Action Note */}
            <div className="flex flex-col gap-[5px]">
              <label className="text-[11px] font-bold text-[#1A1A1A]">Action Note</label>
              <textarea
                value={panelData.action_note || ''}
                onChange={(e) => handleFieldChange('action_note', e.target.value)}
                className="
                  w-full h-[60px] p-[8px]
                  bg-[#F0F0F0] text-[#1A1A1A] border-2 border-[#000000]
                  font-sans text-[12px] leading-[1.3]
                  resize-none
                  hover:border-4 hover:p-[6px]
                  focus:outline-3 focus:outline-[#000000] focus:outline-offset-0
                "
                placeholder="Describe the action or movement"
              />
            </div>

            {/* Lighting Mood */}
            <div className="flex flex-col gap-[5px]">
              <label className="text-[11px] font-bold text-[#1A1A1A]">Lighting Mood</label>
              <input
                type="text"
                value={panelData.lighting_mood || ''}
                onChange={(e) => handleFieldChange('lighting_mood', e.target.value)}
                className="
                  w-full p-[8px]
                  bg-[#F0F0F0] text-[#1A1A1A] border-2 border-[#000000]
                  font-sans text-[13px]
                  hover:border-4 hover:p-[6px]
                  focus:outline-3 focus:outline-[#000000] focus:outline-offset-0
                "
                placeholder="e.g., warm, dramatic, natural"
              />
            </div>

            {/* Pose Query */}
            <div className="flex flex-col gap-[5px]">
              <label className="text-[11px] font-bold text-[#1A1A1A]">Pose Query</label>
              <textarea
                value={panelData.pose_query || ''}
                onChange={(e) => handleFieldChange('pose_query', e.target.value)}
                className="
                  w-full h-[60px] p-[8px]
                  bg-[#F0F0F0] text-[#1A1A1A] border-2 border-[#000000]
                  font-sans text-[12px] leading-[1.3]
                  resize-none
                  hover:border-4 hover:p-[6px]
                  focus:outline-3 focus:outline-[#000000] focus:outline-offset-0
                "
                placeholder="Describe the pose and position"
              />
            </div>

            {/* Characters */}
            <div className="flex flex-col gap-[5px]">
              <label className="text-[11px] font-bold text-[#1A1A1A]">Characters</label>
              {(panelData.characters || []).map((char, idx) => (
                <div key={idx} className="flex flex-col gap-[5px] p-[8px] bg-[#E8E8E8] border-2 border-[#000000]">
                  <input
                    type="text"
                    value={char.name || ''}
                    onChange={(e) => handleCharacterChange(idx, 'name', e.target.value)}
                    className="
                      w-full p-[6px]
                      bg-[#F0F0F0] text-[#1A1A1A] border-2 border-[#000000]
                      font-sans text-[12px]
                      hover:border-4 hover:p-[4px]
                    "
                    placeholder="Character name"
                  />
                  <input
                    type="text"
                    value={char.position || ''}
                    onChange={(e) => handleCharacterChange(idx, 'position', e.target.value)}
                    className="
                      w-full p-[6px]
                      bg-[#F0F0F0] text-[#1A1A1A] border-2 border-[#000000]
                      font-sans text-[12px]
                      hover:border-4 hover:p-[4px]
                    "
                    placeholder="Position (e.g., center midground)"
                  />
                </div>
              ))}
            </div>

            {/* Error Message */}
            {jsonError && (
              <div className="p-[10px] bg-[#FFE8E8] border-2 border-[#E30613]">
                <p className="text-[11px] text-[#990000] font-bold">
                  ⚠️ {jsonError}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Footer with Regenerate Button */}
        <div className="p-[20px] border-t-2 border-[#000000]">
          {/* Blue accent bar */}
          <div className="h-[10px] bg-[#00509A] -mx-[20px] -mt-[20px] mb-[20px]" />
          <button
            onClick={handleRegenerate}
            disabled={isRegenerating || !!jsonError}
            className={`
              w-full py-[15px]
              border-2 border-[#000000]
              text-[14px] font-bold uppercase tracking-[0.02em]
              flex items-center justify-center gap-[10px]
              min-h-[50px]
              ${isRegenerating || jsonError
                ? 'bg-[#A0A0A0] text-[#606060] cursor-not-allowed disabled-pattern'
                : 'bg-[#00509A] text-[#F0F0F0] hover:bg-[#E30613] hover:border-4 hover:py-[13px] active:bg-[#990000]'
              }
            `}
            style={{ fontFamily: 'var(--font-futura), Century Gothic, sans-serif' }}
            title={jsonError ? 'Fix validation errors before regenerating' : ''}
          >
            <RefreshCw className={`w-[20px] h-[20px] ${isRegenerating ? 'animate-spin' : ''}`} strokeWidth={2} />
            <span>{isRegenerating ? 'Regenerating...' : 'Regenerate panel'}</span>
          </button>
        </div>
      </div>
    </>
  )
}
