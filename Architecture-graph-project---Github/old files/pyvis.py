import pandas as pd
from pyvis.network import Network
import networkx as nx

class HierarchicalKnowledgeGraph:
    def __init__(self, excel_file):
        self.df = pd.read_excel(excel_file)
        self.G = nx.Graph()
        self.load_initial_graph()
        self.net = Network(height="800px", width="100%", bgcolor="#ffffff", font_color="black")
        self.net.from_nx(self.G)
        self.configure_nodes()

    def load_initial_graph(self):
        for _, row in self.df.iterrows():
            # Convert node and parent to string to ensure compatibility
            node = str(row['node'])
            parent = str(row['parent']) if pd.notnull(row['parent']) else None
            
            self.G.add_node(node, type=row['type'])
            if parent and parent != 'nan':
                self.G.add_edge(parent, node, relationship=row['relationship'])

    def configure_nodes(self):
        for node in self.net.nodes:
            node_type = self.G.nodes[node['id']]['type']
            if node_type == 'lead':
                node['color'] = '#FF6B6B'  # Red
                node['size'] = 30
            elif node_type == 'member':
                node['color'] = '#4ECDC4'  # Teal
                node['size'] = 25
            else:  # child
                node['color'] = '#45B7D1'  # Light Blue
                node['size'] = 20
            node['title'] = f"Type: {node_type}"

        for edge in self.net.edges:
            edge['title'] = self.G[edge['from']][edge['to']]['relationship']

    def create_graph(self, output_file='knowledge_graph.html'):
        self.net.show_buttons(filter_=['physics'])
        self.net.save_graph(output_file)
        print(f"Graph has been saved to {output_file}")

# Usage
excel_file = 'test data.xlsx'
kg = HierarchicalKnowledgeGraph(excel_file)
kg.create_graph()