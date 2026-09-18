"""
Cypher Knowledge Graph Engine for Streamlit Virtual Laboratory
Experiment 10: Query Knowledge Graphs Using Cypher (Roll No. 47)

This module implements:
1. Three predefined Knowledge Graphs (University, Movies, E-Commerce) using NetworkX.
2. Deterministic, layered (multipartite) coordinates for clean, non-overlapping visualization.
3. The 8 required demonstration queries with questions, concepts, plain-English breakdowns, and interpretations.
4. A self-contained Cypher parser and execution engine supporting:
   - MATCH (nodes, directed relationships, multi-hop patterns)
   - WHERE (filtering with comparisons and logical AND)
   - RETURN (projections and count() aggregation)
5. Educational traversal hop sequencing for step-by-step animation.
"""

import re
import time
from typing import Dict, List, Tuple, Any, Optional
import networkx as nx
import pandas as pd


# ======================================================================================
# 1. KNOWLEDGE GRAPH DATASETS (NETWORKX)
# ======================================================================================

def create_university_graph() -> nx.DiGraph:
    """
    University graph - 10 nodes:
    Students: Alice (age 20), Bob (age 21), Charlie (age 19)
    Courses: Artificial Intelligence, Data Science, Cyber Security
    Teachers: Prof. Sharma, Prof. Rao
    Departments: Computer Engineering, Information Technology

    Relationships:
    Alice-STUDIES->Artificial Intelligence; Bob-STUDIES->Data Science; Charlie-STUDIES->Cyber Security;
    Sharma-TEACHES->Artificial Intelligence; Rao-TEACHES->Data Science;
    Artificial Intelligence-BELONGS_TO->Computer Engineering; Data Science-BELONGS_TO->Computer Engineering;
    Cyber Security-BELONGS_TO->Information Technology.
    """
    G = nx.DiGraph(name="University Knowledge Graph")

    nodes = [
        ("Alice", {"label": "Student", "name": "Alice", "age": 20}),
        ("Bob", {"label": "Student", "name": "Bob", "age": 21}),
        ("Charlie", {"label": "Student", "name": "Charlie", "age": 19}),
        ("Artificial Intelligence", {"label": "Course", "name": "Artificial Intelligence"}),
        ("Data Science", {"label": "Course", "name": "Data Science"}),
        ("Cyber Security", {"label": "Course", "name": "Cyber Security"}),
        ("Prof. Sharma", {"label": "Teacher", "name": "Prof. Sharma"}),
        ("Prof. Rao", {"label": "Teacher", "name": "Prof. Rao"}),
        ("Computer Engineering", {"label": "Department", "name": "Computer Engineering"}),
        ("Information Technology", {"label": "Department", "name": "Information Technology"}),
    ]
    for node_id, attrs in nodes:
        G.add_node(node_id, **attrs)

    edges = [
        ("Alice", "Artificial Intelligence", {"type": "STUDIES"}),
        ("Bob", "Data Science", {"type": "STUDIES"}),
        ("Charlie", "Cyber Security", {"type": "STUDIES"}),
        ("Prof. Sharma", "Artificial Intelligence", {"type": "TEACHES"}),
        ("Prof. Rao", "Data Science", {"type": "TEACHES"}),
        ("Artificial Intelligence", "Computer Engineering", {"type": "BELONGS_TO"}),
        ("Data Science", "Computer Engineering", {"type": "BELONGS_TO"}),
        ("Cyber Security", "Information Technology", {"type": "BELONGS_TO"}),
    ]
    for u, v, attrs in edges:
        G.add_edge(u, v, **attrs)

    return G


