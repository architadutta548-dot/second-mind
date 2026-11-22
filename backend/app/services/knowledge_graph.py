
import networkx as nx

from app.services.concept_extractor import extract_concepts
from app.services.relationship_extractor import extract_relationships


class KnowledgeGraph:

    def __init__(self):
        self.graph = nx.Graph()

    def get_relationship_strength(self, evidence_count):
        """
        Classify relationship strength using
        distinct supporting memories.
        """

        if evidence_count >= 5:
            return "very_high"

        elif evidence_count >= 3:
            return "high"

        elif evidence_count == 2:
            return "moderate"

        return "low"

    def add_concept(self, concept, category="general", memory_id=None):

        if not self.graph.has_node(concept):

            self.graph.add_node(
                concept,
                categories=[category],
                supporting_memory_ids=[]
            )

        node_data = self.graph.nodes[concept]

        if category not in node_data["categories"]:
            node_data["categories"].append(category)

        if (
            memory_id is not None
            and memory_id not in node_data["supporting_memory_ids"]
        ):
            node_data["supporting_memory_ids"].append(memory_id)

        node_data["memory_count"] = len(
            node_data["supporting_memory_ids"]
        )

    def add_relationship(
        self,
        source,
        target,
        relationship,
        evidence_type="observed",
        memory_id=None,
        confidence="not_assessed"
    ):

        if source == target:
            return

        if self.graph.has_edge(source, target):

            edge_data = self.graph[source][target]

            if (
                memory_id is not None
                and memory_id not in edge_data["supporting_memory_ids"]
            ):
                edge_data["supporting_memory_ids"].append(memory_id)

            edge_data["evidence_count"] = len(
                edge_data["supporting_memory_ids"]
            )

            edge_data["strength"] = self.get_relationship_strength(
                edge_data["evidence_count"]
            )

        else:

            supporting_ids = []

            if memory_id is not None:
                supporting_ids.append(memory_id)

            evidence_count = len(supporting_ids)

            self.graph.add_edge(
                source,
                target,
                relationship=relationship,
                evidence_type=evidence_type,
                supporting_memory_ids=supporting_ids,
                evidence_count=evidence_count,
                strength=self.get_relationship_strength(
                    evidence_count
                ),
                confidence=confidence
            )

    def get_connections(self, concept):

        if not self.graph.has_node(concept):
            return []

        connections = []

        for neighbor in self.graph.neighbors(concept):

            edge_data = self.graph.get_edge_data(
                concept, neighbor
            )

            connections.append({
                "related_concept": neighbor,
                "relationship": edge_data["relationship"],
                "evidence_type": edge_data["evidence_type"],
                "evidence_count": edge_data["evidence_count"],
                "supporting_memory_ids": (
                    edge_data["supporting_memory_ids"]
                ),
                "strength": edge_data["strength"],
                "confidence": edge_data["confidence"]
            })

        return connections

    def get_graph_data(self):

        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),

            "nodes": [
                {
                    "id": node,
                    "categories": data["categories"],
                    "supporting_memory_ids": (
                        data["supporting_memory_ids"]
                    ),
                    "memory_count": data["memory_count"]
                }
                for node, data in self.graph.nodes(data=True)
            ],

            "edges": [
                {
                    "source": source,
                    "target": target,
                    "relationship": data["relationship"],
                    "evidence_type": data["evidence_type"],
                    "evidence_count": data["evidence_count"],
                    "supporting_memory_ids": (
                        data["supporting_memory_ids"]
                    ),
                    "strength": data["strength"],
                    "confidence": data["confidence"]
                }
                for source, target, data in self.graph.edges(data=True)
            ]
        }


def build_graph_from_memories(memories):

    graph = KnowledgeGraph()

    for memory in memories:

        concepts = extract_concepts(
            f"{memory.title}. {memory.content}"
        )

        category = memory.category or "general"

        # Add concepts and track their source memories
        for concept in concepts:

            graph.add_concept(
                concept,
                category,
                memory.id
            )

        # Extract relationships between concepts
        relationships = extract_relationships(concepts)

        for relationship in relationships:

            graph.add_relationship(
                source=relationship["source"],
                target=relationship["target"],
                relationship=relationship["relationship"],
                evidence_type=relationship["evidence_type"],
                memory_id=memory.id,
                confidence=relationship["confidence"]
            )

    return graph.get_graph_data()
