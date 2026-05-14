
import re
import pandas as pd
import streamlit as st


# =========================================================
# 1. Taxonomy
# 英文审稿意见用英文 keywords 匹配
# 员工看到的 category / severity / response_mode / suggested_action 是中文
# =========================================================

taxonomy = [
    {
        "category": "创新性 / 研究贡献",
        "keywords": [
            "novelty", "contribution", "originality", "innovative",
            "prior work", "previous studies", "distinguish", "gap",
            "research gap", "advance", "incremental", "incremental contribution",
            "not clear what is new", "lack of novelty"
        ],
        "severity": "重大问题",
        "response_mode": "主题合并回应",
        "suggested_action": "建议在引言和讨论部分进一步明确本文的研究贡献，并说明与已有研究相比的区别。"
    },
    {
        "category": "研究方法",
        "keywords": [
            "method", "methods", "methodology", "procedure", "protocol",
            "design", "experimental design", "control", "intervention",
            "workflow", "reproducibility", "replicable", "study design",
            "inclusion criteria", "exclusion criteria", "measurement"
        ],
        "severity": "重大问题",
        "response_mode": "逐条回应",
        "suggested_action": "建议补充或澄清研究方法、实验设计、操作流程、纳入排除标准、测量方式和对照设置等关键细节。"
    },
    {
        "category": "统计 / 数据分析",
        "keywords": [
            "statistics", "statistical", "sample size", "p-value", "p value",
            "regression", "power", "significance", "confidence interval",
            "data analysis", "effect size", "model", "robustness",
            "sensitivity analysis", "multivariate", "univariate", "adjusted",
            "missing data", "normality", "variance"
        ],
        "severity": "重大问题",
        "response_mode": "逐条回应",
        "suggested_action": "建议认真核查统计方法、样本量说明、显著性结果、模型设定和数据分析过程，并在正文中补充必要解释。"
    },
    {
        "category": "研究结果",
        "keywords": [
            "results", "findings", "outcome", "outcomes",
            "main finding", "main findings", "inconsistent", "consistency",
            "reported results", "result section", "data presentation"
        ],
        "severity": "重大问题",
        "response_mode": "逐条回应",
        "suggested_action": "建议检查结果表述是否清楚，正文、图表和数据是否一致，并避免对结果作过度解释。"
    },
    {
        "category": "文献 / 参考文献",
        "keywords": [
            "literature", "citation", "reference", "references",
            "related work", "recent studies", "missing references",
            "cite", "cited", "prior studies", "previous literature",
            "up-to-date references", "recent literature"
        ],
        "severity": "中等问题",
        "response_mode": "主题合并回应",
        "suggested_action": "建议补充或更新相关文献，并说明本文与已有研究之间的关系。"
    },
    {
        "category": "讨论 / 理论解释",
        "keywords": [
            "discussion", "interpretation", "implication", "implications",
            "mechanism", "explain", "contextualize", "theoretical",
            "practical implications", "meaning", "interpret", "why",
            "underlying mechanism"
        ],
        "severity": "中等问题",
        "response_mode": "主题合并回应",
        "suggested_action": "建议修改讨论部分，进一步解释研究发现的含义、可能机制、理论价值和实际启示。"
    },
    {
        "category": "局限性",
        "keywords": [
            "limitation", "limitations", "weakness", "weaknesses",
            "bias", "generalizability", "generalisation",
            "external validity", "caution", "limitations section"
        ],
        "severity": "中等问题",
        "response_mode": "主题合并回应",
        "suggested_action": "建议补充或强化局限性部分，说明研究结论的适用范围和需要谨慎解释的地方。"
    },
    {
        "category": "结论过度 / 论断边界",
        "keywords": [
            "overstate", "overstated", "overclaim", "overinterpret",
            "too strong", "strong conclusion", "causal", "causality",
            "conclusion is not supported", "unsupported conclusion",
            "claims are not supported"
        ],
        "severity": "重大问题",
        "response_mode": "逐条回应",
        "suggested_action": "建议检查结论是否超出数据支持范围，必要时弱化表述，并明确哪些结论是数据支持的，哪些只是推测。"
    },
    {
        "category": "摘要 / 标题 / 关键词",
        "keywords": [
            "abstract", "title", "keywords", "key words",
            "summary", "structured abstract", "headline"
        ],
        "severity": "小问题",
        "response_mode": "简要汇总回应",
        "suggested_action": "建议检查摘要、标题和关键词是否准确反映研究内容，避免夸大结论或遗漏核心信息。"
    },
    {
        "category": "语言 / 表达清晰度",
        "keywords": [
            "language", "grammar", "clarity", "readability", "English",
            "writing", "unclear", "wording", "sentence", "sentences",
            "editing", "proofreading", "polish", "awkward", "ambiguous"
        ],
        "severity": "小问题",
        "response_mode": "简要汇总回应",
        "suggested_action": "建议对全文进行语言润色，提升表达清晰度、可读性、语法准确性和术语一致性。"
    },
    {
        "category": "图表",
        "keywords": [
            "figure", "figures", "table", "tables", "legend",
            "caption", "axis", "axes", "label", "labels",
            "visual", "resolution", "supplementary figure", "supplementary table"
        ],
        "severity": "小问题",
        "response_mode": "简要汇总回应",
        "suggested_action": "建议修改图表、图注、表注、坐标轴和标题，使其更加清楚、完整，并与正文保持一致。"
    },
    {
        "category": "格式 / 期刊规范",
        "keywords": [
            "format", "formatting", "style", "reference style",
            "journal style", "typo", "typographical",
            "proofread", "layout", "template", "guidelines",
            "author guidelines"
        ],
        "severity": "小问题",
        "response_mode": "简要汇总回应",
        "suggested_action": "建议按照期刊要求统一格式、参考文献样式、排版、拼写和投稿规范细节。"
    },
    {
        "category": "伦理 / 审批 / 知情同意",
        "keywords": [
            "ethics", "ethical approval", "irb", "institutional review board",
            "informed consent", "consent", "approval", "trial registration",
            "registered", "registration"
        ],
        "severity": "重大问题",
        "response_mode": "逐条回应",
        "suggested_action": "建议认真核查伦理审批、知情同意、注册信息等内容，并在方法或声明部分补充完整信息。"
    },
    {
        "category": "数据可得性 / 代码可得性",
        "keywords": [
            "data availability", "available data", "dataset", "code availability",
            "repository", "supplementary data", "raw data", "open data",
            "materials availability"
        ],
        "severity": "中等问题",
        "response_mode": "主题合并回应",
        "suggested_action": "建议补充数据、代码或材料可得性说明；如不能公开，应说明合理原因。"
    },
    {
        "category": "泛泛的 AI 式意见",
        "keywords": [
            "improve", "strengthen", "expand", "enhance", "elaborate",
            "more comprehensive", "more rigorous", "should be improved",
            "could be improved", "further clarification", "more clearly",
            "better explain", "more detail", "would benefit from",
            "needs to be strengthened", "provide more details"
        ],
        "severity": "小问题",
        "response_mode": "主题合并回应",
        "suggested_action": "这类意见通常比较泛泛，建议与相关实质问题合并回应，不必机械逐条展开。"
    }
]


