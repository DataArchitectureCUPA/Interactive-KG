# Frontend Documentation


## Streamlit Interface

### Overview
The Streamlit interface provides an intuitive, interactive way to visualize and manipulate knowledge graphs. The interface is designed with a focus on usability and responsiveness, leveraging Streamlit's native components for optimal performance.

### Page Configuration and Layout

#### Base Configuration
```python
st.set_page_config(
    page_title="Knowledge Graph Visualizer",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("Interactive Knowledge Graph Visualizer")
```

#### Layout Structure
The interface uses a two-column layout for optimal space utilization:
```python
left_col, right_col = st.columns([1, 3])
```

Key design decisions:
- Left column (1/4 width): Contains all interactive controls
- Right column (3/4 width): Dedicated to graph visualization
- Responsive design that adapts to different screen sizes

### Input Components

#### File Upload Section
```python
def handle_file_upload():
    excel_file = st.file_uploader(
        "Upload Excel file",
        type="xlsx",
        help="Upload an Excel file containing graph data"
    )
    
    if excel_file is not None:
        try:
            return HierarchicalKnowledgeGraph(excel_file)
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            st.write("Please ensure your Excel file has the correct format:")
            st.code("Required columns: node, parent, type, relationship")
            return None
```

Features:
- Restricted to .xlsx files
- Clear error messaging
- Format requirements display
- Immediate feedback on upload

#### Control Panel Organization

##### Node Control Section
```python
with left_col:
    st.header("Graph Controls")
    
    # Node Filter Section
    with st.expander("Node Filtering", expanded=True):
        st.subheader("Single Node Filter")
        node_options = kg.get_node_options()
        filter_node = st.selectbox(
            "Select Node",
            ["None"] + node_options,
            help="Filter graph to show only this node and its connections"
        )
        
        st.subheader("Path Filter")
        col1, col2 = st.columns(2)
        with col1:
            start_node = st.selectbox(
                "Start Node",
                node_options,
                help="Starting node for path"
            )
        with col2:
            end_node = st.selectbox(
                "End Node",
                node_options,
                help="Ending node for path"
            )
```


##### Relationship Controls
```python
with st.expander("Relationship Settings", expanded=True):
    # Relationship Filter
    relationship_types = kg.get_relationship_types()
    visible_relationships = st.multiselect(
        "Visible Relationships",
        relationship_types,
        default=relationship_types,
        help="Select which types of relationships to display"
    )
    
    # Relationship Display Settings
    st.checkbox(
        "Show relationship labels",
        value=True,
        key="show_labels",
        help="Toggle visibility of relationship labels on edges"
    )
```

Features:
- Multi-select functionality
- Default selection of all relationships
- Toggle controls for visual elements
- Clear labeling and help text

#### Visual Customization Panel
```python
with st.expander("Appearance Settings"):
    # Color Settings
    st.subheader("Node Colors")
    colors = {
        "lead": st.color_picker(
            "Lead Node Color",
            "#FF6B6B",
            help="Color for lead nodes"
        ),
        "member": st.color_picker(
            "Member Node Color",
            "#4ECDC4",
            help="Color for member nodes"
        ),
        "child": st.color_picker(
            "Child Node Color",
            "#45B7D1",
            help="Color for child nodes"
        )
    }
    
    # Size Settings
    st.subheader("Node Sizes")
    sizes = {
        "lead": st.slider("Lead Node Size", 20, 40, 30),
        "member": st.slider("Member Node Size", 15, 35, 25),
        "child": st.slider("Child Node Size", 10, 30, 20)
    }
```

Customization options:
- Color pickers for each node type
- Size controls with reasonable ranges
- Grouped settings for related properties
- Live preview of changes

### Interactive Features

#### Action Buttons
```python
with left_col:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Apply Filters", type="primary"):
            update_graph_visualization()
    with col2:
        if st.button("Reset Graph", type="secondary"):
            reset_graph_state()
```



