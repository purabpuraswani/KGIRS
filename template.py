"""
Streamlit Virtual Laboratory - Experiment 10
Title: Query Knowledge Graphs Using Cypher
Roll No.: 47

Preserves the 4-Section Architecture:
  1. Theory: Knowledge Graphs, Property Graphs, Cypher Syntax, Traversal, and Key Terminology.
  2. Simulation: Interactive Knowledge Graph Explorer, Cypher Query Engine, Traversal Animation, Results & Trial Logger.
  3. Quiz: 10 Conceptual Questions with Automated Self-Grading and Feedback.
  4. Report Generation: Student Information, Recorded Trials, Observations, and PDF Download.
"""

import os
import time
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
import networkx as nx
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from fpdf import FPDF

import cypher_engine as ce


# ======================================================================================
# 1. EXPERIMENT CONFIGURATION & EDUCATIONAL CONTENT
# ======================================================================================

EXPERIMENT_CONFIG = {
    "title": "Roll No. 47 / Experiment 10: Query Knowledge Graphs Using Cypher",
    "course": "Knowledge Engineering & Graph Databases",
    "experiment_no": "Experiment 10",
    "roll_no": "Roll No. 47",
    "objectives": [
        "Understand the formal architecture of Knowledge Graphs and the Property Graph Model (PGM).",
        "Formulate declarative graph queries using the Cypher query language (MATCH, WHERE, RETURN, count).",
        "Trace single-hop and multi-hop graph traversals across academic, entertainment, and e-commerce domains.",
        "Analyze graph pattern matching semantics, node filtering, and relationship directionality.",
        "Synthesize experimental query trials, evaluate execution metrics, and document observations in a formal lab report."
    ]
}

THEORY_CONTENT = {
    "background": """
### 1. Fundamentals of Knowledge Graphs
A **Knowledge Graph (KG)** is a structured representation of real-world knowledge that encodes entities (nodes) and their semantic interrelations (edges) in a machine-readable graph topology. Unlike relational databases that fragment domain models across flat tables linked by foreign keys, Knowledge Graphs represent data natively as interconnected networks.

### 2. The Property Graph Model (PGM)
In the modern Property Graph Model, the graph is composed of four fundamental building blocks:
* **Nodes (Vertices)**: Represent discrete domain entities (e.g., `Student`, `Course`, `Person`, `Product`).
* **Labels**: Categorize nodes into semantic sets (e.g., `:Student`, `:Teacher`), enabling efficient indexing and schema partitioning.
* **Properties**: Key-value attribute dictionaries attached directly to nodes and relationships (e.g., `age: 20`, `title: "Inception"`).
* **Relationships (Edges)**: Directed, typed semantic connections (e.g., `-[:STUDIES]->`, `-[:DIRECTED]->`, `-[:PURCHASED]->`) that link a source node directly to a target node.

### 3. Declarative Querying with Cypher
**Cypher** is the standard declarative graph query language. It employs visual ASCII-art conventions to formulate intuitive graph path patterns:
* **Node Pattern**: Nodes are wrapped in parentheses: `(alias:Label {property: value})`. For example, `(s:Student)` binds variable `s` to any node labeled `Student`.
* **Relationship Pattern**: Directed relationships are enclosed in brackets and hyphens with arrowheads:
  - Forward: `(a)-[:REL_TYPE]->(b)`
  - Backward: `(a)<-[:REL_TYPE]-(b)`
* **The MATCH Clause**: Specifies the topological sub-graph pattern to search for within the knowledge graph.
* **The WHERE Clause**: Enforces predicate constraints on node or relationship properties (e.g., `WHERE s.age > 20`).
* **The RETURN Clause**: Specifies which properties, node identifiers, or aggregated projections should be emitted in tabular form.
* **Aggregation**: Functions such as `count()` aggregate values. Non-aggregated fields in the `RETURN` clause implicitly form the grouping key.

### 4. Graph Traversal: Single-Hop vs. Multi-Hop
* **Single-Hop Traversal**: Traverses a single edge between two directly adjacent nodes (e.g., `(s:Student)-[:STUDIES]->(c:Course)`).
* **Multi-Hop Traversal**: Sequences multiple edges to connect distant entities without computationally intensive relational JOINs.
  - *Linear Multi-Hop*: `(s:Student)-[:STUDIES]->(c:Course)-[:BELONGS_TO]->(d:Department)` traces a 2-hop transitive path from Student to Department.
  - *Convergent / Star Multi-Hop*: `(p:Person)-[:ACTED_IN]->(m:Movie)<-[:DIRECTED]-(d:Person)` identifies co-occurring relationships converging onto a common pivot node `m`.
    """,
    "procedure": [
        "Step 1: Review the Theoretical Framework, learning objectives, and key terminology below.",
        "Step 2: Navigate to the 'Simulation' section from the sidebar navigator.",
        "Step 3: Select a Knowledge Graph domain (University, Movies, or E-Commerce).",
        "Step 4: In 'Learning Mode', select a predefined Cypher demonstration query to explore key traversal patterns.",
        "Step 5: Click 'Execute Query' to evaluate the query against the NetworkX knowledge graph simulator.",
        "Step 6: Observe the interactive graph visualization, hop-by-hop traversal animation, and result table.",
        "Step 7: Switch to 'Experiment Mode' to modify clauses or compose custom Cypher queries.",
        "Step 8: Click 'Record Current Trial' to capture parameters, query text, and performance metrics into your session log.",
        "Step 9: Complete the 10-question Concept Assessment Quiz to test your understanding.",
        "Step 10: In 'Report Generation', enter your student credentials, verify your logged trials, and download your formal PDF report."
    ],
    "key_terms": {
        "Knowledge Graph (KG)": "A graph-structured knowledge base representing entities, concepts, and semantic relationships.",
        "Node (Vertex)": "A discrete domain entity stored with an identifier, labels, and key-value properties.",
        "Relationship (Edge)": "A directed, typed link connecting a start node to an end node.",
        "Label": "A tag that categorizes nodes into functional types for schema definition and indexing.",
        "Property": "A key-value attribute pair stored directly on nodes or relationships.",
        "Cypher": "A declarative graph query language utilizing ASCII-art patterns to query property graphs.",
        "MATCH": "The Cypher clause specifying graph path patterns to locate in the database.",
        "WHERE": "The filtering clause applying boolean predicate conditions to matched paths.",
        "RETURN": "The projection clause defining variables, attributes, or aggregates in the output.",
        "Multi-Hop Traversal": "Navigating across a chain of two or more relationships to discover indirect connections.",
        "Aggregation (count)": "Collapsing matching rows to count occurrences, grouping by non-aggregated return fields."
    }
}

