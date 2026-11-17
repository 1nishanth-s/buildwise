import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from '../App';
import { BuildDetails } from '../pages/BuildDetails';
import { UpgradeDetails } from '../pages/UpgradeDetails';
import { Sidebar } from '../components/layout/Sidebar';

describe('BuildWise-AI Frontend Tests', () => {
  it('1. Renders App navigation and verifies sidebar is strictly navigation-only', () => {
    render(<App />);

    // Sidebar navigation items
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Build a PC')).toBeInTheDocument();
    expect(screen.getByText('Upgrade a PC')).toBeInTheDocument();
    expect(screen.getByText('My Builds')).toBeInTheDocument();
    expect(screen.getByText('My Upgrades')).toBeInTheDocument();
    expect(screen.getByText('History')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();

    // Verify absence of manual component library / dragging palette in sidebar
    expect(screen.queryByText('Component Library')).not.toBeInTheDocument();
    expect(screen.queryByText('Drag to Canvas')).not.toBeInTheDocument();
  });

  it('2. Verifies Build Mode contains EXACTLY TWO user inputs (Primary Usage and Total Budget)', () => {
    render(
      <MemoryRouter>
        <BuildDetails />
      </MemoryRouter>
    );

    // Input 1: Primary Usage
    expect(screen.getByText('1. Primary Usage')).toBeInTheDocument();
    expect(screen.getAllByText('Gaming').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('Content Creation / Video Editing')).toBeInTheDocument();
    expect(screen.getByText('Productivity / Workstation')).toBeInTheDocument();

    // Input 2: Total Budget
    expect(screen.getByText('2. Total Budget (INR)')).toBeInTheDocument();
    const budgetInput = screen.getByLabelText(/Total Budget/i);
    expect(budgetInput).toBeInTheDocument();

    // Ensure NO unnecessary component selection or brand dropdowns exist
    expect(screen.queryByText('Select Processor')).not.toBeInTheDocument();
    expect(screen.queryByText('Preferred Brand')).not.toBeInTheDocument();
    expect(screen.queryByText('Select Motherboard')).not.toBeInTheDocument();
    expect(screen.queryByText('Select GPU')).not.toBeInTheDocument();

    // Submit button
    expect(screen.getByRole('button', { name: /Generate My PC Build/i })).toBeInTheDocument();
  });

  it('3. Verifies Build Mode budget validation and usage selection', () => {
    render(
      <MemoryRouter>
        <BuildDetails />
      </MemoryRouter>
    );

    const budgetInput = screen.getByLabelText(/Total Budget/i) as HTMLInputElement;
    const submitBtn = screen.getByRole('button', { name: /Generate My PC Build/i });

    // Select usage
    const workstationBtn = screen.getByText('Productivity / Workstation');
    fireEvent.click(workstationBtn);

    // Invalid budget < 18,000
    fireEvent.change(budgetInput, { target: { value: '10000' } });
    expect(screen.getByText(/Minimum viable budget for a complete PC/i)).toBeInTheDocument();
    expect(submitBtn).toBeDisabled();

    // Valid budget >= 18,000
    fireEvent.change(budgetInput, { target: { value: '75000' } });
    expect(submitBtn).not.toBeDisabled();
  });

  it('4. Verifies Upgrade Mode renders existing hardware fields, budget, and goal selector', () => {
    render(
      <MemoryRouter>
        <UpgradeDetails />
      </MemoryRouter>
    );

    // Existing hardware section
    expect(screen.getByText(/Current PC Hardware Configuration/i)).toBeInTheDocument();
    expect(screen.getByText('Processor (CPU)')).toBeInTheDocument();
    expect(screen.getByText('Graphics Card (GPU)')).toBeInTheDocument();
    expect(screen.getByText('Motherboard')).toBeInTheDocument();
    expect(screen.getByText('RAM Memory')).toBeInTheDocument();
    expect(screen.getByText('Power Supply Unit (PSU)')).toBeInTheDocument();

    // Upgrade Goal options
    expect(screen.getByText('Upgrade Goal')).toBeInTheDocument();
    expect(screen.getByText('Better Gaming Performance')).toBeInTheDocument();
    expect(screen.getByText('Higher FPS in Esports Titles')).toBeInTheDocument();

    // Upgrade Budget
    expect(screen.getByLabelText(/Upgrade Budget/i)).toBeInTheDocument();

    // Action button
    expect(
      screen.getByRole('button', { name: /Analyze My PC and Recommend Upgrades/i })
    ).toBeInTheDocument();
  });

  it('5. Verifies Global AI Disclaimer appears on every page with exact text', () => {
    render(<App />);

    const disclaimer = screen.getByTestId('global-ai-disclaimer');
    expect(disclaimer).toBeInTheDocument();
    expect(disclaimer).toHaveTextContent(
      'AI-generated recommendations may contain mistakes. Please verify component specifications, compatibility, prices and availability before purchasing.'
    );
  });

  it('6. Verifies top-right quick-action buttons are removed from Navbar', () => {
    render(<App />);

    // Verify "+ Build PC" and "↻ Upgrade PC" quick action buttons are NOT present in header navbar
    expect(screen.queryByRole('link', { name: /\+ Build PC/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('link', { name: /↻ Upgrade PC/i })).not.toBeInTheDocument();
  });
});
