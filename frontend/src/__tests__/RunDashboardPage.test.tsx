import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import RunDashboardPage from '../pages/RunDashboardPage';

describe('RunDashboardPage', () => {
  it('renders the dashboard layout with all panels', async () => {
    render(
      <MemoryRouter initialEntries={["/dashboard/run-123"]}>
        <Routes>
          <Route path="/dashboard/:runId" element={<RunDashboardPage />} />
        </Routes>
      </MemoryRouter>
    );

    // Check for main header
    expect(screen.getByText(/Multi-Turn LLM Evaluation/i)).toBeInTheDocument();
    expect(screen.getByText(/Evaluated #run-123/i)).toBeInTheDocument();

    // Check for panels
    expect(screen.getByText('Define Test Scenarios')).toBeInTheDocument();
    expect(screen.getByText('LLM Configuration')).toBeInTheDocument();
    expect(screen.getByText('Metrics Selection')).toBeInTheDocument();
    expect(screen.getByText('Run Control')).toBeInTheDocument();
    expect(screen.getByText('Turn Control')).toBeInTheDocument();
    // Turn Review label is now part of a menu button text "Turn Review ▾"
    expect(screen.getByRole('button', { name: /Turn Review/i })).toBeInTheDocument();

    // Check for specific content in panels
    expect(screen.getAllByText('Gemini 1.5 Pro')[0]).toBeInTheDocument();
    expect(screen.getByText('Completeness')).toBeInTheDocument();
    expect(screen.getByText('Running Tests')).toBeInTheDocument();
  });
});