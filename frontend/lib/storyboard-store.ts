import { create } from 'zustand'

const API_BASE = 'http://127.0.0.1:8000/frame-forge/api'

async function generatePanels(
  sceneDescription: string,
  style: string,
  panelCount: number,
  characterImage: File | null   // add this
): Promise<StoryboardPanel[]> {
  const formData = new FormData()
  formData.append('scene_prompt', sceneDescription)
  formData.append('num_panels', panelCount.toString())
  formData.append('visual_style', style || 'cinematic, photorealistic')
  if (characterImage) {
    formData.append('character_reference', characterImage)  // add this
  }

  const response = await fetch(`${API_BASE}/generate`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(`API error: ${response.statusText} - ${JSON.stringify(error.detail || error)}`)
  }
  
  const data = await response.json()
  
  // Map backend response to StoryboardPanel format
  return (data.panels || []).map((panel: any, idx: number) => ({
    id: `panel-${idx}`,
    shotType: panel.shotType || panel.shot_type || 'MS',
    imageUrl: data.generated_images?.[idx] 
      ? `data:image/png;base64,${data.generated_images[idx]}` 
      : '',
    caption: panel.caption || '',
    prompt: data.sdxl_prompts?.[idx] || '',
    order: idx,
  }))
}

async function regeneratePanelAPI(
  panel: StoryboardPanel,
  customPrompt: string,
  characterImage: File | null
): Promise<string> {
  // Convert panel back to snake_case for backend
  const panelData = {
    shotType: panel.shotType,
    caption: panel.caption,
    prompt: panel.prompt,
    // Include any other panel properties
  }
  
  const formData = new FormData()
  formData.append('panel_json', JSON.stringify(panelData))
  formData.append('custom_prompt', customPrompt)
  if (characterImage) {
    formData.append('character_image', characterImage)
  }

  const response = await fetch(`${API_BASE}/regenerate`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(`API error: ${response.statusText} - ${JSON.stringify(error.detail || error)}`)
  }
  
  const data = await response.json()
  
  // Extract base64 image from response
  const imageBase64 = data.generated_image
  return `data:image/png;base64,${imageBase64}`
}

export type ShotType = 'ECU' | 'CU' | 'MS' | 'WS' | 'ELS' | 'OTS' | 'POV'

// Style is now a string to support the extensive style library
export type StyleType = string

export interface StoryboardPanel {
  id: string
  shotType: ShotType
  imageUrl: string
  caption: string
  prompt: string
  order: number
}

interface PanelInput {
  shot_type: ShotType;
  caption: string;
}

export type AppState = 'empty' | 'loading' | 'generated'

interface StoryboardState {
  appState: AppState
  sceneDescription: string
  characterImage: File | null
  characterImagePreview: string | null
  style: StyleType
  panelCount: number
  panels: StoryboardPanel[]
  selectedPanelId: string | null
  isDrawerOpen: boolean
  
  // Actions
  setSceneDescription: (description: string) => void
  setCharacterImage: (file: File | null) => void
  setStyle: (style: StyleType) => void
  setPanelCount: (count: number) => void
  generateStoryboard: () => Promise<void>
  selectPanel: (id: string) => void
  closeDrawer: () => void
  updatePanelCaption: (id: string, caption: string) => void
  updatePanelShotType: (id: string, shotType: ShotType) => void
  updatePanelPrompt: (id: string, prompt: string) => void
  regeneratePanel: (id: string) => Promise<void>
  reorderPanels: (startIndex: number, endIndex: number) => void
  reset: () => void
}

const SHOT_TYPES: ShotType[] = ['ECU', 'CU', 'MS', 'WS', 'ELS', 'OTS', 'POV']