#### Statistics and Information Display
```python
def display_graph_statistics(graph_data):
    with st.container():
        st.subheader("Graph Statistics")
        
        # Create metrics in two columns
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "Total Nodes",
                len(graph_data['nodes']),
                delta=f"{sum(1 for n in graph_data['nodes'] if n['visible'])} visible"
            )
        with col2:
            st.metric(
                "Total Relationships",
                len(graph_data['links']),
                delta=f"{sum(1 for l in graph_data['links'] if l['visible'])} visible"
            )
        
        # Additional statistics
        with st.expander("Detailed Statistics"):
            st.write("Node Types Distribution:")
            node_types = pd.DataFrame([n['type'] for n in graph_data['nodes']]).value_counts()
            st.bar_chart(node_types)
```



### State Management

#### Session State Handling
```python
def initialize_session_state():
    if 'graph_settings' not in st.session_state:
        st.session_state.graph_settings = {
            'filter_node': None,
            'visible_relationships': set(),
            'color_scheme': {},
            'show_labels': True
        }

def update_session_state(key, value):
    st.session_state.graph_settings[key] = value
```

State management features:
- Persistent settings across reruns
- Efficient state updates
- Clear state initialization
- Centralized state management



## D3.js Visualization

### Core Configuration

#### Initialization
```javascript
// Basic configuration parameters
const width = 800;
const height = 600;
const NODE_SIZES = {
    'lead': 30,
    'member': 25,
    'child': 20
};

// Initialize the SVG container
const svg = d3.select("#graph-container")
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("id", "graph-svg");

// Add a background rectangle for better interaction
svg.append("rect")
    .attr("width", width)
    .attr("height", height)
    .attr("fill", "white");

// Create a group for the graph elements
const g = svg.append("g");
```


#### Force Simulation Setup
```javascript
const simulation = d3.forceSimulation()
    .force("link", d3.forceLink()
        .id(d => d.id)
        .distance(d => {
            // Adjust distance based on node types
            return (d.source.type === 'lead' || d.target.type === 'lead') ? 250 : 200;
        })
        .strength(0.7)
    )
    .force("charge", d3.forceManyBody()
        .strength(d => {
            // Adjust repulsion based on node type
            return d.type === 'lead' ? -1000 : -700;
        })
    )
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collision", d3.forceCollide().radius(d => d.size * 2))
    .alphaDecay(0.05);
```

Force configuration features:
- Dynamic link distances
- Type-based charge strength
- Collision detection
- Customizable alpha decay
- Center force for layout balance

### Visual Elements

#### Node Rendering
```javascript
function createNodes() {
    // Create node groups
    const nodeGroup = nodeGroup.selectAll("g")
        .data(nodes, d => d.id)
        .enter()
        .append("g")
        .attr("class", "node");

    // Add rectangle backgrounds
    nodeGroup.append("rect")
        .attr("width", d => d.size * 4)
        .attr("height", d => d.size * 2)
        .attr("rx", 5)
        .attr("ry", 5)
        .attr("fill", d => typeColorMap[d.type])
        .attr("stroke", d => d3.color(typeColorMap[d.type]).darker())
        .attr("stroke-width", 1.5)
        .style("filter", "drop-shadow(2px 2px 3px rgba(0,0,0,0.2))");

    // Add text labels
    nodeGroup.append("text")
        .attr("text-anchor", "middle")
        .attr("dominant-baseline", "middle")
        .attr("fill", d => shouldUseDarkText(d.type) ? "#333" : "#fff")
        .text(d => d.id);

    return nodeGroup;
}

// Helper function for text color contrast
function shouldUseDarkText(nodeType) {
    const backgroundColor = d3.color(typeColorMap[nodeType]);
    const luminance = (0.299 * backgroundColor.r + 
                      0.587 * backgroundColor.g + 
                      0.114 * backgroundColor.b) / 255;
    return luminance > 0.5;
}
```

Node rendering features:
- Grouped node elements
- Rounded rectangles with shadows
- Dynamic text color based on background
- Automatic text positioning
- Smooth scaling

