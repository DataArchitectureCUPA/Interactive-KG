import pandas as pd
import networkx as nx
import json
import streamlit as st
import streamlit.components.v1 as components

class HierarchicalKnowledgeGraph:
    def __init__(self, excel_file):
        self.df = pd.read_excel(excel_file)
        self.G = nx.Graph()
        self.load_initial_graph()
        self.visible_nodes = set()
        self.visible_edges = set()

    def load_initial_graph(self):
        for _, row in self.df.iterrows():
            node = str(row['node'])
            parent = str(row['parent']) if pd.notnull(row['parent']) else None
            
            self.G.add_node(node, type=row['type'])
            if parent and parent != 'nan':
                self.G.add_edge(parent, node, relationship=row['relationship'])

    def get_graph_data(self, start_node=None, end_node=None, visible_relationships=None):
        if start_node and end_node:
            try:
                paths = list(nx.all_simple_paths(self.G, source=start_node, target=end_node))
                self.visible_nodes = set(node for path in paths for node in path)
                self.visible_edges = set((path[i], path[i+1]) for path in paths for i in range(len(path)-1))
            except nx.NetworkXNoPath:
                st.warning(f"No path found between {start_node} and {end_node}")
                self.visible_nodes = set()
                self.visible_edges = set()
        else:
            self.visible_nodes = set(self.G.nodes())
            self.visible_edges = set(self.G.edges())

        nodes = []
        for node in self.visible_nodes:
            data = self.G.nodes[node]
            nodes.append({
                "id": node,
                "type": data['type'],
                "size": 30 if data['type'] == 'lead' else (25 if data['type'] == 'member' else 20),
            })
        
        links = []
        for source, target in self.visible_edges:
            data = self.G.edges[source, target]
            if visible_relationships is None or data.get('relationship', '') in visible_relationships:
                links.append({
                    "source": source,
                    "target": target,
                    "relationship": data.get('relationship', '')
                })
        
        return {"nodes": nodes, "links": links}

    def get_node_options(self):
        return sorted(list(self.G.nodes()))

    def get_relationship_types(self):
        return sorted(set(data['relationship'] for _, _, data in self.G.edges(data=True)))

    def expand_node(self, node, visible_relationships=None):
        neighbors = set(self.G.neighbors(node))
        self.visible_nodes.update(neighbors)
        new_edges = set((node, neighbor) for neighbor in neighbors)
        self.visible_edges.update(new_edges)

        new_nodes = []
        for new_node in neighbors:
            if new_node not in self.visible_nodes:
                data = self.G.nodes[new_node]
                new_nodes.append({
                    "id": new_node,
                    "type": data['type'],
                    "size": 30 if data['type'] == 'lead' else (25 if data['type'] == 'member' else 20),
                })

        new_links = []
        for source, target in new_edges:
            data = self.G.edges[source, target]
            if visible_relationships is None or data.get('relationship', '') in visible_relationships:
                new_links.append({
                    "source": source,
                    "target": target,
                    "relationship": data.get('relationship', '')
                })

        return {"nodes": new_nodes, "links": new_links}

