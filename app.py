import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter

st.set_page_config(page_title="Idempotent Graph Calculator", layout="wide")

st.title(r"Computational Verification of $G_{Id}(\mathbb{Z}_n)$ and $L(G_{Id}(\mathbb{Z}_n))$")
st.write(
    "Enter a positive integer n to construct the graph, compute its M-polynomial "
    "and edge-degree distribution, and view the graph and its line graph."
)

def idempotents_in_Zn(n):
    """Return the idempotents in Z_n."""
    return {a for a in range(n) if (a * a - a) % n == 0}

def build_graph(n):
    """Build G_Id(Z_n): vertices are 0,...,n-1; x,y are adjacent if x+y is idempotent mod n."""
    idempotents = idempotents_in_Zn(n)
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for i in range(n):
        for j in range(i + 1, n):
            if (i + j) % n in idempotents:
                G.add_edge(i, j)
    return G

def m_polynomial(G):
    """Return a formatted M-polynomial and edge-degree counts."""
    degrees = dict(G.degree())
    counts = Counter()
    for u, v in G.edges():
        i, j = sorted((degrees[u], degrees[v]))
        counts[(i, j)] += 1

    terms = []
    for (i, j), multiplicity in sorted(counts.items()):
        coefficient = "" if multiplicity == 1 else str(multiplicity)
        terms.append(f"{coefficient}x^{{{i}}}y^{{{j}}}")
    return " + ".join(terms) if terms else "0", counts

def draw_graph(G, title, line_graph=False, max_nodes=150):
    """Draw a graph when its size is suitable for an interactive web page."""
    if G.number_of_nodes() > max_nodes:
        st.info(
            f"{title} has {G.number_of_nodes()} vertices. The drawing is hidden "
            f"to keep the application responsive (limit: {max_nodes} vertices). "
            "The numerical calculations are still shown."
        )
        return

    fig, ax = plt.subplots(figsize=(9, 7))
    if G.number_of_nodes() <= 30:
        pos = nx.circular_layout(G)
    else:
        pos = nx.spring_layout(G, seed=42)

    if line_graph:
        labels = {
            node: f"{node[0]}-{node[1]}" if isinstance(node, tuple) and len(node) == 2 else str(node)
            for node in G.nodes()
        }
        node_size = 250 if G.number_of_nodes() <= 60 else 100
        font_size = 7 if G.number_of_nodes() <= 40 else 5
    else:
        labels = {node: str(node) for node in G.nodes()}
        node_size = 450 if G.number_of_nodes() <= 60 else 150
        font_size = 8 if G.number_of_nodes() <= 40 else 5

    nx.draw_networkx(
        G, pos, ax=ax, labels=labels, node_size=node_size,
        font_size=font_size, with_labels=True, width=0.8
    )
    ax.set_title(title)
    ax.axis("off")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with st.sidebar:
    st.header("Input")
    n = st.number_input(
        "Enter n",
        min_value=2,
        max_value=100,
        value=20,
        step=1,
        help="This demo limits n to 100 to help keep the public app responsive."
    )
    show_graphs = st.checkbox("Display graph drawings", value=True)
    calculate = st.button("Calculate", type="primary", use_container_width=True)

st.caption("For larger n, calculations and especially line-graph drawings may require substantially more time and memory.")

if calculate:
    n = int(n)
    with st.spinner(f"Constructing graphs for n = {n}..."):
        G = build_graph(n)
        L = nx.line_graph(G)
        poly_G, counts_G = m_polynomial(G)
        poly_L, counts_L = m_polynomial(L)
        idempotents = sorted(idempotents_in_Zn(n))

    st.subheader(f"Results for n = {n}")
    st.write(f"**Idempotents in Zₙ:** {idempotents}")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Original graph")
        st.metric("Vertices", G.number_of_nodes())
        st.metric("Edges", G.number_of_edges())
        st.markdown("**M-polynomial**")
        st.code(f"M(G, x, y) = {poly_G}", language=None)
        st.markdown("**Edge-degree distribution**")
        if counts_G:
            st.dataframe(
                [{"(i, j)": f"({i}, {j})", "m_{i,j}": count}
                 for (i, j), count in sorted(counts_G.items())],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.write("No edges; the M-polynomial is 0.")

    with c2:
        st.markdown("### Line graph")
        st.metric("Vertices", L.number_of_nodes())
        st.metric("Edges", L.number_of_edges())
        st.markdown("**M-polynomial**")
        st.code(f"M(L(G), x, y) = {poly_L}", language=None)
        st.markdown("**Edge-degree distribution**")
        if counts_L:
            st.dataframe(
                [{"(i, j)": f"({i}, {j})", "m_{i,j}": count}
                 for (i, j), count in sorted(counts_L.items())],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.write("No edges; the M-polynomial is 0.")

    if show_graphs:
        st.subheader("Graph drawings")
        left, right = st.columns(2)
        with left:
            draw_graph(G, f"$G_{{Id}}(Z_{{{n}}})$")
        with right:
            draw_graph(L, f"$L(G_{{Id}}(Z_{{{n}}}))$", line_graph=True)

    st.success("Calculation completed.")
else:
    st.info("Choose n in the sidebar and click **Calculate** to display the results.")

st.divider()
st.caption(
    "Research note: this application implements the adjacency rule "
    "x ≠ y and x + y is idempotent modulo n. Please compare sample outputs "
    "with the verified calculations in your thesis before publication."
)