#### Edge Rendering
```javascript
function createEdges() {
    // Create arrow markers
    const defs = svg.append("defs");
    
    const markerData = [
        { id: "arrow-standard", color: "#999" },
        { id: "arrow-highlighted", color: "#666" }
    ];

    defs.selectAll("marker")
        .data(markerData)
        .enter()
        .append("marker")
        .attr("id", d => d.id)
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 28)
        .attr("refY", 0)
        .attr("markerWidth", 8)
        .attr("markerHeight", 8)
        .attr("orient", "auto")
        .append("path")
        .attr("d", "M0,-5L10,0L0,5")
        .attr("fill", d => d.color);

    // Create edge elements
    const linkGroup = g.append("g")
        .attr("class", "links");

    const link = linkGroup.selectAll("g")
        .data(links)
        .enter()
        .append("g")
        .attr("class", "link");

    // Add edge lines
    link.append("line")
        .attr("stroke", "#999")
        .attr("stroke-width", d => d.highlighted ? 2 : 1)
        .attr("marker-end", d => `url(#${d.highlighted ? "arrow-highlighted" : "arrow-standard"})`);

    // Add edge labels
    link.append("text")
        .attr("class", "link-label")
        .attr("text-anchor", "middle")
        .attr("dy", -5)
        .text(d => d.relationship);

    return link;
}
```

Edge rendering features:
- Custom arrow markers
- Highlighting support
- Relationship labels
- Dynamic stroke width
- Grouped edge elements

### Interactivity

#### Zoom and Pan
```javascript
function setupZoom() {
    const zoom = d3.zoom()
        .scaleExtent([0.2, 4])
        .on("zoom", (event) => {
            g.attr("transform", event.transform);
            // Adjust label sizes based on zoom level
            g.selectAll(".node text")
                .style("font-size", `${12 / event.transform.k}px`);
            g.selectAll(".link-label")
                .style("font-size", `${10 / event.transform.k}px`);
        });

    svg.call(zoom);
    
    // Add zoom controls
    const zoomControls = d3.select("#graph-container")
        .append("div")
        .attr("class", "zoom-controls");
        
    zoomControls.append("button")
        .text("+")
        .on("click", () => zoom.scaleBy(svg, 1.2));
        
    zoomControls.append("button")
        .text("-")
        .on("click", () => zoom.scaleBy(svg, 0.8));
        
    zoomControls.append("button")
        .text("Reset")
        .on("click", () => zoom.transform(svg, d3.zoomIdentity));
}
```

Zoom features:
- Scale limits
- Dynamic text scaling
- Custom zoom controls
- Reset functionality
- Smooth transitions

#### Drag Behavior
```javascript
function setupDrag() {
    const drag = d3.drag()
        .on("start", (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
            // Add dragging class for visual feedback
            d3.select(event.sourceEvent.target.parentNode)
                .classed("dragging", true);
        })
        .on("drag", (event, d) => {
            d.fx = event.x;
            d.fy = event.y;
        })
        .on("end", (event, d) => {
            if (!event.active) simulation.alphaTarget(0);
            // Remove dragging class
            d3.select(event.sourceEvent.target.parentNode)
                .classed("dragging", false);
            // Optional: keep node fixed or release it
            if (!event.sourceEvent.shiftKey) {
                d.fx = null;
                d.fy = null;
            }
        });

    return drag;
}
```

Drag features:
- Visual feedback during drag
- Shift key to fix position
- Smooth animation
- Force simulation integration

#### Node Expansion
```javascript
function setupNodeExpansion() {
    nodes.on("dblclick", (event, d) => {
        event.stopPropagation();
        
        // Visual feedback for expansion
        const node = d3.select(event.target.parentNode);
        node.classed("expanding", true);
        
        // Notify parent frame
        parent.postMessage({
            type: "node_expanded",
            node: d.id
        }, "*");
        
        // Remove visual feedback after delay
        setTimeout(() => node.classed("expanding", false), 500);
    });
}
```

Expansion features:
- Double-click activation
- Visual feedback
- Event propagation control
- Parent frame communication

### Animation and Transitions

#### Force Simulation Updates
```javascript
function updateSimulation() {
    simulation
        .nodes(nodes)
        .force("link").links(links);

    simulation.on("tick", () => {
        // Update node positions
        nodeGroup.attr("transform", d => `translate(${d.x},${d.y})`);
        
        // Update edge positions with curved paths
        link.select("line")
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);
            
        // Update edge label positions
        link.select("text")
            .attr("x", d => (d.source.x + d.target.x) / 2)
            .attr("y", d => (d.source.y + d.target.y) / 2);
    });
}
```

Animation features:
- Smooth position updates
- Edge following
- Label positioning
- Performance optimization

#### Transition Effects
```javascript
function applyTransitions() {
    // Node transitions
    const nodeTransition = node.transition()
        .duration(750)
        .ease(d3.easeElastic);
        
    nodeTransition.select("rect")
        .attr("width", d => d.size * 4)
        .attr("height", d => d.size * 2);
        
    // Edge transitions
    const linkTransition = link.transition()
        .duration(750)
        .ease(d3.easeQuadOut);
        
    linkTransition.select("line")
        .attr("stroke-width", d => d.highlighted ? 2 : 1)
        .style("opacity", d => d.visible ? 1 : 0.3);
}
```

Transition features:
- Smooth size changes
- Elastic easing
- Opacity changes
- Duration control

### Export Functionality

#### SVG Export
```javascript
function setupExport() {
    function downloadSVG() {
        const svgData = new XMLSerializer()
            .serializeToString(document.getElementById("graph-svg"));
        const svgBlob = new Blob([svgData], {
            type: "image/svg+xml;charset=utf-8"
        });
        
        // Clean up SVG for export
        const cleanSvg = cleanupSVGForExport(svgData);
        
        // Create download link
        const link = document.createElement("a");
        link.href = URL.createObjectURL(svgBlob);
        link.download = "knowledge_graph.svg";
        link.click();
        URL.revokeObjectURL(link.href);
    }
    
    function cleanupSVGForExport(svgData) {
        // Remove temporary elements
        // Add viewBox attribute
        // Embed styles
        // Return cleaned SVG
    }
}
```

Export features:
- SVG cleanup
- Style embedding
- Proper metadata
- Resource cleanup

## Component Communication

### Overview

The Knowledge Graph Visualizer implements bidirectional communication between Streamlit and D3.js to create a responsive and interactive visualization system. This documentation outlines how data and events flow between these components.

### Streamlit → D3.js Communication

#### Basic Integration

```python
components.html(
    d3_code,
    height=700,
    width=None
)
```

The `components.html()` function serves as the primary bridge for embedding D3.js visualizations within Streamlit. It handles:
- Initial graph rendering
- Layout configuration
- Control settings propagation
- Dynamic data updates

#### Dynamic Updates

```python
def update_visualization(graph_data):
    d3_code = generate_d3_code(graph_data)
    components.html(
        d3_code,
        height=700
    )
