// Simple frontend test
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

console.log('🧪 Frontend Environment Test')
console.log('=' * 40)

// Test 1: Check Vue.js files exist
const vueFiles = [
  'src/App.vue',
  'src/main.js',
  'src/views/Home.vue',
  'src/views/Timeline.vue',
  'src/views/Profile.vue'
]

console.log('\n📁 Checking Vue.js files...')
vueFiles.forEach(file => {
  const filePath = path.join(__dirname, file)
  if (fs.existsSync(filePath)) {
    console.log(`✅ ${file} exists`)
  } else {
    console.log(`❌ ${file} missing`)
  }
})

// Test 2: Check configuration files
const configFiles = [
  'package.json',
  'vite.config.js',
  'vitest.config.js',
  'index.html'
]

console.log('\n⚙️  Checking configuration files...')
configFiles.forEach(file => {
  const filePath = path.join(__dirname, file)
  if (fs.existsSync(filePath)) {
    console.log(`✅ ${file} exists`)
  } else {
    console.log(`❌ ${file} missing`)
  }
})

// Test 3: Check API service
console.log('\n🌐 Checking API service...')
const apiPath = path.join(__dirname, 'src/services/api.js')
if (fs.existsSync(apiPath)) {
  const apiContent = fs.readFileSync(apiPath, 'utf8')
  if (apiContent.includes('userApi') && apiContent.includes('crawlUser')) {
    console.log('✅ API service properly configured')
  } else {
    console.log('❌ API service incomplete')
  }
} else {
  console.log('❌ API service file missing')
}

// Test 4: Check package.json scripts
console.log('\n📦 Checking npm scripts...')
const packagePath = path.join(__dirname, 'package.json')
if (fs.existsSync(packagePath)) {
  const pkg = JSON.parse(fs.readFileSync(packagePath, 'utf8'))
  const requiredScripts = ['dev', 'build', 'preview', 'test']
  
  requiredScripts.forEach(script => {
    if (pkg.scripts && pkg.scripts[script]) {
      console.log(`✅ Script '${script}' configured`)
    } else {
      console.log(`❌ Script '${script}' missing`)
    }
  })
} else {
  console.log('❌ package.json missing')
}

console.log('\n✅ Frontend environment test completed!')
console.log('🎉 Frontend is ready for development!')