# =========================================================
# 2. Core functions
# =========================================================

def split_comments(text, min_comment_length=15):
    """
    Split reviewer comments into smaller comment units.
    Input is usually English reviewer comments.
    """
    text = text.strip()
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Split by blank lines, reviewer labels, comment labels, or numbered comments.
    parts = re.split(
        r"\n\s*\n|(?=Reviewer\s*\d+\s*:)|(?=Reviewer's comment\s*\d+)|(?=Comment\s*\d+)|(?=Major comment\s*\d+)|(?=Minor comment\s*\d+)|(?=\d+\.\s+)",
        text,
        flags=re.IGNORECASE
    )

    comments = []
    current_reviewer = "未识别审稿人"

    for part in parts:
        part = part.strip()
        if not part:
            continue

        reviewer_match = re.match(r"Reviewer\s*(\d+)\s*:", part, flags=re.IGNORECASE)
        if reviewer_match:
            current_reviewer = f"审稿人 {reviewer_match.group(1)}"
            part = re.sub(r"Reviewer\s*\d+\s*:", "", part, flags=re.IGNORECASE).strip()

        if len(part) >= min_comment_length:
            comments.append({
                "reviewer": current_reviewer,
                "comment_text": part
            })

    return comments


def classify_comment(comment_text, taxonomy):
    """
    Classify one reviewer comment based on English keyword matching.
    Output labels and guidance are Chinese.
    """
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
            "category": "未分类 / 需要人工判断",
            "score": 0,
            "matched_keywords": [],
            "severity": "中等问题",
            "response_mode": "主题合并回应",
            "suggested_action": "系统没有识别到明确类别。建议人工判断该意见是否涉及核心科学问题；如果只是泛泛建议，可与相关意见合并处理。"
        }

    # Sort by score first. If tie, keep taxonomy order implicitly.
    category_scores = sorted(category_scores, key=lambda x: x["score"], reverse=True)
    return category_scores[0]


