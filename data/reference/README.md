# Sun Protection Behaviours — Data Reference

## 数据来源
澳大利亚统计局（ABS）— 防晒行为调查，2023年11月至2024年2月，澳大利亚15岁及以上人口。

---

## CSV 结构：7列，共 9,272 行

| 列名 | 类型 | 说明 |
|---|---|---|
| `table` | string | 来源表编号，共10张：`Table 1a/1b` … `Table 5a/5b`。`a` 表为绝对量，`b` 表为比例/误差 |
| `section` | string | 数值类型，每张表内部分两段：`Estimate ('000)` 或 `Relative Standard Error (%)` / `Proportion of persons (%)` 或 `95% Margin of Error (%)` |
| `group_label` | string | 分组维度名称，例如：`Age group`、`State or territory of usual residence`、`Remoteness area`、`Country of birth`、`Highest educational attainment`、`SEIFA`（社会经济指数） |
| `characteristic` | string | 分组维度下的具体取值，例如：`15–24 years`、`Victoria`、`Born overseas` |
| `gender` | string | 性别维度：`Males` / `Females` / `Persons`（男+女合计）/ `All`（Table 4/5 无性别细分时） |
| `metric` | string | 具体指标名称（见下方各表说明） |
| `value` | float | 数值。单位取决于 `section`：千人 or 百分比 |

---

## 五组表的含义

### Table 1（1a + 1b）— 防晒霜使用
过去一个月内，是否在大多数日子使用 SPF30+ 防晒霜。

`metric` 取值：`Used SPF30 or higher sunscreen on most days` / `Did not use...` / `Total`

### Table 2（2a + 2b）— 上周晒伤情况
过去一周内是否经历过晒伤。

`metric` 取值：`Experienced sunburn` / `Did not experience sunburn` / `Total`

### Table 3（3a + 3b）— 过去12个月日晒行为
过去12个月内是否主动尝试晒黑。

`metric` 取值：`Attempted to get a suntan` / `Did not attempt to get a suntan` / `Total`

### Table 4（4a + 4b）— 上周户外时间
上周在紫外线高峰时段（peak UV time）在户外超过15分钟的天数。

`metric` 格式：`Days last week outdoors... | Monday / Tuesday / ... / Total / Mean / Median`

### Table 5（5a + 5b）— 防晒措施使用
上周在户外时使用了哪些防晒措施（可多选）。

`metric` 格式：`Type of sun protection measure... | 防晒霜 / 帽子 / 遮阴 / 防晒衣 / 墨镜 / 无措施 / Total / 三种以上`

---

## 如何读取一个值（示例）

> **问题**：15–24 岁男性中，上周经历晒伤的比例是多少？
```
table          = "Table 2b"
section        = "Proportion of persons (%)"
group_label    = "Age group"
characteristic = "15–24 years"
gender         = "Males"
metric         = "Experienced sunburn"
→ value        = 17.4   （即 17.4%）
```