```

When graph data changes (e.g., through filters or new data), Streamlit triggers a re-render of the D3.js component with updated information.

### D3.js → Streamlit Communication

#### Event System

D3.js communicates user interactions back to Streamlit using the browser's postMessage API:

```javascript
class GraphEventManager {
    sendEvent(type, data) {
        window.parent.postMessage({
            type,
            payload: data
        }, "*");
    }
    
    handleNodeClick(node) {
        this.sendEvent("node_clicked", {
            id: node.id,
            properties: node.properties
        });
    }
}

const eventManager = new GraphEventManager();
```

### Event Handling in Streamlit

```python
def create_event_listener():
    component_html = """
    <script>
    window.addEventListener('message', function(event) {
        const { type, payload } = event.data;
        
        switch(type) {
            case 'node_clicked':
                handleNodeSelection(payload);
                break;
            case 'graph_updated':
                refreshVisualization(payload);
                break;
        }
    });
    </script>
    """
    return component_html
```

### Data Flow Architecture

#### 1. Initial Load
1. Streamlit initializes visualization parameters
2. D3.js receives configuration and data
3. Graph renders in its initial state

#### 2. User Interactions
1. User interacts with graph (e.g., clicks, drags)
2. D3.js captures events
3. Events propagate to Streamlit
4. Streamlit updates application state
5. Changes reflect back in visualization

#### 3. State Updates
1. Streamlit maintains source of truth
2. State changes trigger D3.js updates
3. Visualization reflects current state

