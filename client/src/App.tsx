/// import { useState } from 'react'

import './App.css'
import Hero from './components/Hero'
import SearchBar from './components/SearchBar'

function App() {

  const handleSearch = (query: string) => {
    console.log("Search query:", query)

  }

  return (
    <>
      <Hero />
      <div>
        <SearchBar onSearch={handleSearch} />
      </div>
    </>
  )
}

export default App
