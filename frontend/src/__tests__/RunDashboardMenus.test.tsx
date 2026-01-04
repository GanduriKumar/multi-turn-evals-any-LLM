import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import RunDashboardPage from '../pages/RunDashboardPage'

function setup(onRunAction?: any, onAbortAction?: any) {
  render(
    <MemoryRouter initialEntries={["/dashboard/run-1"]}>
      <Routes>
        <Route path="/dashboard/:runId" element={<RunDashboardPage onRunAction={onRunAction} onAbortAction={onAbortAction} />} />
      </Routes>
    </MemoryRouter>
  )
}

describe('RunDashboard menus', () => {
  it('invokes onRunAction when selecting Pause/Resume', async () => {
    const onRun = vi.fn()
    setup(onRun)
    // Open Pause menu
    fireEvent.click(screen.getByRole('button', { name: /Pause/i }))
    // Click Pause Now item
    fireEvent.click(screen.getByRole('menuitem', { name: /Pause Now/i }))
    expect(onRun).toHaveBeenCalledWith('pause')

    // Re-open and click Resume
    fireEvent.click(screen.getByRole('button', { name: /Pause/i }))
    fireEvent.click(screen.getByRole('menuitem', { name: /Resume/i }))
    expect(onRun).toHaveBeenCalledWith('resume')
  })

  it('invokes onAbortAction when selecting Abort options', async () => {
    const onAbort = vi.fn()
    setup(undefined, onAbort)
    fireEvent.click(screen.getByRole('button', { name: /Abort/i }))
    fireEvent.click(screen.getByRole('menuitem', { name: /Abort Job/i }))
    expect(onAbort).toHaveBeenCalledWith('abort')

    fireEvent.click(screen.getByRole('button', { name: /Abort/i }))
    fireEvent.click(screen.getByRole('menuitem', { name: /Abort & Delete Artifacts/i }))
    expect(onAbort).toHaveBeenCalledWith('abort_delete')
  })
})
