import streamlit as st
from openai import OpenAI

# -----------------------------
# PAGE SETTINGS
# -----------------------------
st.set_page_config(
    page_title="BLOG1 Blog Post Generator",
    page_icon="📝",
    layout="wide"
)

st.title("📝 BLOG1 Blog Post Generator")
st.write("Enter a blog title and generate a BLOG1-style outline and full blog post.")

# -----------------------------
# OPENAI CLIENT
# -----------------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# -----------------------------
# BLOG1 RULES
# -----------------------------
BLOG_RULES = """
You are writing for the user's AI/small-business blog.

Follow these BLOG1 rules:

1. Create a skimmable SEO-focused blog post.
2. Use a 7-part structure.
3. Include a clear intro and conclusion.
4. Each section must have useful H2 or H3 headings.
5. Internal links must be naturally integrated inside paragraphs.
6. Internal links must be bold.
7. Do not repeat the same internal link twice.
8. Add one unique MidJourney image prompt after each section.
9. Every MidJourney prompt must end exactly with:
--ar 1:1 --stylize 150 --v 7
10. Do not repeat image concepts.
11. Make the article useful for small business owners and beginners.
12. Make the tone clear, practical, and easy to skim.
13. Include a meta description.
14. Include suggested tags/labels at the end.
"""

DEFAULT_INTERNAL_LINKS = """
Use these placeholder internal links if the user does not provide links:
- AI Tools for Small Business Owners
- How Small Businesses Can Use ChatGPT
- Best AI Automation Ideas for Beginners
- AI Marketing Tools for Small Business
- How to Save Time With AI
- Simple AI Workflows for Business Owners
- AI Content Creation Tips
- AI Productivity Tools
"""

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.header("Settings")

model_choice = st.sidebar.selectbox(
    "OpenAI model",
    ["gpt-4.1-mini", "gpt-4o-mini", "gpt-4.1"],
    index=0
)

word_target = st.sidebar.selectbox(
    "Blog length",
    ["Short: 800-1000 words", "Medium: 1200-1500 words", "Long: 1800-2200 words"],
    index=1
)

st.sidebar.write("Add your real internal links below.")
internal_links = st.sidebar.text_area(
    "Internal links / post titles",
    value=DEFAULT_INTERNAL_LINKS,
    height=220
)

# -----------------------------
# MAIN INPUT
# -----------------------------
title = st.text_input(
    "Blog title",
    placeholder="Example: 7 AI Jobs Small Businesses Will Replace First in 2026"
)

main_keyword = st.text_input(
    "Main keyword optional",
    placeholder="Example: AI jobs small business"
)

audience = st.text_input(
    "Target audience optional",
    value="small business owners, beginners, and people interested in AI tools"
)

# -----------------------------
# KEYWORD RESEARCH
# -----------------------------
if st.button("Generate Keywords"):

    prompt = f"""
    You are an SEO keyword expert.

    Use the current year 2026, not 2024.

    Blog Title:
    {title}

    Generate:

    1. Main Keyword
    2. 10 Secondary Keywords
    3. 10 Long Tail Keywords
    4. 10 Questions People Ask

    Format clearly.
    """

    response = client.chat.completions.create(
        model=model_choice,
        messages=[
            {"role": "system", "content": "You are an SEO keyword researcher."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5
    )

    st.session_state.keywords = response.choices[0].message.content


# -----------------------------
# SESSION STATE
# -----------------------------
if "outline" not in st.session_state:
    st.session_state.outline = ""

if "blog_post" not in st.session_state:
    st.session_state.blog_post = ""

if "keywords" not in st.session_state:
    st.session_state.keywords = ""

if "current_part" not in st.session_state:
    st.session_state.current_part = 0

if "parts" not in st.session_state:
    st.session_state.parts = []

if st.session_state.keywords:
    st.subheader("Keyword Research")

    st.text_area(
        "Keywords",
        value=st.session_state.keywords,
        height=300
    )

# -----------------------------
# FUNCTIONS
# -----------------------------
def generate_outline(title, main_keyword, audience, model_choice):
    prompt = f"""
Create a BLOG1-style SEO outline for this blog post.

Title: {title}
Main keyword: {main_keyword}
Target audience: {audience}

Rules:
{BLOG_RULES}

Internal links available:
{internal_links}

Output format:
1. SEO title
2. Meta description
3. Main keyword
4. Supporting keywords
5. 7-part outline
6. Internal link plan
7. Image prompt plan
"""

    response = client.chat.completions.create(
        model=model_choice,
        messages=[
            {"role": "system", "content": "You are an expert SEO blog strategist and AI blog editor."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content


def generate_blog(title, main_keyword, audience, outline, word_target, model_choice):
    prompt = f"""
Write the full BLOG1 blog post using the outline below.

Title: {title}
Main keyword: {main_keyword}
Target audience: {audience}
Length target: {word_target}

BLOG1 rules:
{BLOG_RULES}

Internal links available:
{internal_links}

Outline:
{outline}

Important:
- Use bold internal links naturally inside paragraphs.
- Do not repeat the same internal link twice.
- Add one MidJourney prompt after each main section.
- Every MidJourney prompt must end exactly with:
--ar 1:1 --stylize 150 --v 7
- Add final tags/labels at the end.
- Add meta description at the end.
- Make it ready to paste into Blogger.
"""

    response = client.chat.completions.create(
        model=model_choice,
        messages=[
            {"role": "system", "content": "You are an expert SEO blog writer who follows strict formatting rules."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.75
    )

    return response.choices[0].message.content


# -----------------------------
# BUTTONS
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    if st.button("1. Generate Outline", use_container_width=True):
        if not title:
            st.warning("Please enter a blog title first.")
        else:
            with st.spinner("Generating outline..."):
                st.session_state.outline = generate_outline(
                    title, main_keyword, audience, model_choice
                )
            st.success("Outline generated!")

with col2:
    if st.button("2. Generate Full Blog Post", use_container_width=True):
        if not title:
            st.warning("Please enter a blog title first.")
        elif not st.session_state.outline:
            st.warning("Please generate an outline first.")
        else:
            with st.spinner("Generating full blog post..."):
                st.session_state.blog_post = generate_blog(
                    title, main_keyword, audience,
                    st.session_state.outline, word_target, model_choice
                )
            st.success("Blog post generated!")

# -----------------------------
# OUTPUT
# -----------------------------
if st.session_state.outline:
    st.subheader("Generated Outline")
    st.text_area(
        "Outline",
        value=st.session_state.outline,
        height=350
    )

    st.download_button(
        "Download Outline",
        st.session_state.outline,
        file_name="blog_outline.txt",
        mime="text/plain"
    )

if st.session_state.blog_post:
    st.subheader("Generated Blog Post")
    st.text_area(
        "Blog Post",
        value=st.session_state.blog_post,
        height=650
    )

    st.download_button(
        "Download Blog Post",
        st.session_state.blog_post,
        file_name="blog_post.txt",
        mime="text/plain"
    )

# -----------------------------
# FOOTER
# -----------------------------
st.divider()
st.write("Phase 1 complete: title → outline → full BLOG1 blog post.")
