/// import { useState } from 'react'

import './App.css'
import Hero from './components/Hero'
import SearchBar from './components/SearchBar'
import ResultSummary from './components/ResultSummary'

function App() {

  const handleSearch = (query: string) => {
    console.log("Search query:", query)

  }

  return (
    // <>
    //   <Hero />
    //   <div>
    //     <SearchBar onSearch={handleSearch} />
    //   </div>
    //   <ResultSummary />
    // </>

//     <div className="app-container">
// +      <Hero />
// +      <main className="main-content">
// +        <SearchBar onSearch={handleSearch} />
// +        <ResultSummary />
// +      </main>
// +    </div>

    <div className="app-container">
+      <Hero />
+      <div className="search-wrapper">
+        <SearchBar onSearch={handleSearch} />
+      </div>
+
+      <ResultSummary />
+    </div>
  )
}

export default App
