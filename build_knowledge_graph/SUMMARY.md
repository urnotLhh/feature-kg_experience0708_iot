# 知识图谱构建系统总结

## 🎯 项目概述

本项目为IoT设备识别构建了可扩展的知识图谱系统，支持从设备banner信息自动提取特征，构建多层次知识图谱，为TransE等知识图谱嵌入模型提供训练数据。

## ✅ 已完成功能

### 1. 数据格式标准化
- ✅ 创建了标准化的JSON格式训练数据 (`graph_entities.json`)
- ✅ 支持多种数据格式：JSON、文本、CSV
- ✅ 详细的数据格式说明文档 (`README_data_format.md`)

### 2. 可扩展中层特征系统
- ✅ 自动从标签数据生成中层特征配置
- ✅ 支持5个中层特征层：设备类型、厂商、型号、设备厂商组合、厂商型号组合
- ✅ 可扩展的特征提取规则
- ✅ 配置持久化和动态更新

### 3. 知识图谱构建器
- ✅ 多层次实体构建（底层banner特征 → 中层特征 → 高层设备实体）
- ✅ 自动生成增强三元组
- ✅ 支持真实数据训练
- ✅ 标准输出格式（TransE兼容）

### 4. 完整演示系统
- ✅ 一键运行完整流程
- ✅ 自动文件检查和错误处理
- ✅ 详细的进度显示和统计信息

## 📊 数据要求说明

### 训练数据格式

#### 推荐格式 - JSON文件 (`graph_entities.json`)
```json
[
  {
    "banner": "220 SHARP MX-M264N Ver 01.05.00.0s.12 FTP server.\n",
    "id": "device_001",
    "port": 21,
    "protocol": "ftp",
    "true_vendor": "sharp",
    "true_product": "MX-M264N",
    "device_type": "printer",
    "model": "MX-M264N",
    "version": "01.05.00.0s.12"
  }
]
```

#### 必需字段
- `banner`: 设备的banner信息（字符串）
- `true_vendor`: 设备厂商（字符串）
- `true_product`: 设备产品型号（字符串）

#### 可选字段
- `id`: 设备唯一标识符
- `port`: 端口号
- `protocol`: 协议类型
- `device_type`: 设备类型
- `model`: 设备型号
- `version`: 设备版本

### 数据质量要求

1. **Banner信息**
   - 必须包含设备的特征信息
   - 建议包含厂商名称、产品型号、版本号等
   - 长度建议在10-1000字符之间

2. **标签信息**
   - `true_vendor`: 必须准确，用于构建厂商实体
   - `true_product`: 必须准确，用于构建产品实体
   - 建议使用小写字母，避免特殊字符

3. **数据完整性**
   - 每个记录至少包含banner和标签信息
   - 缺失的字段可以使用空字符串或"unknown"表示
   - 建议提供尽可能完整的设备信息

## 🏗️ 系统架构

### 核心组件

1. **ExtensibleKGEBuilder** - 知识图谱构建器
   - 加载中层特征配置
   - 处理训练数据
   - 构建多层次实体
   - 生成三元组

2. **ExtensibleMiddleLayer** - 中层特征管理器
   - 特征层配置管理
   - 动态特征提取
   - 知识库管理

3. **LabelProcessor** - 标签处理器
   - 标签数据清洗
   - 中层特征生成
   - 配置文件输出

### 工作流程

```
训练数据 → 特征提取 → 中层特征 → 知识图谱 → 三元组输出
   ↓           ↓          ↓         ↓         ↓
JSON/文本    Banner    设备类型    实体关系    TransE训练
格式数据     解析      厂商型号    三元组      数据
```

## 📈 当前成果

### 示例数据统计
- **训练样本**: 10条SHARP设备数据
- **生成实体**: 36个
- **生成关系**: 8种
- **生成三元组**: 134个

### 输出文件
- `extensible_triples.txt`: 标准三元组格式
- `entity.vocab`: 实体词汇表
- `relation.vocab`: 关系词汇表
- `extensible_knowledge_graph.json`: 完整知识图谱

### 三元组示例
```
banner_b2b99f48    indicates_device    printer_sharp_MX-M264N
banner_b2b99f48    contains_manufacturers    sharp
sharp    indicates_manufacturer    sharp
printer_sharp_MX-M264N    has_manufacturer    sharp
printer_sharp_MX-M264N    is_type    printer
printer_sharp_MX-M264N    has_model    MX-M264N
```

## 🚀 使用方法

### 快速开始
```bash
# 1. 准备训练数据
# 将设备数据保存为 input/graph_entities.json

# 2. 运行完整演示
python run_complete_demo.py

# 3. 或分步执行
python extensible_kge_builder.py
```

### 自定义数据
1. 按照格式要求准备训练数据
2. 放置在 `input/` 目录下
3. 运行构建器
4. 检查 `output/extensible_kge/` 目录下的结果

## 🎯 应用场景

1. **IoT设备识别**
   - 从HTTP banner识别设备类型、厂商、型号
   - 基于知识图谱的设备特征匹配

2. **设备关系挖掘**
   - 发现设备间的关联关系
   - 厂商-产品关系分析

3. **安全分析**
   - 基于设备特征进行安全风险评估
   - 设备漏洞关联分析

4. **知识图谱嵌入**
   - 为TransE、TransH、TransR等模型提供训练数据
   - 支持设备相似性计算

## 🔄 扩展性

### 添加新的特征层
1. 在 `middle_features_config.json` 中添加新层配置
2. 定义提取规则和关键词
3. 重新运行构建器

### 支持新的数据格式
1. 在 `load_training_data_from_files` 函数中添加解析逻辑
2. 确保输出格式符合要求

### 自定义关系类型
1. 在构建器中添加新的关系映射
2. 更新三元组生成逻辑

## 📝 注意事项

1. **数据隐私**: 确保不包含敏感信息
2. **版权问题**: 使用合法的数据来源
3. **数据质量**: 优先使用高质量、标注准确的数据
4. **数据量**: 建议至少包含1000条记录以获得良好的训练效果
5. **数据多样性**: 包含不同厂商、不同类型的设备

## 🎯 下一步计划

1. **模型训练**: 使用生成的三元组训练TransE等嵌入模型
2. **设备识别**: 对新banner进行设备类型预测
3. **关系推理**: 基于知识图谱进行设备关系推理
4. **安全分析**: 结合设备特征进行安全风险评估
5. **性能优化**: 优化大规模数据处理性能
6. **可视化**: 添加知识图谱可视化功能 