def create_movie_graph() -> nx.DiGraph:
    """
    Movie graph - 10 nodes:
    People: Alice, Bob, Christopher Nolan, Greta
    Movies: Inception, Interstellar, Barbie
    Genres: Sci-Fi, Comedy, Drama

    Relationships:
    Alice-ACTED_IN->Inception; Alice-ACTED_IN->Interstellar; Bob-ACTED_IN->Barbie;
    Christopher Nolan-DIRECTED->Inception; Christopher Nolan-DIRECTED->Interstellar; Greta-DIRECTED->Barbie;
    Inception-HAS_GENRE->Sci-Fi; Interstellar-HAS_GENRE->Sci-Fi; Barbie-HAS_GENRE->Comedy.
    """
    G = nx.DiGraph(name="Movie Knowledge Graph")

    nodes = [
        ("Alice", {"label": "Person", "name": "Alice"}),
        ("Bob", {"label": "Person", "name": "Bob"}),
        ("Christopher Nolan", {"label": "Person", "name": "Christopher Nolan"}),
        ("Greta", {"label": "Person", "name": "Greta"}),
        ("Inception", {"label": "Movie", "name": "Inception", "title": "Inception"}),
        ("Interstellar", {"label": "Movie", "name": "Interstellar", "title": "Interstellar"}),
        ("Barbie", {"label": "Movie", "name": "Barbie", "title": "Barbie"}),
        ("Sci-Fi", {"label": "Genre", "name": "Sci-Fi"}),
        ("Comedy", {"label": "Genre", "name": "Comedy"}),
        ("Drama", {"label": "Genre", "name": "Drama"}),
    ]
    for node_id, attrs in nodes:
        G.add_node(node_id, **attrs)

    edges = [
        ("Alice", "Inception", {"type": "ACTED_IN"}),
        ("Alice", "Interstellar", {"type": "ACTED_IN"}),
        ("Bob", "Barbie", {"type": "ACTED_IN"}),
        ("Christopher Nolan", "Inception", {"type": "DIRECTED"}),
        ("Christopher Nolan", "Interstellar", {"type": "DIRECTED"}),
        ("Greta", "Barbie", {"type": "DIRECTED"}),
        ("Inception", "Sci-Fi", {"type": "HAS_GENRE"}),
        ("Interstellar", "Sci-Fi", {"type": "HAS_GENRE"}),
        ("Barbie", "Comedy", {"type": "HAS_GENRE"}),
    ]
    for u, v, attrs in edges:
        G.add_edge(u, v, **attrs)

    return G


def create_ecommerce_graph() -> nx.DiGraph:
    """
    E-Commerce graph:
    Customers: Rahul, Priya, Aman
    Products: Laptop, Smartphone, Headphones, Keyboard
    Categories: Electronics, Accessories

    Relationships:
    Rahul-PURCHASED->Laptop; Rahul-PURCHASED->Headphones;
    Priya-PURCHASED->Smartphone; Priya-PURCHASED->Keyboard;
    Aman-PURCHASED->Laptop; Aman-PURCHASED->Smartphone;
    Laptop-BELONGS_TO->Electronics; Smartphone-BELONGS_TO->Electronics;
    Headphones-BELONGS_TO->Accessories; Keyboard-BELONGS_TO->Accessories.
    """
    G = nx.DiGraph(name="E-Commerce Knowledge Graph")

    nodes = [
        ("Rahul", {"label": "Customer", "name": "Rahul"}),
        ("Priya", {"label": "Customer", "name": "Priya"}),
        ("Aman", {"label": "Customer", "name": "Aman"}),
        ("Laptop", {"label": "Product", "name": "Laptop"}),
        ("Smartphone", {"label": "Product", "name": "Smartphone"}),
        ("Headphones", {"label": "Product", "name": "Headphones"}),
        ("Keyboard", {"label": "Product", "name": "Keyboard"}),
        ("Electronics", {"label": "Category", "name": "Electronics"}),
        ("Accessories", {"label": "Category", "name": "Accessories"}),
    ]
    for node_id, attrs in nodes:
        G.add_node(node_id, **attrs)

    edges = [
        ("Rahul", "Laptop", {"type": "PURCHASED"}),
        ("Rahul", "Headphones", {"type": "PURCHASED"}),
        ("Priya", "Smartphone", {"type": "PURCHASED"}),
        ("Priya", "Keyboard", {"type": "PURCHASED"}),
        ("Aman", "Laptop", {"type": "PURCHASED"}),
        ("Aman", "Smartphone", {"type": "PURCHASED"}),
        ("Laptop", "Electronics", {"type": "BELONGS_TO"}),
        ("Smartphone", "Electronics", {"type": "BELONGS_TO"}),
        ("Headphones", "Accessories", {"type": "BELONGS_TO"}),
        ("Keyboard", "Accessories", {"type": "BELONGS_TO"}),
    ]
    for u, v, attrs in edges:
        G.add_edge(u, v, **attrs)

    return G


GRAPH_REGISTRY = {
    "University": create_university_graph,
    "Movies": create_movie_graph,
    "E-Commerce": create_ecommerce_graph
}

