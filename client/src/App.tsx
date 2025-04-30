import { useState } from 'react'
import reactLogo from './assets/react.svg'
import './App.css'

function App() {
  const [measured, setMeasured] = useState("measure")

  return (
    <>
      <div>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <div className="card">
        <button onClick={() => setMeasured((measured) => {
         if (measured == "measure") 
            return "measured"
         else 
            return "measure"   
          })}>
          {measured}
        </button>
      </div>
    </>
  )
}

export default App