def analyze_comments(comments, taxonomy):
    """
    Analyze all reviewer comments and return a pandas DataFrame.
    """
    rows = []

    for i, item in enumerate(comments, start=1):
        comment_text = item["comment_text"]
        classification = classify_comment(comment_text, taxonomy)

        rows.append({
            "意见编号": f"C{i}",
            "审稿人": item["reviewer"],
            "原始英文意见": comment_text,
            "系统分类": classification["category"],
            "重要程度": classification["severity"],
            "建议回应方式": classification["response_mode"],
            "匹配关键词": "; ".join(classification["matched_keywords"]),
            "建议修改动作": classification["suggested_action"]
        })

    return pd.DataFrame(rows)


def generate_thematic_response_plan(df):
    """
    Group comments by category and generate a thematic response plan.
    """
    plans = []

    for category, group in df.groupby("系统分类"):
        comment_ids = ", ".join(group["意见编号"].tolist())
        reviewers = ", ".join(sorted(group["审稿人"].unique()))
        severity = group["重要程度"].iloc[0]
        response_mode = group["建议回应方式"].iloc[0]
        suggested_action = group["建议修改动作"].iloc[0]

        if response_mode == "逐条回应":
            response_strategy = "建议逐条、具体回应。尤其是涉及研究方法、统计分析、数据结果、伦理审批或核心结论的问题，不建议简单合并。"
        elif response_mode == "主题合并回应":
            response_strategy = "建议将相似意见合并成一个主题统一回应。这样可以避免对重复、泛泛或 AI 风格较强的意见进行机械式逐条回复。"
        elif response_mode == "简要汇总回应":
            response_strategy = "建议简要回应，说明已根据意见对稿件进行了相应修改即可。通常不需要展开长篇解释。"
        else:
            response_strategy = "建议人工判断该意见是否需要单独回应，或是否可以与其他相关意见合并处理。"

        plans.append({
            "回复主题": category,
            "相关意见编号": comment_ids,
            "相关审稿人": reviewers,
            "重要程度": severity,
            "建议回应方式": response_mode,
            "回应策略": response_strategy,
            "建议修改动作": suggested_action
        })

    plan_df = pd.DataFrame(plans)

    # Sort major issues first.
    severity_order = {
        "重大问题": 1,
        "中等问题": 2,
        "小问题": 3
    }

    if not plan_df.empty:
        plan_df["排序"] = plan_df["重要程度"].map(severity_order).fillna(99)
        plan_df = plan_df.sort_values(by=["排序", "回复主题"]).drop(columns=["排序"])

    return plan_df