QUIZ_QUESTIONS = [
    {
        "id": 1,
        "question": "What is the primary structural characteristic of the Property Graph Model compared to a relational database?",
        "options": [
            "A) It stores data exclusively as serialized plain text documents without schema",
            "B) Entities and their relationships are stored as first-class graph elements with labels and properties",
            "C) Data must always be organized into 3NF normalized rectangular tables linked by foreign keys",
            "D) Relationships cannot have directions, types, or attributes"
        ],
        "answer_index": 1,
        "explanation": "Property graphs treat entities (nodes) and connections (relationships) as first-class constructs with labels and key-value attributes."
    },
    {
        "id": 2,
        "question": "In Cypher ASCII-art syntax, which visual delimiter represents an entity node?",
        "options": [
            "A) Square brackets: [s:Student]",
            "B) Curly braces: {s:Student}",
            "C) Parentheses: (s:Student)",
            "D) Angle brackets: <s:Student>"
        ],
        "answer_index": 2,
        "explanation": "In Cypher, nodes are encapsulated in parentheses e.g. (s:Student) mimicking rounded network vertices."
    },
    {
        "id": 3,
        "question": "Which pattern correctly expresses a directed traversal from student 's' to course 'c' via relationship 'STUDIES'?",
        "options": [
            "A) (s:Student)<-[:STUDIES]-(c:Course)",
            "B) (s:Student)-[:STUDIES]->(c:Course)",
            "C) (s:Student)==[STUDIES]==>(c:Course)",
            "D) (s:Student)->[:STUDIES]->(c:Course)"
        ],
        "answer_index": 1,
        "explanation": "The standard Cypher syntax for a forward directed relationship is -[:REL_TYPE]-> between node parentheses."
    },
    {
        "id": 4,
        "question": "In the query 'MATCH (p:Person)-[:ACTED_IN]->(m:Movie)<-[:DIRECTED]-(d:Person)', what role does the node 'm' play?",
        "options": [
            "A) It serves as the disconnected root of an independent binary tree",
            "B) It is an intermediate pivot node where both directed relationships converge",
            "C) It is discarded by the Cypher engine because actors cannot be linked to directors",
            "D) It creates an infinite cyclical traversal loop"
        ],
        "answer_index": 1,
        "explanation": "Node 'm' acts as a shared convergent pivot: the actor acted in 'm', and the director directed the same film 'm'."
    },
    {
        "id": 5,
        "question": "What is the primary function of the Cypher WHERE clause?",
        "options": [
            "A) To physically delete records from disk storage",
            "B) To filter candidate graph paths matched by the MATCH clause using boolean predicate expressions",
            "C) To define database indexes and foreign key constraints",
            "D) To specify which output columns appear in the final report"
        ],
        "answer_index": 1,
        "explanation": "WHERE filters matched topological candidate paths by evaluating boolean conditions on node or edge properties."
    },
    {
        "id": 6,
        "question": "Why does multi-hop traversal in native graph engines typically outperform multi-table SQL JOINs?",
        "options": [
            "A) Graph engines use index-free adjacency, following direct memory pointers between connected nodes",
            "B) Graph engines convert all queries into static text files",
            "C) Relational databases cannot handle queries with more than two tables",
            "D) Graph engines ignore all relationship directions and types"
        ],
        "answer_index": 0,
        "explanation": "Index-free adjacency enables native graph systems to traverse relationships via direct pointers in O(1) time per step."
    },
    {
        "id": 7,
        "question": "In the query 'MATCH (c:Customer)-[:PURCHASED]->(p:Product) RETURN c.name, count(p) AS products', how is grouping determined?",
        "options": [
            "A) An explicit 'GROUP BY' clause is strictly required in Cypher",
            "B) Non-aggregated fields in the RETURN clause (c.name) implicitly define the grouping keys",
            "C) Cypher counts all products globally and outputs only a single scalar number",
            "D) The query is invalid and causes a syntax exception"
        ],
        "answer_index": 1,
        "explanation": "In Cypher, aggregation functions like count() automatically group by all non-aggregated projection columns in RETURN."
    },
    {
        "id": 8,
        "question": "In the University graph, what is the result of 'MATCH (s:Student) WHERE s.age > 20 RETURN s.name, s.age'?",
        "options": [
            "A) Alice (20), Bob (21), and Charlie (19)",
            "B) Bob (age 21) only",
            "C) Alice (age 20) and Bob (age 21)",
            "D) No rows are returned"
        ],
        "answer_index": 1,
        "explanation": "Alice is 20, Bob is 21, and Charlie is 19. Only Bob has an age strictly greater than 20 (> 20)."
    },
    {
        "id": 9,
        "question": "What is the semantic difference between '-[:TEACHES]->' and '<-[:TEACHES]-' in a Cypher query?",
        "options": [
            "A) There is no difference; direction is completely ignored in Cypher",
            "B) Arrowheads enforce the direction of traversal along the directed graph relationship",
            "C) Backward arrows '<-' convert the query into a delete operation",
            "D) Forward arrows '->' only match undirected relationships"
        ],
        "answer_index": 1,
        "explanation": "The arrowhead specifies the required relationship orientation; '<-[:TEACHES]-' traverses an incoming edge from right to left."
    },
    {
        "id": 10,
        "question": "What happens if a user submits a mutating clause such as 'CREATE' or 'MERGE' in this read-only lab simulator?",
        "options": [
            "A) The entire database is wiped without notice",
            "B) The query executes and silently modifies the server graph",
            "C) A clear educational notice is displayed explaining that mutating clauses are disabled in this simulator",
            "D) The application crashes with an unhandled runtime error"
        ],
        "answer_index": 2,
        "explanation": "The simulator is designed for educational exploration of retrieval queries; mutating statements trigger a clear educational error."
    }
]


