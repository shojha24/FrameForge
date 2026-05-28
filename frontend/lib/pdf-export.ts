import { jsPDF } from 'jspdf'
import { StoryboardPanel } from './storyboard-store'

export async function exportStoryboardToPDF(
  panels: StoryboardPanel[],
  title: string = 'Storyboard'
): Promise<void> {
  if (panels.length === 0) {
    console.warn('No panels to export')
    return
  }

  const pdf = new jsPDF({
    orientation: 'landscape',
    unit: 'mm',
    format: 'a4',
  })

  const pageWidth = pdf.internal.pageSize.getWidth()
  const pageHeight = pdf.internal.pageSize.getHeight()
  const margin = 15
  const contentWidth = pageWidth - 2 * margin
  const contentHeight = pageHeight - 2 * margin

  let isFirstPage = true

  for (let i = 0; i < panels.length; i++) {
    const panel = panels[i]

    if (!isFirstPage) {
      pdf.addPage()
    }
    isFirstPage = false

    // Title on first page only
    if (i === 0) {
      pdf.setFontSize(20)
      pdf.text(title, margin, margin + 10)
      pdf.setFontSize(10)
      pdf.text(`Panel ${i + 1} of ${panels.length}`, margin, margin + 20)
    } else {
      pdf.setFontSize(10)
      pdf.text(`Panel ${i + 1} of ${panels.length}`, margin, margin + 5)
    }

    try {
      // Extract image data from base64 or URL
      let imageData: string | null = null

      if (panel.imageUrl.startsWith('data:image')) {
        // Already base64
        imageData = panel.imageUrl
      } else if (panel.imageUrl) {
        // Try to fetch and convert to base64
        try {
          const response = await fetch(panel.imageUrl)
          const blob = await response.blob()
          imageData = await blobToBase64(blob)
        } catch (e) {
          console.warn(`Failed to fetch image for panel ${i + 1}:`, e)
        }
      }

      // Add image if available
      if (imageData) {
        const imgY = i === 0 ? margin + 30 : margin + 15
        const imgHeight = contentHeight - (i === 0 ? 45 : 30)
        const imgWidth = contentWidth

        // Calculate aspect ratio and fit
        const maxHeight = imgHeight
        let finalHeight = maxHeight
        let finalWidth = (finalHeight * 16) / 9 // Assuming 16:9 aspect ratio

        if (finalWidth > imgWidth) {
          finalWidth = imgWidth
          finalHeight = (finalWidth * 9) / 16
        }

        const imgX = margin + (contentWidth - finalWidth) / 2

        try {
          pdf.addImage(
            imageData,
            'PNG',
            imgX,
            imgY,
            finalWidth,
            finalHeight
          )
        } catch (e) {
          console.warn(`Failed to add image for panel ${i + 1}:`, e)
        }
      }

      // Add caption and metadata
      const metaY =
        (i === 0 ? margin + 30 : margin + 15) +
        ((contentHeight - (i === 0 ? 45 : 30)) * 9) / 16 +
        5
      const metaStartY = Math.min(metaY + 10, pageHeight - 30)

      pdf.setFontSize(8)
      pdf.setTextColor(100)

      // Shot type
      if (panel.shotType) {
        pdf.text(`Shot: ${panel.shotType}`, margin, metaStartY)
      }

      // Caption
      if (panel.caption) {
        const captionLines = pdf.splitTextToSize(
          panel.caption,
          contentWidth - 10
        )
        pdf.text(captionLines, margin + 5, metaStartY + 5)
      }
    } catch (e) {
      console.error(`Error processing panel ${i + 1}:`, e)
    }
  }

  // Save the PDF
  pdf.save(`${title}.pdf`)
}

function blobToBase64(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onloadend = () => {
      const result = reader.result as string
      resolve(result)
    }
    reader.onerror = reject
    reader.readAsDataURL(blob)
  })
}
