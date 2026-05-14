
import re
import pandas as pd
import streamlit as st

# =========================
# 1. Taxonomy
# =========================

taxonomy = [
    {
        "category": "Novelty / Contribution",
        "keywords": [
            "novelty", "contribution", "originality", "innovative",
            "prior work", "previous studies", "distinguish", "gap",
            "新颖", "创新", "贡献", "已有研究", "前人研究"
        ],
        "severity": "Major",
        "response_mode": "Thematic",
        "suggested_action": "Clarify the study's contribution and better distinguish it from prior work, especially in the Introduction and Discussion."
    },
    {
        "category": "Methodology",
        "keywords": [
            "method", "methods", "methodology", "procedure", "protocol",
            "design", "experimental design", "control", "intervention",
            "方法", "研究设计", "实验设计", "流程", "对照", "方案"
        ],
        "severity": "Major",
        "response_mode": "Point-by-point",
        "suggested_action": "Clarify methodological details and consider adding missing procedural information or controls."
    },
    {
        "category": "Statistics / Data Analysis",
        "keywords": [
            "statistics", "statistical", "sample size", "p-value", "regression",
            "power", "significance", "confidence interval", "data analysis",
            "统计", "样本量", "显著性", "回归", "置信区间", "数据分析"
        ],
        "severity": "Major",
        "response_mode": "Point-by-point",
        "suggested_action": "Check the analysis, justify the statistical approach, and report key statistical details more clearly."
    },
    {
        "category": "Results",
        "keywords": [
            "results", "findings", "outcome", "effect size",
            "结果", "发现", "效应量", "主要结果"
        ],
        "severity": "Major",
        "response_mode": "Point-by-point",
        "suggested_action": "Clarify the results, ensure consistency between text, tables, and figures, and avoid overinterpretation."
    },
    {
        "category": "Literature / References",
        "keywords": [
            "literature", "citation", "reference", "related work",
            "recent studies", "missing references", "cite",
            "文献", "引用", "参考文献", "相关研究", "最新研究"
        ],
        "severity": "Moderate",
        "response_mode": "Thematic",
        "suggested_action": "Add or update relevant literature and explain how the present study relates to previous work."
    },
    {
        "category": "Discussion / Interpretation",
        "keywords": [
            "discussion", "interpretation", "implication", "mechanism",
            "explain", "contextualize",
            "讨论", "解释", "意义", "机制", "阐释"
        ],
        "severity": "Moderate",
        "response_mode": "Thematic",
        "suggested_action": "Revise the Discussion to better interpret the findings and explain their implications."
    },
    {
        "category": "Limitations",
        "keywords": [
            "limitation", "limitations", "weakness", "bias", "generalizability",
            "局限", "局限性", "不足", "偏倚", "推广性"
        ],
        "severity": "Moderate",
        "response_mode": "Thematic",
        "suggested_action": "Add or strengthen the limitations section and clarify the boundary of the conclusions."
    },
    {
        "category": "Language / Clarity",
        "keywords": [
            "language", "grammar", "clarity", "readability", "English",
            "writing", "unclear", "wording",
            "语言", "语法", "表达", "清晰", "可读性", "英文", "措辞"
        ],
        "severity": "Minor",
        "response_mode": "Summary",
        "suggested_action": "Edit the manuscript for clarity, readability, grammar, and consistency."
    },
    {
        "category": "Figures / Tables",
        "keywords": [
            "figure", "figures", "table", "tables", "legend", "caption",
            "图", "表", "图例", "表格", "标题", "说明"
        ],
        "severity": "Minor",
        "response_mode": "Summary",
        "suggested_action": "Revise figures, tables, captions, and legends for clarity and consistency."
    },
    {
        "category": "Formatting / Journal Style",
        "keywords": [
            "format", "formatting", "style", "reference style",
            "journal style", "typo", "proofread",
            "格式", "期刊格式", "参考文献格式", "排版", "错别字"
        ],
        "severity": "Minor",
        "response_mode": "Summary",
        "suggested_action": "Correct formatting, reference style, typographical, and presentation issues."
    },
    {
        "category": "Generic AI-style Comment",
        "keywords": [
            "improve", "strengthen", "expand", "enhance", "elaborate",
            "more comprehensive", "more rigorous", "should be improved",
            "提高", "加强", "扩展", "进一步阐述", "更加全面", "更加严谨"
        ],
        "severity": "Minor",
        "response_mode": "Thematic",
        "suggested_action": "Group this with related substantive issues and respond in a compressed thematic manner."
    }
]


