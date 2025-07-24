import pandas as pd
import networkx as nx
import json
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import base64

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
        for node in self.G.nodes():
            data = self.G.nodes[node]
            nodes.append({
                "id": node,
                "type": data['type'],
                "size": 30 if data['type'] == 'lead' else (25 if data['type'] == 'member' else 20),
                "visible": node in self.visible_nodes
            })
        
        links = []
        for source, target in self.G.edges():
            data = self.G.edges[source, target]
            if visible_relationships is None or data.get('relationship', '') in visible_relationships:
                links.append({
                    "source": source,
                    "target": target,
                    "relationship": data.get('relationship', ''),
                    "visible": (source, target) in self.visible_edges or (target, source) in self.visible_edges
                })
        
        return {"nodes": nodes, "links": links}

    def get_node_options(self):
        return sorted(list(self.G.nodes()))

    def get_relationship_types(self):
        return sorted(set(data['relationship'] for _, _, data in self.G.edges(data=True)))

    def expand_node(self, node, visible_relationships=None):
        neighbors = set(self.G.neighbors(node))
        self.visible_nodes.update(neighbors)
        self.visible_nodes.add(node)
        new_edges = set((node, neighbor) for neighbor in neighbors)
        self.visible_edges.update(new_edges)

        new_nodes = []
        for new_node in neighbors.union({node}):
            data = self.G.nodes[new_node]
            new_nodes.append({
                "id": new_node,
                "type": data['type'],
                "size": 30 if data['type'] == 'lead' else (25 if data['type'] == 'member' else 20),
                "visible": True
            })

        new_links = []
        for source, target in new_edges:
            data = self.G.edges[source, target]
            if visible_relationships is None or data.get('relationship', '') in visible_relationships:
                new_links.append({
                    "source": source,
                    "target": target,
                    "relationship": data.get('relationship', ''),
                    "visible": True
                })

        return {"nodes": new_nodes, "links": new_links}

# D3.js visualization code with download functionality
D3_CODE = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://d3js.org/d3.v5.min.js"></script>
    <script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
    <style>
        #graph-container {
            position: relative;
            width: 800px;
            height: 600px;
        }
        .links line {
            stroke-linecap: round;
        }
        .node-labels {
            pointer-events: none;
            user-select: none;
        }
        .link-labels {
            pointer-events: none;
            user-select: none;
        }
        .download-panel {
            position: absolute;
            top: 10px;
            right: 10px;
            background: white;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            z-index: 1000;
        }
        .download-button {
            display: block;
            margin: 5px 0;
            padding: 8px 16px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            width: 100%;
        }
        .download-button:hover {
            background-color: #45a049;
        }
        .reset-button {
            display: block;
            margin: 5px 0;
            padding: 8px 16px;
            background-color: #f44336;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            width: 100%;
        }
        .reset-button:hover {
            background-color: #da190b;
        }
    </style>