# ======================================================================================
# 2. LAB REPORT PDF EXPORTER
# ======================================================================================

class LabReportPDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}} | Virtual Laboratory Report - Experiment 10", align="C")


def generate_pdf_report(student_name: str, student_id: str, date_str: str,
                        trials_df: pd.DataFrame, quiz_score: int, quiz_total: int,
                        student_notes: str) -> bytes:
    """Compiles experiment benchmark records into a proper, formatted PDF report document."""
    pdf = LabReportPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    # Document Header Title
    pdf.set_text_color(15, 23, 42)
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 8, EXPERIMENT_CONFIG["title"], align="L", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(0, 6, "Department of Computer Engineering - Knowledge Engineering Virtual Laboratory", align="L", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # Student & Session Info Box
    pdf.set_fill_color(241, 245, 249)
    pdf.set_draw_color(203, 213, 225)
    pdf.rect(10, 26, 190, 22, "FD")

    pdf.set_xy(14, 28)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(38, 5, "Student Name:", 0)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(57, 5, student_name or "N/A", 0)

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(35, 5, "Student Roll / ID:", 0)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(50, 5, student_id or "Roll No. 47", 1)

    pdf.set_xy(14, 36)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(38, 5, "Experiment Date:", 0)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(57, 5, date_str or datetime.now().strftime("%Y-%m-%d"), 0)

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(35, 5, "Quiz Evaluation:", 0)
    pdf.set_font("Helvetica", "B", 9)
    if quiz_score >= max(1, quiz_total // 2):
        pdf.set_text_color(16, 185, 129)
    else:
        pdf.set_text_color(239, 68, 68)
    perc = int((quiz_score / quiz_total) * 100 if quiz_total else 0)
    pdf.cell(50, 5, f"{quiz_score} / {quiz_total} ({perc}%)", 1)

    pdf.ln(12)

    # 1. Learning Objectives
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 7, "1. Learning Objectives", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(51, 65, 85)
    for obj in EXPERIMENT_CONFIG["objectives"]:
        clean_obj = str(obj).replace("$", "").replace("\\", "")
        pdf.cell(5, 5, "-", 0)
        pdf.cell(0, 5, f" {clean_obj}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # 2. Recorded Trials Table
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 7, "2. Recorded Experimental Queries & Traversal Trials", new_x="LMARGIN", new_y="NEXT")

    if trials_df.empty:
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(0, 6, "No Cypher simulation trials recorded during this session.", new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.set_fill_color(37, 99, 235)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 8)

        cols = ["Trial #", "Graph", "Query", "Rows", "Hops", "Time (ms)", "Timestamp"]
        display_cols = [c for c in cols if c in trials_df.columns]
        col_widths = {
            "Trial #": 15,
            "Graph": 24,
            "Query": 85,
            "Rows": 15,
            "Hops": 15,
            "Time (ms)": 18,
            "Timestamp": 18
        }

        for c in display_cols:
            w = col_widths.get(c, 25)
            pdf.cell(w, 6, str(c), 1, 0, "C", True)
        pdf.ln()

        pdf.set_fill_color(248, 250, 252)
        pdf.set_text_color(30, 41, 59)
        pdf.set_font("Helvetica", "", 7)
        fill = False

        for _, row in trials_df.iterrows():
            for c in display_cols:
                w = col_widths.get(c, 25)
                val = row.get(c, "")
                if c == "Query":
                    val_str = str(val)[:46] + ("..." if len(str(val)) > 46 else "")
                elif isinstance(val, float):
                    val_str = f"{val:.2f}"
                else:
                    val_str = str(val)
                pdf.cell(w, 5, val_str, 1, 0, "C" if c != "Query" else "L", fill)
            pdf.ln()
            fill = not fill
    pdf.ln(5)

    # 3. Observations & Discussion
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 7, "3. Observations, Traversal Analysis & Conclusion", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(51, 65, 85)
    notes_text = student_notes.strip() if student_notes.strip() else (
        "The experimental trials successfully verified that declarative Cypher pattern queries (MATCH, WHERE, RETURN) "
        "effectively retrieve nodes, relationships, and multi-hop paths from Knowledge Graphs without requiring relational JOINs. "
        "Traversal across directed edges and aggregations via count() demonstrated consistent execution behavior."
    )
    pdf.multi_cell(0, 5, notes_text)
    pdf.ln(8)

    # Sign-off line
    pdf.set_draw_color(180, 180, 180)
    pdf.line(130, pdf.get_y() + 15, 190, pdf.get_y() + 15)
    pdf.set_xy(130, pdf.get_y() + 17)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(60, 4, "Instructor / Student Signature", align="C")

    return bytes(pdf.output())


# ======================================================================================
# 3. GRAPH VISUALIZATION & ANIMATION RENDERER (PLOTLY)
# ======================================================================================

LABEL_COLOR_MAP = {
    "Student": "#2563EB",       # Royal Blue
    "Course": "#059669",        # Emerald Green
    "Teacher": "#D97706",       # Amber / Orange
    "Department": "#7C3AED",    # Purple
    "Person": "#2563EB",        # Royal Blue
    "Movie": "#D97706",         # Amber / Orange
    "Genre": "#7C3AED",         # Purple
    "Customer": "#0D9488",      # Teal
    "Product": "#4F46E5",       # Indigo
    "Category": "#DB2777"       # Pink / Magenta
}

def get_graph_layout_positions(graph: nx.DiGraph) -> Dict[str, Tuple[float, float]]:
    """Calculates deterministic layout coordinates for nodes in the graph."""
    return nx.spring_layout(graph, seed=42, k=1.2, iterations=100)


def render_knowledge_graph(graph: nx.DiGraph,
                           active_nodes: Optional[set] = None,
                           active_edges: Optional[List[Tuple[str, str, str]]] = None,
                           current_hop_desc: str = "") -> go.Figure:
    """
    Renders an interactive Plotly knowledge graph visualization.
    Highlights active nodes and edges during traversal matching.
    """
    pos = get_graph_layout_positions(graph)
    fig = go.Figure()

    is_highlight_mode = (active_nodes is not None) or (active_edges is not None)
    active_node_set = active_nodes if active_nodes is not None else set()
    active_edge_set = set()
    if active_edges:
        for item in active_edges:
            active_edge_set.add((item[0], item[1]))

    # Edge annotations (Arrows) and Edge Labels
    annotations = []
    edge_label_x, edge_label_y, edge_label_text, edge_label_color = [], [], [], []

    for u, v, data in graph.edges(data=True):
        rel_type = data.get("type", "RELATED")
        is_active_edge = (u, v) in active_edge_set

        if is_highlight_mode:
            arrow_color = "#DC2626" if is_active_edge else "rgba(203, 213, 225, 0.4)"
            arrow_width = 3.0 if is_active_edge else 1.0
        else:
            arrow_color = "#64748B"
            arrow_width = 1.6

        annotations.append(dict(
            ax=pos[u][0], ay=pos[u][1],
            x=pos[v][0], y=pos[v][1],
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True,
            arrowhead=3,
            arrowsize=1.2,
            arrowwidth=arrow_width,
            arrowcolor=arrow_color,
            opacity=1.0 if (not is_highlight_mode or is_active_edge) else 0.35
        ))

        mx = (pos[u][0] + pos[v][0]) / 2.0
        my = (pos[u][1] + pos[v][1]) / 2.0
        edge_label_x.append(mx)
        edge_label_y.append(my)
        edge_label_text.append(f"[:{rel_type}]")
        edge_label_color.append("#991B1B" if is_active_edge else "#475569")

    # Edge Labels trace
    fig.add_trace(go.Scatter(
        x=edge_label_x, y=edge_label_y,
        mode="text",
        text=edge_label_text,
        textfont=dict(size=9, color=edge_label_color, family="Courier New"),
        hoverinfo="none",
        showlegend=False
    ))

    # Add Nodes
    node_x, node_y, node_colors, node_sizes, node_borders, node_texts, hover_texts = [], [], [], [], [], [], []

    for n, data in graph.nodes(data=True):
        node_x.append(pos[n][0])
        node_y.append(pos[n][1])
        label = data.get("label", "Entity")
        base_color = LABEL_COLOR_MAP.get(label, "#3B82F6")

        is_active_node = n in active_node_set

        if is_highlight_mode:
            if is_active_node:
                node_colors.append("#F59E0B")  # Vibrant Amber highlight
                node_sizes.append(34)
                node_borders.append(dict(width=3, color="#78350F"))
            else:
                node_colors.append("rgba(226, 232, 240, 0.7)")
                node_sizes.append(22)
                node_borders.append(dict(width=1, color="#CBD5E1"))
        else:
            node_colors.append(base_color)
            node_sizes.append(28)
            node_borders.append(dict(width=2, color="#FFFFFF"))

        node_texts.append(f"<b>{n}</b><br><span style='font-size:10px;'>({label})</span>")

        props_str = "<br>".join([f"• <b>{k}</b>: {v}" for k, v in data.items() if k != "label"])
        hover_texts.append(f"<b>{n}</b> [:{label}]<br>{props_str}")

    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        text=node_texts,
        textposition="top center",
        hovertext=hover_texts,
        hoverinfo="text",
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(
                width=[b["width"] for b in node_borders],
                color=[b["color"] for b in node_borders]
            )
        ),
        showlegend=False
    ))

    title_text = f"<b>{graph.graph.get('name', 'Knowledge Graph')}</b>"
    if current_hop_desc:
        title_text += f"<br><span style='font-size:12px; color:#DC2626;'>{current_hop_desc}</span>"

    fig.update_layout(
        title=dict(text=title_text, font=dict(size=14, color="#1E293B")),
        annotations=annotations,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1.4, 1.4]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1.4, 1.4]),
        height=480,
        margin=dict(l=25, r=25, t=55, b=25),
        plot_bgcolor="#F8FAFC",
        paper_bgcolor="#FFFFFF"
    )

    return fig