# Carefully designed, non-overlapping coordinates (flowing Left -> Right)
GRAPH_POSITIONS = {
    "University": {
        # Tier 0: Students & Teachers (x = 0.0)
        "Alice": (0.0, 3.2),
        "Bob": (0.0, 2.1),
        "Charlie": (0.0, 1.0),
        "Prof. Sharma": (0.0, 4.2),
        "Prof. Rao": (0.0, 0.0),
        # Tier 1: Courses (x = 1.8)
        "Artificial Intelligence": (1.8, 3.4),
        "Data Science": (1.8, 1.7),
        "Cyber Security": (1.8, 0.5),
        # Tier 2: Departments (x = 3.6)
        "Computer Engineering": (3.6, 2.6),
        "Information Technology": (3.6, 0.5)
    },
    "Movies": {
        # Tier 0: People (x = 0.0)
        "Alice": (0.0, 3.2),
        "Christopher Nolan": (0.0, 2.1),
        "Bob": (0.0, 1.0),
        "Greta": (0.0, 0.0),
        # Tier 1: Movies (x = 1.8)
        "Inception": (1.8, 2.9),
        "Interstellar": (1.8, 1.8),
        "Barbie": (1.8, 0.5),
        # Tier 2: Genres (x = 3.6)
        "Sci-Fi": (3.6, 2.4),
        "Comedy": (3.6, 0.5),
        "Drama": (3.6, -0.4)
    },
    "E-Commerce": {
        # Tier 0: Customers (x = 0.0)
        "Rahul": (0.0, 2.4),
        "Priya": (0.0, 1.2),
        "Aman": (0.0, 0.0),
        # Tier 1: Products (x = 1.8)
        "Laptop": (1.8, 2.7),
        "Headphones": (1.8, 1.9),
        "Smartphone": (1.8, 1.0),
        "Keyboard": (1.8, 0.1),
        # Tier 2: Categories (x = 3.6)
        "Electronics": (3.6, 1.9),
        "Accessories": (3.6, 0.6)
    }
}