# D3.js code for graph visualization
D3_CODE = """
<script src="https://d3js.org/d3.v5.min.js"></script>
<div id="d3-graph"></div>
<script>
let data = __DATA__;
const colorScheme = __COLOR_SCHEME__;

const width = 800;
const height = 600;

const color = d3.scaleOrdinal()
    .domain(['lead', 'member', 'child'])
    .range(colorScheme);

const svg = d3.select("#d3-graph")
    .append("svg")
    .attr("width", width)
    .attr("height", height);

const g = svg.append("g");

svg.call(d3.zoom()
    .scaleExtent([0.5, 5])
    .on("zoom", () => {
        g.attr("transform", d3.event.transform);
    }));

let simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(d => d.id).distance(100))
    .force("charge", d3.forceManyBody().strength(-300))
    .force("center", d3.forceCenter(width / 2, height / 2));

let link = g.append("g")
    .attr("class", "links")
    .selectAll("line");

let node = g.append("g")
    .attr("class", "nodes")
    .selectAll("circle");

let nodeText = g.append("g")
    .attr("class", "node-labels")
    .selectAll("text");

let linkText = g.append("g")
    .attr("class", "link-labels")
    .selectAll("text");

function updateGraph() {
    // Update links
    link = link.data(data.links, d => `${d.source.id || d.source}-${d.target.id || d.target}`);
    link.exit().remove();
    link = link.enter().append("line")
        .attr("stroke", "#999")
        .attr("stroke-opacity", 0.6)
        .attr("stroke-width", 1)
        .merge(link);

    // Update nodes
    node = node.data(data.nodes, d => d.id);
    node.exit().remove();
    node = node.enter().append("circle")
        .attr("r", d => d.size)
        .attr("fill", d => color(d.type))
        .on("click", expandNode)
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended))
        .merge(node);

    // Update node labels
    nodeText = nodeText.data(data.nodes, d => d.id);
    nodeText.exit().remove();
    nodeText = nodeText.enter().append("text")
        .text(d => d.id)
        .attr("font-size", 10)
        .attr("dx", 12)
        .attr("dy", 4)
        .merge(nodeText);

    // Update link labels
    linkText = linkText.data(data.links, d => `${d.source.id || d.source}-${d.target.id || d.target}`);
    linkText.exit().remove();
    linkText = linkText.enter().append("text")
        .text(d => d.relationship)
        .attr("font-size", 8)
        .attr("fill", "#666")
        .merge(linkText);

    // Update and restart the simulation
    simulation.nodes(data.nodes);
    simulation.force("link").links(data.links);
    simulation.alpha(1).restart();
}

function expandNode(d) {
    updatePythonValue("expandedNode", d.id);
}

function dragstarted(d) {
    if (!d3.event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
}

function dragended(d) {
    if (!d3.event.active) simulation.alphaTarget(0);
}

simulation.on("tick", () => {
    link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

    node
        .attr("cx", d => d.x)
        .attr("cy", d => d.y);

    nodeText
        .attr("x", d => d.x)
        .attr("y", d => d.y);

    linkText
        .attr("x", d => (d.source.x + d.target.x) / 2)
        .attr("y", d => (d.source.y + d.target.y) / 2);
});

updateGraph();

// Function to update data from Python
function updateData(newData) {
    data.nodes = data.nodes.concat(newData.nodes);
    data.links = data.links.concat(newData.links);
    updateGraph();
}
</script>
"""

# Streamlit app
st.title("Hierarchical Knowledge Graph")

excel_file = st.file_uploader("Upload Excel file", type="xlsx")

if excel_file is not None:
    kg = HierarchicalKnowledgeGraph(excel_file)
    
    # Add filter functionality
    st.sidebar.header("Path Filter")
    start_node = st.sidebar.selectbox("Start Node", kg.get_node_options(), key="start_node")
    end_node = st.sidebar.selectbox("End Node", kg.get_node_options(), key="end_node")
    
    # Add edge filter functionality
    st.sidebar.header("Edge Filter")
    relationship_types = kg.get_relationship_types()
    visible_relationships = st.sidebar.multiselect("Visible Relationships", relationship_types, default=relationship_types)
    
    if st.sidebar.button("Apply Filters"):
        graph_data = kg.get_graph_data(start_node, end_node, visible_relationships)
    else:
        graph_data = kg.get_graph_data(visible_relationships=visible_relationships)

    # Color customization
    st.sidebar.header("Color Customization")
    lead_color = st.sidebar.color_picker("Lead Node Color", "#FF6B6B")
    member_color = st.sidebar.color_picker("Member Node Color", "#4ECDC4")
    child_color = st.sidebar.color_picker("Child Node Color", "#45B7D1")
    color_scheme = [lead_color, member_color, child_color]

    # Render D3.js visualization
    d3_code = D3_CODE.replace("__DATA__", json.dumps(graph_data)).replace("__COLOR_SCHEME__", json.dumps(color_scheme))
    components.html(d3_code, height=650, width=800)

    # Display graph statistics
    st.write(f"Number of nodes: {len(graph_data['nodes'])}")
    st.write(f"Number of relationships: {len(graph_data['links'])}")

    # Handle node expansion
    if st.session_state.get("expandedNode"):
        expanded_node = st.session_state.expandedNode
        new_data = kg.expand_node(expanded_node, visible_relationships)
        st.session_state.expandedNode = None
        components.html(
            f"""
            <script>
            updateData({json.dumps(new_data)});
            </script>
            """,
            height=0,
        )

    # Initialize session state for expanded nodes if not already done
    if "expanded_nodes" not in st.session_state:
        st.session_state.expanded_nodes = set()

    # Update session state when a node is expanded
    if st.session_state.get("expandedNode"):
        st.session_state.expanded_nodes.add(st.session_state.expandedNode)