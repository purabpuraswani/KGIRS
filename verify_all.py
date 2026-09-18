import sys
import pandas as pd
import cypher_engine as ce
import app

def test_graphs():
    ug = ce.create_university_graph()
    assert len(ug.nodes) == 10, f"Expected 10 nodes in University graph, got {len(ug.nodes)}"
    assert len(ug.edges) == 8, f"Expected 8 edges in University graph, got {len(ug.edges)}"

    mg = ce.create_movie_graph()
    assert len(mg.nodes) == 10, f"Expected 10 nodes in Movie graph, got {len(mg.nodes)}"
    assert len(mg.edges) == 9, f"Expected 9 edges in Movie graph, got {len(mg.edges)}"

    eg = ce.create_ecommerce_graph()
    assert len(eg.nodes) == 9, f"Expected 9 nodes in E-commerce graph, got {len(eg.nodes)}"
    assert len(eg.edges) == 10, f"Expected 10 edges in E-commerce graph, got {len(eg.edges)}"
    print("Graph definitions verification: PASSED")

def test_queries():
    graphs = {
        "University": ce.create_university_graph(),
        "Movies": ce.create_movie_graph(),
        "E-Commerce": ce.create_ecommerce_graph()
    }
    for demo in ce.DEMONSTRATION_QUERIES:
        g = graphs[demo["graph"]]
        q = demo["query"]
        res = ce.execute_cypher_query(g, q)
        assert res["success"], f"Query {demo['id']} failed: {res['error']}"
        assert len(res["dataframe"]) > 0, f"Query {demo['id']} returned 0 rows"
        print(f"  [Q{demo['id']}] {q} => {len(res['dataframe'])} rows (PASS)")
    print("All 8 demonstration queries verification: PASSED")

def test_quiz():
    assert len(app.QUIZ_QUESTIONS) == 10, f"Expected 10 quiz questions, got {len(app.QUIZ_QUESTIONS)}"
    for q in app.QUIZ_QUESTIONS:
        assert 0 <= q["answer_index"] < len(q["options"]), f"Invalid answer index in Q{q['id']}"
        assert q["explanation"], f"Missing explanation in Q{q['id']}"
    print("Quiz structure and grading verification: PASSED")

def test_pdf():
    dummy_trials = pd.DataFrame([
        {"Trial #": 1, "Graph": "University", "Query": "MATCH (s:Student) RETURN s.name, s.age", "Rows": 3, "Hops": 0, "Time (ms)": 1.2, "Timestamp": "12:00:00"},
        {"Trial #": 2, "Graph": "University", "Query": "MATCH (s:Student)-[:STUDIES]->(c:Course) RETURN s.name, c.name", "Rows": 3, "Hops": 3, "Time (ms)": 0.8, "Timestamp": "12:01:00"}
    ])
    pdf_bytes = app.generate_pdf_report(
        student_name="Test Student",
        student_id="Roll No. 47",
        date_str="2026-09-17",
        trials_df=dummy_trials,
        quiz_score=10,
        quiz_total=10,
        student_notes="Verified knowledge graph traversals successfully."
    )
    assert len(pdf_bytes) > 1000, "PDF output suspiciously small"
    assert pdf_bytes.startswith(b"%PDF"), "Invalid PDF header bytes"
    print(f"PDF report generation verification: PASSED ({len(pdf_bytes)} bytes)")

def test_plotly():
    for g_name, g_fn in ce.GRAPH_REGISTRY.items():
        g = g_fn()
        fig = app.render_knowledge_graph(g_name, g)
        assert len(fig.data) >= 2, f"Plotly figure trace count too low for {g_name}"
    print("Plotly graph rendering verification: PASSED")

if __name__ == "__main__":
    test_graphs()
    test_queries()
    test_quiz()
    test_pdf()
    test_plotly()
    print("\nALL VERIFICATION TESTS PASSED SUCCESSFULLY!")