# =========================
# 2. Core functions
# =========================

def split_comments(text):
    text = text.strip()
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    parts = re.split(
        r"\n\s*\n|(?=Reviewer\s*\d+\s*:)|(?=Reviewer's comment\s*\d+)|(?=Comment\s*\d+)|(?=\d+\.\s+)",
        text,
        flags=re.IGNORECASE
    )

    comments = []
    current_reviewer = "Unknown"

    for part in parts:
        part = part.strip()
        if not part:
            continue

        reviewer_match = re.match(r"Reviewer\s*(\d+)\s*:", part, flags=re.IGNORECASE)
        if reviewer_match:
            current_reviewer = f"Reviewer {reviewer_match.group(1)}"
            part = re.sub(r"Reviewer\s*\d+\s*:", "", part, flags=re.IGNORECASE).strip()

        if len(part) >= 15:
            comments.append({
                "reviewer": current_reviewer,
                "comment_text": part
            })

    return comments


def classify_comment(comment_text, taxonomy):
    text_lower = comment_text.lower()
    category_scores = []

    for item in taxonomy:
        score = 0
        matched_keywords = []

        for keyword in item["keywords"]:
            keyword_lower = keyword.lower()
            if keyword_lower in text_lower:
                score += 1
                matched_keywords.append(keyword)

        if score > 0:
            category_scores.append({
                "category": item["category"],
                "score": score,
                "matched_keywords": matched_keywords,
                "severity": item["severity"],
                "response_mode": item["response_mode"],
                "suggested_action": item["suggested_action"]
            })

    if not category_scores:
        return {
            "category": "Unclassified / Needs Human Review",
            "score": 0,
            "matched_keywords": [],
            "severity": "Moderate",
            "response_mode": "Thematic",
            "suggested_action": "Review this comment manually and decide whether it requires a direct response or can be grouped with related comments."
        }

    category_scores = sorted(category_scores, key=lambda x: x["score"], reverse=True)
    return category_scores[0]


def analyze_comments(comments, taxonomy):
    rows = []

    for i, item in enumerate(comments, start=1):
        comment_text = item["comment_text"]
        classification = classify_comment(comment_text, taxonomy)

        rows.append({
            "comment_id": f"C{i}",
            "reviewer": item["reviewer"],
            "comment_text": comment_text,
            "category": classification["category"],
            "severity": classification["severity"],
            "response_mode": classification["response_mode"],
            "matched_keywords": "; ".join(classification["matched_keywords"]),
            "suggested_action": classification["suggested_action"]
        })

    return pd.DataFrame(rows)


def generate_thematic_response_plan(df):
    plans = []

    for category, group in df.groupby("category"):
        comment_ids = ", ".join(group["comment_id"].tolist())
        reviewers = ", ".join(sorted(group["reviewer"].unique()))
        severity = group["severity"].iloc[0]
        response_mode = group["response_mode"].iloc[0]
        suggested_action = group["suggested_action"].iloc[0]

        if response_mode == "Point-by-point":
            response_strategy = "Respond directly and specifically, especially if the issue affects methods, data, analysis, or conclusions."
        elif response_mode == "Thematic":
            response_strategy = "Group similar comments and provide one integrated thematic response."
        elif response_mode == "Summary":
            response_strategy = "Provide a brief summary response and indicate that the manuscript has been revised accordingly."
        else:
            response_strategy = "Review manually and decide whether a direct or grouped response is needed."

        plans.append({
            "theme": category,
            "related_comment_ids": comment_ids,
            "related_reviewers": reviewers,
            "severity": severity,
            "recommended_response_mode": response_mode,
            "response_strategy": response_strategy,
            "suggested_revision_action": suggested_action
        })

    return pd.DataFrame(plans)


