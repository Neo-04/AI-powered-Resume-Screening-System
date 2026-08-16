import HomePage from './pages/HomePage'
import { useScreeningWorkflow } from './hooks/useScreeningWorkflow'

function App() {
  const workflow = useScreeningWorkflow()

  return (
    <main>
      <HomePage workflow={workflow} />
    </main>
  )
}

export default App
