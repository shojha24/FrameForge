'use client'

import { useCallback } from 'react'
import { Upload, X, ChevronDown } from 'lucide-react'
import { useStoryboardStore } from '@/lib/storyboard-store'

const STYLE_CATEGORIES = [
  {
    name: 'Foundational',
    styles: ['Rough Charcoal', 'Blue Sketch', 'Technical Ink', 'Graphite Hatch', 'Marker Comp', 'Blueprint Lines', 'Loose Watercolor', 'Contour Line', 'Scribble Gesture', 'Chalk Pastel'],
  },
  {
    name: 'Cinematic',
    styles: ['Film Noir', 'Vivid Technicolor', 'Gritty Western', 'Cyberpunk Neon', 'Gothic Horror', 'Period Drama', 'Spy Thriller', 'Surrealist Dream', 'Victorian Steampunk', 'Space Opera'],
  },
  {
    name: 'Animation',
    styles: ['90s Anime', 'Studio Ghibli', 'Rubber Hose', 'Flat Vector', 'Ligne Claire', 'Woodblock Print', 'Paper Cutout', 'Stop-Motion Clay', 'Pop Art', 'Golden Comic'],
  },
  {
    name: 'Realistic',
    styles: ['Hyper Realistic', 'Vintage Polaroid', 'Tilt Shift', 'Infrared Photo', 'Documentary Handheld', 'Security Cam', 'Brutalist Concrete', 'Macro Focus', 'Drone Aerial', 'Action Fisheye'],
  },
  {
    name: 'Textural',
    styles: ['Fine Etching', 'Sand Animation', 'Oil Impasto', 'Digital Glitch', 'Classroom Chalkboard', 'Stipple Pointillism', 'Coffee Wash', 'X-Ray', 'Bioluminescent Glow', 'Stitched Embroidery'],
  },
  {
    name: 'Historical Art',
    styles: ['Art Deco', 'Art Nouveau', 'Bauhaus Geometry', 'Impressionist Dab', 'Expressionist Distortion', 'Dada Collage', 'Romantic Painting', '80s Synthwave', 'Lo-Fi Grain', 'Continuous Line'],
  },
  {
    name: 'Conceptual',
    styles: ['Drafting Schematic', '8-Bit Pixel', '3D Voxel', 'Thermal Heatmap', 'Legal Pad', 'Cave Painting', 'Stained Glass', 'Vellum Layer', 'Urban Sketch', 'Anatomy Study'],
  },
  {
    name: 'Atmospheric',
    styles: ['Golden Hour', 'Heavy Mist', 'Internal Glow', 'Sunset Silhouette', 'High Key', 'Low Key', 'Volumetric Ray', 'Monochrome Wash', 'Solarized Tones', 'Dappled Light'],
  },
  {
    name: 'Global',
    styles: ['Chinese Manhua', 'Aztec Codex', 'Celtic Knot', 'Bollywood Glamour', 'Nordic Minimal', 'Wax Pattern', 'Calligraphic Script', 'Aboriginal Dot', 'Swiss Grid', 'Nostalgic Americana'],
  },
  {
    name: 'Modern Digital',
    styles: ['Clay Render', 'Wireframe Mesh', 'Isometric View', 'Cel Shaded', 'Deep Dream', 'Raw Brutalism', 'Dark Mode', 'AR Overlay', 'VR Stroke', 'Liquid Metal'],
  },
]