</head>
<body>
    <div id="graph-container">
        <div class="download-panel">
            <button class="download-button" onclick="downloadSVG()">Download SVG</button>
            <button class="download-button" onclick="downloadPNG()">Download PNG</button>
            <button class="reset-button" onclick="resetPositions()">Reset Positions</button>
        </div>
    </div>

    <script>
        const data = __DATA__;
        const colorScheme = __COLOR_SCHEME__;
        
        const typeColorMap = {
            'lead': colorScheme[0],
            'member': colorScheme[1],
            'child': colorScheme[2]
        };
        
        const width = 800;
        const height = 600;
        
        const svg = d3.select("#graph-container")
            .append("svg")
            .attr("width", width)
            .attr("height", height)
            .attr("id", "graph-svg");
        
        svg.append("rect")
            .attr("width", width)
            .attr("height", height)
            .attr("fill", "white");
            
        const g = svg.append("g");
        
        const zoom = d3.zoom()
            .scaleExtent([0.5, 5])
            .on("zoom", () => {
                g.attr("transform", d3.event.transform);
            });
            
        svg.call(zoom);
        
        // Define arrow markers with different colors
        const arrowColors = ['#999', '#666', '#333'];
        svg.append("defs").selectAll("marker")
            .data(arrowColors)
            .enter().append("marker")
            .attr("id", (d, i) => `arrow-${i}`)
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", 28)  // Adjusted to position arrow at node edge
            .attr("refY", 0)
            .attr("markerWidth", 8)
            .attr("markerHeight", 8)
            .attr("orient", "auto")
            .append("path")
            .attr("d", "M0,-5L10,0L0,5")
            .attr("fill", d => d);
            
        const simulation = d3.forceSimulation()
            .force("link", d3.forceLink().id(d => d.id).distance(200))
            .force("charge", d3.forceManyBody().strength(-700))
            .force("center", d3.forceCenter(width / 2, height / 2));
            
        const linkGroup = g.append("g").attr("class", "links");
        const nodeGroup = g.append("g").attr("class", "nodes");
        const nodeLabelGroup = g.append("g").attr("class", "node-labels");
        const linkLabelGroup = g.append("g").attr("class", "link-labels");
        
        let link = linkGroup.selectAll("line");  // Changed from path to line
        let node = nodeGroup.selectAll("rect");
        let nodeLabel = nodeLabelGroup.selectAll("text");
        let linkLabel = linkLabelGroup.selectAll("text");

        const drag = d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended);
        
        function updateGraph() {
            // Update links - now using straight lines
            link = link.data(data.links, d => `${d.source.id || d.source}-${d.target.id || d.target}`);
            link.exit().remove();
            
            const linkEnter = link.enter().append("line")
                .attr("stroke", "#999")
                .attr("stroke-opacity", 0.6)
                .attr("stroke-width", 1.5)
                .attr("marker-end", (d, i) => `url(#arrow-${i % 3})`);  // Cycle through arrow colors
                
            link = linkEnter.merge(link)
                .style("visibility", d => d.visible ? "visible" : "hidden");
                
            // Rest of the update function remains the same
            node = node.data(data.nodes, d => d.id);
            node.exit().remove();
            
            const nodeEnter = node.enter().append("rect")
                .attr("width", d => d.size * 4)
                .attr("height", d => d.size * 2)
                .attr("rx", 5)
                .attr("ry", 5)
                .attr("fill", d => typeColorMap[d.type])
                .call(drag);
                    
            node = nodeEnter.merge(node)
                .style("opacity", d => d.visible ? 1 : 0.3);
                
            nodeLabel = nodeLabel.data(data.nodes, d => d.id);
            nodeLabel.exit().remove();
            
            const nodeLabelEnter = nodeLabel.enter().append("text")
                .attr("text-anchor", "middle")
                .attr("dominant-baseline", "middle")
                .style("font-size", "12px")
                .text(d => d.id);
                
            nodeLabel = nodeLabelEnter.merge(nodeLabel)
                .style("opacity", d => d.visible ? 1 : 0.3);
                
            linkLabel = linkLabel.data(data.links, d => `${d.source.id || d.source}-${d.target.id || d.target}`);
            linkLabel.exit().remove();
            
            const linkLabelEnter = linkLabel.enter().append("text")
                .attr("font-size", "10px")
                .attr("fill", "#666")
                .text(d => d.relationship);
                
            linkLabel = linkLabelEnter.merge(linkLabel)
                .style("visibility", d => d.visible ? "visible" : "hidden");
                
            simulation.nodes(data.nodes);
            simulation.force("link").links(data.links);
            simulation.alpha(1).restart();
        }
        
        // Drag functions remain the same
        function dragstarted(d) {
            if (!d3.event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }
        
        function dragged(d) {
            d.fx = d3.event.x;
            d.fy = d3.event.y;
            d.x = d3.event.x;
            d.y = d3.event.y;
        }
        
        function dragended(d) {
            if (!d3.event.active) simulation.alphaTarget(0);
        }

        function resetPositions() {
            data.nodes.forEach(d => {
                d.fx = null;
                d.fy = null;
            });
            simulation.alpha(1).restart();
        }
        
        // Updated tick function for straight lines
        simulation.on("tick", () => {
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            
            node
                .attr("x", d => d.x - d.size * 2)
                .attr("y", d => d.y - d.size);
                
            nodeLabel
                .attr("x", d => d.x)
                .attr("y", d => d.y);
                
            linkLabel
                .attr("x", d => (d.source.x + d.target.x) / 2)
                .attr("y", d => (d.source.y + d.target.y) / 2 - 5);
        });
        
        // Download functions remain the same
        function downloadSVG() {
            const svgElement = document.getElementById("graph-svg");
            const svgData = new XMLSerializer().serializeToString(svgElement);
            const svgBlob = new Blob([svgData], {type: "image/svg+xml;charset=utf-8"});
            const svgUrl = URL.createObjectURL(svgBlob);
            
            const downloadLink = document.createElement("a");
            downloadLink.href = svgUrl;
            downloadLink.download = "knowledge_graph.svg";
            document.body.appendChild(downloadLink);
            downloadLink.click();
            document.body.removeChild(downloadLink);
            URL.revokeObjectURL(svgUrl);
        }
        
        async function downloadPNG() {
            const svgElement = document.getElementById("graph-svg");
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            
            canvas.width = width;
            canvas.height = height;
            
            const image = new Image();
            const svgData = new XMLSerializer().serializeToString(svgElement);
            const svgBlob = new Blob([svgData], {type: 'image/svg+xml;charset=utf-8'});
            const svgUrl = URL.createObjectURL(svgBlob);
            
            image.onload = () => {
                context.fillStyle = 'white';
                context.fillRect(0, 0, canvas.width, canvas.height);
                context.drawImage(image, 0, 0);
                
                const pngUrl = canvas.toDataURL('image/png');
                const downloadLink = document.createElement('a');
                downloadLink.href = pngUrl;
                downloadLink.download = 'knowledge_graph.png';
                document.body.appendChild(downloadLink);
                downloadLink.click();
                document.body.removeChild(downloadLink);
                
                URL.revokeObjectURL(svgUrl);
            };
            
            image.src = svgUrl;
        }
        
        updateGraph();
    </script>
</body>
</html>
"""

# Streamlit app
def main():
    st.set_page_config(page_title="Knowledge Graph Visualizer", layout="wide")
    st.title("Interactive Knowledge Graph Visualizer")
    
    # File upload
    excel_file = st.file_uploader("Upload Excel file", type="xlsx")
    
    if excel_file is not None:
        try:
            # Initialize the graph
            kg = HierarchicalKnowledgeGraph(excel_file)
            
            # Create columns for layout
            left_col, right_col = st.columns([1, 3])
            
            with left_col:
                st.header("Graph Controls")
                
                # Path filter
                st.subheader("Path Filter")
                node_options = kg.get_node_options()
                start_node = st.selectbox("Start Node", node_options, key="start_node")
                end_node = st.selectbox("End Node", node_options, key="end_node")
                
                # Relationship filter
                st.subheader("Relationship Filter")
                relationship_types = kg.get_relationship_types()
                visible_relationships = st.multiselect(
                    "Visible Relationships",
                    relationship_types,
                    default=relationship_types
                )
                
                # Color customization
                st.subheader("Color Settings")
                lead_color = st.color_picker("Lead Node Color", "#FF6B6B")
                member_color = st.color_picker("Member Node Color", "#4ECDC4")
                child_color = st.color_picker("Child Node Color", "#45B7D1")
                
                # Apply filters button
                if st.button("Apply Filters"):
                    graph_data = kg.get_graph_data(start_node, end_node, visible_relationships)
                else:
                    graph_data = kg.get_graph_data(visible_relationships=visible_relationships)
                
                # Display graph statistics
                st.subheader("Graph Statistics")
                st.write(f"Total Nodes: {len(graph_data['nodes'])}")
                st.write(f"Visible Nodes: {sum(1 for node in graph_data['nodes'] if node['visible'])}")
                st.write(f"Total Relationships: {len(graph_data['links'])}")
                st.write(f"Visible Relationships: {sum(1 for link in graph_data['links'] if link['visible'])}")

            with right_col:
                # Prepare color scheme
                color_scheme = [lead_color, member_color, child_color]
                
                # Render D3.js visualization
                d3_code = D3_CODE.replace("__DATA__", json.dumps(graph_data)).replace("__COLOR_SCHEME__", json.dumps(color_scheme))
                components.html(d3_code, height=700, width=None)

        except Exception as e:
            st.error(f"Error processing the file: {str(e)}")
            st.write("Please make sure your Excel file has the correct format with columns: 'node', 'parent', 'type', and 'relationship'")
            return

if __name__ == "__main__":
    main()