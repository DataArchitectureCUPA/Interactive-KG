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

    def load_initial_graph(self):
        for _, row in self.df.iterrows():
            node = str(row['node'])
            parent = str(row['parent']) if pd.notnull(row['parent']) else None
            
            self.G.add_node(node, type=row['type'])
            if parent and parent != 'nan':
                self.G.add_edge(parent, node, relationship=row['relationship'])

    def get_graph_data(self):
        nodes = []
        for node, data in self.G.nodes(data=True):
            nodes.append({
                "id": node,
                "type": data['type'],
                "size": 30 if data['type'] == 'lead' else (25 if data['type'] == 'member' else 20),
                "children": list(self.G.neighbors(node))  # Add children information
            })
        
        links = []
        for source, target, data in self.G.edges(data=True):
            links.append({
                "source": source,
                "target": target,
                "relationship": data.get('relationship', '')
            })
        
        return {"nodes": nodes, "links": links}

# D3.js code for graph visualization
D3_CODE = """
<script src="https://d3js.org/d3.v5.min.js"></script>
<div id="d3-graph"></div>
<script>
const data = __DATA__;
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

const g = svg.append("g"); // Create a group for all nodes and links

svg.call(d3.zoom()
    .scaleExtent([0.5, 5])
    .on("zoom", () => {
        g.attr("transform", d3.event.transform); // Apply the zoom transformation to the group
    }));

let simulation = d3.forceSimulation(data.nodes)
    .force("link", d3.forceLink(data.links).id(d => d.id).distance(100))
    .force("charge", d3.forceManyBody().strength(-300))
    .force("center", d3.forceCenter(width / 2, height / 2));

let link = g.append("g")
    .selectAll("line")
    .data(data.links)
    .enter().append("line")
    .attr("stroke", "#999")
    .attr("stroke-opacity", 0.6)
    .attr("stroke-width", 1);

let node = g.append("g")
    .selectAll("circle")
    .data(data.nodes)
    .enter().append("circle")
    .attr("r", d => d.size)
    .attr("fill", d => color(d.type))
    .on("click", clicked)
    .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

let text = g.append("g")
    .selectAll("text")
    .data(data.nodes)
    .enter().append("text")
    .text(d => d.id)
    .attr("font-size", 10)
    .attr("dx", 12)
    .attr("dy", 4);

node.append("title")
    .text(d => `Type: ${d.type}`);

link.append("title")
    .text(d => d.relationship);

simulation.on("tick", () => {
    link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

    node
        .attr("cx", d => d.x)
        .attr("cy", d => d.y);

    text
        .attr("x", d => d.x)
        .attr("y", d => d.y);
});

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
    // Comment out the next two lines to make nodes stay where they're dragged
    // d.fx = null;
    // d.fy = null;
}

function clicked(d) {
    if (d.children && d.children.length > 0) {
        const isExpanded = !d.isExpanded;
        d.isExpanded = isExpanded;
        
        if (isExpanded) {
            // Show children
            data.nodes = data.nodes.concat(d.children.map(child => ({
                id: child,
                type: data.nodes.find(n => n.id === child).type,
                size: 20,
                children: []
            })));
            data.links = data.links.concat(d.children.map(child => ({
                source: d.id,
                target: child,
                relationship: 'child'
            })));
        } else {
            // Hide children
            data.nodes = data.nodes.filter(n => !d.children.includes(n.id));
            data.links = data.links.filter(l => l.source.id !== d.id || !d.children.includes(l.target.id));
        }
        
        updateGraph();
    }
}



function updateGraph() {
    node = node.data(data.nodes, d => d.id);
    node.exit().remove();
    node = node.enter().append("circle")
        .attr("r", d => d.size)
        .attr("fill", d => color(d.type))
        .on("click", clicked)
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended))
        .merge(node);

    link = link.data(data.links, d => `${d.source.id}-${d.target.id}`);
    link.exit().remove();
    link = link.enter().append("line")
        .attr("stroke", "#999")
        .attr("stroke-opacity", 0.6)
        .attr("stroke-width", 1)
        .merge(link);

    text = text.data(data.nodes, d => d.id);
    text.exit().remove();
    text = text.enter().append("text")
        .text(d => d.id)
        .attr("font-size", 10)
        .attr("dx", 12)
        .attr("dy", 4)
        .merge(text);

    simulation.nodes(data.nodes);
    simulation.force("link").links(data.links);
    simulation.alpha(1).restart();
}

function filterNodes(nodeType) {
    data.nodes.forEach(node => {
        node.hidden = nodeType !== 'all' && node.type !== nodeType;
    });
    updateGraph();
}

window.filterNodes = filterNodes;
</script>
"""

# Streamlit app
st.title("Hierarchical Knowledge Graph")

excel_file = st.file_uploader("Upload Excel file", type="xlsx")

if excel_file is not None:
    kg = HierarchicalKnowledgeGraph(excel_file)
    graph_data = kg.get_graph_data()

    # Color customization
    st.sidebar.header("Color Customization")
    lead_color = st.sidebar.color_picker("Lead Node Color", "#FF6B6B")
    member_color = st.sidebar.color_picker("Member Node Color", "#4ECDC4")
    child_color = st.sidebar.color_picker("Child Node Color", "#45B7D1")
    color_scheme = [lead_color, member_color, child_color]

    # Node filtering
    st.sidebar.header("Node Filtering")
    node_types = ['all'] + list(set(node['type'] for node in graph_data['nodes']))
    selected_type = st.sidebar.selectbox("Filter nodes by type", node_types)
    
    if st.sidebar.button("Apply Filter"):
        st.components.v1.html(f"filterNodes('{selected_type}');", height=0)

    # Render D3.js visualization
    d3_code = D3_CODE.replace("__DATA__", json.dumps(graph_data)).replace("__COLOR_SCHEME__", json.dumps(color_scheme))
    components.html(d3_code, height=650, width=800)

    # Display graph statistics
    st.write(f"Number of nodes: {len(graph_data['nodes'])}")
    st.write(f"Number of relationships: {len(graph_data['links'])}")