DEMONSTRATION_QUERIES = [
    {
        "id": 1,
        "graph": "University",
        "title": "Query 1 — Node Retrieval",
        "query_type": "Node Retrieval",
        "question": "Which students are present in the graph?",
        "query": "MATCH (s:Student) RETURN s.name, s.age",
        "concept": "Node filtering by label (:Student) and property projection (s.name, s.age).",
        "breakdown": {
            "match": "Find all nodes with label :Student.",
            "traverse": "Direct node inspection (no relationship traversal needed).",
            "where": "None (all matching students are kept).",
            "return_desc": "Display student name and age properties."
        },
        "interpretation": "Retrieved 3 students: Alice (age 20), Bob (age 21), and Charlie (age 19)."
    },
    {
        "id": 2,
        "graph": "University",
        "title": "Query 2 — Relationship Retrieval",
        "query_type": "Relationship Retrieval",
        "question": "Which courses are the students studying?",
        "query": "MATCH (s:Student)-[:STUDIES]->(c:Course) RETURN s.name, c.name",
        "concept": "1-hop directed relationship traversal along the [:STUDIES] edge.",
        "breakdown": {
            "match": "Find a Student connected to a Course.",
            "traverse": "Follow the 1-hop STUDIES relationship (Student → Course).",
            "where": "None.",
            "return_desc": "Display the student name and course name."
        },
        "interpretation": "Each student is enrolled in a course: Alice studies AI, Bob studies Data Science, and Charlie studies Cyber Security."
    },
    {
        "id": 3,
        "graph": "University",
        "title": "Query 3 — Filtering",
        "query_type": "Filtering with WHERE",
        "question": "Which students are older than 20?",
        "query": "MATCH (s:Student) WHERE s.age > 20 RETURN s.name, s.age",
        "concept": "Filtering node candidates using the WHERE clause on numerical properties.",
        "breakdown": {
            "match": "Find all nodes with label :Student.",
            "traverse": "Direct node inspection.",
            "where": "Filter candidates where student age is strictly greater than 20 (s.age > 20).",
            "return_desc": "Display qualified student name and age."
        },
        "interpretation": "Bob is 21 years old, so the WHERE condition selects Bob."
    },
    {
        "id": 4,
        "graph": "University",
        "title": "Query 4 — Multi-Hop",
        "query_type": "Multi-Hop Traversal",
        "question": "Who teaches the course studied by each student?",
        "query": "MATCH (s:Student)-[:STUDIES]->(c:Course)<-[:TEACHES]-(t:Teacher) RETURN s.name, c.name, t.name",
        "concept": "Multi-hop path pattern with reverse traversal (<-[:TEACHES]-).",
        "breakdown": {
            "match": "Find a Student, Course, and Teacher pattern.",
            "traverse": "Follow STUDIES (Student → Course) and reverse TEACHES (Teacher → Course).",
            "where": "None.",
            "return_desc": "Display the student, course, and teacher names."
        },
        "interpretation": "Found teaching assignments: Prof. Sharma teaches Alice's AI course, and Prof. Rao teaches Bob's Data Science course."
    },
    {
        "id": 5,
        "graph": "University",
        "title": "Query 5 — Multi-Hop Chain",
        "query_type": "Multi-Hop Chain",
        "question": "Which department does each student's course belong to?",
        "query": "MATCH (s:Student)-[:STUDIES]->(c:Course)-[:BELONGS_TO]->(d:Department) RETURN s.name, c.name, d.name",
        "concept": "2-hop linear transitive traversal across three distinct entity tiers.",
        "breakdown": {
            "match": "Find a 2-hop chain from Student through Course to Department.",
            "traverse": "Follow STUDIES (Student → Course), then BELONGS_TO (Course → Department).",
            "where": "None.",
            "return_desc": "Display the student, course, and department names."
        },
        "interpretation": "Traced academic departments: AI and Data Science belong to Computer Engineering, while Cyber Security belongs to Information Technology."
    },
    {
        "id": 6,
        "graph": "Movies",
        "title": "Query 6 — Movie Multi-Hop",
        "query_type": "Movie Multi-Hop",
        "question": "Who directed the movies acted in by each person?",
        "query": "MATCH (p:Person)-[:ACTED_IN]->(m:Movie)<-[:DIRECTED]-(d:Person) RETURN p.name, m.title, d.name",
        "concept": "Multi-hop path matching connecting two Person nodes through a common Movie node.",
        "breakdown": {
            "match": "Find an Actor and Director connected through a shared Movie.",
            "traverse": "Follow ACTED_IN (Person → Movie) and reverse DIRECTED (Person → Movie).",
            "where": "None.",
            "return_desc": "Display the actor name, movie title, and director name."
        },
        "interpretation": "Connected actors to directors: Christopher Nolan directed Alice in Inception and Interstellar; Greta directed Bob in Barbie."
    },
    {
        "id": 7,
        "graph": "E-Commerce",
        "title": "Query 7 — E-Commerce Multi-Hop",
        "query_type": "E-Commerce Multi-Hop",
        "question": "Which category does each purchased product belong to?",
        "query": "MATCH (c:Customer)-[:PURCHASED]->(p:Product)-[:BELONGS_TO]->(cat:Category) RETURN c.name, p.name, cat.name",
        "concept": "2-hop transitive traversal from customer purchases to product categories.",
        "breakdown": {
            "match": "Find a 2-hop chain from Customer through Product to Category.",
            "traverse": "Follow PURCHASED (Customer → Product), then BELONGS_TO (Product → Category).",
            "where": "None.",
            "return_desc": "Display customer name, product name, and category name."
        },
        "interpretation": "Classified 6 purchases: Laptop & Smartphone belong to Electronics; Headphones & Keyboard belong to Accessories."
    },
    {
        "id": 8,
        "graph": "E-Commerce",
        "title": "Query 8 — Aggregation",
        "query_type": "Aggregation with count()",
        "question": "How many products has each customer purchased?",
        "query": "MATCH (c:Customer)-[:PURCHASED]->(p:Product) RETURN c.name, count(p) AS products",
        "concept": "Cypher aggregation using count() with implicit group-by on non-aggregated columns.",
        "breakdown": {
            "match": "Find all products purchased by each customer.",
            "traverse": "Follow the PURCHASED relationship (Customer → Product).",
            "where": "None.",
            "return_desc": "Display customer name and count total purchased products."
        },
        "interpretation": "Aggregated purchases: Rahul, Priya, and Aman have each purchased exactly 2 products."
    }
]


# ======================================================================================
# 2. CYPHER PARSER & TRAVERSAL ENGINE
# ======================================================================================

class CypherSyntaxError(Exception):
    """Raised when query syntax is invalid or unsupported."""
    pass


def parse_node_spec(spec: str) -> Dict[str, Any]:
    """Parses a single node pattern like '(s:Student)' or '(n)' or '(:Movie)'."""
    spec = spec.strip()
    if not (spec.startswith("(") and spec.endswith(")")):
        raise CypherSyntaxError(f"Malformed node pattern: '{spec}'. Nodes must be enclosed in parentheses e.g. (s:Student).")
    inner = spec[1:-1].strip()
    if not inner:
        return {"var": "_", "label": None}
    
    parts = inner.split(":", 1)
    var = parts[0].strip() or None
    label = parts[1].strip() if len(parts) > 1 else None
    return {"var": var, "label": label}


