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

const width = 800;
const height = 600;

const color = d3.scaleOrdinal()
    .domain(['lead', 'member', 'child'])
    .range(['#FF6B6B', '#4ECDC4', '#45B7D1']);

const svg = d3.select("#d3-graph")
    .append("svg")
    .attr("width", width)
    .attr("height", height);

const g = svg.append("g"); // Create a group for all nodes and links

svg.call(d3.zoom()
    .scaleExtent([0.5, 5])
    .on("zoom", (event) => {
        g.attr("transform", event.transform); // Apply the zoom transformation to the group
    }));


const simulation = d3.forceSimulation(data.nodes)
    .force("link", d3.forceLink(data.links).id(d => d.id).distance(100))
    .force("charge", d3.forceManyBody().strength(-300))
    .force("center", d3.forceCenter(width / 2, height / 2));

const link = svg.append("g")
    .selectAll("line")
    .data(data.links)
    .enter().append("line")
    .attr("stroke", "#999")
    .attr("stroke-opacity", 0.6)
    .attr("stroke-width", 1);

const node = svg.append("g")
    .selectAll("circle")
    .data(data.nodes)
    .enter().append("circle")
    .attr("r", d => d.size)
    .attr("fill", d => color(d.type))
    .on("click", function(event, d) {
        if (d.children && d.children.length > 0) {
            const isVisible = d3.select(this).classed("expanded");
            d3.select(this).classed("expanded", !isVisible);
            const childrenLinks = data.links.filter(link => link.source === d.id && d.children.includes(link.target));
            if (isVisible) {
                // Hide children
                link.filter(l => childrenLinks.includes(l)).remove();
                svg.selectAll("circle")
                    .filter(n => childrenLinks.map(cl => cl.target).includes(n.id))
                    .remove();
            } else {
                // Show children
                const childNodes = d.children.map(child => ({
                    id: child,
                    type: data.nodes.find(n => n.id === child).type,
                    size: 20,  // Default size for children
                    children: list(data.G.neighbors(child)) // Get child nodes of the child
                }));
                
                // Append child nodes and links
                svg.selectAll("circle")
                    .data(childNodes)
                    .enter().append("circle")
                    .attr("r", d => d.size)
                    .attr("fill", d => color(d.type))
                    .attr("cx", Math.random() * width)
                    .attr("cy", Math.random() * height)
                    .on("click", event => event.stopPropagation()) // Prevent click from bubbling
                    .call(d3.drag()
                        .on("start", dragstarted)
                        .on("drag", dragged)
                        .on("end", dragended));
                
                svg.selectAll("line")
                    .data(childrenLinks)
                    .enter().append("line")
                    .attr("stroke", "#999")
                    .attr("stroke-opacity", 0.6)
                    .attr("stroke-width", 1);
            }
        }
    })
    .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

const text = svg.append("g")
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

function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(event, d) {
    d.fx = event.x;  // Set fixed x position
    d.fy = event.y;  // Set fixed y position
    simulation.alpha(0.3).restart(); // Restart the simulation to update positions
}

function dragended(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}
</script>
"""

# Streamlit app
st.title("Hierarchical Knowledge Graph")

excel_file = st.file_uploader("Upload Excel file", type="xlsx")

if excel_file is not None:
    kg = HierarchicalKnowledgeGraph(excel_file)
    graph_data = kg.get_graph_data()

    # Render D3.js visualization
    d3_code = D3_CODE.replace("__DATA__", json.dumps(graph_data))
    components.html(d3_code, height=650, width=800)

    # Display graph statistics
    st.write(f"Number of nodes: {len(graph_data['nodes'])}")
    st.write(f"Number of relationships: {len(graph_data['links'])}")

    
