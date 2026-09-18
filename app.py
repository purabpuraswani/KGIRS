"""
Virtual Laboratory Experiment 10: Query Knowledge Graphs Using Cypher
Roll No.: 47

Preserves the 4-Section Architecture:
  1. Theory: Understanding Knowledge Graphs & Cypher (Visual Conceptual Guide)
  2. Simulation: Knowledge Graph Explorer, Cypher Query Engine, Traversal Animation & Trial Logger
  3. Quiz: 10 Practical Conceptual Questions with Automatic Scoring
  4. Report Generation: Student Credentials, Recorded Trials, Observations & PDF Export
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
        "Retrieve entities (nodes) and their attributes from a knowledge graph using Cypher.",
        "Query direct semantic connections between entities via one-hop relationship traversal.",
        "Filter graph paths using boolean conditions on node properties with the WHERE clause.",
        "Traverse complex multi-hop paths to discover indirect relationships and convergent patterns.",
        "Perform aggregation using count() with implicit group-by semantics.",
        "Synthesize query observations, evaluate execution metrics, and document conclusions."
    ]
}

QUIZ_QUESTIONS = [
    {
        "id": 1,
        "question": "What is the fundamental structure of a Knowledge Graph?",
        "options": [
            "A) Serialized plain-text documents with no defined schema",
            "B) Entities represented as nodes and connections represented as directed relationships",
            "C) Strictly isolated relational tables connected only by database foreign keys",
            "D) Hierarchical XML trees where connections cannot have types or directions"
        ],
        "answer_index": 1,
        "explanation": "A knowledge graph natively represents entities as nodes and connections between them as relationships."
    },
    {
        "id": 2,
        "question": "In Cypher syntax, which visual symbol represents an entity node?",
        "options": [
            "A) Square brackets: [s:Student]",
            "B) Curly braces: {s:Student}",
            "C) Parentheses: (s:Student)",
            "D) Angle brackets: <s:Student>"
        ],
        "answer_index": 2,
        "explanation": "In Cypher, nodes are enclosed in parentheses e.g. (s:Student) mimicking rounded network vertices."
    },
    {
        "id": 3,
        "question": "Which Cypher pattern correctly denotes a forward directed relationship from student 's' to course 'c'?",
        "options": [
            "A) (s:Student)<-[:STUDIES]-(c:Course)",
            "B) (s:Student)-[:STUDIES]->(c:Course)",
            "C) (s:Student)-->[STUDIES]-->(c:Course)",
            "D) (s:Student)===[:STUDIES]==>(c:Course)"
        ],
        "answer_index": 1,
        "explanation": "The standard syntax for a forward directed relationship is -[:REL_TYPE]->."
    },
    {
        "id": 4,
        "question": "What does the query 'MATCH (s:Student)-[:STUDIES]->(c:Course) RETURN s.name, c.name' retrieve?",
        "options": [
            "A) All teachers and their assigned departments",
            "B) Each student and the course they are currently studying",
            "C) Only students older than 20 years old",
            "D) The total number of courses offered by the university"
        ],
        "answer_index": 1,
        "explanation": "The query traverses the 1-hop [:STUDIES] relationship between students and courses, returning their names."
    },
    {
        "id": 5,
        "question": "In the query 'MATCH (p:Person)-[:ACTED_IN]->(m:Movie)<-[:DIRECTED]-(d:Person)', what is the structural role of node 'm'?",
        "options": [
            "A) It is a disconnected outlier node",
            "B) It serves as a shared convergent pivot node connecting the actor and director",
            "C) It deletes all relationships attached to it",
            "D) It creates an infinite cyclical traversal loop"
        ],
        "answer_index": 1,
        "explanation": "Node 'm' acts as a shared pivot where the incoming ACTED_IN and DIRECTED edges converge on the same film."
    },
    {
        "id": 6,
        "question": "In the University graph, what is the output of 'MATCH (s:Student) WHERE s.age > 20 RETURN s.name, s.age'?",
        "options": [
            "A) Alice (age 20) and Bob (age 21)",
            "B) Bob (age 21) only",
            "C) Charlie (age 19) only",
            "D) All 3 students"
        ],
        "answer_index": 1,
        "explanation": "Alice is 20, Bob is 21, and Charlie is 19. Only Bob has age > 20."
    },
    {
        "id": 7,
        "question": "What is the primary function of the WHERE clause in a Cypher query?",
        "options": [
            "A) To physically remove nodes from the disk",
            "B) To filter candidate graph paths based on boolean property predicates",
            "C) To create new directed edges between existing nodes",
            "D) To specify which output columns appear in the result table"
        ],
        "answer_index": 1,
        "explanation": "WHERE filters matched candidate paths by evaluating conditions on node or relationship properties."
    },
    {
        "id": 8,
        "question": "Why is multi-hop traversal in graph databases more efficient than multi-table SQL JOINs?",
        "options": [
            "A) Graph traversals use index-free adjacency, following direct pointers between connected nodes",
            "B) Graph engines convert all queries into flat text files",
            "C) Relational databases cannot handle more than two tables",
            "D) Graph engines skip checking node labels and relationship types"
        ],
        "answer_index": 0,
        "explanation": "Index-free adjacency allows the engine to follow direct pointers between nodes without global table scans."
    },
    {
        "id": 9,
        "question": "In 'MATCH (c:Customer)-[:PURCHASED]->(p:Product) RETURN c.name, count(p) AS products', how is grouping determined?",
        "options": [
            "A) An explicit 'GROUP BY' clause is mandatory in Cypher",
            "B) Non-aggregated fields in RETURN (c.name) implicitly act as the grouping keys",
            "C) The query counts all products globally and discards customer names",
            "D) Cypher cannot perform aggregation without external Python code"
        ],
        "answer_index": 1,
        "explanation": "In Cypher, aggregation functions automatically group results by any non-aggregated columns present in RETURN."
    },
    {
        "id": 10,
        "question": "What is the function of the RETURN clause in a Cypher query?",
        "options": [
            "A) To terminate the database process immediately",
            "B) To specify which node properties, variables, or aggregated values to project in the result",
            "C) To define a new database constraint",
            "D) To navigate backwards along a relationship"
        ],
        "answer_index": 1,
        "explanation": "The RETURN clause defines the output columns and projections emitted from the matched graph paths."
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
    """Compiles experiment benchmark records into an official PDF report document."""
    pdf = LabReportPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    # Document Header Title
    pdf.set_text_color(15, 23, 42)
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 8, EXPERIMENT_CONFIG["title"], align="L", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(0, 5, "Department of Computer Engineering - Knowledge Engineering Virtual Laboratory", align="L", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # Student & Session Info Box
    pdf.set_fill_color(241, 245, 249)
    pdf.set_draw_color(203, 213, 225)
    pdf.rect(10, 25, 190, 20, "FD")

    pdf.set_xy(14, 27)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(35, 5, "Student Name:", 0)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(60, 5, student_name or "N/A", 0)

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(35, 5, "Student Roll / ID:", 0)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(50, 5, student_id or "Roll No. 47", 1)

    pdf.set_xy(14, 34)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(35, 5, "Experiment Date:", 0)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(60, 5, date_str or datetime.now().strftime("%Y-%m-%d"), 0)

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

    pdf.ln(10)

    # 1. Objectives
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 6, "1. Learning Objectives", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(51, 65, 85)
    for obj in EXPERIMENT_CONFIG["objectives"]:
        pdf.cell(5, 4.5, "-", 0)
        pdf.cell(0, 4.5, f" {obj}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # 2. Knowledge Graphs Used
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 6, "2. Knowledge Graph Domains Evaluated", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(51, 65, 85)
    pdf.cell(0, 4.5, "1. University Graph (10 nodes: Students, Courses, Teachers, Departments; 8 relationships: STUDIES, TEACHES, BELONGS_TO)", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 4.5, "2. Movie Graph (10 nodes: Actors, Directors, Movies, Genres; 9 relationships: ACTED_IN, DIRECTED, HAS_GENRE)", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 4.5, "3. E-Commerce Graph (9 nodes: Customers, Products, Categories; 10 relationships: PURCHASED, BELONGS_TO)", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # 3. Recorded Trials Table
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 6, "3. Recorded Experimental Query Trials", new_x="LMARGIN", new_y="NEXT")

    if trials_df.empty:
        pdf.set_font("Helvetica", "I", 8.5)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(0, 5, "No Cypher simulation trials recorded during this session.", new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.set_fill_color(37, 99, 235)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 7.5)

        cols = ["Trial #", "Graph", "Query Type", "Query", "Rows", "Hops", "Time (ms)", "Timestamp"]
        display_cols = [c for c in cols if c in trials_df.columns]
        col_widths = {
            "Trial #": 12,
            "Graph": 20,
            "Query Type": 26,
            "Query": 72,
            "Rows": 12,
            "Hops": 12,
            "Time (ms)": 16,
            "Timestamp": 18
        }

        for c in display_cols:
            w = col_widths.get(c, 20)
            pdf.cell(w, 5.5, str(c), 1, 0, "C", True)
        pdf.ln()

        pdf.set_fill_color(248, 250, 252)
        pdf.set_text_color(30, 41, 59)
        pdf.set_font("Helvetica", "", 7)
        fill = False

        for _, row in trials_df.iterrows():
            for c in display_cols:
                w = col_widths.get(c, 20)
                val = row.get(c, "")
                if c == "Query":
                    val_str = str(val)[:42] + ("..." if len(str(val)) > 42 else "")
                elif isinstance(val, float):
                    val_str = f"{val:.2f}"
                else:
                    val_str = str(val)
                pdf.cell(w, 4.8, val_str, 1, 0, "C" if c != "Query" else "L", fill)
            pdf.ln()
            fill = not fill
    pdf.ln(4)

    # 4. Observations & Discussion
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 6, "4. Experimental Observations & Traversal Analysis", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(51, 65, 85)
    notes_text = student_notes.strip() if student_notes.strip() else (
        "The experimental trials successfully verified that declarative Cypher pattern queries (MATCH, WHERE, RETURN) "
        "effectively retrieve nodes, relationships, and multi-hop paths from Knowledge Graphs without requiring relational JOINs. "
        "Traversal across directed edges and aggregations via count() demonstrated consistent execution behavior."
    )
    pdf.multi_cell(0, 4.5, notes_text)
    pdf.ln(3)

    # 5. Academic Conclusion
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 6, "5. Conclusion", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(51, 65, 85)
    conclusion_text = (
        "The experiment demonstrated how Cypher can be used to query knowledge graphs by retrieving nodes, relationships, "
        "filtered information, and multi-hop connections. The interactive traversal helped visualize how graph patterns are matched "
        "and how connected entities can be used to retrieve meaningful information."
    )
    pdf.multi_cell(0, 4.5, conclusion_text)
    pdf.ln(6)

    # Sign-off line
    pdf.set_draw_color(180, 180, 180)
    pdf.line(130, pdf.get_y() + 10, 190, pdf.get_y() + 10)
    pdf.set_xy(130, pdf.get_y() + 12)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(60, 4, "Instructor / Student Signature", align="C")

    return bytes(pdf.output())


# ======================================================================================
# 3. KNOWLEDGE GRAPH VISUALIZER (PLOTLY)
# ======================================================================================

LABEL_COLOR_MAP = {
    "Student": "#3B82F6",       # Blue
    "Course": "#10B981",        # Emerald Green
    "Teacher": "#F59E0B",       # Amber / Orange
    "Department": "#8B5CF6",    # Purple
    "Person": "#3B82F6",        # Blue
    "Movie": "#F59E0B",         # Amber / Orange
    "Genre": "#8B5CF6",         # Purple
    "Customer": "#0D9488",      # Teal
    "Product": "#4F46E5",       # Indigo
    "Category": "#DB2777"       # Pink / Magenta
}


def render_knowledge_graph(graph_name: str,
                           graph: nx.DiGraph,
                           active_nodes: Optional[set] = None,
                           active_edges: Optional[List[Tuple[str, str, str]]] = None) -> go.Figure:
    """
    Renders an interactive Plotly knowledge graph visualization.
    Uses deterministic layered positions to eliminate label overlapping.
    Active nodes/edges are vividly highlighted while other elements remain clear and readable.
    """
    pos = ce.GRAPH_POSITIONS.get(graph_name, {})
    if not pos:
        pos = nx.spring_layout(graph, seed=42)

    fig = go.Figure()

    is_highlight_mode = (active_nodes is not None) or (active_edges is not None)
    active_node_set = active_nodes if active_nodes is not None else set()
    active_edge_set = set()
    if active_edges:
        for item in active_edges:
            active_edge_set.add((item[0], item[1]))

    # Edge annotations (Arrows) & mid-point labels
    annotations = []
    edge_label_x, edge_label_y, edge_label_text, edge_label_color, edge_label_size = [], [], [], [], []

    for u, v, data in graph.edges(data=True):
        rel_type = data.get("type", "RELATED")
        is_active_edge = (u, v) in active_edge_set

        if is_highlight_mode:
            arrow_color = "#E11D48" if is_active_edge else "#94A3B8"
            arrow_width = 3.2 if is_active_edge else 1.2
            opacity = 1.0 if is_active_edge else 0.5
        else:
            arrow_color = "#64748B"
            arrow_width = 1.8
            opacity = 0.85

        annotations.append(dict(
            ax=pos[u][0], ay=pos[u][1],
            x=pos[v][0], y=pos[v][1],
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True,
            arrowhead=3,
            arrowsize=1.2,
            arrowwidth=arrow_width,
            arrowcolor=arrow_color,
            opacity=opacity
        ))

        # Midpoint label
        mx = (pos[u][0] + pos[v][0]) / 2.0
        my = (pos[u][1] + pos[v][1]) / 2.0
        edge_label_x.append(mx)
        edge_label_y.append(my)
        edge_label_text.append(f"[:{rel_type}]")
        edge_label_color.append("#BE123C" if is_active_edge else "#475569")
        edge_label_size.append(10 if is_active_edge else 9)

    # Edge Labels trace
    fig.add_trace(go.Scatter(
        x=edge_label_x, y=edge_label_y,
        mode="text",
        text=edge_label_text,
        textfont=dict(size=edge_label_size, color=edge_label_color, family="Courier New"),
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
                node_colors.append("#F59E0B")  # Vivid Amber highlight
                node_sizes.append(34)
                node_borders.append(dict(width=3, color="#92400E"))
            else:
                node_colors.append("#E2E8F0")  # Soft slate fill (still readable!)
                node_sizes.append(26)
                node_borders.append(dict(width=1.5, color="#94A3B8"))
        else:
            node_colors.append(base_color)
            node_sizes.append(30)
            node_borders.append(dict(width=2, color="#FFFFFF"))

        # Label above node
        node_texts.append(f"<b>{n}</b><br><span style='font-size:9.5px;'>({label})</span>")

        # Hover attributes
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

    # Compute bounds with generous margins
    xs = [pos[n][0] for n in graph.nodes()]
    ys = [pos[n][1] for n in graph.nodes()]
    x_min, x_max = min(xs) - 0.5, max(xs) + 0.6
    y_min, y_max = min(ys) - 0.7, max(ys) + 0.9

    fig.update_layout(
        annotations=annotations,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[x_min, x_max]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[y_min, y_max]),
        height=380,
        margin=dict(l=15, r=15, t=15, b=15),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )

    return fig


# ======================================================================================
# 4. SECTION RENDERERS: THEORY, SIMULATION, QUIZ, REPORT
# ======================================================================================

# ======================================================================================
# 3B. THEORY VISUAL BUILDING BLOCKS (SVG helpers + small components)
# ======================================================================================

def _flat(html_str: str) -> str:
    """Collapses a multi-line HTML/SVG string to a single line before it reaches
    st.markdown(unsafe_allow_html=True).

    Streamlit's markdown renderer follows CommonMark: a blank (or whitespace-only)
    line inside an unsafe_allow_html block ends the raw-HTML block early, and any
    following line indented 4+ spaces is then read as an *indented code block* —
    i.e. shown as literal escaped text instead of being rendered. Our SVG builders
    below sometimes interpolate an empty string (e.g. an optional highlight ring),
    which leaves a whitespace-only line and triggers exactly that. Flattening to one
    line removes any possibility of a stray blank/indented line breaking the block.
    """
    return " ".join(line.strip() for line in html_str.splitlines() if line.strip())


_KG_ARROW_DEFS = """
<defs>
  <marker id="kgArrowMuted" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
    <path d="M0,0 L10,5 L0,10 z" fill="#94A3B8"/>
  </marker>
  <marker id="kgArrowActive" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7.5" markerHeight="7.5" orient="auto-start-reverse">
    <path d="M0,0 L10,5 L0,10 z" fill="#DC2626"/>
  </marker>