# ======================================================================================
# 4. SECTION RENDERERS: THEORY, SIMULATION, QUIZ, REPORT
# ======================================================================================

def render_theory_section():
    """Renders Section 1: Theory, Background, Objectives, and Procedure."""
    st.header("Theoretical Framework & Concepts")
    st.markdown(THEORY_CONTENT["background"])

    st.divider()
    st.subheader("Learning Objectives (Roll No. 47 / Experiment 10)")
    for i, obj in enumerate(EXPERIMENT_CONFIG["objectives"]):
        st.write(f"- **Goal {i+1}**: {obj}")

    st.divider()
    st.subheader("Experimental Procedure")
    for step in THEORY_CONTENT["procedure"]:
        st.write(f"- {step}")

    st.divider()
    with st.expander("Key Terminology & Cypher Reference Guide", expanded=True):
        var_df = pd.DataFrame(
            list(THEORY_CONTENT["key_terms"].items()),
            columns=["Graph / Cypher Term", "Technical Definition & Semantic Role"]
        )
        st.table(var_df)


def render_simulation_section():
    """Renders Section 2: Interactive Execution Sandbox, Plotly Visualizer, and Data Logger."""
    st.header("Interactive Cypher Knowledge Graph Sandbox")
    st.caption("Explore graph topologies, formulate Cypher queries, step through multi-hop traversals, and log trial data.")

    # 1. Domain Selector
    col_graph, col_mode = st.columns([1.5, 2.5])
    with col_graph:
        selected_graph_name = st.selectbox(
            "Select Knowledge Graph Domain",
            options=["University", "Movies", "E-Commerce"],
            index=0,
            key="selected_graph_name"
        )
    with col_mode:
        sim_mode = st.radio(
            "Investigation Mode",
            options=["Learning Mode (Demonstration Queries)", "Experiment Mode (Free-Form Cypher Editor)"],
            horizontal=True,
            key="sim_mode"
        )

    current_graph = ce.GRAPH_REGISTRY[selected_graph_name]()

    # 2. Query Setup depending on Mode
    target_query = ""
    demo_info = None

    if "Learning Mode" in sim_mode:
        demo_subset = [d for d in ce.DEMONSTRATION_QUERIES if d["graph"] == selected_graph_name]
        demo_titles = [f"Query {d['id']}: {d['title']}" for d in demo_subset]
        
        selected_demo_title = st.selectbox(
            "Select Demonstration Pattern",
            options=demo_titles,
            index=0,
            key=f"demo_query_select_{selected_graph_name}"
        )
        selected_demo_idx = demo_titles.index(selected_demo_title)
        demo_info = demo_subset[selected_demo_idx]

        st.info(f"**Question:** {demo_info['question']}\n\n**Concept Taught:** {demo_info['concept']}")
        target_query = st.text_area(
            "Cypher Query (Learning Mode)",
            value=demo_info["query"],
            height=70,
            key=f"query_input_demo_{demo_info['id']}"
        )
    else:
        st.markdown("**Cypher Query Editor (Supported: MATCH, WHERE, RETURN, count)**")
        default_custom = "MATCH (s:Student)-[:STUDIES]->(c:Course) RETURN s.name, c.name"
        if selected_graph_name == "Movies":
            default_custom = "MATCH (p:Person)-[:ACTED_IN]->(m:Movie)<-[:DIRECTED]-(d:Person) RETURN p.name, m.title, d.name"
        elif selected_graph_name == "E-Commerce":
            default_custom = "MATCH (c:Customer)-[:PURCHASED]->(p:Product)-[:BELONGS_TO]->(cat:Category) RETURN c.name, p.name, cat.name"

        target_query = st.text_area(
            "Enter Cypher Query",
            value=st.session_state.get("custom_query_text", default_custom),
            height=85,
            key="custom_query_editor"
        )
        st.session_state["custom_query_text"] = target_query

        with st.expander("Supported Cypher Syntax Cheat-Sheet"):
            st.code("""-- 1. Single Node Retrieval with Properties:
MATCH (s:Student) RETURN s.name, s.age

-- 2. Property Filtering with WHERE:
MATCH (s:Student) WHERE s.age > 20 RETURN s.name, s.age

-- 3. One-Hop Directed Traversal:
MATCH (s:Student)-[:STUDIES]->(c:Course) RETURN s.name, c.name

-- 4. Multi-Hop Transitive Path:
MATCH (s:Student)-[:STUDIES]->(c:Course)-[:BELONGS_TO]->(d:Department) RETURN s.name, c.name, d.name

-- 5. Convergent Multi-Hop Pattern:
MATCH (p:Person)-[:ACTED_IN]->(m:Movie)<-[:DIRECTED]-(d:Person) RETURN p.name, m.title, d.name

-- 6. Aggregation with count():
MATCH (c:Customer)-[:PURCHASED]->(p:Product) RETURN c.name, count(p) AS products""", language="sql")

    # 3. Action Buttons
    col_exec, col_anim = st.columns([1.5, 2.5])
    with col_exec:
        run_clicked = st.button("Execute Cypher Query", type="primary", width="stretch")
    with col_anim:
        play_anim_clicked = st.button("Play Hop-by-Hop Traversal Animation", width="stretch")

    if run_clicked or ("last_result" not in st.session_state) or (st.session_state.get("last_query") != target_query):
        with st.spinner("Parsing Cypher & evaluating graph pattern..."):
            res = ce.execute_cypher_query(current_graph, target_query)
            st.session_state["last_result"] = res
            st.session_state["last_query"] = target_query
            st.session_state["last_graph"] = selected_graph_name

    res = st.session_state.get("last_result", {})

    st.divider()

    # 4. Status & Performance Metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        if res.get("success"):
            st.metric("Query Status", "SUCCESS", delta="Valid Pattern")
        else:
            st.metric("Query Status", "FAILED", delta="-Syntax Error")
    with m2:
        num_rows = len(res.get("dataframe", []))
        st.metric("Records Returned", f"{num_rows} row(s)")
    with m3:
        hops_count = len(res.get("matched_edges", []))
        st.metric("Matched Relationships", f"{hops_count} edge(s)")
    with m4:
        exec_ms = res.get("execution_time_ms", 0.0)
        st.metric("Execution Latency", f"{exec_ms} ms")

    if not res.get("success"):
        st.error(f"**Query Execution Error:**\n\n{res.get('error')}")
        fig = render_knowledge_graph(current_graph)
        st.plotly_chart(fig, width="stretch")
        return

    # 5. Traversal Animation & Interactive Graph
    paths = res.get("traversal_paths", [])
    all_matched_nodes = set(res.get("matched_nodes", []))
    all_matched_edges = res.get("matched_edges", [])

    step_descriptions = ["Step 0: Overview of Knowledge Graph"]
    step_node_subsets = [set()]
    step_edge_subsets = [[]]

    if paths:
        sample_path = paths[0]
        cumulative_nodes = set()
        cumulative_edges = []

        for item in sample_path:
            if item["type"] == "node":
                cumulative_nodes = set(cumulative_nodes)
                cumulative_nodes.add(item["id"])
                step_descriptions.append(f"Hop {len(step_descriptions)}: Locate Node '{item['id']}' (:{item.get('label')})")
                step_node_subsets.append(set(cumulative_nodes))
                step_edge_subsets.append(list(cumulative_edges))
            elif item["type"] == "edge":
                cumulative_edges = list(cumulative_edges)
                cumulative_edges.append((item["u"], item["v"], item["rel_type"]))
                step_descriptions.append(f"Hop {len(step_descriptions)}: Traverse -[:{item['rel_type']}]-> ({item['u']} -> {item['v']})")
                step_node_subsets.append(set(cumulative_nodes))
                step_edge_subsets.append(list(cumulative_edges))

        step_descriptions.append(f"Final: Complete Matched Paths ({len(paths)} path[s] discovered)")
        step_node_subsets.append(all_matched_nodes)
        step_edge_subsets.append(all_matched_edges)

    col_scrub, col_desc = st.columns([2, 3])
    with col_scrub:
        if len(step_descriptions) > 1:
            step_idx = st.slider(
                "Hop-by-Hop Traversal Scrubber",
                min_value=0,
                max_value=len(step_descriptions) - 1,
                value=len(step_descriptions) - 1,
                key="traversal_step_slider"
            )
        else:
            step_idx = 0
            st.caption("No multi-hop traversal steps to scrub for single-node / empty queries.")
    with col_desc:
        st.markdown(f"**Active Step:** `{step_descriptions[step_idx]}`")

    plot_placeholder = st.empty()

    if play_anim_clicked:
        for s in range(len(step_descriptions)):
            curr_nodes = step_node_subsets[s] if s > 0 else None
            curr_edges = step_edge_subsets[s] if s > 0 else None
            fig_anim = render_knowledge_graph(
                current_graph,
                active_nodes=curr_nodes,
                active_edges=curr_edges,
                current_hop_desc=step_descriptions[s]
            )
            plot_placeholder.plotly_chart(fig_anim, width="stretch")
            time.sleep(0.55)
    else:
        active_n = step_node_subsets[step_idx] if step_idx > 0 else None
        active_e = step_edge_subsets[step_idx] if step_idx > 0 else None
        fig = render_knowledge_graph(
            current_graph,
            active_nodes=active_n,
            active_edges=active_e,
            current_hop_desc=step_descriptions[step_idx] if step_idx > 0 else ""
        )
        plot_placeholder.plotly_chart(fig, width="stretch")

    # 6. Educational "What Happened?" & "Explain Query"
    st.subheader("Query Execution & Traversal Explanation")
    st.info(f"**What Happened:** {res['explanation']['what_happened']}")

    with st.expander("Explain Query: MATCH -> Traversal -> WHERE -> RETURN Breakdown", expanded=True):
        eq1, eq2 = st.columns(2)
        with eq1:
            st.markdown(f"**1. Pattern Matching (MATCH):**\n{res['explanation']['match_phase']}")
            st.markdown(f"**2. Graph Traversal Walk:**\n{res['explanation']['traversal_phase']}")
        with eq2:
            st.markdown(f"**3. Predicate Evaluation (WHERE):**\n{res['explanation']['where_phase']}")
            st.markdown(f"**4. Projection & Aggregation (RETURN):**\n{res['explanation']['return_phase']}")

    # 7. Tabular Query Results
    st.subheader("Query Results Table")
    df_res = res.get("dataframe", pd.DataFrame())
    if not df_res.empty:
        st.dataframe(df_res, width="stretch", hide_index=True)
    else:
        st.warning("Query executed successfully, but 0 records satisfied the criteria.")

    # 8. Experimental Data Logger
    st.divider()
    st.subheader("Experimental Data Log Book")
    col_log1, col_log2 = st.columns([1.5, 3.5])

    with col_log1:
        st.caption("Capture current query parameters and metrics into your session trial table:")
        if st.button("Record Current Trial", type="primary", width="stretch"):
            trial_record = {
                "Trial #": len(st.session_state["trials"]) + 1,
                "Graph": selected_graph_name,
                "Query": target_query,
                "Rows": len(df_res),
                "Hops": len(all_matched_edges),
                "Time (ms)": res.get("execution_time_ms", 0.0),
                "Timestamp": datetime.now().strftime("%H:%M:%S")
            }
            st.session_state["trials"].append(trial_record)
            st.toast(f"Trial #{trial_record['Trial #']} successfully saved!")

        if st.button("Clear Logged Trials", width="stretch"):
            st.session_state["trials"] = []
            st.toast("Trial log cleared.")

    with col_log2:
        if st.session_state["trials"]:
            df_trials = pd.DataFrame(st.session_state["trials"])
            st.dataframe(df_trials, width="stretch", hide_index=True)
            csv_data = df_trials.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Download Trials as CSV",
                data=csv_data,
                file_name="cypher_experiment_trials.csv",
                mime="text/csv",
                width="stretch"
            )
        else:
            st.info("No trials recorded yet. Execute queries and click 'Record Current Trial' to build your dataset.")


