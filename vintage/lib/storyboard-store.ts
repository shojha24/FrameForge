import { create } from 'zustand'

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

const generateMockPanels = (description: string, style: StyleType, panelCount: number): StoryboardPanel[] => {
  // Create a varied shot sequence based on panel count
  const baseSequence: ShotType[] = ['WS', 'MS', 'CU', 'OTS', 'ECU', 'MS', 'WS', 'CU', 'POV', 'ELS', 'MS', 'ECU']
  const shotSequence = baseSequence.slice(0, panelCount)
  
  // Fill remaining slots if needed
  while (shotSequence.length < panelCount) {
    shotSequence.push(SHOT_TYPES[shotSequence.length % SHOT_TYPES.length])
  }
  
  return shotSequence.map((shotType, index) => ({
    id: `panel-${Date.now()}-${index}`,
    shotType,
    imageUrl: `/api/placeholder/640/360?text=${shotType}`,
    caption: '',
    prompt: `${style} style, ${shotType} shot: ${description.slice(0, 100)}...`,
    order: index,
  }))
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
    const { sceneDescription, style, panelCount } = get()
    if (!sceneDescription.trim()) return
    
    set({ appState: 'loading' })
    
    // Simulate AI generation delay
    await new Promise(resolve => setTimeout(resolve, 3000))
    
    const panels = generateMockPanels(sceneDescription, style, panelCount)
    set({ appState: 'generated', panels })
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
    // Simulate regeneration
    await new Promise(resolve => setTimeout(resolve, 1500))
    // In real implementation, this would call the AI service
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