def parse_rel_spec(spec: str) -> Dict[str, Any]:
    """
    Parses relationship pattern:
    -[:TYPE]-> (forward)
    <-[:TYPE]- (backward)
    """
    spec = spec.strip()
    direction = "forward"
    if spec.startswith("<-") and spec.endswith("-"):
        direction = "backward"
        inner = spec[2:-1].strip()
    elif spec.startswith("-") and spec.endswith("->"):
        direction = "forward"
        inner = spec[1:-2].strip()
    elif spec.startswith("-") and spec.endswith("-"):
        direction = "both"
        inner = spec[1:-1].strip()
    else:
        raise CypherSyntaxError(f"Malformed relationship pattern '{spec}'. Must use '-[:TYPE]->' or '<-[:TYPE]-'.")

    rel_type = None
    rel_var = None
    if inner.startswith("[") and inner.endswith("]"):
        r_content = inner[1:-1].strip()
        if ":" in r_content:
            v, t = r_content.split(":", 1)
            rel_var = v.strip() or None
            rel_type = t.strip() or None
        else:
            rel_var = r_content.strip() or None
    elif inner:
        raise CypherSyntaxError(f"Relationship specifier must be enclosed in brackets e.g. -[:TYPE]->. Found '{inner}'.")

    return {"direction": direction, "type": rel_type, "var": rel_var}