def generate_rebuttal_outline(plan_df):
    lines = []

    lines.append("Dear Editor,")
    lines.append("")
    lines.append(
        "We thank the editor and reviewers for their careful reading of our manuscript "
        "and for their constructive comments. Because several comments overlap in scope, "
        "we have organized our responses thematically while ensuring that all substantive "
        "concerns are addressed."
    )
    lines.append("")
    lines.append("Summary of major revisions:")
    lines.append("1. [Briefly summarize major revision 1]")
    lines.append("2. [Briefly summarize major revision 2]")
    lines.append("3. [Briefly summarize major revision 3]")
    lines.append("")
    lines.append("Detailed responses:")
    lines.append("")

    for idx, row in plan_df.iterrows():
        lines.append(f"Response Theme {idx + 1}: {row['theme']}")
        lines.append(f"Related comments: {row['related_comment_ids']}")
        lines.append(f"Recommended response mode: {row['recommended_response_mode']}")
        lines.append("")
        lines.append("Response:")

        if row["recommended_response_mode"] == "Point-by-point":
            lines.append(
                "We thank the reviewer for this important comment. "
                "We have addressed this issue by [describe specific revision, analysis, clarification, or justification]."
            )
        elif row["recommended_response_mode"] == "Thematic":
            lines.append(
                "Several comments raised concerns related to this issue. "
                "We have revised the manuscript to address this point more clearly. "
                "Specifically, we have [summarize the grouped revisions]."
            )
        elif row["recommended_response_mode"] == "Summary":
            lines.append(
                "We thank the reviewer for this helpful suggestion. "
                "We have revised the manuscript accordingly."
            )
        else:
            lines.append(
                "We thank the reviewer for this comment. "
                "We have considered this point carefully and revised the manuscript where appropriate."
            )

        lines.append("")
        lines.append(f"Suggested revision action: {row['suggested_revision_action']}")
        lines.append("")
        lines.append("-" * 80)
        lines.append("")

    return "\n".join(lines)


# =========================
# 3. Streamlit UI
# =========================

st.set_page_config(
    page_title="Review Comment Rebuttal Helper",
    layout="wide"
)

st.title("Review Comment Rebuttal Helper")
st.caption("Paste reviewer comments, classify them, group repeated issues, and generate a rebuttal outline.")

with st.sidebar:
    st.header("Settings")
    show_raw_comments = st.checkbox("Show raw segmented comments", value=True)
    show_keywords = st.checkbox("Show matched keywords", value=True)
    min_comment_length = st.slider("Minimum comment length", 5, 100, 15)

default_text = """Reviewer 1:
The novelty of the manuscript is unclear. The authors should better distinguish their work from prior studies.

The methodology requires more detail, especially regarding the experimental design and controls.

The language should be improved for clarity and readability.

Reviewer 2:
The discussion should be expanded to include limitations and practical implications.

The authors should cite more recent literature.

The figures and tables need clearer captions.
"""

review_text = st.text_area(
    "Paste reviewer comments here:",
    value=default_text,
    height=300
)

analyze_button = st.button("Analyze comments", type="primary")

if analyze_button:
    comments = split_comments(review_text)

    comments = [
        item for item in comments
        if len(item["comment_text"]) >= min_comment_length
    ]

    if len(comments) == 0:
        st.warning("No valid comments detected. Please check the input text.")
    else:
        df = analyze_comments(comments, taxonomy)
        plan_df = generate_thematic_response_plan(df)
        rebuttal_outline = generate_rebuttal_outline(plan_df)

        st.success(f"Detected {len(df)} comment(s) and grouped them into {len(plan_df)} response theme(s).")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total comments", len(df))
        col2.metric("Major comments", int((df["severity"] == "Major").sum()))
        col3.metric("Response themes", len(plan_df))

        st.divider()

        st.subheader("1. Thematic Response Plan")
        st.dataframe(
            plan_df,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("2. Comment Classification")

        display_columns = [
            "comment_id",
            "reviewer",
            "category",
            "severity",
            "response_mode",
            "suggested_action"
        ]

        if show_keywords:
            display_columns.append("matched_keywords")

        st.dataframe(
            df[display_columns],
            use_container_width=True,
            hide_index=True
        )

        if show_raw_comments:
            st.subheader("3. Segmented Comments")
            for _, row in df.iterrows():
                with st.expander(f"{row['comment_id']} | {row['reviewer']} | {row['category']}"):
                    st.write(row["comment_text"])
                    st.write("**Suggested action:**")
                    st.write(row["suggested_action"])

        st.subheader("4. Draft Rebuttal Outline")
        st.text_area(
            "Copy and edit this outline:",
            value=rebuttal_outline,
            height=500
        )

        st.download_button(
            label="Download rebuttal outline as TXT",
            data=rebuttal_outline,
            file_name="rebuttal_outline.txt",
            mime="text/plain"
        )

        csv_data = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="Download classification table as CSV",
            data=csv_data,
            file_name="comment_classification.csv",
            mime="text/csv"
        )

else:
    st.info("Paste comments above and click Analyze comments.")