def render_quiz_section():
    """Renders Section 3: Assessment Quiz with Self-Grading and Feedback."""
    st.header("Concept Assessment Quiz")
    st.write("Answer the 10 conceptual questions below to test your understanding of Knowledge Graphs and Cypher.")

    with st.form("lab_quiz_form"):
        user_responses = {}
        for q in QUIZ_QUESTIONS:
            st.subheader(f"Question {q['id']}")
            st.write(q["question"])
            selected = st.radio(
                label=f"Options for Question {q['id']}:",
                options=q["options"],
                index=st.session_state["quiz_answers"].get(q["id"], 0),
                key=f"quiz_radio_{q['id']}",
                label_visibility="collapsed"
            )
            user_responses[q["id"]] = q["options"].index(selected)

        submitted = st.form_submit_button("Submit Quiz for Grading", type="primary")

    if submitted:
        score = 0
        st.session_state["quiz_answers"] = user_responses
        st.session_state["quiz_submitted"] = True

        st.divider()
        st.subheader("Evaluation Results and Detailed Feedback")
        for q in QUIZ_QUESTIONS:
            user_ans = user_responses.get(q["id"])
            correct_ans = q["answer_index"]
            if user_ans == correct_ans:
                score += 1
                st.success(f"**Question {q['id']}: Correct!**\n\n_{q['explanation']}_")
            else:
                st.error(f"**Question {q['id']}: Incorrect.** (Your answer: {q['options'][user_ans]})\n\n"
                         f"**Correct Answer:** {q['options'][correct_ans]}\n\n"
                         f"**Reasoning:** _{q['explanation']}_")

        st.session_state["quiz_score"] = score
        perc = (score / len(QUIZ_QUESTIONS)) * 100
        st.info(f"Final Quiz Score: **{score} / {len(QUIZ_QUESTIONS)}** ({perc:.0f}%)")

    elif st.session_state.get("quiz_submitted", False):
        st.success(f"Quiz already submitted. Current score: **{st.session_state.get('quiz_score', 0)} / {len(QUIZ_QUESTIONS)}**")


