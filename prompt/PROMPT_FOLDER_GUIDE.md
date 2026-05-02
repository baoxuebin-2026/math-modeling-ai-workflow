# MMAgent 提示词文件夹完整介绍

## 📁 文件夹结构
```
MMAgent/prompt/
├── __init__.py                 # 空文件，Python 包初始化
├── template.py                 # 核心提示词模板（730 行）
├── constants.py                # 建模方法库常量
└── decompose_prompt.json       # 任务分解原则示例库
```

---

## 📄 文件详细介绍

### 1. **template.py** - 核心提示词模板库
**文件大小**: 730 行  
**作用**: 包含所有 MM-Agent 系统使用的提示词模板

#### 主要提示词分类：

**问题分析阶段**
- `PROBLEM_ANALYSIS_PROMPT` - 深度问题分析
- `PROBLEM_ANALYSIS_CRITIQUE_PROMPT` - 分析批评（5个维度评估）
- `PROBLEM_ANALYSIS_IMPROVEMENT_PROMPT` - 分析改进

**问题建模阶段**
- `PROBLEM_MODELING_PROMPT` - 创新数学建模
- `PROBLEM_MODELING_CRITIQUE_PROMPT` - 建模批评（5个维度）
- `PROBLEM_MODELING_IMPROVEMENT_PROMPT` - 建模改进

**任务分解阶段**
- `DECOMPOSE_PRINCIPLE_PROMPT` - 任务分解原则总结
- `TASK_DECOMPOSE_PROMPT` - 将解决方案分解为子任务
- `TASK_DESCRIPTION_PROMPT` - 细化子任务描述

**任务求解阶段**
- `TASK_ANALYSIS_PROMPT` - 子任务分析
- `TASK_FORMULAS_PROMPT` - 数学公式推导
- `TASK_FORMULAS_CRITIQUE_PROMPT` - 公式批评
- `TASK_FORMULAS_IMPROVEMENT_PROMPT` - 公式改进
- `TASK_MODELING_PROMPT` - 建模方法描述
- `TASK_MODELING_CRITIQUE_PROMPT` - 建模批评
- `TASK_MODELING_IMPROVEMENT_PROMPT` - 建模改进

**代码生成阶段**
- `TASK_CODING_PROMPT` - 自动代码生成
- `TASK_CODING_DEBUG_PROMPT` - 代码调试

**结果总结阶段**
- `TASK_RESULT_PROMPT` - 任务结果总结
- `TASK_RESULT_WITH_CODE_PROMPT` - 包含代码执行结果的总结
- `TASK_ANSWER_PROMPT` - 最终答案生成

**依赖分析阶段**
- `TASK_DEPENDENCY_ANALYSIS_PROMPT` - 任务依赖分析
- `TASK_DEPENDENCY_ANALYSIS_WITH_CODE_PROMPT` - 包含代码依赖的分析
- `DAG_CONSTRUCTION_PROMPT` - 构建任务依赖图（DAG）

**其他**
- `PROBLEM_PROMPT` - 问题格式化
- `DATA_DESCRIPTION_PROMPT` - 数据描述总结
- `METHOD_CRITIQUE_PROMPT` - 建模方法评估
- `CREATE_CHART_PROMPT` - 图表生成
- `PROBLEM_EXTRACT_PROMPT` - 问题信息提取

#### 提示词特点：
✅ 使用 `{placeholder}` 格式，易于集成  
✅ 支持 Actor-Critic 迭代框架  
✅ 强调深度思考和创新性  
✅ 要求纯文本输出（无 Markdown）  
✅ 包含详细的评估维度和标准  

---

### 2. **constants.py** - 建模方法库
**文件大小**: 约 500+ 行  
**作用**: 定义 `modeling_methods` 常量，包含所有支持的建模方法

#### 包含的方法分类：

**运筹学 (Operations Research)**
- 规划论 (Linear/Integer/Dynamic Programming)
- 图论 (最短路径、最小生成树、流问题等)
- 随机规划 (Markov、排队论、库存论等)

**优化方法 (Optimization Methods)**
- 确定性算法 (贪心、分治、动态规划、回溯)
- 启发式算法 (模拟退火、遗传算法、粒子群等)
- 迭代算法 (梯度下降、牛顿法、共轭梯度等)
- 约束优化 (线性规划求解器、KKT条件等)

**机器学习 (Machine Learning)**
- 分类 (KNN、SVM、决策树、随机森林、XGBoost等)
- 聚类 (K-Means、DBSCAN、层次聚类等)
- 回归 (线性、岭、Lasso、弹性网等)
- 降维 (PCA、t-SNE、自编码器等)
- 集成学习 (Bagging、Boosting、Stacking等)

**预测方法 (Prediction)**
- 离散预测 (Markov、HMM、灰色预测等)
- 连续预测 (ARIMA、GARCH、微分方程等)

**评估方法 (Evaluation)**
- 评分评估 (AHP、TOPSIS、DEA等)
- 统计评估 (相关性检验、拟合度检验等)