def generate_rebuttal_outline(plan_df):
    """
    Generate a Chinese guidance-style rebuttal outline.
    The final English rebuttal can be written from these prompts.
    """
    lines = []

    lines.append("给编辑和审稿人的回复框架")
    lines.append("")
    lines.append("一、开头建议")
    lines.append(
        "感谢编辑和审稿人对本文的认真阅读和建设性意见。由于部分意见在内容上存在重叠，"
        "我们按照主题对回复进行了整理，同时确保所有实质性问题都得到回应。"
    )
    lines.append("")
    lines.append("二、主要修改概述")
    lines.append("1. [简要概括主要修改 1，例如：补充研究贡献说明]")
    lines.append("2. [简要概括主要修改 2，例如：完善方法或统计说明]")
    lines.append("3. [简要概括主要修改 3，例如：扩展讨论和局限性部分]")
    lines.append("")
    lines.append("三、详细回复建议")
    lines.append("")

    for idx, row in plan_df.iterrows():
        lines.append(f"回复主题 {idx + 1}：{row['回复主题']}")
        lines.append(f"相关意见编号：{row['相关意见编号']}")
        lines.append(f"相关审稿人：{row['相关审稿人']}")
        lines.append(f"重要程度：{row['重要程度']}")
        lines.append(f"建议回应方式：{row['建议回应方式']}")
        lines.append("")
        lines.append("员工处理建议：")

        if row["建议回应方式"] == "逐条回应":
            lines.append(
                "这类意见建议逐条认真回应。处理时应明确说明："
                "是否接受该意见、稿件中具体修改了什么、修改位置在哪里；"
                "如果没有完全采纳，需要给出清楚、礼貌、基于学术理由的解释。"
            )
        elif row["建议回应方式"] == "主题合并回应":
            lines.append(
                "这类意见可以合并为一个主题统一回应。处理时可说明："
                "多条意见都涉及同一问题，作者已在相应章节中统一修改，"
                "并概括主要修改内容。"
            )
        elif row["建议回应方式"] == "简要汇总回应":
            lines.append(
                "这类意见通常属于语言、格式、图表或呈现层面的问题。"
                "回复时可以简要说明已经根据意见完成修改，不必逐句展开解释。"
            )
        else:
            lines.append(
                "该意见建议人工进一步判断。若涉及核心科学问题，应单独回应；"
                "若只是泛泛建议，可以与相关主题合并处理。"
            )

        lines.append("")
        lines.append(f"建议修改动作：{row['建议修改动作']}")
        lines.append("")
        lines.append("可改写为英文 rebuttal 的句式：")

        if row["建议回应方式"] == "逐条回应":
            lines.append(
                "We thank the reviewer for this important comment. "
                "We have addressed this issue by [describe the specific revision, analysis, clarification, or justification]."
            )
        elif row["建议回应方式"] == "主题合并回应":
            lines.append(
                "Several comments raised concerns related to this issue. "
                "We have revised the manuscript to address this point more clearly. "
                "Specifically, we have [summarize the grouped revisions]."
            )
        elif row["建议回应方式"] == "简要汇总回应":
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
        lines.append("-" * 80)
        lines.append("")

    return "\n".join(lines)


def build_mapping_table(df):
    """
    Build a comment-to-response mapping table.
    """
    mapping_df = df[[
        "意见编号",
        "审稿人",
        "系统分类",
        "建议回应方式",
        "建议修改动作"
    ]].copy()

    mapping_df = mapping_df.rename(columns={
        "系统分类": "对应回复主题",
        "建议修改动作": "建议处理方式"
    })

    return mapping_df


# =========================================================
# 3. Streamlit UI
# =========================================================

st.set_page_config(
    page_title="审稿意见归类与回复建议工具",
    layout="wide"
)

st.title("审稿意见归类与回复建议工具")
st.caption("粘贴英文审稿意见，系统会用中文给出分类、重要程度、回应方式和修改建议。")