def render_report_section():
    """Renders Section 4: Dynamic Lab Report Generator with Guaranteed PDF Export."""
    st.header("Lab Report Generation")
    st.write("Compile your student details, experimental query trials, quiz evaluation, and observations into an official PDF report.")

    col1, col2, col3 = st.columns(3)
    with col1:
        student_name = st.text_input("Student Name", value=st.session_state["student_info"].get("name", "Student Name"))
    with col2:
        student_id = st.text_input("Student Roll / ID", value=st.session_state["student_info"].get("id", "Roll No. 47"))
    with col3:
        lab_date = st.date_input("Experiment Date", value=datetime.now())

    st.session_state["student_info"]["name"] = student_name
    st.session_state["student_info"]["id"] = student_id
    st.session_state["student_info"]["date"] = str(lab_date)

    st.subheader("Technical Observations & Conclusions")
    student_notes = st.text_area(
        "Enter your interpretation of results, query comparisons, and observations:",
        value=st.session_state.get("student_notes", (
            "The experiment demonstrated that declarative Cypher pattern queries (MATCH, WHERE, RETURN) "
            "provide an intuitive, efficient mechanism for traversing knowledge graphs. Single-hop traversals directly follow "
            "pointers between adjacent nodes, while multi-hop patterns link distant entities without relational JOIN operations. "
            "The WHERE clause successfully filtered candidates, and aggregation via count() performed automatic grouping by non-aggregated columns."
        )),
        height=130
    )
    st.session_state["student_notes"] = student_notes

    trials_df = pd.DataFrame(st.session_state["trials"]) if st.session_state["trials"] else pd.DataFrame()

    st.divider()
    st.subheader("Report Summary Preview")
    st.write(f"**Experiment:** {EXPERIMENT_CONFIG['title']}")
    st.write(f"**Student:** {student_name} | **Roll / ID:** {student_id} | **Date:** {lab_date}")
    st.write(f"**Quiz Score:** {st.session_state.get('quiz_score', 0)} / {len(QUIZ_QUESTIONS)}")

    if not trials_df.empty:
        st.dataframe(trials_df, hide_index=True, width="stretch")
    else:
        st.info("Note: No trials recorded in the Simulation tab yet. The report will reflect 0 recorded trials.")

    # Generate PDF bytes and write file to disk
    pdf_bytes = generate_pdf_report(
        student_name=student_name,
        student_id=student_id,
        date_str=str(lab_date),
        trials_df=trials_df,
        quiz_score=st.session_state.get("quiz_score", 0),
        quiz_total=len(QUIZ_QUESTIONS),
        student_notes=student_notes
    )

    # Save to local files for guaranteed download
    os.makedirs("static", exist_ok=True)
    with open("static/lab_report.pdf", "wb") as f:
        f.write(pdf_bytes)
    with open("lab_report.pdf", "wb") as f:
        f.write(pdf_bytes)

    st.divider()
    st.subheader("Download Official Lab Report (.pdf)")

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        st.link_button(
            "Open / Download PDF Document",
            url="/app/static/lab_report.pdf",
            type="primary",
            width="stretch"
        )

    with col_btn2:
        st.download_button(
            label="Download lab_report.pdf",
            data=pdf_bytes,
            file_name="lab_report_experiment_10.pdf",
            mime="application/pdf",
            key="stream_pdf_btn",
            width="stretch"
        )


