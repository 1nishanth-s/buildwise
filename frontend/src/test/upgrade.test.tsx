import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { ReactFlowProvider } from '@xyflow/react';
import { PropertiesPanel } from '../components/panels/PropertiesPanel';
import { WorkflowNode } from '../components/nodes/WorkflowNode';
import { WorkflowCanvas } from '../pages/WorkflowCanvas';
import { api } from '../services/api';

describe('Phase 13: Multi-Component Upgrade Frontend Tests', () => {
  it('1. WorkflowNode renders PRIMARY UPGRADE, REQUIRED DEPENDENCY, and RETAINED badges with proper styling', () => {
    // 1A. Primary GPU node
    const primaryNodeProps: any = {
      id: 'n-gpu',
      data: {
        kind: 'component',
        category: 'gpu',
        label: 'NVIDIA RTX 4070 Super',
        subtitle: '12GB GDDR6X',
        status: 'recommended',
        price: 58999,
        upgrade_role: 'primary',
      },
      selected: false,
      type: 'workflowNode',
    };

    const { unmount } = render(
      <ReactFlowProvider>
        <WorkflowNode {...primaryNodeProps} />
      </ReactFlowProvider>
    );
    expect(screen.getByText('NVIDIA RTX 4070 Super')).toBeInTheDocument();
    expect(screen.getByText('Primary Upgrade')).toBeInTheDocument();
    expect(screen.getByText('₹58,999')).toBeInTheDocument();
    unmount();

    // 1B. Required Dependent PSU node
    const dependentNodeProps: any = {
      id: 'n-psu',
      data: {
        kind: 'component',
        category: 'psu',
        label: 'Corsair RM750e 750W 80+ Gold',
        subtitle: '750W Fully Modular',
        status: 'dependency',
        price: 7999,
        upgrade_role: 'dependency',
        dependency_reason: 'Required replacement: 450W PSU cannot power RTX 4070 Super (requires >= 650W)',
      },
      selected: false,
      type: 'workflowNode',
    };

    const { unmount: unmountDep } = render(
      <ReactFlowProvider>
        <WorkflowNode {...dependentNodeProps} />
      </ReactFlowProvider>
    );
    expect(screen.getByText('Corsair RM750e 750W 80+ Gold')).toBeInTheDocument();
    expect(screen.getByText('Required Dependency')).toBeInTheDocument();
    expect(screen.getByText('₹7,999')).toBeInTheDocument();
    unmountDep();

    // 1C. Retained CPU node at Rs 0
    const retainedNodeProps: any = {
      id: 'n-cpu',
      data: {
        kind: 'component',
        category: 'cpu',
        label: 'AMD Ryzen 5 3600',
        subtitle: '6-Core AM4 Processor',
        status: 'reusable',
        price: 0,
        upgrade_role: 'retained',
      },
      selected: false,
      type: 'workflowNode',
    };

    render(
      <ReactFlowProvider>
        <WorkflowNode {...retainedNodeProps} />
      </ReactFlowProvider>
    );
    expect(screen.getByText('AMD Ryzen 5 3600')).toBeInTheDocument();
    expect(screen.getByText('Retained')).toBeInTheDocument();
    expect(screen.getByText('₹0 (Kept)')).toBeInTheDocument();
  });

  it('2. PropertiesPanel displays Required Dependency Reason and installed hardware baseline', () => {
    const dependentData = {
      kind: 'component' as const,
      category: 'psu' as const,
      label: 'Corsair RM750e 750W 80+ Gold',
      subtitle: 'ATX 3.0 Power Supply',
      price: 7999,
      seller: 'MD Computers',
      priceBasis: 'Verified retailer observation',
      availability: 'available',
      upgrade_role: 'dependency' as const,
      dependency_reason: 'Required replacement: Insufficient PSU capacity. Proposed GPU requires 650W, installed is 450W.',
      baseline_name: 'Corsair CV450 450W (Existing)',
      specs: {
        wattage_w: 750,
        efficiency: '80 Plus Gold',
        modular: 'Fully Modular',
      },
      alternatives: [
        {
          id: 'psu-tt-750',
          name: 'Thermaltake Toughpower GF1 750W',
          brand: 'Thermaltake',
          price: 7499,
          specs: { wattage_w: 750 },
        },
      ],
    };

    const mockReplace = vi.fn();
    const mockClose = vi.fn();

    render(
      <PropertiesPanel
        nodeData={dependentData}
        onClose={mockClose}
        onReplaceComponent={mockReplace}
      />
    );

    // Component classification pill
    expect(screen.getByText('Required Dependency')).toBeInTheDocument();

    // Dependency Reason Alert Box
    expect(screen.getByText('Required Dependency Reason')).toBeInTheDocument();
    expect(
      screen.getByText('Required replacement: Insufficient PSU capacity. Proposed GPU requires 650W, installed is 450W.')
    ).toBeInTheDocument();

    // Installed hardware display
    expect(screen.getByText('Current Installed')).toBeInTheDocument();
    expect(screen.getByText('Corsair CV450 450W (Existing)')).toBeInTheDocument();

    // Price
    expect(screen.getByText('₹7,999')).toBeInTheDocument();
  });

  it('3. PropertiesPanel displays Retained Component at Rs 0 cost without seller quote', () => {
    const retainedData = {
      kind: 'component' as const,
      category: 'ram' as const,
      label: 'Corsair Vengeance LPX 16GB (2x8GB) DDR4',
      subtitle: 'Installed DDR4-3200 Memory',
      price: 0,
      seller: 'Installed Hardware',
      priceBasis: 'Original hardware',
      availability: 'installed',
      upgrade_role: 'retained' as const,
      baseline_name: 'Corsair Vengeance LPX 16GB',
    };

    render(
      <PropertiesPanel
        nodeData={retainedData}
        onClose={vi.fn()}
        onReplaceComponent={vi.fn()}
      />
    );

    expect(screen.getByText('Retained Component')).toBeInTheDocument();
    expect(screen.getByText('Retained Cost')).toBeInTheDocument();
    expect(screen.getByText('₹0 (Installed)')).toBeInTheDocument();
    expect(screen.queryByText('Required Dependency Reason')).not.toBeInTheDocument();
  });

  it('4. WorkflowCanvas renders multi-component upgrade budget tracking and over-budget warning', async () => {
    const mockUpgradeProject = {
      id: 'p_test_upgrade_canvas_01',
      mode: 'upgrade',
      name: 'Gaming GPU & PSU Upgrade · Rs 45,000',
      createdAt: '2026-11-16T08:00:00Z',
      inputs: {
        existingHardware: { cpu: 'Ryzen 5 3600', gpu: 'GTX 1650', psu: '450W' },
        budget: 45000,
        goal: 'Better Gaming Performance',
      },
      summary: {
        total: 52000,
        budget: 45000,
        remaining: -7000,
        status: 'warning',
        primaryCategories: ['gpu'],
        dependentCategories: ['psu'],
        retainedCategories: ['cpu', 'motherboard', 'ram', 'storage'],
        notes: ['Plan exceeds budget by ₹7,000. All required dependencies were retained for hardware safety.'],
      },
      recommendationSnapshot: {
        components: {
          gpu: { category: 'gpu', name: 'RTX 4070 Super', price: 44000, upgrade_role: 'primary' },
          psu: { category: 'psu', name: '750W Gold PSU', price: 8000, upgrade_role: 'dependency' },
        },
      },
      nodes: [
        {
          id: 'n-gpu',
          type: 'workflowNode',
          position: { x: 100, y: 100 },
          data: {
            kind: 'component',
            category: 'gpu',
            label: 'RTX 4070 Super',
            price: 44000,
            status: 'recommended',
            upgrade_role: 'primary',
          },
        },
      ],
      edges: [],
    };

    vi.spyOn(api, 'getProject').mockResolvedValue(mockUpgradeProject as any);

    render(
      <MemoryRouter initialEntries={['/workflow/p_test_upgrade_canvas_01']}>
        <Routes>
          <Route path="/workflow/:id" element={<WorkflowCanvas />} />
        </Routes>
      </MemoryRouter>
    );

    // Verify project name in header
    expect(await screen.findByText('Gaming GPU & PSU Upgrade · Rs 45,000')).toBeInTheDocument();

    // Verify budget tracking values in header
    expect(screen.getByText('₹52,000')).toBeInTheDocument(); // Total
    expect(screen.getByText('₹45,000')).toBeInTheDocument(); // Budget
    expect(screen.getByText('₹-7,000')).toBeInTheDocument(); // Remaining (negative)

    // Verify Review Needed status
    expect(screen.getByText('Review Needed')).toBeInTheDocument();
  });

  it('5. PropertiesPanel component swap invokes replace handler with proper category and component ID', () => {
    const mockData = {
      kind: 'component' as const,
      category: 'gpu' as const,
      label: 'AMD Radeon RX 7600',
      subtitle: '8GB GDDR6',
      price: 26000,
      seller: 'MD Computers',
      priceBasis: 'Verified retailer observation',
      availability: 'available',
      upgrade_role: 'primary' as const,
      specs: { vram_gb: 8, tgp_w: 165 },
      alternatives: [
        {
          id: 'gpu_rtx_4060',
          name: 'NVIDIA GeForce RTX 4060',
          brand: 'NVIDIA',
          price: 28000,
          specs: { vram_gb: 8, tgp_w: 115 },
        },
      ],
    };

    const mockReplace = vi.fn();
    const mockClose = vi.fn();

    render(
      <PropertiesPanel
        nodeData={mockData}
        onClose={mockClose}
        onReplaceComponent={mockReplace}
      />
    );

    expect(screen.getByText('AMD Radeon RX 7600')).toBeInTheDocument();
    expect(screen.getByText('Primary Upgrade')).toBeInTheDocument();

    // Expand alternatives drawer
    const altToggle = screen.getByText(/Compatible Alternatives/i);
    fireEvent.click(altToggle);

    expect(screen.getByText('NVIDIA GeForce RTX 4060')).toBeInTheDocument();
    expect(screen.getByText('₹28,000')).toBeInTheDocument();

    // Trigger swap
    const swapBtn = screen.getByRole('button', { name: /Swap This Component/i });
    fireEvent.click(swapBtn);

    expect(mockReplace).toHaveBeenCalledWith('gpu', 'gpu_rtx_4060');
  });
});