with st.sidebar:
    st.header("设置")
    show_raw_comments = st.checkbox("显示切分后的原始意见", value=True)
    show_keywords = st.checkbox("显示匹配到的英文关键词", value=True)
    min_comment_length = st.slider("最短意见长度", 5, 150, 15)

    st.divider()
    st.markdown("### 使用建议")
    st.write("1. 直接粘贴英文 reviewer comments。")
    st.write("2. 点击 Analyze。")
    st.write("3. 先看“主题合并方案”，再看逐条分类。")
    st.write("4. 重大问题优先处理。")

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
    "请在这里粘贴英文审稿意见：",
    value=default_text,
    height=320
)

analyze_button = st.button("Analyze / 开始分析", type="primary")

if analyze_button:
    comments = split_comments(review_text, min_comment_length=min_comment_length)

    if len(comments) == 0:
        st.warning("没有识别到有效审稿意见。请检查输入文本，或降低左侧的最短意见长度。")
    else:
        df = analyze_comments(comments, taxonomy)
        plan_df = generate_thematic_response_plan(df)
        mapping_df = build_mapping_table(df)
        rebuttal_outline = generate_rebuttal_outline(plan_df)

        st.success(f"已识别 {len(df)} 条意见，并合并为 {len(plan_df)} 个回复主题。")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("意见总数", len(df))
        col2.metric("重大问题", int((df["重要程度"] == "重大问题").sum()))
        col3.metric("中等问题", int((df["重要程度"] == "中等问题").sum()))
        col4.metric("回复主题数", len(plan_df))

        st.divider()

        st.subheader("1. 主题合并方案")
        st.write("优先看这里：它告诉员工哪些意见可以合并回应，哪些需要逐条回应。")
        st.dataframe(
            plan_df,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("2. 逐条意见分类")
        search_term = st.text_input("搜索意见、分类、审稿人或关键词：", value="")

        display_columns = [
            "意见编号",
            "审稿人",
            "系统分类",
            "重要程度",
            "建议回应方式",
            "建议修改动作"
        ]

        if show_keywords:
            display_columns.append("匹配关键词")

        filtered_df = df.copy()

        if search_term.strip():
            term = search_term.lower().strip()
            filtered_df = df[
                df.apply(
                    lambda row: term in " ".join([str(x) for x in row.values]).lower(),
                    axis=1
                )
            ]

        st.dataframe(
            filtered_df[display_columns],
            use_container_width=True,
            hide_index=True
        )

        st.subheader("3. Comment-to-response 对照表")
        st.write("这个表可以帮助员工确认每条审稿意见是否已经被某个回复主题覆盖。")
        st.dataframe(
            mapping_df,
            use_container_width=True,
            hide_index=True
        )

        if show_raw_comments:
            st.subheader("4. 切分后的原始英文意见")
            for _, row in df.iterrows():
                with st.expander(f"{row['意见编号']} | {row['审稿人']} | {row['系统分类']} | {row['重要程度']}"):
                    st.write(row["原始英文意见"])
                    st.write("**中文处理建议：**")
                    st.write(row["建议修改动作"])

        st.subheader("5. 回复框架与员工处理提示")
        st.text_area(
            "可复制到 Word 或内部流程中继续修改：",
            value=rebuttal_outline,
            height=550
        )

        st.download_button(
            label="下载回复框架 TXT",
            data=rebuttal_outline,
            file_name="rebuttal_outline_cn_guidance.txt",
            mime="text/plain"
        )

        csv_data = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="下载逐条分类 CSV",
            data=csv_data,
            file_name="comment_classification_cn.csv",
            mime="text/csv"
        )

        mapping_csv = mapping_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="下载对照表 CSV",
            data=mapping_csv,
            file_name="comment_response_mapping_cn.csv",
            mime="text/csv"
        )

else:
    st.info("请粘贴英文审稿意见，然后点击 Analyze / 开始分析。")
