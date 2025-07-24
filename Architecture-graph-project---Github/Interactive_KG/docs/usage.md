# Usage Guide - How to use the application

## Quick Start Tutorial

### First Steps
1. Launch the application
2. Upload your Excel file
3. Explore the initial graph visualization
4. Try basic interactions (zoom, drag, click)

## Data Preparation

### Excel File Requirements

#### Required Columns
- `node`: Unique identifier for each node
- `parent`: Identifier of the parent node (can be empty for root nodes)
- `type`: Node type (lead, member, or child)
- `relationship`: Description of the relationship between the node and its parent

#### Data Validation Rules
- Node IDs must be unique
- Parent nodes must exist in the dataset
- Node types must be one of: lead, member, child
- Relationships should be meaningful and consistent

### Example Dataset

| node    | parent  | type   | relationship | description        |
|---------|---------|--------|--------------|-------------------|
| Team A  | null    | lead   | null         | Main team         |
| Bob     | Team A  | member | reports_to   | Team leader      |
| Project1| Bob     | child  | manages      | Active project   |

## Using the Application

### Starting the Application

1. Navigate to your project directory
2. Run the Streamlit application:
```bash
streamlit run interactive_kg.py.py
```
3. Open your web browser to `http://localhost:8501`

### Interface Overview

The application interface is divided into two main sections:

1. **Left Panel**: Control panel for graph manipulation
2. **Right Panel**: Interactive graph visualization

## Control Panel Features

### Node Filter

Filter the graph to focus on specific nodes:

1. Select a node from the "Filter Single Node" dropdown
2. Click "Apply Node Filter" to update the visualization
3. Only the selected node and its direct connections will be shown

### Path Filter

Visualize paths between two nodes:

1. Select a starting node from "Start Node" dropdown
2. Select an ending node from "End Node" dropdown
3. Click "Apply Filters" to show all paths between the selected nodes

### Relationship Filter

Control which types of relationships are displayed:

1. Use the "Visible Relationships" multi-select to choose relationship types
2. All selected relationship types will be shown in the graph
3. Deselected relationships will be hidden

### Color Settings

Customize the appearance of different node types:

1. Use color pickers to set colors for:
   - Lead Node Color
   - Member Node Color
   - Child Node Color
2. Changes are applied immediately to the visualization

## Interactive Visualization

### Basic Interactions

- **Drag Nodes**: Click and drag to reposition nodes
- **Zoom**: Use mouse wheel to zoom in/out
- **Pan**: Click and drag the background to move the entire graph
- **Double-Click**: Double-click a node to expand its connections

### Node Types

The visualization uses different colors and sizes for different node types:

- **Lead Nodes**: Largest size, default color red
- **Member Nodes**: Medium size, default color teal
- **Child Nodes**: Smallest size, default color blue

### Relationship Display

Relationships are shown as:

- Directed arrows between nodes
- Labels on the arrows indicating relationship type
- Different arrow colors for visual distinction

## Exporting Results

### Export Options

The visualization can be exported in two formats:

1. **SVG Format**
   - Click "Download SVG" button
   - Vector format, suitable for scaling
   - Editable in vector graphics software

2. **PNG Format**
   - Click "Download PNG" button
   - Raster format, suitable for direct use
   - Fixed resolution