#### 使用方式：
```python
from MMAgent.prompt.constants import modeling_methods

# 在提示词中引用
prompt = TASK_FORMULAS_PROMPT.format(
    modeling_methods=modeling_methods,
    ...
)
```

---

### 3. **decompose_prompt.json** - 任务分解原则库
**文件大小**: 32 行（但内容很丰富）  
**作用**: 为不同类型的问题提供任务分解的参考原则

#### 结构：
```json
{
  "问题类型": {
    "子任务数": "分解原则描述"
  }
}
```

#### 包含的问题类型：
- **"A"** - 约束优化类问题（3、4、5个子任务）
- **"B"** - 评估决策类问题（3、4、5个子任务）
- **"C"** - 数据分析预测类问题（3、4、5个子任务）
- **"D"** - 系统建模分析类问题（3、4、5个子任务）
- **"E"** - 参数估计验证类问题（3、4、5个子任务）
- **"F"** - 策略规划实施类问题（3、4、5个子任务）

#### 每个分解原则包含：
- 第1个子任务：通常是基础模型构建
- 第2个子任务：模型优化或扩展
- 第3个子任务：敏感性分析或验证
- 第4个子任务（如有）：外部因素整合
- 第5个子任务（如有）：推广和应用

#### 使用方式：
```python
import json5

with open('decompose_prompt.json', 'r') as f:
    decompose_principles = json5.load(f)

# 获取特定问题类型的分解原则
principle = decompose_principles["C"]["4"]  # C类问题的4个子任务分解
```

---

### 4. **__init__.py** - 包初始化文件
**文件大小**: 空文件  
**作用**: 将 prompt 文件夹标记为 Python 包

---

## 🎯 使用流程

### 基本使用：
```python
from MMAgent.prompt.template import (
    PROBLEM_ANALYSIS_PROMPT,
    TASK_FORMULAS_PROMPT,
    TASK_CODING_PROMPT
)
from MMAgent.prompt.constants import modeling_methods

# 1. 问题分析
analysis_prompt = PROBLEM_ANALYSIS_PROMPT.format(
    modeling_problem="你的问题",
    user_prompt=""
)

# 2. 公式推导
formula_prompt = TASK_FORMULAS_PROMPT.format(
    modeling_methods=modeling_methods,
    data_summary="数据描述",
    task_description="任务描述",
    task_analysis="任务分析",
    prompt="额外提示"
)

# 3. 代码生成
code_prompt = TASK_CODING_PROMPT.format(
    data_file="数据文件路径",
    data_summary="数据描述",
    variable_description="变量描述",
    task_description="任务描述",
    task_analysis="任务分析",
    modeling_formulas="公式",
    modeling_process="建模过程",
    dependent_file_prompt="依赖文件",
    code_template="代码模板"
)
```

---

## 💡 关键特性

### 1. **Actor-Critic 框架**
每个阶段都遵循：
- **Actor** - 生成初始内容
- **Critic** - 批评和评估
- **Improvement** - 基于批评改进

### 2. **多维度评估**
批评提示词包含 5 个维度：
- 深度思考 (Depth of Thinking)
- 新颖性 (Novelty of Perspective)
- 结果评估 (Critical Evaluation)
- 严谨性 (Rigor and Precision)
- 上下文意识 (Contextual Awareness)

### 3. **格式规范**
- 要求纯文本输出（无 Markdown）
- 段落形式（避免列表）
- 使用 LaTeX 表示数学公式
- 清晰的上下文传递

### 4. **灵活扩展**
- 所有提示词都支持 `user_prompt` 参数
- 可以添加自定义指令
- 支持多轮迭代改进

---

## 📊 提示词统计

| 类别 | 数量 | 说明 |
|------|------|------|
| 问题分析 | 3 | 分析、批评、改进 |
| 问题建模 | 3 | 建模、批评、改进 |
| 任务分解 | 3 | 分解、描述、原则 |
| 任务求解 | 9 | 分析、公式、建模、代码等 |
| 结果总结 | 3 | 结果、答案、依赖分析 |
| 其他 | 5+ | 数据、方法、图表等 |
| **总计** | **30+** | 完整的建模工作流 |

---

## 🚀 最佳实践

1. **按顺序使用** - 遵循问题分析 → 建模 → 分解 → 求解的流程
2. **迭代改进** - 充分利用 Critic 和 Improvement 提示词
3. **上下文传递** - 每个阶段都继承前一阶段的输出
4. **灵活定制** - 根据需要添加 `user_prompt` 参数
5. **方法选择** - 从 `constants.py` 中选择合适的建模方法

---

## 📝 总结

MM-Agent 的提示词系统是一个完整、精心设计的框架，包含：
- ✅ 30+ 个精心设计的提示词
- ✅ 100+ 种建模方法库
- ✅ 6 种问题类型的分解原则
- ✅ Actor-Critic 迭代框架
- ✅ 完整的工作流支持

所有文件都可以直接拿来用，无需修改！
