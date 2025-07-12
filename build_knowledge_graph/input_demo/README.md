# 标签数据处理 - 中层特征生成

本目录包含用于处理标签数据并生成中层特征的脚本。

## 文件说明

### 核心脚本
- `process_labels_to_middle_features.py` - 主要处理脚本，从标签文件生成中层特征配置
- `demo_middle_features.py` - 演示脚本，展示如何使用生成的中层特征

### 输出文件
- `build_middle_feature_result/middle_features_config.json` - 生成的中层特征配置文件
- `build_middle_feature_result/processing_report.md` - 处理报告

## 快速开始

### 1. 处理标签数据
```bash
# 运行标签处理脚本
python process_labels_to_middle_features.py
```

这将：
- 读取 `../input/lable.txt` 文件
- 提取设备类型、厂商、型号信息
- 生成中层特征配置
- 保存到 `build_middle_feature_result/middle_features_config.json`

### 2. 查看演示
```bash
# 运行演示脚本
python demo_middle_features.py
```

这将：
- 加载生成的配置文件
- 显示配置摘要
- 演示banner分析
- 生成示例三元组

## 标签文件格式

标签文件 `lable.txt` 采用CSV格式：
```
设备类型,厂商,型号
camera,axis,m1054
router,cisco,isr4321
printer,hp,laserjet
```

### 字段说明
- **设备类型**: 设备的主要类型（camera, router, switch等）
- **厂商**: 设备制造商（axis, cisco, hikvision等）
- **型号**: 具体设备型号（m1054, isr4321等）

## 生成的中层特征

### 1. 设备类型层
- **功能**: 提取设备类型信息
- **关键词**: 从标签中提取的所有设备类型
- **关系**: indicates_device_type, is_type

### 2. 厂商层
- **功能**: 提取厂商信息
- **关键词**: 从标签中提取的所有厂商
- **关系**: indicates_manufacturer, has_manufacturer

### 3. 型号层
- **功能**: 提取型号信息
- **关键词**: 从标签中提取的所有型号
- **关系**: indicates_model, has_model

### 4. 设备厂商组合层
- **功能**: 设备类型和厂商的组合
- **关键词**: 格式为 "设备类型_厂商" 的组合
- **关系**: typical_for, has_manufacturer

### 5. 厂商型号组合层
- **功能**: 厂商和型号的组合
- **关键词**: 格式为 "厂商_型号" 的组合
- **关系**: produces, has_model

## 配置结构

生成的配置文件包含以下结构：

```json
{
  "middle_features": {
    "device_types": {
      "name": "设备类型层",
      "description": "从标签中提取的设备类型信息",
      "enabled": true,
      "priority": 1,
      "extraction_rules": {
        "keywords": ["camera", "router", "switch", ...],
        "regex_patterns": []
      },
      "relations": {
        "indicates_device_type": "指示设备类型",
        "is_type": "是类型"
      },
      "knowledge_base": {
        "camera": "摄像头设备",
        "router": "路由器设备",
        ...
      }
    }
  },
  "statistics": {
    "total_lines": 17890,
    "valid_lines": 15000,
    ...
  },
  "summary": {
    "total_device_types": 50,
    "total_manufacturers": 200,
    "total_models": 1000,
    ...
  }
}
```

## 使用示例

### Banner分析示例
```python
# 示例banner
banner = "Server: Hikvision-Webs/1.0"

# 提取特征
features = extract_features_from_banner(banner)
# 结果: {'manufacturers': ['hikvision'], 'device_types': ['camera']}
```

### 三元组生成示例
```python
# 生成的三元组
triples = [
    ("banner_1234", "indicates_device", "camera_hikvision_ds2cd2342"),
    ("banner_1234", "contains_feature", "hikvision"),
    ("hikvision", "indicates_manufacturer", "hikvision"),
    ("hikvision", "indicates_device_type", "camera")
]
```

## 集成到可扩展中层特征系统

生成的配置文件可以直接用于可扩展中层特征系统：

```python
# 加载配置
with open('build_middle_feature_result/middle_features_config.json', 'r') as f:
    config = json.load(f)

# 使用配置
middle_features = config['middle_features']
for feature_name, feature_config in middle_features.items():
    if feature_config['enabled']:
        # 处理该中层特征
        keywords = feature_config['extraction_rules']['keywords']
        relations = feature_config['relations']
        # ...
```

## 下一步

1. **添加banner和标签的关系映射**
   - 创建banner特征提取规则
   - 建立banner到中层特征的映射关系

2. **扩展知识库**
   - 添加更多设备类型描述
   - 补充厂商详细信息
   - 增加型号规格说明

3. **优化提取规则**
   - 添加正则表达式模式
   - 改进关键词匹配算法
   - 增加模糊匹配功能

4. **集成到KGE系统**
   - 将中层特征集成到知识图谱构建器
   - 训练TransE等嵌入模型
   - 进行设备识别推理

## 注意事项

- 确保标签文件编码为UTF-8
- 处理大量数据时注意内存使用
- 可以根据需要调整关键词过滤规则
- 建议定期更新知识库信息 