import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { PropertiesPanel } from '../components/panels/PropertiesPanel';
import { WorkflowNode } from '../components/nodes/WorkflowNode';
import { ReactFlowProvider } from '@xyflow/react';

describe('Workflow Canvas & Properties Panel Tests', () => {
  it('1. PropertiesPanel displays hardware specs, price, seller, and ML predictions', () => {
    const mockData = {
      kind: 'component' as const,
      category: 'cpu' as const,
      label: 'AMD Ryzen 5 7600',
      subtitle: 'AMD AM5 Processor',
      price: 18999,
      seller: 'MD Computers',
      priceBasis: 'Verified retailer observation',
      availability: 'available',
      specs: {
        cores: 6,
        threads: 12,
        socket: 'AM5',
        tdp_w: 65,
      },
      reason: 'Optimal mid-tier gaming processor with high IPC.',
      mlPrediction: {
        metric: 'Predicted Cinebench R23 Multi-Core',
        score: 14500,
        status: 'success' as const,
      },
      empiricalBenchmark: {
        metric: 'Cinebench R23 Multi-Core',
        score: 14200,
        source: 'Lab benchmark',
      },
      alternatives: [
        {
          id: 'cpu-r7-7700x',
          name: 'AMD Ryzen 7 7700X',
          brand: 'AMD',
          price: 28500,
          specs: { cores: 8, threads: 16 },
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

    // Verify component info
    expect(screen.getByText('AMD Ryzen 5 7600')).toBeInTheDocument();
    expect(screen.getByText('₹18,999')).toBeInTheDocument();
    expect(screen.getByText('MD Computers')).toBeInTheDocument();
    expect(screen.getByText('Verified retailer observation')).toBeInTheDocument();

    // Verify ML estimate and empirical benchmark
    expect(screen.getByText('14,500 pts')).toBeInTheDocument();
    expect(screen.getByText('14,200 pts')).toBeInTheDocument();

    // Verify reason
    expect(screen.getByText(/Optimal mid-tier gaming processor/i)).toBeInTheDocument();

    // Expand alternatives drawer
    const altToggle = screen.getByText(/Compatible Alternatives/i);
    fireEvent.click(altToggle);

    expect(screen.getByText('AMD Ryzen 7 7700X')).toBeInTheDocument();
    expect(screen.getByText('₹28,500')).toBeInTheDocument();

    // Trigger swap
    const swapBtn = screen.getByRole('button', { name: /Swap This Component/i });
    fireEvent.click(swapBtn);
    expect(mockReplace).toHaveBeenCalledWith('cpu', 'cpu-r7-7700x');
  });

  it('2. WorkflowNode renders compact status badge, price, and handles', () => {
    const mockNodeProps: any = {
      id: 'n-gpu',
      data: {
        kind: 'component',
        category: 'gpu',
        label: 'NVIDIA RTX 4070 Super',
        subtitle: '12GB GDDR6X',
        status: 'recommended',
        price: 58999,
        specs: { vram_gb: 12 },
        mlPrediction: {
          metric: 'Predicted Time Spy Graphics',
          score: 21200,
          status: 'success',
        },
      },
      selected: false,
      type: 'workflowNode',
      zIndex: 1,
      isConnectable: true,
      xPos: 0,
      yPos: 0,
      dragging: false,
    };

    render(
      <ReactFlowProvider>
        <WorkflowNode {...mockNodeProps} />
      </ReactFlowProvider>
    );

    expect(screen.getByText('NVIDIA RTX 4070 Super')).toBeInTheDocument();
    expect(screen.getByText('12GB GDDR6X')).toBeInTheDocument();
    expect(screen.getByText('₹58,999')).toBeInTheDocument();
    expect(screen.getByText(/21,200 pts/i)).toBeInTheDocument();
    expect(screen.getByText(/Recommended/i)).toBeInTheDocument();
    // Compatibility badge
    expect(screen.getByText('Compatible')).toBeInTheDocument();
  });

  it('3. WorkflowNode removes why-selected description paragraphs from component canvas cards', () => {
    const mockNodeProps: any = {
      id: 'n-cpu',
      data: {
        kind: 'component',
        category: 'cpu',
        label: 'AMD Ryzen 5 7600',
        subtitle: 'AM5 Processor',
        description: 'Why selected: High single-core speed optimal for gaming workloads.',
        status: 'recommended',
        price: 18999,
      },
      selected: false,
      type: 'workflowNode',
    };

    render(
      <ReactFlowProvider>
        <WorkflowNode {...mockNodeProps} />
      </ReactFlowProvider>
    );

    expect(screen.getByText('AMD Ryzen 5 7600')).toBeInTheDocument();
    expect(screen.queryByText(/Why selected: High single-core speed/i)).not.toBeInTheDocument();
  });
});