def parse_match_clause(match_str: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Parses a multi-hop MATCH path string:
    e.g. (s:Student)-[:STUDIES]->(c:Course)<-[:TEACHES]-(t:Teacher)
    Returns:
      nodes_spec: list of node dictionaries
      rels_spec: list of relationship dictionaries connecting consecutive nodes
    """
    match_str = match_str.strip()
    if not match_str:
        raise CypherSyntaxError("MATCH pattern cannot be empty.")

    node_matches = list(re.finditer(r"\([^)]*\)", match_str))
    if not node_matches:
        raise CypherSyntaxError(f"No valid node pattern found in MATCH clause: '{match_str}'.")

    if node_matches[0].start() > 0 and match_str[:node_matches[0].start()].strip():
        raise CypherSyntaxError(f"Unexpected token before initial node pattern: '{match_str[:node_matches[0].start()].strip()}'.")
    if node_matches[-1].end() < len(match_str) and match_str[node_matches[-1].end():].strip():
        raise CypherSyntaxError(f"Dangling relationship or token after last node: '{match_str[node_matches[-1].end():].strip()}'. Every relationship must connect two nodes e.g. (a)-[:REL]->(b).")

    nodes_spec = []
    for m in node_matches:
        nodes_spec.append(parse_node_spec(m.group(0)))

    rels_spec = []
    for i in range(len(node_matches) - 1):
        span_start = node_matches[i].end()
        span_end = node_matches[i+1].start()
        rel_token = match_str[span_start:span_end].strip()
        if not rel_token:
            raise CypherSyntaxError(f"Missing relationship connector between nodes at '{match_str[node_matches[i].start():node_matches[i+1].end()]}'.")
        rel_info = parse_rel_spec(rel_token)
        rels_spec.append(rel_info)

    return nodes_spec, rels_spec


def parse_where_clause(where_str: str, bound_vars: set) -> List[Dict[str, Any]]:
    """
    Parses WHERE clause into condition dicts:
    e.g. 's.age > 20' or 's.name = "Alice"'
    Supports operators: >, <, >=, <=, =, !=
    """
    where_str = where_str.strip()
    if not where_str:
        return []

    tokens = re.split(r"\s+AND\s+", where_str, flags=re.IGNORECASE)
    conditions = []

    for tok in tokens:
        tok = tok.strip()
        op_match = re.search(r"(>=|<=|!=|<>|>|<|=)", tok)
        if not op_match:
            raise CypherSyntaxError(f"Unsupported or malformed WHERE expression: '{tok}'. Must contain comparison operator (=, >, <, >=, <=, !=).")
        
        op = op_match.group(0)
        lhs = tok[:op_match.start()].strip()
        rhs = tok[op_match.end():].strip()

        if "." not in lhs:
            raise CypherSyntaxError(f"WHERE clause LHS must be 'variable.property'. Found: '{lhs}'.")
        var, prop = lhs.split(".", 1)
        var = var.strip()
        prop = prop.strip()

        if bound_vars and var not in bound_vars:
            raise CypherSyntaxError(f"Variable '{var}' in WHERE clause is not declared in MATCH pattern (Declared: {', '.join(sorted(bound_vars))}).")

        if (rhs.startswith("'") and rhs.endswith("'")) or (rhs.startswith('"') and rhs.endswith('"')):
            val = rhs[1:-1]
        else:
            try:
                val = float(rhs) if "." in rhs else int(rhs)
            except ValueError:
                val = rhs

        conditions.append({
            "var": var,
            "prop": prop,
            "op": "=" if op == "==" else op,
            "val": val
        })

    return conditions


def parse_return_clause(return_str: str, bound_vars: set) -> List[Dict[str, Any]]:
    """
    Parses RETURN items:
    - s.name, s.age
    - c.name, count(p) AS products
    - p.name, m.title, d.name
    """
    return_str = return_str.strip()
    if not return_str:
        raise CypherSyntaxError("RETURN clause cannot be empty.")

    items = []
    raw_items = [x.strip() for x in re.split(r",(?![^(]*\))", return_str) if x.strip()]

    for item in raw_items:
        alias = None
        as_match = re.search(r"\s+AS\s+", item, flags=re.IGNORECASE)
        if as_match:
            alias = item[as_match.end():].strip()
            expr = item[:as_match.start()].strip()
        else:
            expr = item

        count_match = re.match(r"^count\(\s*([a-zA-Z0-9_.]+)\s*\)$", expr, flags=re.IGNORECASE)
        if count_match:
            target = count_match.group(1).strip()
            var = target.split(".")[0]
            prop = target.split(".")[1] if "." in target else None
            if bound_vars and var not in bound_vars:
                raise CypherSyntaxError(f"Variable '{var}' in count() is not declared in MATCH pattern.")
            items.append({
                "type": "count",
                "var": var,
                "prop": prop,
                "alias": alias or f"count({target})",
                "raw": expr
            })
        else:
            if "." in expr:
                var, prop = expr.split(".", 1)
                var = var.strip()
                prop = prop.strip()
                if bound_vars and var not in bound_vars:
                    raise CypherSyntaxError(f"Variable '{var}' in RETURN clause is not declared in MATCH pattern (Declared: {', '.join(sorted(bound_vars))}).")
                items.append({
                    "type": "prop",
                    "var": var,
                    "prop": prop,
                    "alias": alias or f"{var}.{prop}",
                    "raw": expr
                })
            else:
                var = expr.strip()
                if bound_vars and var not in bound_vars:
                    raise CypherSyntaxError(f"Variable '{var}' in RETURN clause is not declared in MATCH pattern (Declared: {', '.join(sorted(bound_vars))}).")
                items.append({
                    "type": "node",
                    "var": var,
                    "prop": "name",
                    "alias": alias or var,
                    "raw": expr
                })

    return items


def execute_cypher_query(graph: nx.DiGraph, query: str) -> Dict[str, Any]:
    """
    Executes a supported Cypher query against a NetworkX graph.
    """
    start_time = time.perf_counter()
    q = query.strip().rstrip(";").strip()

    # Friendly educational check for unsupported / mutating clauses
    disallowed = ["CREATE", "MERGE", "DELETE", "DETACH", "SET", "REMOVE", "DROP", "CALL", "LOAD CSV"]
    for word in disallowed:
        if re.search(rf"\b{word}\b", q, flags=re.IGNORECASE):
            return {
                "success": False,
                "error": f"That syntax is outside the supported Cypher subset for this experiment. Supported clauses: MATCH, WHERE, RETURN, and count().",
                "dataframe": pd.DataFrame(),
                "execution_time_ms": round((time.perf_counter() - start_time) * 1000, 2)
            }

    match_match = re.search(r"MATCH\s+(.*?)(?=\s+WHERE\s+|\s+RETURN\s+|$)", q, flags=re.IGNORECASE | re.DOTALL)
    if not match_match:
        return {
            "success": False,
            "error": "Query must start with a valid MATCH pattern. Example: MATCH (s:Student) RETURN s.name",
            "dataframe": pd.DataFrame(),
            "execution_time_ms": round((time.perf_counter() - start_time) * 1000, 2)
        }
    match_str = match_match.group(1).strip()

    where_match = re.search(r"WHERE\s+(.*?)(?=\s+RETURN\s+|$)", q, flags=re.IGNORECASE | re.DOTALL)
    where_str = where_match.group(1).strip() if where_match else None

    return_match = re.search(r"RETURN\s+(.*)$", q, flags=re.IGNORECASE | re.DOTALL)
    if not return_match:
        return {
            "success": False,
            "error": "Query is missing the required RETURN clause. Example: RETURN s.name, s.age",
            "dataframe": pd.DataFrame(),
            "execution_time_ms": round((time.perf_counter() - start_time) * 1000, 2)
        }
    return_str = return_match.group(1).strip()

    try:
        nodes_spec, rels_spec = parse_match_clause(match_str)
        bound_vars = {spec["var"] for spec in nodes_spec if spec["var"]}
        where_conditions = parse_where_clause(where_str, bound_vars) if where_str else []
        return_items = parse_return_clause(return_str, bound_vars)
    except CypherSyntaxError as e:
        return {
            "success": False,
            "error": f"That syntax is outside the supported Cypher subset for this experiment: {str(e)}",
            "dataframe": pd.DataFrame(),
            "execution_time_ms": round((time.perf_counter() - start_time) * 1000, 2)
        }

    # Graph Pattern Search
    num_nodes = len(nodes_spec)
    all_bindings: List[Dict[str, Any]] = []
    traversal_paths: List[List[Dict[str, Any]]] = []

    if num_nodes == 1:
        spec = nodes_spec[0]
        var = spec["var"] or "n"
        req_label = spec["label"]

        for n, data in graph.nodes(data=True):
            if req_label and data.get("label") != req_label:
                continue
            binding = {var: n}
            all_bindings.append(binding)
            traversal_paths.append([{"type": "node", "id": n, "label": data.get("label"), "step": 1}])
    else:
        def match_path(node_idx: int, current_path_nodes: List[str], current_hops: List[Dict[str, Any]]):
            if node_idx == num_nodes:
                binding = {}
                for i, spec in enumerate(nodes_spec):
                    if spec["var"]:
                        binding[spec["var"]] = current_path_nodes[i]
                all_bindings.append(binding)
                traversal_paths.append(list(current_hops))
                return

            if node_idx == 0:
                spec = nodes_spec[0]
                for n, data in graph.nodes(data=True):
                    if spec["label"] and data.get("label") != spec["label"]:
                        continue
                    match_path(1, [n], [{"type": "node", "id": n, "label": data.get("label"), "step": 1}])
            else:
                prev_node = current_path_nodes[-1]
                rel = rels_spec[node_idx - 1]
                target_spec = nodes_spec[node_idx]
                req_rel_type = rel["type"]
                direction = rel["direction"]

                candidates: List[Tuple[str, str, str]] = []
                if direction == "forward":
                    for neighbor in graph.successors(prev_node):
                        e_data = graph.get_edge_data(prev_node, neighbor)
                        if req_rel_type and e_data.get("type") != req_rel_type:
                            continue
                        candidates.append((neighbor, prev_node, neighbor))
                elif direction == "backward":
                    for predecessor in graph.predecessors(prev_node):
                        e_data = graph.get_edge_data(predecessor, prev_node)
                        if req_rel_type and e_data.get("type") != req_rel_type:
                            continue
                        candidates.append((predecessor, predecessor, prev_node))
                else:
                    for neighbor in set(list(graph.successors(prev_node)) + list(graph.predecessors(prev_node))):
                        e_data = graph.get_edge_data(prev_node, neighbor) or graph.get_edge_data(neighbor, prev_node)
                        if req_rel_type and e_data.get("type") != req_rel_type:
                            continue
                        candidates.append((neighbor, prev_node, neighbor))

                for next_n, eu, ev in candidates:
                    n_data = graph.nodes[next_n]
                    if target_spec["label"] and n_data.get("label") != target_spec["label"]:
                        continue
                    
                    e_type = graph.get_edge_data(eu, ev).get("type", "RELATED")
                    new_hop_edge = {
                        "type": "edge",
                        "u": eu,
                        "v": ev,
                        "rel_type": e_type,
                        "direction": direction,
                        "step": len(current_hops) + 1
                    }
                    new_hop_node = {
                        "type": "node",
                        "id": next_n,
                        "label": n_data.get("label"),
                        "step": len(current_hops) + 2
                    }
                    match_path(node_idx + 1, current_path_nodes + [next_n], current_hops + [new_hop_edge, new_hop_node])

        match_path(0, [], [])

    # Apply WHERE filtering
    filtered_bindings: List[Dict[str, Any]] = []
    filtered_paths: List[List[Dict[str, Any]]] = []

    for b, p in zip(all_bindings, traversal_paths):
        passes = True
        for cond in where_conditions:
            var = cond["var"]
            prop = cond["prop"]
            op = cond["op"]
            target_val = cond["val"]

            if var not in b:
                passes = False
                break
            node_id = b[var]
            node_data = graph.nodes.get(node_id, {})
            val = node_data.get(prop)

            if val is None:
                passes = False
                break

            try:
                if op == "=":
                    if str(val).strip().lower() != str(target_val).strip().lower():
                        passes = False
                elif op in ("!=", "<>"):
                    if str(val).strip().lower() == str(target_val).strip().lower():
                        passes = False
                elif op == ">":
                    if not (float(val) > float(target_val)):
                        passes = False
                elif op == "<":
                    if not (float(val) < float(target_val)):
                        passes = False
                elif op == ">=":
                    if not (float(val) >= float(target_val)):
                        passes = False
                elif op == "<=":
                    if not (float(val) <= float(target_val)):
                        passes = False
            except (ValueError, TypeError):
                passes = False
            if not passes:
                break

        if passes:
            filtered_bindings.append(b)
            filtered_paths.append(p)

    # Evaluate RETURN & Aggregations
    has_aggregation = any(item["type"] == "count" for item in return_items)
    
    rows: List[Dict[str, Any]] = []
    if not has_aggregation:
        for b in filtered_bindings:
            row = {}
            for item in return_items:
                col_name = item["alias"]
                var = item["var"]
                prop = item["prop"]
                node_id = b.get(var)
                if node_id and node_id in graph.nodes:
                    node_attrs = graph.nodes[node_id]
                    val = node_attrs.get(prop, node_id)
                else:
                    val = None
                row[col_name] = val
            rows.append(row)
    else:
        groups: Dict[Tuple, List[Dict[str, Any]]] = {}
        group_cols = [item for item in return_items if item["type"] != "count"]

        for b in filtered_bindings:
            key_parts = []
            for item in group_cols:
                var = item["var"]
                prop = item["prop"]
                node_id = b.get(var)
                node_attrs = graph.nodes.get(node_id, {})
                val = node_attrs.get(prop, node_id) if node_id else None
                key_parts.append(val)
            key = tuple(key_parts)
            if key not in groups:
                groups[key] = []
            groups[key].append(b)

        for key, member_bindings in groups.items():
            row = {}
            for i, item in enumerate(group_cols):
                row[item["alias"]] = key[i]
            for item in return_items:
                if item["type"] == "count":
                    count_val = len(member_bindings)
                    row[item["alias"]] = count_val
            rows.append(row)

    df = pd.DataFrame(rows)

    matched_nodes = set()
    matched_edges = []
    for p in filtered_paths:
        for item in p:
            if item["type"] == "node":
                matched_nodes.add(item["id"])
            elif item["type"] == "edge":
                matched_edges.append((item["u"], item["v"], item["rel_type"]))

    num_matches = len(df)

    # Check if query matches a predefined demo query for tailored educational text
    norm_query = re.sub(r"\s+", " ", q.strip()).lower()
    matched_demo = None
    for d in DEMONSTRATION_QUERIES:
        d_norm = re.sub(r"\s+", " ", d["query"].strip()).lower()
        if norm_query == d_norm:
            matched_demo = d
            break

    if matched_demo:
        breakdown = dict(matched_demo["breakdown"])
        interpretation = matched_demo["interpretation"]
    else:
        # Generate plain student-friendly breakdown
        match_desc = f"Find pattern with {len(nodes_spec)} entity node(s)."
        if rels_spec:
            traverse_desc = f"Follow {', '.join(r['type'] or 'connection' for r in rels_spec)} relationship(s)."
        else:
            traverse_desc = "Direct node lookup (no relationships)."
        
        where_desc = f"Filter by: {where_str}" if where_str else "None."
        return_desc = f"Display requested columns: {', '.join(item['alias'] for item in return_items)}."

        breakdown = {
            "match": match_desc,
            "traverse": traverse_desc,
            "where": where_desc,
            "return_desc": return_desc
        }
        interpretation = f"Query executed successfully and returned {num_matches} matching connection(s)."

    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

    return {
        "success": True,
        "dataframe": df,
        "rows": rows,
        "matched_nodes": list(matched_nodes),
        "matched_edges": list(set(matched_edges)),
        "traversal_paths": filtered_paths,
        "execution_time_ms": elapsed_ms,
        "breakdown": breakdown,
        "interpretation": interpretation,
        "num_matches": num_matches,
        "error": None
    }