const generateMockPanels = async (description: string, style: StyleType, panelCount: number): Promise<StoryboardPanel[]> => {

  // Create a varied shot sequence based on panel count
  const baseSequence: ShotType[] = ['WS', 'MS', 'CU', 'OTS', 'ECU', 'MS', 'WS', 'CU', 'POV', 'ELS', 'MS', 'ECU']
  const shotSequence = baseSequence.slice(0, panelCount)
  
  // Fill remaining slots if needed
  while (shotSequence.length < panelCount) {
    shotSequence.push(SHOT_TYPES[shotSequence.length % SHOT_TYPES.length])
  }
  
  return shotSequence.map((shotType, index) => ({
    id: `panel-${index}-${crypto.randomUUID()}`, 
    shotType, 
    imageUrl: `/api/placeholder/640/360?text=${shotType}`,
    caption: '',
    prompt: `${style} style, ${shotType} shot: ${description.slice(0, 100)}...`,
    order: index,
  }));
}

export const useStoryboardStore = create<StoryboardState>((set, get) => ({
  appState: 'empty',
  sceneDescription: '',
  characterImage: null,
  characterImagePreview: null,
  style: 'Rough Charcoal',
  panelCount: 6,
  panels: [],
  selectedPanelId: null,
  isDrawerOpen: false,

  setSceneDescription: (description) => set({ sceneDescription: description }),
  
  setCharacterImage: (file) => {
    if (file) {
      const reader = new FileReader()
      reader.onloadend = () => {
        set({ characterImage: file, characterImagePreview: reader.result as string })
      }
      reader.readAsDataURL(file)
    } else {
      set({ characterImage: null, characterImagePreview: null })
    }
  },
  
  setStyle: (style) => set({ style }),
  
  setPanelCount: (count) => set({ panelCount: count }),
  
  generateStoryboard: async () => {
    const { sceneDescription, style, panelCount, characterImage } = get()
    if (!sceneDescription.trim()) return
    
    set({ appState: 'loading' })
    
    // Generate Story Panels
    try {
      const panels = await generatePanels(sceneDescription, style, panelCount, characterImage);
      console.log("Panels generated:", panels);
  
      set({ appState: 'generated', panels });
    } catch (error) {
      console.error("An Unexpected Error Occured:", error)
      
      set({ appState: 'empty' })
    }
  },
  
  selectPanel: (id) => set({ selectedPanelId: id, isDrawerOpen: true }),
  
  closeDrawer: () => set({ isDrawerOpen: false, selectedPanelId: null }),
  
  updatePanelCaption: (id, caption) => set((state) => ({
    panels: state.panels.map(p => p.id === id ? { ...p, caption } : p)
  })),
  
  updatePanelShotType: (id, shotType) => set((state) => ({
    panels: state.panels.map(p => p.id === id ? { ...p, shotType } : p)
  })),
  
  updatePanelPrompt: (id, prompt) => set((state) => ({
    panels: state.panels.map(p => p.id === id ? { ...p, prompt } : p)
  })),
  
  regeneratePanel: async (id) => {
    const state = get()
    const panel = state.panels.find(p => p.id === id)
    if (!panel) return
    
    try {
      const newImageUrl = await regeneratePanelAPI(
        panel,
        panel.prompt,
        state.characterImage
      )
      
      // Update the panel with the new image
      set((state) => ({
        panels: state.panels.map(p => 
          p.id === id ? { ...p, imageUrl: newImageUrl } : p
        )
      }))
    } catch (error) {
      console.error('Panel regeneration failed:', error)
      throw error
    }
  },
  
  reorderPanels: (startIndex, endIndex) => set((state) => {
    const newPanels = [...state.panels]
    const [removed] = newPanels.splice(startIndex, 1)
    newPanels.splice(endIndex, 0, removed)
    return { panels: newPanels.map((p, i) => ({ ...p, order: i })) }
  }),
  
  reset: () => set({
    appState: 'empty',
    sceneDescription: '',
    characterImage: null,
    characterImagePreview: null,
    style: 'Rough Charcoal',
    panelCount: 6,
    panels: [],
    selectedPanelId: null,
    isDrawerOpen: false,
  }),
}))