# ======================================================================================
# 5. MAIN ENTRYPOINT & NAVIGATION
# ======================================================================================

def init_session_state():
    """Initializes Streamlit session state variables."""
    if "trials" not in st.session_state:
        st.session_state["trials"] = []
    if "quiz_answers" not in st.session_state:
        st.session_state["quiz_answers"] = {}
    if "quiz_submitted" not in st.session_state:
        st.session_state["quiz_submitted"] = False
    if "quiz_score" not in st.session_state:
        st.session_state["quiz_score"] = 0
    if "student_info" not in st.session_state:
        st.session_state["student_info"] = {
            "name": "Student Name",
            "id": "Roll No. 47",
            "date": str(datetime.now().date())
        }
    if "student_notes" not in st.session_state:
        st.session_state["student_notes"] = ""


def main():
    st.set_page_config(
        page_title="Exp 10: Query Knowledge Graphs Using Cypher",
        page_icon=None,
        layout="wide"
    )

    init_session_state()

    # Native Streamlit Title (No custom CSS)
    st.title(EXPERIMENT_CONFIG["title"])

    # Navigation Sidebar
    section = st.sidebar.radio(
        "Lab Navigator",
        options=["Theory", "Simulation", "Quiz", "Report Generation"]
    )

    st.sidebar.divider()
    st.sidebar.subheader("Progress Tracker")
    quiz_status = "Done" if st.session_state.get("quiz_submitted", False) else "Pending"
    st.sidebar.write(f"- **Quiz Status:** {quiz_status}")
    if st.session_state.get("quiz_submitted", False):
        st.sidebar.write(f"- **Quiz Score:** `{st.session_state.get('quiz_score', 0)} / {len(QUIZ_QUESTIONS)}`")
    st.sidebar.write(f"- **Recorded Trials:** `{len(st.session_state['trials'])}`")

    # Section Dispatcher
    if section == "Theory":
        render_theory_section()
    elif section == "Simulation":
        render_simulation_section()
    elif section == "Quiz":
        render_quiz_section()
    elif section == "Report Generation":
        render_report_section()


if __name__ == "__main__":
    main()
