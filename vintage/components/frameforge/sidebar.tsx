'use client'

import { useCallback } from 'react'
import { Upload, X, ChevronDown, Sparkles } from 'lucide-react'
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

const PANEL_COUNTS = [4, 6, 8, 10, 12]

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
    <aside className="w-[320px] min-w-[320px] border-r-2 border-white bg-[#111111] flex flex-col h-full overflow-hidden">
      <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-8">
        {/* Scene Description */}
        <div className="flex flex-col gap-3">
          <label 
            htmlFor="scene-description"
            className="text-sm font-bold uppercase tracking-wider text-white"
            style={{ fontFamily: 'var(--font-cooper-black), Georgia, serif' }}
          >
            Scene description
          </label>
          <textarea
            id="scene-description"
            value={sceneDescription}
            onChange={(e) => setSceneDescription(e.target.value)}
            placeholder="Write your 2-4 sentence scene description here..."
            className="
              w-full h-[160px] p-4
              bg-[#1A1A1A] text-[#F5F5F0] border-2 border-white
              font-serif text-base leading-relaxed
              placeholder:text-[#666666]
              resize-none
              sharp-shadow
              hover:bg-[#222222]
              focus:shadow-[4px_4px_0px_0px_rgba(255,255,255,0.4)]
            "
          />
        </div>

        {/* Character Reference */}
        <div className="flex flex-col gap-3">
          <label 
            className="text-sm font-bold uppercase tracking-wider text-white"
            style={{ fontFamily: 'var(--font-cooper-black), Georgia, serif' }}
          >
            Character reference
          </label>
          
          {characterImagePreview ? (
            <div className="relative sharp-shadow">
              <img
                src={characterImagePreview}
                alt="Character reference"
                className="w-full h-[120px] object-cover border-2 border-white"
              />
              <button
                onClick={() => setCharacterImage(null)}
                className="
                  absolute top-2 right-2
                  w-8 h-8 bg-[#0A0A0A] border-2 border-white
                  flex items-center justify-center
                  hover:bg-white hover:text-[#0A0A0A]
                  transition-colors duration-100
                "
              >
                <X className="w-4 h-4" strokeWidth={2.5} />
              </button>
            </div>
          ) : (
            <label
              onDrop={handleDrop}
              onDragOver={(e) => e.preventDefault()}
              className="
                flex flex-col items-center justify-center gap-3
                w-full h-[120px] p-4
                bg-[#1A1A1A] border-2 border-dashed border-[#666666]
                cursor-pointer sharp-shadow
                hover:border-white hover:bg-[#222222]
                transition-colors duration-100
              "
            >
              <Upload className="w-6 h-6 text-[#666666]" strokeWidth={2} />
              <div className="text-center">
                <p className="text-xs font-bold uppercase tracking-wider text-[#666666]">
                  Upload character
                </p>
                <p className="text-[10px] text-[#444444] font-mono mt-1">(IP-Adapter)</p>
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
        <div className="flex flex-col gap-3">
          <label 
            className="text-sm font-bold uppercase tracking-wider text-white"
            style={{ fontFamily: 'var(--font-cooper-black), Georgia, serif' }}
          >
            Panel count
          </label>
          <div className="flex gap-0 border-2 border-white sharp-shadow">
            {PANEL_COUNTS.map((count) => (
              <button
                key={count}
                onClick={() => setPanelCount(count)}
                className={`
                  flex-1 py-3
                  font-mono text-sm font-bold
                  border-r border-[#333333] last:border-r-0
                  transition-colors duration-100
                  ${panelCount === count 
                    ? 'bg-white text-[#0A0A0A]' 
                    : 'bg-[#1A1A1A] text-white hover:bg-[#2A2A2A]'
                  }
                `}
              >
                {count}
              </button>
            ))}
          </div>
        </div>

        {/* Style Selection */}
        <div className="flex flex-col gap-3">
          <label 
            className="text-sm font-bold uppercase tracking-wider text-white"
            style={{ fontFamily: 'var(--font-cooper-black), Georgia, serif' }}
          >
            Style
          </label>
          <div className="relative">
            <select
              value={style}
              onChange={(e) => setStyle(e.target.value)}
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
              {STYLE_CATEGORIES.map((category) => (
                <optgroup 
                  key={category.name} 
                  label={category.name}
                  className="bg-[#0A0A0A] text-[#B3B3B3] font-bold"
                >
                  {category.styles.map((s) => (
                    <option 
                      key={s} 
                      value={s}
                      className="bg-[#1A1A1A] text-white py-2"
                    >
                      {s}
                    </option>
                  ))}
                </optgroup>
              ))}
            </select>
            <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none">
              <ChevronDown className="w-5 h-5 text-white" strokeWidth={2.5} />
            </div>
          </div>
        </div>
      </div>

      {/* Generate Button */}
      <div className="p-6 border-t-2 border-[#333333]">
        <button
          onClick={generateStoryboard}
          disabled={!sceneDescription.trim() || isGenerating}
          className={`
            w-full py-4
            border-2 border-white
            font-mono text-sm font-bold uppercase tracking-wider
            flex items-center justify-center gap-3
            sharp-shadow-lg
            transition-colors duration-100
            ${isGenerating || !sceneDescription.trim()
              ? 'bg-[#333333] text-[#666666] cursor-not-allowed border-[#666666] shadow-none'
              : 'bg-white text-[#0A0A0A] hover:bg-[#F5A623] hover:border-[#F5A623]'
            }
          `}
        >
          <Sparkles className={`w-5 h-5 ${isGenerating ? 'animate-pulse' : ''}`} strokeWidth={2} />
          <span>{isGenerating ? 'Generating...' : 'Generate storyboard'}</span>
        </button>
      </div>
    </aside>
  )
}
