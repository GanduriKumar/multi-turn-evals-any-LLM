// MetricsBreakdownPage fallback (module not found)
import './App.css'
import ResultsViewer from './components/ResultsViewer'
import { useState } from 'react'
import { BrowserRouter, Link, Route, Routes, Navigate } from 'react-router-dom'
import DatasetsPage from './pages/DatasetsPage'
import RunSetupPage from './pages/RunSetupPage'
import RunDashboardPage from './pages/RunDashboardPage'
import MetricsBreakdownPage from './pages/MetricsBreakdownPage'
import ConversationDetailPage from './pages/ConversationDetailPage'
import RunComparisonPage from './pages/RunComparisonPage'
import Layout from './components/layout/Layout'

 

function App() {
  const [runId, setRunId] = useState('')

  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/datasets" replace />} />
          <Route path="/datasets" element={<DatasetsPage />} />
          <Route path="/run-setup" element={<RunSetupPage />} />
          <Route path="/dashboard/:runId" element={<RunDashboardPage />} />
          <Route path="/conversation/:runId/:conversationId" element={<ConversationDetailPage />} />
          <Route path="/metrics/:runId" element={<MetricsBreakdownPage />} />
          <Route path="/compare" element={<RunComparisonPage />} />
          <Route path="/reports" element={<div className="p-8 text-center text-gray-500">Reports Page Placeholder</div>} />
          <Route
            path="/viewer"
            element={
              <div>
                <div className="mb-4 bg-gray-100 p-4 rounded">
                  <label className="flex gap-3 items-center">
                    <strong>Run ID:</strong>
                    <input
                      className="border rounded p-2 max-w-md w-full"
                      value={runId}
                      onChange={(e) => setRunId(e.target.value)}
                      placeholder="Enter run ID (e.g. run-20240101...)"
                    />
                  </label>
                </div>
                <ResultsViewer runId={runId} />
              </div>
            }
          />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}

export default App
