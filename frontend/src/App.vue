<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <nav class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <router-link to="/" class="text-xl font-bold text-gray-800">
              User Profiler
            </router-link>
          </div>
          <div class="flex items-center space-x-4">
            <router-link 
              to="/" 
              class="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md"
            >
              Home
            </router-link>
            <router-link 
              to="/logs" 
              class="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md"
            >
              📋 Logs
            </router-link>
          </div>
        </div>
      </div>
    </nav>
    
    <main class="max-w-7xl mx-auto py-6 px-4">
      <router-view />
    </main>
    
    <footer class="bg-white border-t mt-12">
      <div class="max-w-7xl mx-auto py-4 px-4 text-center text-gray-600">
        <p>&copy; 2024 User Profiler System. Built with Vue.js and Python.</p>
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>