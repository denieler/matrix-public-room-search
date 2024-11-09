const fs = require('fs')
const path = require('path')

function generateSitemap(baseDir, baseUrl) {
  const urls = []

  // Recursively find all HTML files
  function findHtmlFiles(dir) {
    const files = fs.readdirSync(dir)
    files.forEach(file => {
      const fullPath = path.join(dir, file)
      const stats = fs.statSync(fullPath)
      if (stats.isDirectory()) {
        findHtmlFiles(fullPath)
      } else if (file.endsWith('.html')) {
        // Get the relative path of the HTML file and convert it to a URL format
        const relativePath = path.relative(baseDir, fullPath).replace(/\\/g, '/')
        const url = `${baseUrl}/${relativePath}`
        urls.push(url)
      }
    })
  }

  // Start scanning from the base directory
  findHtmlFiles(baseDir)

  // Construct the XML for the sitemap
  let sitemap = `<?xml version="1.0" encoding="UTF-8"?>\n`
  sitemap += `<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n`

  urls.forEach(url => {
    sitemap += `  <url>\n`
    sitemap += `    <loc>${url}</loc>\n`
    sitemap += `  </url>\n`
  })

  sitemap += `</urlset>`

  // Save the sitemap to the base directory or any other directory you prefer
  fs.writeFileSync(path.join(baseDir, 'sitemap.xml'), sitemap)
  console.log('Sitemap generated: sitemap.xml')
}

// Usage example
generateSitemap('./', 'https://search-matrix-rooms.denieler.com')