</defs>
"""


def _kg_node(x, y, name, kind, r=28, dim=False, active=False, delay=None, sub=None, label_side="bottom"):
    """Returns an SVG <g> for one graph node, colored consistently by LABEL_COLOR_MAP.

    label_side="bottom" (default) draws the name/label under the circle — use this
    whenever nothing else needs the vertical space directly below the node.
    label_side="right" draws the name/label beside the circle instead — use this for a
    node that sits between two *vertically stacked* edges (e.g. a middle node in a
    top-to-bottom chain), so the incoming/outgoing lines never cross the node's own text.
    """
    color = LABEL_COLOR_MAP.get(kind, "#3B82F6")
    fill = "#E2E8F0" if dim else color
    initial = (kind[0] if kind else "?").upper()
    ring = ""
    if active:
        ring = (f'<circle cx="{x}" cy="{y}" r="{r + 7}" fill="none" stroke="{color}" '
                f'stroke-width="2.5" stroke-dasharray="4 5" opacity="0.9"/>')
    anim_attr = f' class="kg-pop" style="animation-delay:{delay}s"' if delay is not None else ""
    name_color = "#0F172A"
    kind_color = "#64748B" if dim else "#1E293B"
    initial_color = "#0F172A" if dim else "#FFFFFF"

    if label_side == "right":
        tx = x + r + 14
        text_lines = (
            f'<text x="{tx}" y="{y - 2}" text-anchor="start" font-size="13.5" font-weight="800" fill="{name_color}">{name}</text>'
            f'<text x="{tx}" y="{y + 14}" text-anchor="start" font-size="10.5" font-weight="700" fill="{kind_color}" font-family="Consolas,monospace">:{kind}</text>'
        )
        sub_line = ""
        if sub:
            sub_line = f'<text x="{tx}" y="{y + 30}" text-anchor="start" font-size="10" font-weight="600" fill="#64748B">{sub}</text>'
    else:
        text_lines = (
            f'<text x="{x}" y="{y + r + 20}" text-anchor="middle" font-size="13.5" font-weight="800" fill="{name_color}">{name}</text>'
            f'<text x="{x}" y="{y + r + 35}" text-anchor="middle" font-size="10.5" font-weight="700" fill="{kind_color}" font-family="Consolas,monospace">:{kind}</text>'
        )
        sub_line = ""
        if sub:
            sub_line = (f'<text x="{x}" y="{y + r + 49}" text-anchor="middle" font-size="10" '
                        f'font-weight="600" fill="#64748B">{sub}</text>')

    return _flat(f"""<g{anim_attr}>
      {ring}
      <circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="#FFFFFF" stroke-width="3"/>
      <text x="{x}" y="{y + 5}" text-anchor="middle" font-size="13" font-weight="800" fill="{initial_color}">{initial}</text>
      {text_lines}
      {sub_line}
    </g>""")


def _kg_edge(x1, y1, x2, y2, label, active=False, delay=None, glow=False, label_offset=16):
    """Returns an SVG <g> for one directed, labeled relationship arrow."""
    color = "#DC2626" if active else "#94A3B8"
    marker = "kgArrowActive" if active else "kgArrowMuted"
    width = 3.4 if active else 2
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    length = max((dx ** 2 + dy ** 2) ** 0.5, 1)
    nx, ny = -dy / length, dx / length
    lx, ly = mx + nx * label_offset, my + ny * label_offset
    anim_attr = f' class="kg-pop" style="animation-delay:{delay}s"' if delay is not None else ""
    label_w = 20 + len(label) * 6.6
    line_cls = "kg-glowline" if (active and glow) else ""
    return _flat(f"""<g{anim_attr}>
      <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" marker-end="url(#{marker})" class="{line_cls}"/>
      <rect x="{lx - label_w / 2}" y="{ly - 10}" width="{label_w}" height="19" rx="9.5" fill="#FFFFFF" stroke="{color}" stroke-width="1.3"/>
      <text x="{lx}" y="{ly + 4}" text-anchor="middle" font-size="10.5" font-weight="700" fill="{color}" font-family="Consolas,monospace">:{label}</text>
    </g>""")


def _kg_svg(inner, width=640, height=260, extra_class=""):
    return _flat(f"""<div class="kg-diagram {extra_class}">
      <svg viewBox="0 0 {width} {height}" width="100%" height="{height}" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg">
        {_KG_ARROW_DEFS}
        {inner}
      </svg>
    </div>""")


def _kg_css():
    # NOTE ON SCOPING: each st.markdown() call becomes its own isolated DOM fragment in
    # Streamlit — an element opened in one call is NOT a real ancestor of content emitted
    # by a later call, even though they appear adjacent on the page. That means a wrapper
    # like `.kg-theory .kg-card { ... }` can never match anything (no element actually has
    # a `.kg-theory` ancestor), so every rule below is a plain, unscoped, kg-prefixed class
    # selector instead, and shared tokens live on :root (a real ancestor of everything).
    css_raw = """
    <style>
    :root { --ink:#0F172A; --ink-soft:#1E293B; --muted:#64748B; --paper:#FFFFFF;
      --canvas:#F5F7FB; --line:#DCE3ED; --accent:#2563EB; --accent-soft:#DBEAFE; }
    h1.kg-title { font-size:1.9rem; font-weight:850; color:var(--ink); margin:6px 4px 2px 4px; letter-spacing:-0.02em;}
    p.kg-subtitle { color:var(--ink-soft); font-size:1.02rem; margin:0 4px 22px 4px; font-weight:500;}
    h2.kg-h { font-size:1.38rem; font-weight:800; color:var(--ink); margin:30px 4px 4px 4px; letter-spacing:-0.01em; display:flex; align-items:center; gap:10px;}
    h2.kg-h .kg-step-no { display:inline-flex; align-items:center; justify-content:center; width:30px; height:30px; border-radius:9px;
      background:var(--accent); color:#fff; font-size:0.95rem; font-weight:800; flex:none; box-sizing:border-box; }
    h3.kg-h3 { font-size:1.05rem; font-weight:800; color:var(--ink); margin:14px 4px 6px 4px; }
    p.kg-lead { color:var(--ink-soft); font-size:1.01rem; margin:2px 4px 14px 4px; line-height:1.6; font-weight:500; }
    p.kg-p { color:var(--ink-soft); font-size:0.96rem; margin:4px 4px 10px 4px; line-height:1.6; }
    .kg-hint { color:var(--muted); font-size:0.85rem; margin:2px 4px; }
    .kg-card { background:var(--paper); border:1px solid var(--line); border-radius:18px; box-sizing:border-box;
      padding:20px 22px; margin:8px 4px 20px 4px; box-shadow:0 1px 2px rgba(15,23,42,.05); }
    .kg-card-tight { padding:14px 16px; }
    .kg-takeaway { border-left:5px solid var(--accent); background:var(--accent-soft); box-sizing:border-box;
      border-radius:0 14px 14px 0; padding:13px 18px; font-weight:700; color:var(--ink);
      margin:6px 4px 22px 4px; font-size:0.96rem; line-height:1.5; }
    .kg-takeaway::before { content:"TAKEAWAY"; display:block; font-size:0.68rem; font-weight:800;
      letter-spacing:0.09em; color:var(--accent); margin-bottom:4px; }
    .kg-story { background:linear-gradient(180deg,#EEF2FF 0%, #F5F7FB 100%); border:1px solid #E0E7FF; box-sizing:border-box;
      border-radius:20px; padding:22px 24px 10px 24px; margin:6px 4px 22px 4px; }
    .kg-question { font-size:1.08rem; font-weight:700; color:var(--ink); margin:0 0 14px 0; }
    .kg-question .kg-q-mark { color:var(--accent); }
    .kg-diagram { width:100%; margin:6px 0; }
    .kg-legend { display:flex; gap:22px; flex-wrap:wrap; margin:2px 4px 18px 4px; }
    .kg-legend-item { display:flex; align-items:center; gap:8px; font-size:0.85rem; font-weight:700; color:var(--ink-soft); }
    .kg-legend-dot { width:14px; height:14px; border-radius:50%; background:var(--accent); flex:none; }
    .kg-legend-line { width:22px; height:0; border-top:3px solid #94A3B8; flex:none; }
    .kg-code-wrap { background:#0F172A; border-radius:14px; padding:16px 18px; margin:8px 4px 16px 4px; box-sizing:border-box;
      font-family:'SFMono-Regular',Consolas,'Liberation Mono',monospace; font-size:0.92rem; line-height:1.65;
      color:#E2E8F0; overflow-x:auto; }
    .kg-code-wrap .kw { color:#60A5FA; font-weight:700; }
    .kg-code-wrap .lbl { color:#34D399; }
    .kg-code-wrap .rel { color:#FBBF24; }
    .kg-code-wrap .var { color:#F472B6; }
    .kg-code-wrap .plain { color:#94A3B8; }
    .kg-code-wrap .new-token { background:rgba(96,165,250,0.18); border-radius:4px; padding:1px 3px; }
    .kg-pill-row { display:flex; gap:10px; flex-wrap:wrap; margin:10px 4px 18px 4px; }
    .kg-pill { background:var(--paper); border:1.5px solid var(--line); border-radius:12px; box-sizing:border-box;
      padding:9px 13px; font-size:0.84rem; color:var(--ink-soft); font-weight:600; flex:1 1 150px; min-width:130px; }
    .kg-pill b { color:var(--ink); font-family:Consolas,monospace; }
    .kg-compare-grid { display:flex; gap:18px; flex-wrap:wrap; margin:6px 4px 8px 4px; }
    .kg-compare-col { flex:1 1 280px; background:var(--paper); border:1px solid var(--line); box-sizing:border-box;
      border-radius:16px; padding:14px 16px 4px 16px; }
    .kg-compare-col h4 { margin:0 0 6px 0; font-size:0.95rem; font-weight:800; color:var(--ink); }
    .kg-compare-col .kg-hop-badge { display:inline-block; background:var(--ink); color:#fff;
      font-size:0.72rem; font-weight:800; padding:3px 9px; border-radius:8px; margin-bottom:8px; letter-spacing:0.03em; }
    .kg-glossary { display:flex; gap:8px; flex-wrap:wrap; margin:8px 4px 20px 4px; }
    .kg-gterm { background:var(--paper); border:1px solid var(--line); border-radius:999px; box-sizing:border-box;
      padding:7px 14px; font-size:0.82rem; color:var(--ink-soft); }
    .kg-gterm b { color:var(--ink); }
    .kg-flow { display:flex; flex-direction:column; align-items:center; margin:10px 4px 22px 4px; }
    .kg-flow-box { background:var(--paper); border:2px solid var(--line); border-radius:14px; box-sizing:border-box;
      padding:11px 26px; font-weight:800; color:var(--ink); font-size:0.95rem; min-width:200px; text-align:center;
      box-shadow:0 1px 2px rgba(15,23,42,.05); }
    .kg-flow-box.kg-flow-accent { border-color:var(--accent); background:var(--accent-soft); color:var(--accent); }
    .kg-flow-box .kg-flow-sub { display:block; font-weight:500; color:var(--muted); font-size:0.76rem; margin-top:2px; }
    .kg-flow-arrow { color:var(--muted); font-size:1.1rem; line-height:1; margin:4px 0; }
    .kg-result-table { width:100%; border-collapse:collapse; margin:6px 4px 8px 4px; font-size:0.92rem; }
    .kg-result-table th { text-align:left; color:#fff; background:var(--accent); padding:8px 12px;
      font-weight:700; font-size:0.8rem; letter-spacing:0.02em; }
    .kg-result-table td { padding:8px 12px; border-bottom:1px solid var(--line); color:var(--ink-soft); font-weight:600; }
    .kg-result-table tr:last-child td { border-bottom:none; }
    .kg-result-table tr:nth-child(even) td { background:#FAFBFF; }
    .kg-cta { background:linear-gradient(120deg,#1E3A8A 0%, #2563EB 100%); border-radius:20px; box-sizing:border-box;
      padding:26px 28px; margin:26px 4px 8px 4px; text-align:center; color:#fff; }
    .kg-cta p { color:#DBEAFE; font-size:1rem; margin:0 0 4px 0; font-weight:600; }
    .kg-cta .kg-cta-line1 { color:#fff; font-size:1.18rem; font-weight:800; margin-bottom:6px; }
    @keyframes kgFadeUp { from { opacity:0; transform:translateY(9px);} to { opacity:1; transform:translateY(0);} }
    .kg-anim { opacity:0; animation:kgFadeUp .5s ease forwards; }
    .kg-diagram g.kg-pop { opacity:0; animation:kgFadeUp .45s ease forwards; }
    @keyframes kgGlowPulse { 0%,100% { filter:drop-shadow(0 0 0px rgba(220,38,38,0)); } 50% { filter:drop-shadow(0 0 5px rgba(220,38,38,0.75)); } }
    .kg-diagram .kg-glowline { animation:kgGlowPulse 1.6s ease-in-out infinite; }
    </style>
    """
    st.markdown(_flat(css_raw), unsafe_allow_html=True)


# ======================================================================================
# 3C. THEORY SECTION — full visual rewrite
# ======================================================================================

def render_theory_section():
    """
    Section 1: a visual, interactive lesson that teaches Knowledge Graphs and Cypher
    to a complete beginner, top to bottom, using the graph itself as the illustration.
    """
    _kg_css()

    st.markdown(
        '<h1 class="kg-title">Understanding Knowledge Graphs &amp; Cypher</h1>'
        '<p class="kg-subtitle">A visual, ground-up lesson — no prior knowledge assumed. '
        'Follow it top to bottom.</p>',
        unsafe_allow_html=True
    )

    # ------------------------------------------------------------------
    # 1. A real-world story
    # ------------------------------------------------------------------
    st.markdown(
        '<div class="kg-story">'
        '<p class="kg-question">Imagine a university where students, courses and teachers '
        'are connected. <br/><span class="kg-q-mark">Suppose we want to answer: '
        '"Which course is Alice studying, and who teaches it?"</span></p>'
        '</div>',
        unsafe_allow_html=True
    )
    hero_inner = (
        _kg_node(300, 65, "Alice", "Student", r=28, delay=0.0)
        + _kg_edge(300, 131, 300, 223, "STUDIES", active=True, delay=0.15)
        + _kg_node(300, 255, "Artificial Intelligence", "Course", r=32, label_side="right", delay=0.30)
        + _kg_edge(300, 417, 300, 287, "TEACHES", active=True, delay=0.45)
        + _kg_node(300, 445, "Prof. Sharma", "Teacher", r=28, delay=0.60)
    )
    st.markdown(_kg_svg(hero_inner, width=720, height=540), unsafe_allow_html=True)
    st.markdown(
        '<div class="kg-takeaway">Alice, Artificial Intelligence and Prof. Sharma are not '
        'separate facts sitting in isolation — they are connected. That single idea is the '
        'whole foundation of everything below.</div>',
        unsafe_allow_html=True
    )

    # ------------------------------------------------------------------
    # 2. What is a graph?
    # ------------------------------------------------------------------
    st.markdown('<h2 class="kg-h"><span class="kg-step-no">1</span>What is a graph?</h2>', unsafe_allow_html=True)
    st.markdown(
        '<p class="kg-lead">Start with two separate facts. On their own, they don\'t tell '
        'you much.</p>',
        unsafe_allow_html=True
    )
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(
            _kg_svg(_kg_node(150, 90, "Alice", "Student", dim=True) + _kg_node(400, 90, "AI", "Course", dim=True),
                    width=520, height=180),
            unsafe_allow_html=True
        )
        st.markdown('<p class="kg-hint" style="text-align:center;">Two disconnected pieces of information</p>', unsafe_allow_html=True)
    with col_b:
        st.markdown(
            _kg_svg(_kg_node(150, 90, "Alice", "Student") + _kg_edge(180, 90, 372, 90, "STUDIES", active=True) + _kg_node(400, 90, "AI", "Course"),
                    width=520, height=180),
            unsafe_allow_html=True
        )
        st.markdown('<p class="kg-hint" style="text-align:center;">The same two pieces, now connected</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="kg-p">A <b>graph</b> is simply a way of drawing information as connected '
        'pieces instead of separate ones. Once things are connected, we can ask questions '
        'that jump from one piece to another.</p>',
        unsafe_allow_html=True
    )

    # ------------------------------------------------------------------
    # 3. What is a Knowledge Graph?
    # ------------------------------------------------------------------
    st.markdown('<h2 class="kg-h"><span class="kg-step-no">2</span>What is a Knowledge Graph?</h2>', unsafe_allow_html=True)
    st.markdown(
        '<p class="kg-lead">A knowledge graph represents real-world things as '
        '<b>nodes</b>, and the connections between them as <b>relationships</b>.</p>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="kg-legend">'
        '<div class="kg-legend-item"><span class="kg-legend-dot"></span>NODE — a thing (Alice, AI, Prof. Sharma)</div>'
        '<div class="kg-legend-item"><span class="kg-legend-line"></span>RELATIONSHIP — how two things connect (STUDIES, TEACHES)</div>'
        '</div>',
        unsafe_allow_html=True
    )
    kg_inner = (
        _kg_node(140, 130, "Alice", "Student", active=True)
        + _kg_edge(170, 130, 372, 130, "STUDIES", active=True)
        + _kg_node(400, 130, "AI", "Course", active=True)
        + _kg_edge(590, 130, 430, 130, "TEACHES", active=True)
        + _kg_node(620, 130, "Prof. Sharma", "Teacher", active=True)
    )
    st.markdown(_kg_svg(kg_inner, width=760, height=200), unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # 4. What is a node?
    # ------------------------------------------------------------------
    st.markdown('<h2 class="kg-h"><span class="kg-step-no">3</span>What is a node?</h2>', unsafe_allow_html=True)
    st.markdown('<p class="kg-lead">Each circle in the graph represents one real thing.</p>', unsafe_allow_html=True)
    node_inner = (
        _kg_node(120, 90, "Alice", "Student")
        + _kg_node(320, 90, "AI", "Course")
        + _kg_node(520, 90, "Prof. Sharma", "Teacher")
    )
    st.markdown(_kg_svg(node_inner, width=640, height=190), unsafe_allow_html=True)
    st.markdown(
        '<p class="kg-p">A <b>node</b> is one entity — a student, a course, a teacher. '
        'Nothing more complicated than that: if you can point at it and name it, it can be a node.</p>',
        unsafe_allow_html=True
    )

    # ------------------------------------------------------------------
    # 5. What is a label?
    # ------------------------------------------------------------------
    st.markdown('<h2 class="kg-h"><span class="kg-step-no">4</span>What is a label?</h2>', unsafe_allow_html=True)
    st.markdown(
        '<p class="kg-lead">The <b>label</b> tells us what <i>kind</i> of node it is — it '
        'goes right on the node, after a colon.</p>',
        unsafe_allow_html=True
    )
    label_inner = _kg_node(320, 90, "Alice", "Student", active=True)
    st.markdown(_kg_svg(label_inner, width=640, height=190), unsafe_allow_html=True)
    st.markdown(
        '<div class="kg-pill-row">'
        '<div class="kg-pill">Alice &nbsp;→&nbsp; <b>:Student</b></div>'
        '<div class="kg-pill">AI &nbsp;→&nbsp; <b>:Course</b></div>'
        '<div class="kg-pill">Prof. Sharma &nbsp;→&nbsp; <b>:Teacher</b></div>'
        '</div>',
        unsafe_allow_html=True
    )

    # ------------------------------------------------------------------
    # 6. What is a relationship?
    # ------------------------------------------------------------------
    st.markdown('<h2 class="kg-h"><span class="kg-step-no">5</span>What is a relationship?</h2>', unsafe_allow_html=True)
    st.markdown(
        '<p class="kg-lead">A relationship tells us <b>how</b> two nodes are connected — '
        'and the arrow tells us which direction it reads in.</p>',
        unsafe_allow_html=True
    )
    rel_inner_1 = _kg_node(110, 70, "Alice", "Student") + _kg_edge(150, 70, 372, 70, "STUDIES", active=True) + _kg_node(400, 70, "AI", "Course")
    st.markdown(_kg_svg(rel_inner_1, width=640, height=150), unsafe_allow_html=True)
    st.markdown('<p class="kg-hint" style="margin-top:-10px;">Read as: Alice → STUDIES → AI</p>', unsafe_allow_html=True)
    rel_inner_2 = _kg_node(110, 70, "Prof. Sharma", "Teacher") + _kg_edge(160, 70, 362, 70, "TEACHES", active=True) + _kg_node(400, 70, "AI", "Course")
    st.markdown(_kg_svg(rel_inner_2, width=640, height=150), unsafe_allow_html=True)
    st.markdown('<p class="kg-hint" style="margin-top:-10px;">Read as: Prof. Sharma → TEACHES → AI (not the other way around)</p>', unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # 7. What is a property?
    # ------------------------------------------------------------------
    st.markdown('<h2 class="kg-h"><span class="kg-step-no">6</span>What is a property?</h2>', unsafe_allow_html=True)
    st.markdown(
        '<p class="kg-lead">A node can also carry extra facts about itself. Those facts are '
        'called <b>properties</b> — separate from the label.</p>',
        unsafe_allow_html=True
    )
    pcol1, pcol2 = st.columns([1, 1.3])
    with pcol1:
        st.markdown(_kg_svg(_kg_node(160, 90, "Alice", "Student", active=True), width=320, height=190), unsafe_allow_html=True)
    with pcol2:
        st.markdown(
            '<div class="kg-card kg-card-tight" style="margin-top:20px;">'
            '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">'
            '<span style="font-weight:800;color:#0F172A;">Alice</span>'
            '<span style="background:#3B82F6;color:#fff;font-size:0.72rem;font-weight:800;'
            'padding:3px 10px;border-radius:8px;">LABEL &nbsp;:Student</span></div>'
            '<div style="border-top:1px solid #DCE3ED;padding-top:8px;">'
            '<div style="display:flex;justify-content:space-between;padding:4px 0;">'
            '<span style="color:#64748B;font-weight:600;">PROPERTY &nbsp;name</span>'
            '<span style="color:#0F172A;font-weight:700;font-family:Consolas,monospace;">"Alice"</span></div>'
            '<div style="display:flex;justify-content:space-between;padding:4px 0;">'
            '<span style="color:#64748B;font-weight:600;">PROPERTY &nbsp;age</span>'
            '<span style="color:#0F172A;font-weight:700;font-family:Consolas,monospace;">20</span></div>'
            '</div></div>',
            unsafe_allow_html=True
        )
    st.markdown(
        '<p class="kg-p">The <b>label</b> (<code>:Student</code>) says what category Alice '
        'belongs to. The <b>properties</b> (<code>name</code>, <code>age</code>) store details '
        'about that particular Alice.</p>',
        unsafe_allow_html=True
    )

    _render_theory_checkpoint(
        key="cp1",
        prompt="Alice ──STUDIES──▶ AI. What does this arrow mean?",
        options=["Alice is studying AI", "AI is studying Alice", "They are unrelated"],
        correct_index=0,
        explanation="The arrow points from Alice to AI, and the label STUDIES reads in that direction: Alice studies AI."
    )

    # ------------------------------------------------------------------
    # 8. Introducing Cypher
    # ------------------------------------------------------------------
    st.markdown('<h2 class="kg-h"><span class="kg-step-no">7</span>Now, how do we ask the graph a question?</h2>', unsafe_allow_html=True)
    st.markdown(
        '<p class="kg-lead">We understand the graph. But looking at a picture doesn\'t scale '
        'to thousands of nodes — we need a language to <b>describe the pattern</b> we\'re '
        'looking for, and let the graph find it for us. That language is called '
        '<b>Cypher</b>.</p>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="kg-flow">'
        '<div class="kg-flow-box kg-anim" style="animation-delay:.0s;">QUESTION<span class="kg-flow-sub">"Which course does Alice study?"</span></div>'
        '<div class="kg-flow-arrow kg-anim" style="animation-delay:.12s;">↓</div>'
        '<div class="kg-flow-box kg-flow-accent kg-anim" style="animation-delay:.24s;">CYPHER<span class="kg-flow-sub">describes the shape of the answer</span></div>'
        '<div class="kg-flow-arrow kg-anim" style="animation-delay:.36s;">↓</div>'
        '<div class="kg-flow-box kg-anim" style="animation-delay:.48s;">GRAPH PATTERN<span class="kg-flow-sub">matched against the graph</span></div>'
        '<div class="kg-flow-arrow kg-anim" style="animation-delay:.60s;">↓</div>'
        '<div class="kg-flow-box kg-anim" style="animation-delay:.72s;">ANSWER<span class="kg-flow-sub">the matching nodes, returned</span></div>'
        '</div>',
        unsafe_allow_html=True
    )

    # ------------------------------------------------------------------
    # 9. Build the first Cypher query, step by step (interactive)
    # ------------------------------------------------------------------
    st.markdown('<h2 class="kg-h"><span class="kg-step-no">8</span>Build a query, one piece at a time</h2>', unsafe_allow_html=True)
    st.markdown('<p class="kg-lead">Question: <b>"Which courses are students studying?"</b> Drag the slider — watch the query and the graph grow together.</p>', unsafe_allow_html=True)

    step_labels = [
        "1 · MATCH",
        "2 · (s:Student)",
        "3 · -[:STUDIES]->",
        "4 · (c:Course)",
        "5 · RETURN",
    ]
    step_choice = st.select_slider("Query construction step", options=step_labels, value=step_labels[0], label_visibility="collapsed")
    step = step_labels.index(step_choice) + 1

    students = [("Alice", 210), ("Bob", 300), ("Charlie", 390)]
    courses = [("Artificial Intelligence", 210), ("Data Science", 300), ("Cyber Security", 390)]

    nodes_svg = ""
    edges_svg = ""
    for (sname, sy), (cname, cy) in zip(students, courses):
        s_active = step >= 2
        c_active = step >= 4
        e_active = step >= 3
        nodes_svg += _kg_node(130, sy, sname, "Student", dim=not s_active, active=s_active, r=24)
        nodes_svg += _kg_node(560, cy, cname, "Course", dim=not c_active, active=c_active, r=24)
        edges_svg += _kg_edge(160, sy, 528, cy, "STUDIES", active=e_active, label_offset=13)

    st.markdown(_kg_svg(edges_svg + nodes_svg, width=690, height=460), unsafe_allow_html=True)

    lines = ['<span class="kw">MATCH</span>']
    if step >= 2:
        tok = ' <span class="var">(</span><span class="var">s</span><span class="plain">:</span><span class="lbl">Student</span><span class="var">)</span>'
        lines[-1] += f'<span class="{"new-token" if step == 2 else ""}">{tok}</span>'
    if step >= 3:
        tok = '<span class="rel">-[:STUDIES]-&gt;</span>'
        lines[-1] += f'<span class="{"new-token" if step == 3 else ""}">{tok}</span>'
    if step >= 4:
        tok = '<span class="var">(</span><span class="var">c</span><span class="plain">:</span><span class="lbl">Course</span><span class="var">)</span>'
        lines[-1] += f'<span class="{"new-token" if step == 4 else ""}">{tok}</span>'
    if step >= 5:
        tok = '<span class="kw">RETURN</span> <span class="var">s</span><span class="plain">.name, </span><span class="var">c</span><span class="plain">.name</span>'
        lines.append(f'<span class="{"new-token" if step == 5 else ""}">{tok}</span>')

    st.markdown(f'<div class="kg-code-wrap">{"<br/>".join(lines)}</div>', unsafe_allow_html=True)

    step_explanations = {
        1: "<b>MATCH</b> tells Cypher we're about to describe a pattern to look for.",
        2: "<code>(s:Student)</code> looks for a <b>Student</b> node, and calls it <code>s</code> so we can refer back to it.",
        3: "<code>-[:STUDIES]-&gt;</code> follows the <b>STUDIES</b> relationship outward from that student.",
        4: "<code>(c:Course)</code> is where that relationship leads — a <b>Course</b> node, called <code>c</code>.",
        5: "<b>RETURN</b> tells Cypher exactly what to hand back: each student's name and their course's name.",
    }
    st.markdown(f'<p class="kg-p">{step_explanations[step]}</p>', unsafe_allow_html=True)

    if step == 5:
        st.markdown(
            '<table class="kg-result-table"><thead><tr><th>s.name</th><th>c.name</th></tr></thead><tbody>'
            '<tr><td>Alice</td><td>Artificial Intelligence</td></tr>'
            '<tr><td>Bob</td><td>Data Science</td></tr>'
            '<tr><td>Charlie</td><td>Cyber Security</td></tr>'
            '</tbody></table>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="kg-takeaway">The query found every Student connected to a Course '
            'through the STUDIES relationship — one row per match.</div>',
            unsafe_allow_html=True
        )

    _render_theory_checkpoint(
        key="cp2",
        prompt="Which part of the query tells Cypher what to actually display in the result?",
        options=["MATCH", "WHERE", "RETURN"],
        correct_index=2,
        explanation="MATCH finds the pattern and WHERE filters it, but RETURN is what decides what appears in the output."
    )

    # ------------------------------------------------------------------
    # 10. Traversal & hops
    # ------------------------------------------------------------------
    st.markdown('<h2 class="kg-h"><span class="kg-step-no">9</span>Traversal: moving through the graph</h2>', unsafe_allow_html=True)
    st.markdown(
        '<p class="kg-lead"><b>Traversal</b> means moving along the connections of a graph, '
        'from one node to the next. Each relationship you follow is called a <b>hop</b>.</p>',
        unsafe_allow_html=True
    )
    trav_inner = (
        _kg_node(110, 90, "Alice", "Student")
        + _kg_edge(150, 90, 372, 90, "STUDIES", active=True, glow=True)
        + _kg_node(400, 90, "AI", "Course")
    )
    st.markdown(_kg_svg(trav_inner, width=640, height=190), unsafe_allow_html=True)
    st.markdown('<p class="kg-hint" style="text-align:center;margin-top:-8px;">The glowing edge is the traversal in motion</p>', unsafe_allow_html=True)

    hop_inner = (
        _kg_node(90, 90, "Alice", "Student", r=24)
        + _kg_edge(120, 90, 302, 90, "STUDIES", active=True, label_offset=13)
        + _kg_node(330, 90, "AI", "Course", r=24)
        + _kg_edge(360, 90, 572, 90, "BELONGS_TO", active=True, label_offset=13)
        + _kg_node(600, 90, "Computer Eng.", "Department", r=24)
    )
    st.markdown(_kg_svg(hop_inner, width=690, height=190), unsafe_allow_html=True)
    st.markdown(
        '<div class="kg-pill-row">'
        '<div class="kg-pill">Alice → AI &nbsp;=&nbsp; <b>1 hop</b></div>'
        '<div class="kg-pill">Alice → AI → Computer Eng. &nbsp;=&nbsp; <b>2 hops</b></div>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown('<h3 class="kg-h3">One-hop vs. multi-hop</h3>', unsafe_allow_html=True)
    oh_svg = _kg_svg(
        _kg_node(90, 70, "Alice", "Student", r=22) + _kg_edge(115, 70, 262, 70, "STUDIES", active=True, label_offset=13) + _kg_node(285, 70, "AI", "Course", r=22),
        width=380, height=140
    )
    mh_svg = _kg_svg(
        _kg_node(60, 70, "Alice", "Student", r=20)
        + _kg_edge(82, 70, 208, 70, "STUDIES", active=True, label_offset=12)
        + _kg_node(230, 70, "AI", "Course", r=20)
        + _kg_edge(252, 70, 378, 70, "BELONGS_TO", active=True, label_offset=12)
        + _kg_node(400, 70, "Comp. Eng.", "Department", r=20),
        width=440, height=140
    )
    st.markdown(
        f'<div class="kg-compare-grid">'
        f'<div class="kg-compare-col"><span class="kg-hop-badge">ONE HOP</span>{oh_svg}<p class="kg-hint">One relationship followed.</p></div>'
        f'<div class="kg-compare-col"><span class="kg-hop-badge">MULTI-HOP</span>{mh_svg}<p class="kg-hint">Two relationships followed, chained together.</p></div>'
        f'</div>',
        unsafe_allow_html=True
    )

    _render_theory_checkpoint(
        key="cp3",
        prompt="Alice → AI → Computer Eng. — how many hops is this traversal?",
        options=["1 hop", "2 hops", "3 hops"],
        correct_index=1,
        explanation="Two relationships were followed (STUDIES, then BELONGS_TO), so this is a 2-hop traversal."
    )

    # ------------------------------------------------------------------
    # 11. Multi-hop with the teacher
    # ------------------------------------------------------------------
    st.markdown('<h3 class="kg-h3">Back to Alice: her course <i>and</i> its teacher</h3>', unsafe_allow_html=True)
    st.markdown('<p class="kg-p">Can we find Alice\'s course <b>and</b> the teacher who teaches it, in one query? Yes — by following two relationships that converge on the same course node.</p>', unsafe_allow_html=True)
    conv_inner = (
        _kg_node(160, 60, "Alice", "Student")
        + _kg_edge(160, 92, 320, 148, "STUDIES", active=True, glow=True)
        + _kg_node(320, 178, "AI", "Course")
        + _kg_edge(480, 60, 340, 150, "TEACHES", active=True, glow=True)
        + _kg_node(480, 30, "Prof. Sharma", "Teacher")
    )
    st.markdown(_kg_svg(conv_inner, width=640, height=280), unsafe_allow_html=True)
    st.markdown(
        '<div class="kg-code-wrap">'
        '<span class="kw">MATCH</span> <span class="var">(s:Student)</span><span class="rel">-[:STUDIES]-&gt;</span>'
        '<span class="var">(c:Course)</span><span class="rel">&lt;-[:TEACHES]-</span><span class="var">(t:Teacher)</span><br/>'
        '<span class="kw">RETURN</span> <span class="plain">s.name, c.name, t.name</span>'
        '</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="kg-takeaway">We followed more than one relationship to reach the '
        'answer — that\'s a multi-hop traversal, and it needed no table JOINs, just two '
        'connections followed in sequence.</div>',
        unsafe_allow_html=True
    )

    # ------------------------------------------------------------------
    # 12. WHERE
    # ------------------------------------------------------------------
    st.markdown('<h2 class="kg-h"><span class="kg-step-no">10</span>Filtering with WHERE</h2>', unsafe_allow_html=True)
    st.markdown('<p class="kg-lead">Suppose we only want students <b>older than 20</b>.</p>', unsafe_allow_html=True)
    where_inner = (
        _kg_node(110, 90, "Alice", "Student", dim=True, sub="age: 20")
        + _kg_node(320, 90, "Bob", "Student", active=True, sub="age: 21")
        + _kg_node(530, 90, "Charlie", "Student", dim=True, sub="age: 19")
    )
    st.markdown(_kg_svg(where_inner, width=640, height=230), unsafe_allow_html=True)
    st.markdown(
        '<div class="kg-code-wrap">'
        '<span class="kw">MATCH</span> <span class="var">(s:Student)</span><br/>'
        '<span class="kw">WHERE</span> <span class="plain">s.age &gt; 20</span><br/>'
        '<span class="kw">RETURN</span> <span class="plain">s.name, s.age</span>'
        '</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="kg-flow">'
        '<div class="kg-flow-box">MATCH<span class="kg-flow-sub">find all students</span></div>'
        '<div class="kg-flow-arrow">↓</div>'
        '<div class="kg-flow-box">WHERE<span class="kg-flow-sub">keep only age &gt; 20</span></div>'
        '<div class="kg-flow-arrow">↓</div>'
        '<div class="kg-flow-box kg-flow-accent">RETURN<span class="kg-flow-sub">show the answer</span></div>'
        '</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<table class="kg-result-table"><thead><tr><th>s.name</th><th>s.age</th></tr></thead>'
        '<tbody><tr><td>Bob</td><td>21</td></tr></tbody></table>',
        unsafe_allow_html=True
    )

    # ------------------------------------------------------------------
    # 13. RETURN, compared
    # ------------------------------------------------------------------
    st.markdown('<h2 class="kg-h"><span class="kg-step-no">11</span>RETURN decides what you see</h2>', unsafe_allow_html=True)
    rcol1, rcol2 = st.columns(2)
    with rcol1:
        st.markdown('<div class="kg-code-wrap">RETURN s.name</div>', unsafe_allow_html=True)
        st.markdown(
            '<table class="kg-result-table"><thead><tr><th>s.name</th></tr></thead><tbody>'
            '<tr><td>Alice</td></tr><tr><td>Bob</td></tr><tr><td>Charlie</td></tr></tbody></table>',
            unsafe_allow_html=True
        )
    with rcol2:
        st.markdown('<div class="kg-code-wrap">RETURN s.name, s.age</div>', unsafe_allow_html=True)
        st.markdown(
            '<table class="kg-result-table"><thead><tr><th>s.name</th><th>s.age</th></tr></thead><tbody>'
            '<tr><td>Alice</td><td>20</td></tr><tr><td>Bob</td><td>21</td></tr><tr><td>Charlie</td><td>19</td></tr></tbody></table>',
            unsafe_allow_html=True
        )
    st.markdown('<p class="kg-p">Same MATCH, same graph — but RETURN alone controls which columns come back.</p>', unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # 14. Final workflow
    # ------------------------------------------------------------------
    st.markdown('<h2 class="kg-h"><span class="kg-step-no">12</span>The whole Cypher workflow, in one picture</h2>', unsafe_allow_html=True)
    st.markdown(
        '<div class="kg-flow">'
        '<div class="kg-flow-box kg-flow-accent kg-anim" style="animation-delay:.0s;">CYPHER</div>'
        '<div class="kg-flow-arrow kg-anim" style="animation-delay:.1s;">↓</div>'
        '<div class="kg-flow-box kg-anim" style="animation-delay:.2s;">MATCH<span class="kg-flow-sub">find a pattern</span></div>'
        '<div class="kg-flow-arrow kg-anim" style="animation-delay:.3s;">↓</div>'
        '<div class="kg-flow-box kg-anim" style="animation-delay:.4s;">TRAVERSE<span class="kg-flow-sub">follow relationships</span></div>'
        '<div class="kg-flow-arrow kg-anim" style="animation-delay:.5s;">↓</div>'
        '<div class="kg-flow-box kg-anim" style="animation-delay:.6s;">WHERE<span class="kg-flow-sub">optional filter</span></div>'
        '<div class="kg-flow-arrow kg-anim" style="animation-delay:.7s;">↓</div>'
        '<div class="kg-flow-box kg-flow-accent kg-anim" style="animation-delay:.8s;">RETURN<span class="kg-flow-sub">get the result</span></div>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown('<h3 class="kg-h3">Quick glossary</h3>', unsafe_allow_html=True)
    glossary = [
        ("Node", "one entity, e.g. Alice"),
        ("Label", "what kind of node — :Student"),
        ("Property", "a stored fact — age: 20"),
        ("Relationship", "a typed, directed link"),
        ("MATCH", "describes the pattern to find"),
        ("WHERE", "filters by a condition"),
        ("RETURN", "chooses what to show"),
        ("Hop", "one relationship followed"),
    ]
    st.markdown(
        '<div class="kg-glossary">' +
        "".join(f'<div class="kg-gterm"><b>{t}</b> — {d}</div>' for t, d in glossary) +
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="kg-cta">'
        '<div class="kg-cta-line1">You now know how Cypher describes a path through a knowledge graph.</div>'
        '<p>Now let\'s try the same idea on a real, interactive query.</p>'
        '</div>',
        unsafe_allow_html=True
    )
    _, cta_col, _ = st.columns([1, 1, 1])
    with cta_col:
        if st.button("Go to Simulation →", use_container_width=True, type="primary"):
            # The sidebar radio (key="nav_section") is already instantiated earlier in
            # this same script run, and Streamlit forbids writing to a widget's own
            # session_state key after it's been instantiated in that run. So we stash the
            # request in a plain (non-widget) key and apply it in main(), BEFORE the radio
            # is created, on the next run.
            st.session_state["_kg_nav_request"] = "Simulation"
            st.rerun()


def _render_theory_checkpoint(key, prompt, options, correct_index, explanation):
    """A tiny, single-question interactive checkpoint. Not part of the graded Quiz section."""
    state_key = f"theory_{key}"
    st.markdown(f'<div class="kg-card kg-card-tight"><p class="kg-p" style="margin:0 0 6px 0;"><b>Quick check:</b> {prompt}</p></div>', unsafe_allow_html=True)
    choice = st.radio(
        "checkpoint", options, key=f"{state_key}_choice", label_visibility="collapsed", horizontal=True
    )
    if st.button("Check answer", key=f"{state_key}_btn"):
        if options.index(choice) == correct_index:
            st.success(f"Correct — {explanation}")
        else:
            st.error(f"Not quite. {explanation}")

# ======================================================================================
# 3D. SIMULATION SECTION — data: fixed, non-overlapping layouts for the two demo graphs
# ======================================================================================

# x, y, kind  (kind drives color via LABEL_COLOR_MAP, shared with Theory)
# Hand-designed layout: three aligned rows (Student/Course share a row; teachers sit
# just above their course) in tight, uniform 190px spacing so the whole graph reads as
# ONE compact block -- Charlie is never pushed away from the rest. Columns read left to
# right: Students -> Courses/Teachers -> Departments, exactly like a diagram drawn by
# hand on a board.
UNIV_NODES = {
    "Alice": (150, 160, "Student"),
    "Bob": (150, 350, "Student"),
    "Charlie": (150, 540, "Student"),
    "Prof. Sharma": (520, 50, "Teacher"),
    "Prof. Rao": (520, 240, "Teacher"),
    "Artificial Intelligence": (520, 160, "Course"),
    "Data Science": (520, 350, "Course"),
    "Cyber Security": (520, 540, "Course"),
    "Computer Engineering": (870, 255, "Department"),
    "Information Technology": (870, 540, "Department"),
}
# (src, tgt, relationship label, curve bow in px — 0 means a straight edge). Every
# relationship below is a short, local, straight line -- no curves, no arcs, no
# force layout. BELONGS_TO edges from Artificial Intelligence and Data Science both
# converge on Computer Engineering from different angles, so they never overlap.
UNIV_EDGES = [
    ("Alice", "Artificial Intelligence", "STUDIES", 0),
    ("Bob", "Data Science", "STUDIES", 0),
    ("Charlie", "Cyber Security", "STUDIES", 0),
    ("Prof. Sharma", "Artificial Intelligence", "TEACHES", 0),
    ("Prof. Rao", "Data Science", "TEACHES", 0),
    ("Artificial Intelligence", "Computer Engineering", "BELONGS_TO", 0),
    ("Data Science", "Computer Engineering", "BELONGS_TO", 0),
    ("Cyber Security", "Information Technology", "BELONGS_TO", 0),
]
UNIV_VIEWBOX = (1060, 620)

# Movies: a "bowtie" layout for the Alice/Christopher-Nolan fan-out. Alice sits ABOVE
# Inception and Interstellar; Christopher Nolan sits BELOW them; the two movies sit
# SIDE BY SIDE (not stacked) between the two people, with Sci-Fi centered at the
# waist. This is provably crossing-free for straight lines (verified numerically) --
# no curve, arc, or loop is needed. Bob/Greta/Barbie/Comedy form a second, simple
# fan-in cluster placed beside it at the same vertical center, so the whole picture
# reads as one continuous block rather than two separate graphs.
MOVIE_NODES = {
    "Alice": (280, 60, "Person"),
    "Christopher Nolan": (280, 430, "Person"),
    "Inception": (130, 245, "Movie"),
    "Interstellar": (430, 245, "Movie"),
    "Sci-Fi": (280, 245, "Genre"),
    "Bob": (720, 110, "Person"),
    "Greta": (720, 380, "Person"),
    "Barbie": (870, 245, "Movie"),
    "Comedy": (1020, 245, "Genre"),
}
MOVIE_EDGES = [
    ("Alice", "Inception", "ACTED_IN", 0),
    ("Alice", "Interstellar", "ACTED_IN", 0),
    ("Christopher Nolan", "Inception", "DIRECTED", 0),
    ("Christopher Nolan", "Interstellar", "DIRECTED", 0),
    ("Inception", "Sci-Fi", "HAS_GENRE", 0),
    ("Interstellar", "Sci-Fi", "HAS_GENRE", 0),
    ("Bob", "Barbie", "ACTED_IN", 0),
    ("Greta", "Barbie", "DIRECTED", 0),
    ("Barbie", "Comedy", "HAS_GENRE", 0),
]
MOVIE_VIEWBOX = (1150, 520)

SIM_GRAPHS = {
    "University": {
        "nodes": UNIV_NODES, "edges": UNIV_EDGES, "viewbox": UNIV_VIEWBOX,
        "entities": "Students · Courses · Teachers · Departments",
        "desc": "Explore relationships between students, courses, teachers and departments.",
        "mini_kinds": ["Student", "Course", "Teacher"],
        "legend": ["Student", "Course", "Teacher", "Department"],
    },
    "Movies": {
        "nodes": MOVIE_NODES, "edges": MOVIE_EDGES, "viewbox": MOVIE_VIEWBOX,
        "entities": "People · Movies · Genres",
        "desc": "Explore actors, directors, movies and genres.",
        "mini_kinds": ["Person", "Movie", "Genre"],
        "legend": ["Person", "Movie", "Genre"],
    },
}


def _sp(cls, text):
    return f'<span class="{cls}">{text}</span>'


def _sim_code_html(lines):
    """lines: list of lists of (cls, text) tuples -> joined with <br/>."""
    out = []
    for line in lines:
        out.append("".join(_sp(cls, text) for cls, text in line))
    return "<br/>".join(out)


# ---- The 8 fixed demonstration questions (4 per graph), each with its own -----------
# ---- illustrative single-path walkthrough for the traversal animation. Every -------
# ---- one-hop question animates in 3 steps (start -> edge -> target) and every ------
# ---- multi-hop question in 5 steps (start -> edge -> mid -> edge -> target), --------
# ---- exactly matching the worked examples in the spec. ------------------------------

SIM_QUESTIONS = [
    # ---------------------------- UNIVERSITY -----------------------------------------
    {
        "graph": "University",
        "question": "Which courses are students studying?",
        "concept": "One-hop traversal",
        "cypher": "MATCH (s:Student)-[:STUDIES]->(c:Course) RETURN s.name, c.name",
        "code_html": _sim_code_html([
            [("kw", "MATCH"), ("plain", " "), ("var", "("), ("var", "s"), ("plain", ":"),
             ("lbl", "Student"), ("var", ")"), ("rel", "-[:STUDIES]-&gt;"), ("var", "("),
             ("var", "c"), ("plain", ":"), ("lbl", "Course"), ("var", ")")],
            [("kw", "RETURN"), ("plain", " s.name, c.name")],
        ]),
        "translation": [
            ("MATCH", "Find the pattern"),
            ("(s:Student)", "Start at a Student"),
            ("-[:STUDIES]-&gt;", "Follow the STUDIES relationship"),
            ("(c:Course)", "Reach a Course"),
            ("RETURN", "Show the result"),
        ],
        "steps": [
            {"title": "Step 1 — Find a Student", "explain": "Cypher first finds a Student node — Alice.",
             "nodes": {"Alice"}, "edges": set()},
            {"title": "Step 2 — Follow STUDIES", "explain": "We follow the STUDIES relationship from Alice.",
             "nodes": {"Alice"}, "edges": {("Alice", "Artificial Intelligence")}},
            {"title": "Step 3 — Reach the Course", "explain": "The relationship leads us to Artificial Intelligence.",
             "nodes": {"Alice", "Artificial Intelligence"}, "edges": {("Alice", "Artificial Intelligence")}},
        ],
        "interpretation": "The query found Student nodes, followed their STUDIES relationships, and returned the connected Course names.",
    },
    {
        "graph": "University",
        "question": "Which course is Alice studying?",
        "concept": "Node + relationship retrieval",
        "cypher": 'MATCH (s:Student)-[:STUDIES]->(c:Course) WHERE s.name = "Alice" RETURN c.name',
        "code_html": _sim_code_html([
            [("kw", "MATCH"), ("plain", " "), ("var", "(s:Student)"), ("rel", "-[:STUDIES]-&gt;"),
             ("var", "(c:Course)")],
            [("kw", "WHERE"), ("plain", ' s.name = "Alice"')],
            [("kw", "RETURN"), ("plain", " c.name")],
        ]),
        "translation": [
            ("MATCH", "Find the pattern"),
            ("(s:Student)", "Start at a Student"),
            ("-[:STUDIES]-&gt;(c:Course)", "Follow STUDIES to a Course"),
            ('WHERE s.name = "Alice"', "Keep only Alice"),
            ("RETURN", "Show the result"),
        ],
        "steps": [
            {"title": "Step 1 — Find Alice", "explain": "Cypher first finds the Student node named Alice.",
             "nodes": {"Alice"}, "edges": set()},
            {"title": "Step 2 — Follow STUDIES", "explain": "We follow the STUDIES relationship from Alice.",
             "nodes": {"Alice"}, "edges": {("Alice", "Artificial Intelligence")}},
            {"title": "Step 3 — Reach the Course", "explain": "The relationship leads us to Artificial Intelligence.",
             "nodes": {"Alice", "Artificial Intelligence"}, "edges": {("Alice", "Artificial Intelligence")}},
        ],
        "interpretation": "The query found Alice, followed her STUDIES relationship, and returned the connected course name.",
    },
    {
        "graph": "University",
        "question": "Who teaches the course Alice is studying?",
        "concept": "Multi-hop traversal",
        "cypher": 'MATCH (s:Student)-[:STUDIES]->(c:Course)<-[:TEACHES]-(t:Teacher) WHERE s.name = "Alice" RETURN c.name, t.name',
        "code_html": _sim_code_html([
            [("kw", "MATCH"), ("plain", " "), ("var", "(s:Student)"), ("rel", "-[:STUDIES]-&gt;"),
             ("var", "(c:Course)"), ("rel", "&lt;-[:TEACHES]-"), ("var", "(t:Teacher)")],
            [("kw", "WHERE"), ("plain", ' s.name = "Alice"')],
            [("kw", "RETURN"), ("plain", " c.name, t.name")],
        ]),
        "translation": [
            ("MATCH", "Find the pattern"),
            ("(s:Student)", "Start at a Student"),
            ("-[:STUDIES]-&gt;(c:Course)", "Follow STUDIES to a Course"),
            ("&lt;-[:TEACHES]-(t:Teacher)", "Follow TEACHES backward from a Teacher"),
            ('WHERE s.name = "Alice"', "Keep only Alice"),
            ("RETURN", "Show the result"),
        ],
        "steps": [
            {"title": "Step 1 — Find Alice", "explain": "Cypher first finds the Student node named Alice.",
             "nodes": {"Alice"}, "edges": set()},
            {"title": "Step 2 — Follow STUDIES", "explain": "We follow the STUDIES relationship from Alice.",
             "nodes": {"Alice"}, "edges": {("Alice", "Artificial Intelligence")}},
            {"title": "Step 3 — Reach the Course", "explain": "The relationship leads us to Artificial Intelligence.",
             "nodes": {"Alice", "Artificial Intelligence"}, "edges": {("Alice", "Artificial Intelligence")}},
            {"title": "Step 4 — Follow TEACHES", "explain": "Now we follow TEACHES backward, from a Teacher into that same Course.",
             "nodes": {"Alice", "Artificial Intelligence"},
             "edges": {("Alice", "Artificial Intelligence"), ("Prof. Sharma", "Artificial Intelligence")}},
            {"title": "Step 5 — Reach the Teacher", "explain": "That relationship leads us to Prof. Sharma.",
             "nodes": {"Alice", "Artificial Intelligence", "Prof. Sharma"},
             "edges": {("Alice", "Artificial Intelligence"), ("Prof. Sharma", "Artificial Intelligence")}},
        ],
        "interpretation": "The query followed two relationships to connect Alice, her course, and the teacher of that course.",
    },
    {
        "graph": "University",
        "question": "Which department does Alice's course belong to?",
        "concept": "Multi-hop traversal",
        "cypher": 'MATCH (s:Student)-[:STUDIES]->(c:Course)-[:BELONGS_TO]->(d:Department) WHERE s.name = "Alice" RETURN c.name, d.name',
        "code_html": _sim_code_html([
            [("kw", "MATCH"), ("plain", " "), ("var", "(s:Student)"), ("rel", "-[:STUDIES]-&gt;"),
             ("var", "(c:Course)"), ("rel", "-[:BELONGS_TO]-&gt;"), ("var", "(d:Department)")],
            [("kw", "WHERE"), ("plain", ' s.name = "Alice"')],
            [("kw", "RETURN"), ("plain", " c.name, d.name")],
        ]),
        "translation": [
            ("MATCH", "Find the pattern"),
            ("(s:Student)", "Start at a Student"),
            ("-[:STUDIES]-&gt;(c:Course)", "Follow STUDIES to a Course"),
            ("-[:BELONGS_TO]-&gt;(d:Department)", "Follow BELONGS_TO to a Department"),
            ('WHERE s.name = "Alice"', "Keep only Alice"),
            ("RETURN", "Show the result"),
        ],
        "steps": [
            {"title": "Step 1 — Find Alice", "explain": "Cypher first finds the Student node named Alice.",
             "nodes": {"Alice"}, "edges": set()},
            {"title": "Step 2 — Follow STUDIES", "explain": "We follow the STUDIES relationship from Alice.",
             "nodes": {"Alice"}, "edges": {("Alice", "Artificial Intelligence")}},
            {"title": "Step 3 — Reach the Course", "explain": "The relationship leads us to Artificial Intelligence.",
             "nodes": {"Alice", "Artificial Intelligence"}, "edges": {("Alice", "Artificial Intelligence")}},
            {"title": "Step 4 — Follow BELONGS_TO", "explain": "Now we follow BELONGS_TO onward from that Course.",
             "nodes": {"Alice", "Artificial Intelligence"},
             "edges": {("Alice", "Artificial Intelligence"), ("Artificial Intelligence", "Computer Engineering")}},
            {"title": "Step 5 — Reach the Department", "explain": "That relationship leads us to Computer Engineering.",
             "nodes": {"Alice", "Artificial Intelligence", "Computer Engineering"},
             "edges": {("Alice", "Artificial Intelligence"), ("Artificial Intelligence", "Computer Engineering")}},
        ],
        "interpretation": "The query followed two relationships to trace Alice's course through to its department.",
    },
    # ------------------------------- MOVIES -------------------------------------------
    {
        "graph": "Movies",
        "question": "Which movies did Alice act in?",
        "concept": "One-hop traversal",
        "cypher": 'MATCH (p:Person)-[:ACTED_IN]->(m:Movie) WHERE p.name = "Alice" RETURN m.title',
        "code_html": _sim_code_html([
            [("kw", "MATCH"), ("plain", " "), ("var", "(p:Person)"), ("rel", "-[:ACTED_IN]-&gt;"), ("var", "(m:Movie)")],
            [("kw", "WHERE"), ("plain", ' p.name = "Alice"')],
            [("kw", "RETURN"), ("plain", " m.title")],
        ]),
        "translation": [
            ("MATCH", "Find the pattern"),
            ("(p:Person)", "Start at a Person"),
            ("-[:ACTED_IN]-&gt;(m:Movie)", "Follow ACTED_IN to a Movie"),
            ('WHERE p.name = "Alice"', "Keep only Alice"),
            ("RETURN", "Show the result"),
        ],
        "steps": [
            {"title": "Step 1 — Find Alice", "explain": "Cypher first finds the Person node named Alice.",
             "nodes": {"Alice"}, "edges": set()},
            {"title": "Step 2 — Follow ACTED_IN", "explain": "We follow the ACTED_IN relationship from Alice.",
             "nodes": {"Alice"}, "edges": {("Alice", "Inception")}},
            {"title": "Step 3 — Reach the Movie", "explain": "The relationship leads us to Inception — one of Alice's movies.",
             "nodes": {"Alice", "Inception"}, "edges": {("Alice", "Inception")}},
        ],
        "interpretation": "The query found Alice, followed her ACTED_IN relationships, and returned the connected movie titles.",
    },
    {
        "graph": "Movies",
        "question": "Who directed Alice's movies?",
        "concept": "Multi-hop traversal",
        "cypher": 'MATCH (p:Person)-[:ACTED_IN]->(m:Movie)<-[:DIRECTED]-(d:Person) WHERE p.name = "Alice" RETURN m.title, d.name',
        "code_html": _sim_code_html([
            [("kw", "MATCH"), ("plain", " "), ("var", "(p:Person)"), ("rel", "-[:ACTED_IN]-&gt;"),
             ("var", "(m:Movie)"), ("rel", "&lt;-[:DIRECTED]-"), ("var", "(d:Person)")],
            [("kw", "WHERE"), ("plain", ' p.name = "Alice"')],
            [("kw", "RETURN"), ("plain", " m.title, d.name")],
        ]),
        "translation": [
            ("MATCH", "Find the pattern"),
            ("(p:Person)", "Start at a Person"),
            ("-[:ACTED_IN]-&gt;(m:Movie)", "Follow ACTED_IN to a Movie"),
            ("&lt;-[:DIRECTED]-(d:Person)", "Follow DIRECTED backward from a Person"),
            ('WHERE p.name = "Alice"', "Keep only Alice"),
            ("RETURN", "Show the result"),
        ],
        "steps": [
            {"title": "Step 1 — Find Alice", "explain": "Cypher first finds the Person node named Alice.",
             "nodes": {"Alice"}, "edges": set()},
            {"title": "Step 2 — Follow ACTED_IN", "explain": "We follow the ACTED_IN relationship from Alice.",
             "nodes": {"Alice"}, "edges": {("Alice", "Inception")}},
            {"title": "Step 3 — Reach the Movie", "explain": "The relationship leads us to Inception.",
             "nodes": {"Alice", "Inception"}, "edges": {("Alice", "Inception")}},
            {"title": "Step 4 — Follow DIRECTED", "explain": "Now we follow DIRECTED backward, from a director into that same Movie.",
             "nodes": {"Alice", "Inception"},
             "edges": {("Alice", "Inception"), ("Christopher Nolan", "Inception")}},
            {"title": "Step 5 — Reach the Director", "explain": "That relationship leads us to Christopher Nolan.",
             "nodes": {"Alice", "Inception", "Christopher Nolan"},
             "edges": {("Alice", "Inception"), ("Christopher Nolan", "Inception")}},
        ],
        "interpretation": "The query followed two relationships to connect Alice, her movies, and the directors of those movies.",
    },
    {
        "graph": "Movies",
        "question": "What genre are Alice's movies?",
        "concept": "Multi-hop traversal",
        "cypher": 'MATCH (p:Person)-[:ACTED_IN]->(m:Movie)-[:HAS_GENRE]->(g:Genre) WHERE p.name = "Alice" RETURN m.title, g.name',
        "code_html": _sim_code_html([
            [("kw", "MATCH"), ("plain", " "), ("var", "(p:Person)"), ("rel", "-[:ACTED_IN]-&gt;"),
             ("var", "(m:Movie)"), ("rel", "-[:HAS_GENRE]-&gt;"), ("var", "(g:Genre)")],
            [("kw", "WHERE"), ("plain", ' p.name = "Alice"')],
            [("kw", "RETURN"), ("plain", " m.title, g.name")],
        ]),
        "translation": [
            ("MATCH", "Find the pattern"),
            ("(p:Person)", "Start at a Person"),
            ("-[:ACTED_IN]-&gt;(m:Movie)", "Follow ACTED_IN to a Movie"),
            ("-[:HAS_GENRE]-&gt;(g:Genre)", "Follow HAS_GENRE onward to a Genre"),
            ('WHERE p.name = "Alice"', "Keep only Alice"),
            ("RETURN", "Show the result"),
        ],
        "steps": [
            {"title": "Step 1 — Find Alice", "explain": "Cypher first finds the Person node named Alice.",
             "nodes": {"Alice"}, "edges": set()},
            {"title": "Step 2 — Follow ACTED_IN", "explain": "We follow the ACTED_IN relationship from Alice.",
             "nodes": {"Alice"}, "edges": {("Alice", "Inception")}},
            {"title": "Step 3 — Reach the Movie", "explain": "The relationship leads us to Inception.",
             "nodes": {"Alice", "Inception"}, "edges": {("Alice", "Inception")}},
            {"title": "Step 4 — Follow HAS_GENRE", "explain": "Now we follow HAS_GENRE onward from that Movie.",
             "nodes": {"Alice", "Inception"},
             "edges": {("Alice", "Inception"), ("Inception", "Sci-Fi")}},
            {"title": "Step 5 — Reach the Genre", "explain": "That relationship leads us to Sci-Fi.",
             "nodes": {"Alice", "Inception", "Sci-Fi"},
             "edges": {("Alice", "Inception"), ("Inception", "Sci-Fi")}},
        ],
        "interpretation": "The query followed two relationships to connect Alice, her movies, and the genres of those movies.",
    },
    {
        "graph": "Movies",
        "question": "Which director is connected to the movie Bob acted in?",
        "concept": "Multi-hop traversal",
        "cypher": 'MATCH (p:Person)-[:ACTED_IN]->(m:Movie)<-[:DIRECTED]-(d:Person) WHERE p.name = "Bob" RETURN m.title, d.name',
        "code_html": _sim_code_html([
            [("kw", "MATCH"), ("plain", " "), ("var", "(p:Person)"), ("rel", "-[:ACTED_IN]-&gt;"),
             ("var", "(m:Movie)"), ("rel", "&lt;-[:DIRECTED]-"), ("var", "(d:Person)")],
            [("kw", "WHERE"), ("plain", ' p.name = "Bob"')],
            [("kw", "RETURN"), ("plain", " m.title, d.name")],
        ]),
        "translation": [
            ("MATCH", "Find the pattern"),
            ("(p:Person)", "Start at a Person"),
            ("-[:ACTED_IN]-&gt;(m:Movie)", "Follow ACTED_IN to a Movie"),
            ("&lt;-[:DIRECTED]-(d:Person)", "Follow DIRECTED backward from a Person"),
            ('WHERE p.name = "Bob"', "Keep only Bob"),
            ("RETURN", "Show the result"),
        ],
        "steps": [
            {"title": "Step 1 — Find Bob", "explain": "Cypher first finds the Person node named Bob.",
             "nodes": {"Bob"}, "edges": set()},
            {"title": "Step 2 — Follow ACTED_IN", "explain": "We follow the ACTED_IN relationship from Bob.",
             "nodes": {"Bob"}, "edges": {("Bob", "Barbie")}},
            {"title": "Step 3 — Reach the Movie", "explain": "The relationship leads us to Barbie.",
             "nodes": {"Bob", "Barbie"}, "edges": {("Bob", "Barbie")}},
            {"title": "Step 4 — Follow DIRECTED", "explain": "Now we follow DIRECTED backward, from a director into that same Movie.",
             "nodes": {"Bob", "Barbie"},
             "edges": {("Bob", "Barbie"), ("Greta", "Barbie")}},
            {"title": "Step 5 — Reach the Director", "explain": "That relationship leads us to Greta.",
             "nodes": {"Bob", "Barbie", "Greta"},
             "edges": {("Bob", "Barbie"), ("Greta", "Barbie")}},
        ],
        "interpretation": "The query followed two relationships to connect Bob, the movie he acted in, and its director.",
    },
]


def _sim_curve_edge(x1, y1, x2, y2, label, bow=0, control=None, active=False):
    """A curved (quadratic-bezier) variant of _kg_edge, used only where two straight
    edges sharing an endpoint column would otherwise cross. Same visual language,
    same arrow markers (defined once in _KG_ARROW_DEFS, reused via _kg_svg).

    Pass `bow` for a simple perpendicular-offset curve, or an explicit `control`
    (cx, cy) point when two curves need to be routed asymmetrically to actually
    clear each other (a symmetric mirrored bow on both edges of a crossing pair
    still crosses at the shared midpoint -- see MOVIE_EDGES)."""
    color = "#DC2626" if active else "#94A3B8"
    marker = "kgArrowActive" if active else "kgArrowMuted"
    width = 3.4 if active else 2
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    length = max((dx ** 2 + dy ** 2) ** 0.5, 1)
    nx_, ny_ = -dy / length, dx / length
    if control is not None:
        cx, cy = control
    else:
        cx, cy = mx + nx_ * bow, my + ny_ * bow
    lx, ly = cx + nx_ * 14, cy + ny_ * 14
    label_w = 20 + len(label) * 6.6
    return _flat(f"""<g>
      <path d="M {x1},{y1} Q {cx},{cy} {x2},{y2}" fill="none" stroke="{color}" stroke-width="{width}" marker-end="url(#{marker})"/>
      <rect x="{lx - label_w / 2}" y="{ly - 10}" width="{label_w}" height="19" rx="9.5" fill="#FFFFFF" stroke="{color}" stroke-width="1.3"/>
      <text x="{lx}" y="{ly + 4}" text-anchor="middle" font-size="10.5" font-weight="700" fill="{color}" font-family="Consolas,monospace">:{label}</text>
    </g>""")


def _sim_step_dim(graph_key, step):
    """All nodes NOT part of the current step's highlighted path -- 'all other nodes
    remain visible but subdued', per the guided-traversal spec, on every step."""
    all_names = set(SIM_GRAPHS[graph_key]["nodes"].keys())
    explicit = step.get("dim") or set()
    return (all_names - step["nodes"]) | explicit


def _sim_render_graph(graph_key, active_nodes=None, active_edges=None, dim_nodes=None, sub_map=None):
    """Renders the full fixed-layout graph. With every optional arg left at None, every
    node/edge is neutral (the plain 'Explore' view). Pass active_nodes/active_edges to
    highlight a traversal path; pass dim_nodes to fade specific nodes (used by the WHERE
    walkthrough)."""
    g = SIM_GRAPHS[graph_key]
    nodes, edges, viewbox = g["nodes"], g["edges"], g["viewbox"]
    inner = ""
    for (u, v, rel, bow) in edges:
        x1, y1, _ = nodes[u]
        x2, y2, _ = nodes[v]
        is_active = active_edges is not None and (u, v) in active_edges
        if isinstance(bow, tuple):
            inner += _sim_curve_edge(x1, y1, x2, y2, rel, control=bow, active=is_active)
        elif bow:
            inner += _sim_curve_edge(x1, y1, x2, y2, rel, bow=bow, active=is_active)
        else:
            inner += _kg_edge(x1, y1, x2, y2, rel, active=is_active)
    for name, (x, y, kind) in nodes.items():
        is_dim = dim_nodes is not None and name in dim_nodes
        is_active = active_nodes is not None and name in active_nodes
        sub = (sub_map or {}).get(name)
        inner += _kg_node(x, y, name, kind, dim=is_dim, active=is_active, sub=sub)
    return _kg_svg(inner, width=viewbox[0], height=viewbox[1])


def _sim_mini_svg(kinds):
    """A tiny 3-node decorative preview used on the graph-choice cards."""
    xs = [45, 150, 255]
    y = 45
    parts = []
    for i in range(len(xs) - 1):
        parts.append(f'<line x1="{xs[i] + 16}" y1="{y}" x2="{xs[i + 1] - 16}" y2="{y}" '
                      f'stroke="#CBD5E1" stroke-width="2.5"/>')
    for x, k in zip(xs, kinds):
        color = LABEL_COLOR_MAP.get(k, "#3B82F6")
        parts.append(f'<circle cx="{x}" cy="{y}" r="16" fill="{color}" stroke="#fff" stroke-width="2.5"/>')
    inner = "".join(parts)
    return _flat(f'<div class="kg-mini-diagram"><svg viewBox="0 0 300 90" width="100%" height="90" '
                 f'xmlns="http://www.w3.org/2000/svg">{inner}</svg></div>')


def _sim_extra_css():
    """Additive CSS only — new kg-sim-* classes, plus a prefers-reduced-motion override
    for the animation classes Theory already defines. Nothing here redefines or removes
    an existing Theory rule."""
    css_raw = """
    <style>
    .kg-sim-grid2 { display:flex; gap:20px; flex-wrap:wrap; margin:10px 4px 6px 4px; }
    .kg-choice-card { flex:1 1 300px; background:#FFFFFF; border:2px solid #DCE3ED; border-radius:20px;
      box-sizing:border-box; padding:18px 20px 20px 20px; transition:border-color .15s ease; }
    .kg-choice-card.selected { border-color:#2563EB; background:#F5F8FF; }
    .kg-choice-title { font-size:1.15rem; font-weight:850; color:#0F172A; margin:10px 0 4px 0; }
    .kg-choice-entities { font-size:0.8rem; font-weight:700; color:#2563EB; letter-spacing:0.01em; margin-bottom:6px; }
    .kg-choice-desc { font-size:0.88rem; color:#475569; line-height:1.5; }
    .kg-mini-diagram { width:100%; }
    .kg-question-card { background:#FFFFFF; border:2px solid #DCE3ED; border-radius:16px; box-sizing:border-box;
      padding:16px 18px; height:100%; }
    .kg-question-text { font-size:0.98rem; font-weight:750; color:#0F172A; line-height:1.4; margin-bottom:10px; }
    .kg-concept-tag { display:inline-block; background:#DBEAFE; color:#2563EB; font-size:0.72rem; font-weight:800;
      padding:3px 10px; border-radius:8px; letter-spacing:0.02em; }
    .kg-stage-title { font-size:1.32rem; font-weight:850; color:#0F172A; margin:4px 4px 2px 4px; }
    .kg-stage-sub { color:#475569; font-size:0.98rem; margin:0 4px 16px 4px; font-weight:500; }
    .kg-translate { background:#F8FAFC; border:1px solid #DCE3ED; border-radius:14px; box-sizing:border-box;
      padding:12px 16px; margin:10px 4px 14px 4px; }
    .kg-translate-row { display:flex; align-items:baseline; gap:10px; padding:3px 0; font-size:0.85rem; }
    .kg-translate-row .tok { font-family:Consolas,monospace; font-weight:800; color:#2563EB; min-width:150px; flex:none; }
    .kg-translate-row .mean { color:#475569; }
    .kg-step-track { font-family:Consolas,monospace; font-size:0.95rem; color:#2563EB; font-weight:700;
      margin:2px 4px 2px 4px; }
    .kg-step-explain { border-left:4px solid #2563EB; background:#EEF2FF; box-sizing:border-box;
      border-radius:0 12px 12px 0; padding:10px 16px; margin:8px 4px 16px 4px; font-weight:650;
      color:#0F172A; font-size:0.92rem; }
    .kg-step-heading { font-weight:850; color:#0F172A; font-size:1.02rem; margin:4px 4px 4px 4px; }
    .kg-result-banner { background:linear-gradient(120deg,#0F766E 0%, #059669 100%); color:#fff; border-radius:16px;
      box-sizing:border-box; padding:16px 20px; margin:6px 4px 16px 4px; font-weight:800; font-size:1.05rem; }
    .kg-interpret { border-left:5px solid #2563EB; background:#EEF2FF; box-sizing:border-box; border-radius:0 14px 14px 0;
      padding:13px 18px; margin:10px 4px 20px 4px; font-size:0.95rem; color:#0F172A; font-weight:600; line-height:1.55; }
    .kg-interpret::before { content:"WHAT DID THE QUERY DO?"; display:block; font-size:0.68rem; font-weight:800;
      letter-spacing:0.08em; color:#2563EB; margin-bottom:5px; }
    @media (prefers-reduced-motion: reduce) {
      .kg-anim, .kg-diagram g.kg-pop { animation:none !important; opacity:1 !important; }
      .kg-diagram .kg-glowline { animation:none !important; }
    }
    </style>
    """
    st.markdown(_flat(css_raw), unsafe_allow_html=True)


def render_simulation_section():
    """
    Section 2: a guided, discovery-based experience. Theory taught the concepts; here
    the student applies them — choose a graph, explore it, ask a question, watch the
    query traverse the graph step by step, and only then see (and understand) the
    result. Learning Mode (this guided flow) is the default; a separate, tucked-away
    Experiment Mode lets a student write their own Cypher once they're comfortable.
    """
    _kg_css()
    _sim_extra_css()

    for k, v in {
        "sim_stage": "select_graph", "sim_graph": None, "sim_pending_graph": None,
        "sim_question_idx": None, "sim_anim_step": 0, "sim_last_result": None,
        "sim_last_cypher": None,
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v

    stage = st.session_state["sim_stage"]

    # ================================================================
    # STAGE 1 — choose a graph
    # ================================================================
    if stage == "select_graph":
        st.markdown('<h1 class="kg-title">Choose a Knowledge Graph</h1>'
                     '<p class="kg-subtitle">Choose an example and explore how Cypher finds connected information.</p>',
                     unsafe_allow_html=True)

        cols = st.columns(2)
        for col, gname in zip(cols, ["University", "Movies"]):
            g = SIM_GRAPHS[gname]
            with col:
                is_sel = st.session_state["sim_pending_graph"] == gname
                st.markdown(
                    f'<div class="kg-choice-card{" selected" if is_sel else ""}">'
                    f'{_sim_mini_svg(g["mini_kinds"])}'
                    f'<div class="kg-choice-title">{gname}</div>'
                    f'<div class="kg-choice-entities">{g["entities"]}</div>'
                    f'<div class="kg-choice-desc">{g["desc"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                if st.button(f"Select {gname}", key=f"pick_{gname}", use_container_width=True,
                             type="primary" if is_sel else "secondary"):
                    st.session_state["sim_pending_graph"] = gname
                    st.rerun()

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        _, mid, _ = st.columns([1, 1, 1])
        with mid:
            if st.button("Explore Graph →", type="primary", use_container_width=True,
                          disabled=st.session_state["sim_pending_graph"] is None):
                st.session_state["sim_graph"] = st.session_state["sim_pending_graph"]
                st.session_state["sim_stage"] = "explore"
                st.rerun()
        return

    graph_key = st.session_state["sim_graph"]
    g = SIM_GRAPHS[graph_key]

    # ================================================================
    # STAGE 2 — explore the selected graph
    # ================================================================
    if stage == "explore":
        st.markdown(f'<h1 class="kg-title">{graph_key} Knowledge Graph</h1>'
                     f'<p class="kg-subtitle">Explore the entities and relationships before asking the graph a question.</p>',
                     unsafe_allow_html=True)
        st.markdown(
            '<div class="kg-legend">' +
            "".join(
                f'<div class="kg-legend-item"><span class="kg-legend-dot" '
                f'style="background:{LABEL_COLOR_MAP.get(k, "#3B82F6")};"></span>{k}</div>'
                for k in g["legend"]
            ) + '</div>',
            unsafe_allow_html=True
        )
        st.markdown(_sim_render_graph(graph_key), unsafe_allow_html=True)

        back_col, next_col = st.columns([1, 1])
        with back_col:
            if st.button("← Change Graph", use_container_width=True):
                st.session_state["sim_stage"] = "select_graph"
                st.session_state["sim_pending_graph"] = None
                st.rerun()
        with next_col:
            if st.button("Ask a Question →", type="primary", use_container_width=True):
                st.session_state["sim_stage"] = "question"
                st.rerun()
        return

    # ================================================================
    # STAGE 3 — choose a question
    # ================================================================
    if stage == "question":
        st.markdown('<h1 class="kg-title">What would you like to find?</h1>'
                     f'<p class="kg-subtitle">Pick a question about the {graph_key} graph.</p>',
                     unsafe_allow_html=True)
        subset = [(i, q) for i, q in enumerate(SIM_QUESTIONS) if q["graph"] == graph_key]
        cols = st.columns(2)
        for pos, (idx, q) in enumerate(subset):
            with cols[pos % 2]:
                st.markdown(
                    f'<div class="kg-question-card">'
                    f'<div class="kg-question-text">{q["question"]}</div>'
                    f'<span class="kg-concept-tag">{q["concept"]}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                if st.button("Ask this →", key=f"ask_{idx}", use_container_width=True):
                    st.session_state["sim_question_idx"] = idx
                    st.session_state["sim_stage"] = "query"
                    st.session_state["sim_last_result"] = None
                    st.rerun()
                st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        if st.button("← Back to Graph"):
            st.session_state["sim_stage"] = "explore"
            st.rerun()
        return

    q = SIM_QUESTIONS[st.session_state["sim_question_idx"]]

    # ================================================================
    # STAGE 4 — show the Cypher
    # ================================================================
    if stage == "query":
        st.markdown(f'<p class="kg-lead" style="margin:4px 4px 2px 4px;">Question:</p>'
                     f'<h2 class="kg-h" style="margin-top:0;">"{q["question"]}"</h2>',
                     unsafe_allow_html=True)
        st.markdown('<p class="kg-p" style="font-style:normal;">Let\'s find the answer.</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="kg-code-wrap">{q["code_html"]}</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="kg-translate">' +
            "".join(
                f'<div class="kg-translate-row"><span class="tok">{tok}</span>'
                f'<span class="mean">→ {meaning}</span></div>'
                for tok, meaning in q["translation"]
            ) + '</div>',
            unsafe_allow_html=True
        )

        back_col, run_col = st.columns([1, 1])
        with back_col:
            if st.button("← Choose a Different Question", use_container_width=True):
                st.session_state["sim_stage"] = "question"
                st.rerun()
        with run_col:
            if st.button("▶ Run Query", type="primary", use_container_width=True):
                current_graph_obj = ce.GRAPH_REGISTRY[graph_key]()
                res = ce.execute_cypher_query(current_graph_obj, q["cypher"])
                st.session_state["sim_last_result"] = res
                st.session_state["sim_last_cypher"] = q["cypher"]
                st.session_state["sim_anim_step"] = 0
                st.session_state["sim_stage"] = "traverse"
                st.rerun()
        return

    res = st.session_state["sim_last_result"]

    # ================================================================
    # STAGE 5 & 6 — traversal animation (never reveal the result yet)
    # ================================================================
    if stage == "traverse":
        steps = q["steps"]
        num_steps = len(steps)
        cur = min(st.session_state["sim_anim_step"], num_steps - 1)
        st.session_state["sim_anim_step"] = cur
        step = steps[cur]

        st.markdown('<h2 class="kg-h" style="margin-top:6px;">Let\'s follow the query through the graph.</h2>',
                     unsafe_allow_html=True)
        dots = " ".join("●" if i <= cur else "○" for i in range(num_steps))
        st.markdown(f'<div class="kg-step-track">Traversal Progress — Step {cur + 1} of {num_steps} &nbsp; {dots}</div>',
                     unsafe_allow_html=True)
        st.markdown(f'<div class="kg-step-heading">{step["title"]}</div>', unsafe_allow_html=True)

        st.markdown(
            _sim_render_graph(
                graph_key,
                active_nodes=step["nodes"],
                active_edges=step["edges"],
                dim_nodes=_sim_step_dim(graph_key, step),
                sub_map=step.get("sub"),
            ),
            unsafe_allow_html=True
        )
        st.markdown(f'<div class="kg-step-explain">{step["explain"]}</div>', unsafe_allow_html=True)

        ctrl_cols = st.columns([1, 1, 1, 1])
        with ctrl_cols[0]:
            if st.button("← Previous", use_container_width=True, disabled=(cur <= 0)):
                st.session_state["sim_anim_step"] = max(0, cur - 1)
                st.rerun()
        with ctrl_cols[1]:
            play_clicked = st.button("▶ Play", use_container_width=True)
        with ctrl_cols[2]:
            if st.button("Next →", use_container_width=True, disabled=(cur >= num_steps - 1)):
                st.session_state["sim_anim_step"] = min(num_steps - 1, cur + 1)
                st.rerun()
        with ctrl_cols[3]:
            if st.button("Restart", use_container_width=True):
                st.session_state["sim_anim_step"] = 0
                st.rerun()

        if play_clicked:
            placeholder_track = st.empty()
            placeholder_heading = st.empty()
            placeholder_graph = st.empty()
            placeholder_explain = st.empty()
            for s in range(num_steps):
                st_step = steps[s]
                dots_s = " ".join("●" if i <= s else "○" for i in range(num_steps))
                placeholder_track.markdown(
                    f'<div class="kg-step-track">Traversal Progress — Step {s + 1} of {num_steps} &nbsp; {dots_s}</div>',
                    unsafe_allow_html=True)
                placeholder_heading.markdown(f'<div class="kg-step-heading">{st_step["title"]}</div>', unsafe_allow_html=True)
                placeholder_graph.markdown(
                    _sim_render_graph(graph_key, active_nodes=st_step["nodes"], active_edges=st_step["edges"],
                                       dim_nodes=_sim_step_dim(graph_key, st_step), sub_map=st_step.get("sub")),
                    unsafe_allow_html=True
                )
                placeholder_explain.markdown(f'<div class="kg-step-explain">{st_step["explain"]}</div>', unsafe_allow_html=True)
                time.sleep(0.9)
            st.session_state["sim_anim_step"] = num_steps - 1
            st.rerun()

        if cur == num_steps - 1:
            _, mid, _ = st.columns([1, 1, 1])
            with mid:
                if st.button("See Result →", type="primary", use_container_width=True):
                    st.session_state["sim_stage"] = "result"
                    st.rerun()
        return

    # ================================================================
    # STEP 7 & 8 — result, then interpretation
    # ================================================================
    if stage == "result":
        st.markdown('<h2 class="kg-h" style="margin-top:6px;">Query Result</h2>', unsafe_allow_html=True)
        df_res = res.get("dataframe") if res else None
        if res and res.get("success") and df_res is not None and not df_res.empty:
            st.dataframe(df_res, use_container_width=True, hide_index=True)
        else:
            st.info("Query executed, but 0 records matched.")
        st.markdown(f'<div class="kg-interpret">{q["interpretation"]}</div>', unsafe_allow_html=True)

        st.markdown('<p class="kg-lead" style="margin:18px 4px 10px 4px;">Ready to explore another relationship?</p>',
                     unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Try Another Query", type="primary", use_container_width=True):
                st.session_state["sim_stage"] = "question"
                st.session_state["sim_question_idx"] = None
                st.rerun()
        with c2:
            if st.button("Change Graph", use_container_width=True):
                st.session_state["sim_stage"] = "select_graph"
                st.session_state["sim_graph"] = None
                st.session_state["sim_pending_graph"] = None
                st.rerun()

    # ================================================================
    # Experiment Mode (tucked away, off by default) + Experimental Data Log
    # ================================================================
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    with st.expander("🔧 Experiment Mode — write your own Cypher query", expanded=False):
        exp_graph = st.selectbox("Graph", options=["University", "Movies"], key="exp_graph_select")
        default_custom = "MATCH (s:Student)-[:STUDIES]->(c:Course) RETURN s.name, c.name"
        if exp_graph == "Movies":
            default_custom = "MATCH (p:Person)-[:ACTED_IN]->(m:Movie)<-[:DIRECTED]-(d:Person) RETURN p.name, m.title, d.name"
        exp_query = st.text_area("Cypher query (supports MATCH, WHERE, RETURN, count())",
                                  value=st.session_state.get("exp_query_text", default_custom),
                                  height=70, key="exp_query_editor")
        st.session_state["exp_query_text"] = exp_query
        if st.button("▶ Run", key="exp_run"):
            exp_graph_obj = ce.GRAPH_REGISTRY[exp_graph]()
            exp_res = ce.execute_cypher_query(exp_graph_obj, exp_query)
            st.session_state["exp_last_result"] = exp_res
            st.session_state["exp_last_query"] = exp_query
            st.session_state["exp_last_graph"] = exp_graph
        exp_res = st.session_state.get("exp_last_result")
        if exp_res is not None:
            if exp_res.get("success"):
                edf = exp_res.get("dataframe", pd.DataFrame())
                if not edf.empty:
                    st.dataframe(edf, use_container_width=True, hide_index=True)
                else:
                    st.info("Query executed, but 0 records matched.")
            else:
                st.warning(exp_res.get("error"))

    with st.expander("📋 Experimental Data Log", expanded=False):
        log_cols = st.columns([1, 1, 1])
        with log_cols[0]:
            can_record = bool(res and res.get("success") and stage == "result")
            if st.button("Record Current Trial", type="primary", use_container_width=True, disabled=not can_record):
                trial_record = {
                    "Trial #": len(st.session_state["trials"]) + 1,
                    "Graph": graph_key,
                    "Query": st.session_state.get("sim_last_cypher", ""),
                    "Rows": len(res.get("dataframe", pd.DataFrame())),
                    "Hops": len(res.get("matched_edges", [])),
                    "Time (ms)": res.get("execution_time_ms", 0.0),
                    "Timestamp": datetime.now().strftime("%H:%M:%S")
                }
                st.session_state["trials"].append(trial_record)
                st.toast(f"Trial #{trial_record['Trial #']} recorded!")
                st.rerun()
        with log_cols[1]:
            if st.session_state["trials"]:
                df_trials = pd.DataFrame(st.session_state["trials"])
                csv_data = df_trials.to_csv(index=False).encode('utf-8')
                st.download_button("Download Trials as CSV", data=csv_data,
                                    file_name="cypher_trials_exp10.csv", mime="text/csv",
                                    use_container_width=True)
        with log_cols[2]:
            if st.button("Clear Trials", use_container_width=True):
                st.session_state["trials"] = []
                st.toast("Trial log cleared.")
                st.rerun()
        if not can_record and not st.session_state["trials"]:
            st.caption("Run a query through to its result to record a trial.")
        if st.session_state["trials"]:
            st.dataframe(pd.DataFrame(st.session_state["trials"]), use_container_width=True, hide_index=True)

def render_quiz_section():
    """Renders Section 3: Assessment Quiz with Self-Grading and Feedback."""
    st.header("Concept Assessment Quiz")
    st.caption("Answer the 10 conceptual questions below to test your understanding of Knowledge Graphs and Cypher.")

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
    st.caption("Compile student details, experimental query trials, quiz evaluation, and observations into an official PDF report.")

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

    st.subheader("Technical Observations & Traversal Analysis")
    student_notes = st.text_area(
        "Enter your interpretation of results, query comparisons, and observations:",
        value=st.session_state.get("student_notes", (
            "The experimental trials demonstrated how Cypher can be used to query knowledge graphs by retrieving nodes, "
            "relationships, filtered information, and multi-hop connections. The interactive traversal helped visualize how graph "
            "patterns are matched and how connected entities can be used to retrieve meaningful information."
        )),
        height=110
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

    # Native Title (Academic Virtual Lab Header)
    st.title(EXPERIMENT_CONFIG["title"])

    # Navigation Sidebar
    # (key="nav_section" lets the Theory section's "Go to Simulation" button drive this
    # same radio programmatically. A widget's session_state key can't be written after
    # that widget is instantiated in the same run, so the button stashes its request in
    # "_kg_nav_request" instead and we apply it here, before the radio is created.)
    if "_kg_nav_request" in st.session_state:
        st.session_state["nav_section"] = st.session_state.pop("_kg_nav_request")
    section = st.sidebar.radio(
        "Lab Navigator",
        options=["Theory", "Simulation", "Quiz", "Report Generation"],
        key="nav_section"
    )

    st.sidebar.divider()
    st.sidebar.subheader("Progress Tracker")
    quiz_status = "Done" if st.session_state.get("quiz_submitted", False) else "Pending"
    st.sidebar.write(f"- **Quiz:** {quiz_status}")
    if st.session_state.get("quiz_submitted", False):
        st.sidebar.write(f"  *(Score: {st.session_state.get('quiz_score', 0)} / {len(QUIZ_QUESTIONS)})*")
    st.sidebar.write(f"- **Trials Logged:** `{len(st.session_state['trials'])}`")
    report_status = "Ready" if len(st.session_state["trials"]) > 0 else "Not Ready (0 trials)"
    st.sidebar.write(f"- **Report:** {report_status}")

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
