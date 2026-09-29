import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import os
import requests  # 用于向 WPS 接口发射数据

# ==========================================
# 🔬 PMSA-FoodBiochem AI Learning Workstation V2.0
# 👑 食品生物化学高阶思维、酶动力学、代谢仿真与过程性评价平台
# ==========================================

st.set_page_config(page_title="PMSA-FoodBiochem Workstation V2.0", layout="wide", page_icon="🔬")

# WPS 官方多维表格自动化 Webhook 接口地址
WPS_WEBHOOK_URL = "https://www.kdocs.cn/chatflow/api/v2/func/webhook/3EspRZcftLE3c8SSMOu4VeBbqeO" 

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Helvetica+Neue:wght=300;400;600&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        background-color: #F8FAFC;
    }
    .pmsa-card { padding: 24px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border-left: 6px solid; }
    .card-problem { background-color: #EBF8FF; border-left-color: #3182CE; }
    .card-mechanism { background-color: #E6FFFA; border-left-color: #319795; }
    .card-simulation { background-color: #F0FFF4; border-left-color: #38A169; }
    .card-application { background-color: #F7FAFC; border-left-color: #2F855A; }
    .main-title { color: #1A365D; font-weight: 700; font-size: 2.4rem; text-align: center; margin-bottom: 5px; }
    .sub-title { color: #4A5568; font-size: 1.1rem; text-align: center; margin-bottom: 25px; font-style: italic; }
</style>
""", unsafe_allow_html=True)

if "user_role" not in st.session_state: st.session_state.user_role = None
if "uid" not in st.session_state: st.session_state.uid = ""
if "cloud_logs_backup" not in st.session_state: st.session_state.cloud_logs_backup = []

TRANSLATIONS = {
    "zh": {
        "title": "🔬 PMSA-食品生物化学 AI 智慧学习工作站 V2.0",
        "sub": "由 PMSA 教学模型驱动的食品生物化学高阶思维、酶动力学/代谢分析与过程性评价平台",
        "lang_label": "🌐 切换系统语言 / Language",
        "lbl_case": "🌟 1. 选择探究章节模块:",
        "lbl_step": "🧭 2. PMSA 教学流程环节:",
        "logout_btn": "退出当前系统",
        "p_bg": "📖 Problem - 生物化学工业背景与研究痛点",
        "p_focus": "🔬 分子机制与生化代谢焦点",
        "p_task": "🎯 核心生化挑战与高阶任务目标",
        "p_task_1": "* **任务 1:** 解析核心食品生化劣化/转化机制并提出科学假设。\n* **任务 2:** 深度解构酶动力学与生化代谢数据集趋势。",
        "p_download_btn": "📥 下载该模块标准生化数据集模板",
        "m_title": "🌿 Mechanism - 生物化学分子机制与通路图谱建构",
        "m_keyword_lbl": "⚠️ 核心生化机制关键词/酶/代谢通路守卫:",
        "m_lbl": "请梳理该食品生物化学变化/代谢反应的底层分子机制链条:",
        "m_holder": "例如：底物结合酶活性中心 -> 生成中间产物 -> 自由基夺氢链式反应 -> 产生挥发性醛酮类或聚合物...",
        "m_btn": "提交生化机制链条并生成多维诊断",
        "m_success": "✅ 生化机制处理完成！过程性评价痕迹已成功上传至 WPS 云端痕迹表。",
        "s_title": "📊 Simulation - 酶动力学与生化代谢数据挖掘区",
        "s_upload": "📤 上传您个人的实验原始数据集 (支持 CSV/XLSX)",
        "s_preview": "生化数据矩阵快照:",
        "a_title": "🚀 Application - 食品生物技术创新与质量调控方案提报区",
        "a_task_lbl": "💡 当前模块核心任务：",
        "a_intro": "请结合在前几个阶段梳理的生物化学机制与动力学仿真趋势，完成以下结构化的食品生物技术改良与调控方案设计：",
        "a_part1": "📝 第一部分：生物技术创新方案基本信息",
        "a_p1_name": "✨ 1. 方案创新名称:",
        "a_p1_name_holder": "例如：基于复配植物多酚定向抑制果蔬多酚氧化酶（PPO）的绿色保鲜技术",
        "a_p1_route": "🛠️ 2. 核心生物技术路径分类:",
        "a_routes": ["酶抑制与动力学调控", "内源酶激活与肉质重塑", "微生物定向发酵与生物转化", "酶法靶向水解与活性肽制备"],
        "a_part2": "🔬 第二部分：高阶生物工程设计规范",
        "a_t1_lbl": "🎯 任务 1：核心生化调控参数与配方/工艺设计",
        "a_t1_cap": "请具体列出生物技术调控参数（如酶用量、底物浓度、pH、温度、竞争性抑制剂添加量或发酵条件等）。",
        "a_t1_holder": "例：添加0.05%柠檬酸（调pH至4.0）配合0.02%绿原酸，在4℃下处理果肉，抑制PPO催化活性...",
        "a_t2_lbl": "🧬 任务 2：方案背后的生物化学与代谢机制阐述",
        "a_t2_cap": "请简述你采用的上述生物技术，是如何在蛋白质/酶/代谢通路层面上调控食品品质或抑制劣变的？",
        "a_t2_holder": "例：柠檬酸通过螯合PPO活性中心铜离子（Cu2+）降低酶活；低pH导致PPO空间构象改变，底物结合亲和力降低...",
        "a_t3_lbl": "📊 任务 3：生化指标监测与品质验证评价体系",
        "a_t3_cap": "你计划测定哪些关键生化指标（如酶活残留率、MDA含量、水解度DH、风味前体量）来验证方案？",
        "a_t3_holder": "例：测定处理组与对照组在储藏期内的PPO相对活性、褐变指数（A420）、总酚含量及游离氨基酸组分...",
        "a_part3": "📤 第三部分：附件与最终提报",
        "a_file_lbl": "📎 上传更详尽的生化实验设计书/正交试验图表/PDF报告 (可选)",
        "a_submit_btn": "🚀 提交最终食品生物技术调控方案",
        "a_success": "🎉 方案提报成功！学术数据已安全发射至班级过程性看板并实时同步至 WPS。",
        "metric_1": "生化机制建构深度", "metric_2": "动力学数据主张力", "metric_3": "生物技术创新性",
        "cases": [
            "1. 酶促褐变与酶动力学调控 (Enzymatic Browning & Kinetics)",
            "2. 内源酶与肌肉食品成熟/品质重塑 (Endogenous Enzymes & Meat Quality)",
            "3. 食品糖类代谢与美拉德非酶变化 (Carbohydrate Metabolism & Maillard)",
            "4. 脂质生物氧化与自由基链式反应 (Lipid Bio-oxidation & Free Radicals)",
            "5. 食品发酵与微生态生物转化 (Food Fermentation & Biotransformation)",
            "6. 风味前体物的生物合成与转化 (Flavor Precursor Biogenesis)",
            "7. 功能性生物活性肽与酶解靶向制备 (Bioactive Peptides & Enzymatic Hydrolysis)"
        ],
        "steps": ["Problem 科学情境", "Mechanism 机制建构", "Simulation 数据分析", "Application 方案应用", "Analytics 智能评价"]
    },
    "en": {
        "title": "🔬 PMSA-FoodBiochem AI Learning Workstation V2.0",
        "sub": "A PMSA-driven platform for higher-order thinking, enzyme kinetics, metabolic analysis & formative assessment",
        "lang_label": "🌐 Switch System Language",
        "lbl_case": "🌟 1. Select Chapter Module:",
        "lbl_step": "🧭 2. PMSA Pedagogical Stage:",
        "logout_btn": "Sign Out System",
        "p_bg": "📖 Problem - Food Biochemistry Industrial Background & Research Bottlenecks",
        "p_focus": "🔬 Biochemical Mechanism & Metabolic Focus",
        "p_task": "🎯 Core Biochemical Challenges & Task Objectives",
        "p_task_1": "* **Task 1:** Parse core food biochemical degradation/conversion mechanisms and formulate hypotheses.\n* **Task 2:** Deconstruct enzyme kinetics and metabolic dataset trends.",
        "p_download_btn": "📥 Download Standard Biochemical Dataset Template",
        "m_title": "🌿 Mechanism - Biochemical Mechanism & Pathway Mapping",
        "m_keyword_lbl": "⚠️ Core Biochemical Keywords / Enzymes / Pathways Guard:",
        "m_lbl": "Map the underlying biochemical mechanism or metabolic pathway of the food phenomenon:",
        "m_holder": "e.g., Substrate binds to active site -> Intermediate formation -> Radical chain reaction -> Volatile aldehyde/ketone or polymer production...",
        "m_btn": "Submit Mechanism Map for Multidimensional Diagnosis",
        "m_success": "✅ Biochemical mechanism processing complete! Data synchronized with WPS Cloud.",
        "s_title": "📊 Simulation - Enzyme Kinetics & Metabolic Data Mining",
        "s_upload": "📤 Upload Your Empirical Dataset (Supports CSV/XLSX)",
        "s_preview": "Biochemical Data Matrix Snapshot:",
        "a_title": "🚀 Application - Food Biotechnology Innovation & Quality Control Scheme",
        "a_task_lbl": "💡 Core Task for Current Module:",
        "a_intro": "Combine the biochemical mechanisms and kinetic trends explored in previous stages to complete the food biotechnology control design:",
        "a_part1": "Part I: Basic Biotechnology Project Information",
        "a_p1_name": "✨ 1. Project Innovation Title:",
        "a_p1_name_holder": "e.g., Green preservation of fresh fruits via Polyphenol-based Polyphenol Oxidase (PPO) inhibition",
        "a_p1_route": "🛠️ 2. Core Technological Route Classification:",
        "a_routes": ["Enzyme Inhibition & Kinetics", "Endogenous Enzymes & Meat Quality", "Fermentation & Biotransformation", "Enzymatic Hydrolysis & Peptides"],
        "a_part2": "🔬 Part II: Higher-Order Bio-Engineering Specifications",
        "a_t1_lbl": "🎯 Task 1: Core Biochemical Control Parameters & Formulation",
        "a_t1_cap": "Specify biotechnology parameters (e.g., enzyme dosage, substrate concentration, pH, temperature, inhibitor concentration).",
        "a_t1_holder": "e.g., Add 0.05% citric acid (pH 4.0) with 0.02% chlorogenic acid at 4°C to inhibit PPO activity...",
        "a_t2_lbl": "🧬 Task 2: Biochemical & Metabolic Justification",
        "a_t2_cap": "Explain how your approach regulates quality or inhibits deterioration at the protein/enzyme/metabolic pathway level.",
        "a_t2_holder": "e.g., Citric acid chelates Cu2+ at PPO active center; low pH induces conformational changes, lowering substrate affinity...",
        "a_t3_lbl": "📊 Task 3: Biochemical Monitoring & Quality Evaluation",
        "a_t3_cap": "What key biochemical indicators (e.g., residual enzyme activity, MDA, degree of hydrolysis DH) will you measure?",
        "a_t3_holder": "e.g., Measure relative PPO activity, browning index (A420), total phenols, and free amino acids during storage...",
        "a_part3": "📤 Part III: Attachments & Final Submission",
        "a_file_lbl": "📎 Upload detailed biochemical design, orthogonal charts, or PDF report (Optional)",
        "a_submit_btn": "🚀 Submit Final Biotechnology Scheme",
        "a_success": "🎉 Submission Successful! Academic footprint synchronously uploaded to WPS.",
        "metric_1": "Biochemical Mapping Depth", "metric_2": "Kinetic Argumentation", "metric_3": "Biotech Innovation",
        "cases": [
            "1. Enzymatic Browning & Kinetics",
            "2. Endogenous Enzymes & Meat Quality",
            "3. Carbohydrate Metabolism & Maillard",
            "4. Lipid Bio-oxidation & Free Radicals",
            "5. Food Fermentation & Biotransformation",
            "6. Flavor Precursor Biogenesis",
            "7. Bioactive Peptides & Enzymatic Hydrolysis"
        ],
        "steps": ["Problem Context", "Mechanism Mapping", "Simulation Analytics", "Application Output", "Analytics Feedback"]
    }
}

np.random.seed(42)

# 7大《食品生物化学》模块详细语料
MODULE_DESCRIPTIONS = {
    0: { # 酶促褐变与酶动力学调控
        "zh": {
            "problem": "鲜切果蔬加工与储存过程中，多酚氧化酶（PPO）催化酚类底物快速发生酶促褐变，导致品质劣变。如何选择专一性抑制剂进行精准动力学调控？",
            "mechanism": "PPO 活性中心 Cu2+ 催化单酚羟基化和双酚脱氢生成醌 $\to$ 醌类自由基缩合生成黑色素；竞争性/非竞争性抑制剂通过结合活性中心改变 Km 或 Vmax。",
            "application": "针对鲜切苹果或马铃薯，设计一套基于天然多酚/有机酸抑制 PPO 活性与控制酶促褐变的绿色生物保鲜方案。"
        },
        "en": {
            "problem": "During fresh-cut fruit processing, Polyphenol Oxidase (PPO) catalyzes rapid browning. How can we select specific inhibitors via kinetics control?",
            "mechanism": "PPO Cu2+ active site oxidizes phenols to quinones -> Quinones polymerize to melanin; Inhibitors alter Km or Vmax.",
            "application": "Design a green bio-preservation scheme using natural PPO inhibitors for fresh-cut produce."
        }
    },
    1: { # 内源酶与肌肉食品成熟/品质重塑
        "zh": {
            "problem": "畜禽屠宰后肌肉发生僵直与成熟，内源钙激活酶（Calpain）与溶酶体酶（Cathepsin）如何动态重塑肌纤维结构并影响肉品的嫩度与持水力？",
            "mechanism": "糖原无氧酵解导致 pH 下降 $\to$ 钙离子释放激活 Calpain $\to$ 选择性降解 Desmin 和 Titin 等肌纤维微结构蛋白 $\to$ 保水性与嫩度显著改变。",
            "application": "设计一套基于温湿度/离子浓度调控内源酶活性的牛肉/猪肉宰后排毒与精准成熟工艺。"
        },
        "en": {
            "problem": "How do endogenous Calpains and Cathepsins reshape muscle fibril structures and affect meat tenderness/WHC post-mortem?",
            "mechanism": "Post-mortem glycolysis drops pH -> Ca2+ release activates Calpain -> Selective degradation of Desmin/Titin -> Texture & WHC transformation.",
            "application": "Design a post-mortem meat aging process by controlling endogenous enzyme kinetics."
        }
    },
    2: { # 食品糖类代谢与美拉德非酶变化
        "zh": {
            "problem": "热加工过程中还原糖与氨基酸发生美拉德反应，在赋予食品独特风味与色泽的同时，如何生物化学抑制定量丙烯酰胺（Acrylamide）等毒害产物？",
            "mechanism": "天冬酰胺（Asn）与还原糖羰基进行加成缩合 $\to$ Schiff 碱生成 $\to$ Strecker 降解形成丙烯酰胺；天冬酰胺酶（Asparaginase）可预先阻断此通路。",
            "application": "利用天冬酰胺酶预处理结合加工参数调控，设计低丙烯酰胺、高风味的健康烘焙食品方案。"
        },
        "en": {
            "problem": "Maillard reaction creates flavor but generates toxic acrylamide. How can we biochemically block acrylamide formation?",
            "mechanism": "Asparagine + Reducing sugars -> Schiff base -> Strecker degradation to acrylamide; Asparaginase pre-treatment cleaves Asparagine.",
            "application": "Design a healthy baking scheme using Asparaginase pre-treatment to inhibit acrylamide."
        }
    },
    3: { # 脂质生物氧化与自由基链式反应
        "zh": {
            "problem": "富含不饱和脂肪酸（PUFA）的食品极易发生脂质过氧化，引发哈变风味与丙二醛（MDA）积累。如何通过生物抗氧化机制终止自由基链式反应？",
            "mechanism": "脂氧合酶（LOX）或单线态氧引发自由基 $\to$ 夺氢生成氢过氧化物（ROOH） $\to$ β-裂解生成小分子醛酮；生化抗氧化剂（如生育酚、SOD）提供氢原子清除 ROO•。",
            "application": "针对富含 EPA/DHA 的鱼油或坚果食品，构建多屏障内源/外源生物抗氧化稳定体系。"
        },
        "en": {
            "problem": "Lipid peroxidation of PUFA causes rancidity and toxic MDA. How can radical chain reactions be terminated via antioxidant mechanisms?",
            "mechanism": "LOX/singlet oxygen initiates radicals -> ROOH formation -> beta-scission into aldehydes; Antioxidants donate H-atoms to scavenge ROO•.",
            "application": "Construct a multi-barrier antioxidant system for omega-3 rich marine oils or nuts."
        }
    },
    4: { # 食品发酵与微生态生物转化
        "zh": {
            "problem": "发酵乳/发酵蔬菜中，乳酸菌（LAB）如何利用碳水化合物进行同型/异型乳酸发酵，并产生抑菌肽与风味物质？",
            "mechanism": "EMP/PKP 通路代谢葡萄糖 $\to$ 丙酮酸还原为乳酸（降低pH） $\to$ 产生短链脂肪酸（SCFA）与细菌素（Bacteriocin） $\to$ 抑制致病菌并重塑流变学。",
            "application": "设计一款基于多菌种共生发酵的益生菌功能性发酵食品及其生物转化工艺。"
        },
        "en": {
            "problem": "How do Lactic Acid Bacteria convert carbs via lactic fermentation to generate flavor and bacteriocins?",
            "mechanism": "EMP/PKP pathways metabolize glucose to lactic acid -> pH drops -> Production of SCFAs and bacteriocins -> Pathogen inhibition & gelation.",
            "application": "Design a probiotic functional fermented food using co-culture fermentation technology."
        }
    },
    5: { # 风味前体物的生物合成与转化
        "zh": {
            "problem": "水果采后成熟或茶树鲜叶加工过程中，关键香气物质（如青香、果香）是如何由脂质和氨基酸前体生物合成的？",
            "mechanism": "亚麻酸/亚油酸 $\to$ LOX 与氢过氧化物裂解酶（HPL）催化 $\to$ C6/C9 绿叶醛酮 $\to$ 醇脱氢酶（ADH）与醇酰基转移酶（AAT）转化生成挥发性酯类。",
            "application": "开发一套调控果蔬采后风味酶（ADH/AAT）表达与前体转化的香气保全/增香技术。"
        },
        "en": {
            "problem": "How are volatile flavor compounds biosynthesized from lipid and amino acid precursors during fruit ripening?",
            "mechanism": "Linolenic acid -> LOX & HPL catalysis -> C6/C9 aldehydes -> ADH & AAT catalysis to volatile esters.",
            "application": "Develop a flavor preservation scheme regulating ADH/AAT activity in post-harvest produce."
        }
    },
    6: { # 功能性生物活性肽与酶解靶向制备
        "zh": {
            "problem": "如何利用特异性蛋白酶（如碱性蛋白酶、胰蛋白酶）定向水解蛋白源，高效切割释放具有降血压（ACE抑制）或抗氧化的生物活性肽？",
            "mechanism": "蛋白酶专一性识别疏水/碱性氨基酸残基肽键 $\to$ 底物开裂暴露活性末端 $\to$ 活性肽与靶点（如ACE酶活性中心）高效结合。",
            "application": "针对大豆蛋白、乳清蛋白或牦牛乳蛋白，设计一套定量控制水解度（DH）与靶向活性肽制备工艺。"
        },
        "en": {
            "problem": "How can specific proteases be used to hydroylze proteins to target bioactive peptides with ACE-inhibitory activity?",
            "mechanism": "Protease recognizes specific peptide bonds -> Cleavage exposes active terminals -> Peptides dock into active sites of target enzymes.",
            "application": "Design a enzymatic hydrolysis process to produce biopeptides with controlled degree of hydrolysis (DH)."
        }
    }
}

# 数据生成引擎：对应食品生物化学实验数据
def make_biochem_data(module_idx):
    if module_idx == 0: # PPO 酶动力学数据
        substrates = [0.5, 1.0, 2.0, 4.0, 8.0, 12.0]
        v_control = [round(15 * s / (2.0 + s) + np.random.normal(0, 0.2), 2) for s in substrates]
        v_inhibitor = [round(15 * s / (5.0 + s) + np.random.normal(0, 0.2), 2) for s in substrates] # 竞争性抑制：Km增加
        return pd.DataFrame({"Substrate_mM": substrates, "V_Control_(uM/min)": v_control, "V_Inhibitor_(uM/min)": v_inhibitor})
    elif module_idx == 6: # 酶解活性肽 DH 与 ACE 抑制率数据
        times = [10, 30, 60, 90, 120, 180]
        dh = [round(5 + 12 * (t / (30 + t)) + np.random.normal(0, 0.3), 1) for t in times]
        ace_inhibition = [round(20 + 65 * (t / (40 + t)) + np.random.normal(0, 1.0), 1) for t in times]
        return pd.DataFrame({"Hydrolysis_Time_(min)": times, "DH_(%)": dh, "ACE_Inhibition_(%)": ace_inhibition})
    else:
        times = [0, 2, 4, 6, 8, 10]
        indicator_a = [round(100 * np.exp(-0.15 * t) + np.random.normal(0, 1), 1) for t in times]
        indicator_b = [round(5 + 15 * (1 - np.exp(-0.3 * t)) + np.random.normal(0, 0.5), 1) for t in times]
        return pd.DataFrame({"Time_(Days)": times, "Substrate_Remaining_(%)": indicator_a, "Product_Formed_(mg/g)": indicator_b})

CASE_DATA_ENGINE = {
    0: {"func": lambda: make_biochem_data(0), "x": "Substrate_mM", "y": "V_Control_(uM/min)", "kws": ["PPO", "Cu2+", "Km", "Vmax", "Competitive Inhibition"]},
    1: {"func": lambda: make_biochem_data(1), "x": "Time_(Days)", "y": "Product_Formed_(mg/g)", "kws": ["Calpain", "Cathepsin", "Desmin", "Myofibrillar", "Tenderness"]},
    2: {"func": lambda: make_biochem_data(2), "x": "Time_(Days)", "y": "Product_Formed_(mg/g)", "kws": ["Asparagine", "Maillard", "Acrylamide", "Strecker", "Asparaginase"]},
    3: {"func": lambda: make_biochem_data(3), "x": "Time_(Days)", "y": "Product_Formed_(mg/g)", "kws": ["LOX", "Free Radical", "ROOH", "MDA", "Antioxidant"]},
    4: {"func": lambda: make_biochem_data(4), "x": "Time_(Days)", "y": "Product_Formed_(mg/g)", "kws": ["Lactic Acid Bacteria", "EMP Pathway", "Bacteriocin", "pH", "SCFA"]},
    5: {"func": lambda: make_biochem_data(5), "x": "Time_(Days)", "y": "Product_Formed_(mg/g)", "kws": ["Lipoxygenase", "ADH", "AAT", "Esters", "Flavor Precursor"]},
    6: {"func": lambda: make_biochem_data(6), "x": "Hydrolysis_Time_(min)", "y": "ACE_Inhibition_(%)", "kws": ["Protease", "Hydrolysis Degree (DH)", "ACE Inhibition", "Bioactive Peptide", "Cleavage Site"]}
}

LOG_COLUMNS = ["Student_ID", "Chapter_Module", "Stage", "Action_Type", "User_Input_Cleaned", "Score_Total", "Score_Dim1", "Score_Dim2", "Score_Dim3", "Timestamp"]

# 保存学习日志至 WPS
def save_learning_log(student_id, chapter, stage, action, user_text, score_total, dim_scores=None):
    dim_scores = dim_scores or {}
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    payload_data = {
        "Student_ID": str(student_id),
        "Chapter_Module": str(chapter),
        "Stage": str(stage),
        "Action_Type": str(action),
        "User_Input_Cleaned": str(user_text).replace(",", "，"),
        "Score_Total": float(round(score_total, 1)),
        "Score_Dim1": float(round(dim_scores.get("dim1", 0), 1)),
        "Score_Dim2": float(round(dim_scores.get("dim2", 0), 1)),
        "Score_Dim3": float(round(dim_scores.get("dim3", 0), 1)),
        "Timestamp": timestamp
    }
    st.session_state.cloud_logs_backup.append(payload_data)
    
    if WPS_WEBHOOK_URL:
        try:
            requests.post(WPS_WEBHOOK_URL, json=payload_data, timeout=5)
        except Exception:
            pass

# 登录系统逻辑
if st.session_state.user_role is None:
    st.markdown("<div style='margin-top: 80px;'></div>", unsafe_allow_html=True)
    _, c2, _ = st.columns([1, 1.8, 1])
    with c2:
        with st.container(border=True):
            st.markdown(f"<h3 style='text-align: center; color: #1A365D;'>🔬 PMSA-FoodBiochem AI 智慧工作站 V2.0</h3>", unsafe_allow_html=True)
            st.write("---")
            input_uid = st.text_input("👤 请输入学号/工号 (ID):")
            access_token = st.text_input("🔑 请输入系统密钥 (Access Token):", type="password")
            
            if st.button("激活并进入工作站", type="primary", width="stretch"):
                if not input_uid: st.error("❌ 请输入凭证。")
                elif access_token == "student2026":
                    st.session_state.user_role = "Student"; st.session_state.uid = input_uid; st.rerun()
                elif access_token == "teacher7788":
                    st.session_state.user_role = "Teacher"; st.session_state.uid = f"Instructor_{input_uid}"; st.rerun()
                else: st.error("❌ 访问密钥无效。")
else:
    lang = st.sidebar.selectbox(TRANSLATIONS["zh"]["lang_label"], ["zh", "en"])
    t_t = TRANSLATIONS[lang]

    st.sidebar.markdown(f"<div style='background-color:#EDF2F7; padding:12px; border-radius:8px; margin-bottom:15px;'><p style='margin-bottom:4px; font-size:13px;'>👤 <b>ID:</b> <code style='color:#2B6CB0;'>{st.session_state.uid}</code></p><p style='margin-bottom:0px; font-size:13px;'>🎖️ <b>Role:</b> <code style='color:#2F855A;'>{st.session_state.user_role}</code></p></div>", unsafe_allow_html=True)

    if st.sidebar.button(t_t["logout_btn"], width="stretch"):
        st.session_state.user_role = None; st.session_state.uid = ""; st.rerun()

    st.sidebar.markdown("---")
    case_idx = st.sidebar.selectbox(t_t["lbl_case"], range(len(t_t["cases"])), format_func=lambda x: t_t["cases"][x])
    step_name = st.sidebar.radio(t_t["lbl_step"], t_t["steps"])

    st.markdown(f"<h1 class='main-title'>{t_t['title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='sub-title'>{t_t['sub']}</p>", unsafe_allow_html=True)

    module_info = MODULE_DESCRIPTIONS[case_idx][lang]
    df_sim = CASE_DATA_ENGINE[case_idx]["func"]()

    if "Problem" in step_name or "科学情境" in step_name:
        st.markdown(f"<div class='pmsa-card card-problem'><h3>{t_t['p_bg']}</h3></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            with st.container(border=True):
                st.markdown(f"#### {t_t['p_bg']}"); st.info(module_info["problem"])
        with c2:
            with st.container(border=True):
                st.markdown(f"#### {t_t['p_focus']}"); st.success(module_info["mechanism"])
        st.markdown("---")
        st.markdown(f"### {t_t['p_task']}")
        c_t1, c_t2 = st.columns([2, 1])
        with c_t1:
            st.markdown(t_t["p_task_1"])
            st.markdown(f"💡 **Application Target:** `{module_info['application']}`")
        with c_t2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button(label=t_t["p_download_btn"], data=df_sim.to_csv(index=False).encode('utf-8-sig'), file_name=f"FoodBiochem_Template_Module_{case_idx + 1}.csv", mime="text/csv", width="stretch")

    elif "Mechanism" in step_name or "机制建构" in step_name:
        st.markdown(f"<div class='pmsa-card card-mechanism'><h3>🌿 {t_t['m_title']}</h3></div>", unsafe_allow_html=True)
        c1, c2 = st.columns([1.2, 1])
        with c1:
            st.write(f"**{t_t['m_keyword_lbl']}**")
            st.code(", ".join(CASE_DATA_ENGINE[case_idx]["kws"]))
            u_map = st.text_area(t_t["m_lbl"], placeholder=t_t["m_holder"], height=180)
            submit_m = st.button(t_t["m_btn"], type="primary", width="stretch")
        with c2:
            if submit_m and u_map:
                save_learning_log(st.session_state.uid, t_t["cases"][case_idx], "Mechanism", "Submit_Map", u_map, 88.0, {"dim1":90, "dim2":85, "dim3":88})
                st.markdown("#### 🤖 AI Feedback Dashboard")
                st.success(t_t["m_success"])

    elif "Simulation" in step_name or "数据分析" in step_name:
        st.markdown(f"<div class='pmsa-card card-simulation'><h3>📊 {t_t['s_title']}</h3></div>", unsafe_allow_html=True)
        c1, c2 = st.columns([1, 1.5])
        with c1:
            upl = st.file_uploader(t_t["s_upload"], type=["csv", "xlsx"])
            df_use = df_sim.copy()
            st.markdown(f"##### {t_t['s_preview']}")
            st.dataframe(df_use, height=220, width="stretch")
        with c2:
            fig, ax = plt.subplots(figsize=(6, 3.5))
            x_col = CASE_DATA_ENGINE[case_idx]["x"]
            y_cols = [c for c in df_use.columns if c != x_col]
            for col in y_cols:
                ax.plot(df_use[x_col], df_use[col], marker="o", label=col)
            ax.set_xlabel(x_col)
            ax.set_title(f"Biochemical Kinetics Trend (Module {case_idx + 1})")
            ax.legend()
            ax.grid(True, linestyle="--", alpha=0.5)
            fig.tight_layout(); st.pyplot(fig); plt.close()

    elif "Application" in step_name or "方案应用" in step_name:
        st.markdown(f"<div class='pmsa-card card-application'><h3>🚀 {t_t['a_title']}</h3></div>", unsafe_allow_html=True)
        st.markdown(f"{t_t['a_task_lbl']} <code style='color:#2F855A; font-size:14px;'>{module_info['application']}</code>", unsafe_allow_html=True)
        st.write(t_t["a_intro"])
        
        with st.form("app_form_v2_0"):
            st.markdown(f"#### {t_t['a_part1']}")
            c1, c2 = st.columns([2, 1])
            with c1:
                t_in = st.text_input(t_t["a_p1_name"], placeholder=t_t["a_p1_name_holder"])
            with c2:
                tech_route = st.selectbox(t_t["a_p1_route"], t_t["a_routes"])
            
            st.markdown(f"#### {t_t['a_part2']}")
            st.markdown(f"**{t_t['a_t1_lbl']}**")
            st.caption(t_t["a_t1_cap"])
            formula_design = st.text_area("Input 1:", placeholder=t_t["a_t1_holder"], height=90, label_visibility="collapsed")
            
            st.markdown(f"**{t_t['a_t2_lbl']}**")
            st.caption(t_t["a_t2_cap"])
            mechanism_explain = st.text_area("Input 2:", placeholder=t_t["a_t2_holder"], height=90, label_visibility="collapsed")
            
            st.markdown(f"**{t_t['a_t3_lbl']}**")
            st.caption(t_t["a_t3_cap"])
            evaluation_plan = st.text_area("Input 3:", placeholder=t_t["a_t3_holder"], height=90, label_visibility="collapsed")
            
            st.markdown(f"#### {t_t['a_part3']}")
            upl_file = st.file_uploader(t_t["a_file_lbl"], type=["pdf", "docx", "xlsx", "png"])
            
            if st.form_submit_button(t_t["a_submit_btn"], type="primary", width="stretch"):
                if not t_in or not formula_design or not mechanism_explain or not evaluation_plan:
                    st.error("❌ 填写不完整 / Incomplete Form")
                else:
                    full_submission_text = (
                        f"【方案名称】: {t_in}\n"
                        f"【生物技术路径】: {tech_route}\n"
                        f"【任务1-生化工艺参数】: {formula_design}\n"
                        f"【任务2-生化与代谢机制】: {mechanism_explain}\n"
                        f"【任务3-生化指标验证】: {evaluation_plan}"
                    )
                    char_count = len(formula_design) + len(mechanism_explain) + len(evaluation_plan)
                    score = min(100.0, 72.0 + (char_count / 15.0))
                    
                    save_learning_log(st.session_state.uid, t_t["cases"][case_idx], "Application", "Submit_Scheme", full_submission_text, score, {"dim1": score*0.96, "dim2": score, "dim3": score*1.01})
                    st.success(t_t["a_success"])
                    st.balloons()

    elif "Analytics" in step_name or "智能评价" in step_name:
        st.markdown(f"<div class='pmsa-card' style='background-color: #FFFAF0; border-left: 6px solid #DD6B20;'><h3>📈 {t_t['an_title']}</h3></div>", unsafe_allow_html=True)
        df_logs = pd.DataFrame(st.session_state.cloud_logs_backup, columns=LOG_COLUMNS)
        if df_logs.empty:
            st.warning("⚠️ 目前云端看板暂无活跃行为留痕。当学生在前方点击提交后，这里会立刻激活数智化画像。")
        else:
            st.markdown(f"### 👤 您的历史填报痕迹 (ID: {st.session_state.uid})")
            st.dataframe(df_logs, width="stretch")