export function Sidebar() {
  const {
    sceneDescription,
    setSceneDescription,
    characterImagePreview,
    setCharacterImage,
    style,
    setStyle,
    panelCount,
    setPanelCount,
    generateStoryboard,
    appState,
  } = useStoryboardStore()

  const PANEL_COUNTS = [4, 6, 8, 10, 12]

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    const file = e.dataTransfer.files[0]
    if (file && file.type.startsWith('image/')) {
      setCharacterImage(file)
    }
  }, [setCharacterImage])

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setCharacterImage(file)
    }
  }

  const isGenerating = appState === 'loading'

  return (
    <aside className="w-[320px] min-w-[320px] border-r-2 border-[#000000] bg-[#F0F0F0] flex flex-col h-full overflow-hidden">
      {/* Red accent bar */}
      <div className="h-[10px] bg-[#E30613]" />
      
      <div className="flex-1 overflow-y-auto p-[20px] flex flex-col gap-[30px]">
        {/* Scene Description */}
        <div className="flex flex-col gap-[10px]">
          <label 
            htmlFor="scene-description"
            className="text-[12px] font-bold uppercase tracking-[0.02em] text-[#1A1A1A]"
            style={{ fontFamily: 'var(--font-futura), Century Gothic, sans-serif' }}
          >
            Scene description
          </label>
          <textarea
            id="scene-description"
            value={sceneDescription}
            onChange={(e) => setSceneDescription(e.target.value)}
            placeholder="Write your 2-4 sentence scene description here."
            className="
              w-full h-[180px] p-[10px]
              bg-[#F0F0F0] text-[#1A1A1A] border-2 border-[#000000]
              font-sans text-[16px] leading-[1.4]
              placeholder:text-[#808080]
              resize-none
              hover:border-4 hover:p-[8px]
              focus:outline-3 focus:outline-[#000000] focus:outline-offset-0
            "
          />
        </div>

        {/* Character Reference */}
        <div className="flex flex-col gap-[10px]">
          <label 
            className="text-[12px] font-bold uppercase tracking-[0.02em] text-[#1A1A1A]"
            style={{ fontFamily: 'var(--font-futura), Century Gothic, sans-serif' }}
          >
            Character reference
          </label>
          
          {characterImagePreview ? (
            <div className="relative">
              <img
                src={characterImagePreview}
                alt="Character reference"
                className="w-full h-[140px] object-cover border-2 border-[#000000]"
              />
              <button
                onClick={() => setCharacterImage(null)}
                className="
                  absolute top-[10px] right-[10px]
                  w-[44px] h-[44px] bg-[#F0F0F0] border-2 border-[#000000]
                  flex items-center justify-center
                  hover:bg-[#E30613] hover:text-[#F0F0F0] hover:border-4
                "
              >
                <X className="w-[20px] h-[20px]" strokeWidth={2} />
              </button>
            </div>
          ) : (
            <label
              onDrop={handleDrop}
              onDragOver={(e) => e.preventDefault()}
              className="
                flex flex-col items-center justify-center gap-[10px]
                w-full h-[140px] p-[10px]
                bg-[#E0E0E0] border-2 border-dashed border-[#000000]
                cursor-pointer
                hover:bg-[#F7D117] hover:border-solid hover:border-4
              "
            >
              <Upload className="w-[24px] h-[24px] text-[#1A1A1A]" strokeWidth={2} />
              <div className="text-center">
                <p 
                  className="text-[12px] font-bold uppercase text-[#1A1A1A]"
                  style={{ fontFamily: 'var(--font-futura), Century Gothic, sans-serif' }}
                >
                  Upload character
                </p>
                <p className="text-[10px] text-[#606060] font-mono mt-[5px]">(IP-Adapter)</p>
              </div>
              <input
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                className="sr-only"
              />
            </label>
          )}
        </div>

        {/* Panel Count */}
        <div className="flex flex-col gap-[10px]">
          <label 
            className="text-[12px] font-bold uppercase tracking-[0.02em] text-[#1A1A1A]"
            style={{ fontFamily: 'var(--font-futura), Century Gothic, sans-serif' }}
          >
            Panel count
          </label>
          <div className="flex gap-0 border-2 border-[#000000]">
            {PANEL_COUNTS.map((count) => (
              <button
                key={count}
                onClick={() => setPanelCount(count)}
                className={`
                  flex-1 py-[10px]
                  text-[14px] font-bold font-mono
                  border-r border-[#000000] last:border-r-0
                  transition-all duration-[50ms]
                  ${panelCount === count 
                    ? 'bg-[#00509A] text-[#F0F0F0]' 
                    : 'bg-[#F0F0F0] text-[#1A1A1A] hover:bg-[#F7D117] hover:border-4 hover:border-[#000000]'
                  }
                `}
              >
                {count}
              </button>
            ))}
          </div>
        </div>

        {/* Style Selection */}
        <div className="flex flex-col gap-[10px]">
          <label 
            className="text-[12px] font-bold uppercase tracking-[0.02em] text-[#1A1A1A]"
            style={{ fontFamily: 'var(--font-futura), Century Gothic, sans-serif' }}
          >
            Style
          </label>
          <div className="relative">
            <select
              value={style}
              onChange={(e) => setStyle(e.target.value)}
              className="
                w-full p-[10px] pr-[40px]
                bg-[#F0F0F0] text-[#1A1A1A] border-2 border-[#000000]
                font-sans text-[16px]
                appearance-none cursor-pointer
                hover:bg-[#F7D117] hover:border-4 hover:p-[8px] hover:pr-[38px]
                focus:outline-3 focus:outline-[#000000] focus:outline-offset-0
              "
            >
              {STYLE_CATEGORIES.map((category) => (
                <optgroup 
                  key={category.name} 
                  label={category.name}
                  className="bg-[#E0E0E0] text-[#1A1A1A] font-bold"
                >
                  {category.styles.map((s) => (
                    <option 
                      key={s} 
                      value={s}
                      className="bg-[#F0F0F0] text-[#1A1A1A] py-[10px]"
                    >
                      {s}
                    </option>
                  ))}
                </optgroup>
              ))}
            </select>
            <div className="absolute right-[10px] top-1/2 -translate-y-1/2 pointer-events-none">
              <ChevronDown className="w-[20px] h-[20px] text-[#1A1A1A]" strokeWidth={2} />
            </div>
          </div>
        </div>
      </div>

      {/* Generate Button */}
      <div className="p-[20px] border-t-2 border-[#000000]">
        {/* Blue accent bar */}
        <div className="h-[10px] bg-[#00509A] -mx-[20px] -mt-[20px] mb-[20px]" />
        <button
          onClick={generateStoryboard}
          disabled={!sceneDescription.trim() || isGenerating}
          className={`
            w-full py-[20px]
            border-2 border-[#000000]
            text-[16px] font-bold uppercase tracking-[0.02em]
            min-h-[60px]
            ${isGenerating || !sceneDescription.trim()
              ? 'bg-[#A0A0A0] text-[#606060] cursor-not-allowed disabled-pattern'
              : 'bg-[#E30613] text-[#F0F0F0] hover:bg-[#00509A] hover:border-4 hover:py-[18px] active:bg-[#003366]'
            }
          `}
          style={{ fontFamily: 'var(--font-futura), Century Gothic, sans-serif' }}
        >
          {isGenerating ? 'Generating...' : 'Generate storyboard'}
        </button>
      </div>
    </aside>
  )
}
