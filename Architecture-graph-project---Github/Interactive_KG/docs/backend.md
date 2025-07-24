# Backend Documentation

This document provides detailed technical documentation for the backend implementation of the Knowledge Graph Visualizer, focusing on the `HierarchicalKnowledgeGraph` class and its core functionalities.

## HierarchicalKnowledgeGraph Class

### Class Overview

The `HierarchicalKnowledgeGraph` class serves as the core backend component, managing the graph data structure and providing methods for data manipulation and visualization. It utilizes NetworkX for graph operations and Pandas for data handling.

### Class Constructor

```python
def __init__(self, excel_file):
    self.df = pd.read_excel(excel_file)
    self.G = nx.Graph()
    self.load_initial_graph()
    self.visible_nodes = set()
    self.visible_edges = set()
```

#### Parameters
- `excel_file`: Excel file containing the graph data with columns:
  - `node`: Unique identifier for each node
  - `parent`: Parent node identifier
  - `type`: Node type (lead, member, child)
  - `relationship`: Edge relationship type

#### Instance Variables
- `df`: Pandas DataFrame containing the raw graph data
- `G`: NetworkX Graph object storing the graph structure
- `visible_nodes`: Set tracking currently visible nodes
- `visible_edges`: Set tracking currently visible edges

### Core Methods

#### load_initial_graph()

```python
def load_initial_graph(self):
    """
    Load the initial graph structure from the Excel data.
    Creates nodes and edges based on the data relationships.
    
    Notes:
        - Automatically called during initialization
        - Creates the NetworkX graph structure
        - Sets node types and relationship attributes
    """
```

#### get_graph_data()

```python
def get_graph_data(self, start_node=None, end_node=None, visible_relationships=None, filter_node=None):
    """
    Get the filtered graph data based on various parameters.

    Args:
        start_node (str, optional): Starting node for path filtering
        end_node (str, optional): Ending node for path filtering
        visible_relationships (list, optional): List of relationship types to show
        filter_node (str, optional): Single node to filter on

    Returns:
        dict: Dictionary containing:
            - nodes: List of node dictionaries with properties:
                - id: Node identifier
                - type: Node type
                - size: Visual size
                - visible: Visibility flag
            - links: List of edge dictionaries with properties:
                - source: Source node id
                - target: Target node id
                - relationship: Edge relationship type
                - visible: Visibility flag
    """
```

#### expand_node()

```python
def expand_node(self, node, visible_relationships=None):
    """
    Expand a node to show its connections.

    Args:
        node (str): Node identifier to expand
        visible_relationships (list, optional): List of relationship types to show

    Returns:
        dict: Dictionary containing new nodes and links data
            - nodes: List of newly visible nodes
            - links: List of newly visible links
    """
```

### Helper Methods

#### get_node_options()

```python
def get_node_options(self):
    """
    Get list of all node identifiers.

    Returns:
        list: Sorted list of node identifiers
    """
```

#### get_relationship_types()

```python
def get_relationship_types(self):
    """
    Get list of all relationship types in the graph.

    Returns:
        list: Sorted list of unique relationship types
    """
```




## Data Structure  - Supplement

### Graph Structure
- Undirected graph using NetworkX
- Nodes store:
  - Type information (lead, member, child)
  - Visibility state
- Edges store:
  - Relationship type
  - Visibility state

### Visibility Management
- Nodes and edges maintain separate visibility states
- Visibility can be controlled through:
  - Path filtering between nodes
  - Single node filtering
  - Relationship type filtering

## Implementation Details

### Path Finding
- Uses NetworkX's `all_simple_paths` for finding paths between nodes
- Handles cases where no path exists between selected nodes
- Updates visibility states based on path results

### Node Expansion
- Implements neighborhood exploration
- Updates visibility states for new nodes and edges
- Maintains relationship filtering during expansion

### Performance Considerations
- Uses sets for efficient visibility tracking
- Maintains graph structure in memory
- Implements efficient filtering mechanisms

## Integration Points

### Data Input
- Accepts Excel files with required column structure
- Validates data during graph construction
- Handles missing or invalid data gracefully

### Frontend Integration
- Provides data in D3.js-compatible format
- Supports interactive graph manipulation
- Maintains state consistency with frontend

## Examples

### Basic Usage

```python
# Initialize the graph
graph = HierarchicalKnowledgeGraph("data.xlsx")

# Get complete graph data
data = graph.get_graph_data()

# Filter by relationship type
filtered_data = graph.get_graph_data(visible_relationships=["manages", "reports_to"])

# Find paths between nodes
path_data = graph.get_graph_data(start_node="Node1", end_node="Node2")
```

### Node Expansion

```python
# Expand a specific node
expanded_data = graph.expand_node("Node1", visible_relationships=["manages"])
