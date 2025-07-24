# Interactive Knowledge Graph Visualizer

## Overview

The Interactive Knowledge Graph Visualizer is a Streamlit-based web application that allows users to create, visualize, and interact with hierarchical knowledge graphs from Excel data. The application provides an interactive D3.js visualization with filtering capabilities, customizable colors, and export options.

## Installation

### Prerequisites

```bash
pip install pandas networkx streamlit streamlit-components-v1
```

### Project Structure

```

knowledge_graph_visualizer/
docs/
├── index.md       # Overview, installation, quick start
├── usage.md       # User guide and features
├── backend.md     # Python backend documentation
└── frontend.md    # Streamlit & D3.js documentation
└── src/
    └── interactive_kg.py
```

### Getting Started

1. Clone the repository:
```bash
git clone https://github.com/yourusername/knowledge_graph_visualizer.git
cd knowledge_graph_visualizer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the application:
```bash
streamlit run src/interactive_kg.py
```

## Features at a Glance

- Interactive graph visualization using D3.js
- Excel-based data import
- Node filtering and path analysis
- Customizable node colors and relationships
- Export options (SVG, PNG)
- Real-time graph statistics
- Drag-and-drop node positioning
- Zoom and pan capabilities



## Quick Links

- [Usage Guide](usage.md) - Learn how to use the visualizer
- [Confluence problem description page](https://btsservice.atlassian.net/wiki/spaces/ADA/pages/6767509574/AD+Enterprise+Architecture+Model+Graph+Visualisation) 
- [GitHub Repository](https://github.com/frankedwardmorley/Architecture-graph-project---Github.git)

