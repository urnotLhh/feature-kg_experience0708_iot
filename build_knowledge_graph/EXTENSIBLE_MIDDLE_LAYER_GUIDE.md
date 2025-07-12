# 可扩展中层特征系统使用指南

## 概述

可扩展中层特征系统是一个动态的知识图谱构建工具，允许您：
- 动态添加、更新、删除中层特征
- 配置灵活的特征提取规则
- 管理知识库和关系映射
- 重构知识图谱以适应新的特征层

## 快速开始

### 1. 基本使用

```python
from extensible_middle_layer import ExtensibleMiddleLayer

# 初始化中层特征管理器
manager = ExtensibleMiddleLayer("my_config.json")

# 查看当前中层特征
layers = manager.list_middle_layers()
for layer in layers:
    print(f"- {layer['id']}: {layer['name']}")
```

### 2. 添加新的中层特征

```python
# 定义新的中层特征配置
new_layer_config = {
    'name': '安全特征',
    'description': '设备安全相关特征',
    'type': 'text',
    'priority': 1,
    'enabled': True,
    'examples': ['SSL', 'TLS', 'Basic Auth'],
    'extraction_rules': {
        'patterns': [
            r'WWW-Authenticate:\s*(Basic|Digest)',
            r'SSL|TLS',
            r'Certificate'
        ],
        'keywords': ['SSL', 'TLS', 'Basic', 'Digest', 'Certificate'],
        'extraction_method': 'regex_and_keyword'
    },
    'relation_mappings': {
        'to_security_level': 'indicates_security_level',
        'to_authentication': 'indicates_authentication_type'
    }
}

# 添加中层特征
success = manager.add_middle_layer('security_features', new_layer_config)
print(f"添加安全特征层: {'成功' if success else '失败'}")
```

### 3. 添加知识库条目

```python
# 为安全特征层添加知识库条目
manager.add_knowledge_base_entry('security_features', 'SSL', {
    'security_level': 'high',
    'authentication_type': 'certificate_based'
})

manager.add_knowledge_base_entry('security_features', 'Basic Auth', {
    'security_level': 'low',
    'authentication_type': 'password_based'
})
```

### 4. 提取特征

```python
# 测试banner文本
banner_text = """
HTTP/1.1 401 Unauthorized
Server: Hikvision-Webs
WWW-Authenticate: Basic realm="Hikvision Camera"
Content-Type: text/html
"""

# 提取中层特征
features = manager.extract_middle_layer_features(banner_text)
for layer_id, layer_features in features.items():
    print(f"{layer_id}: {layer_features}")
```

## 配置详解

### 中层特征配置结构

```json
{
    "name": "特征名称",
    "description": "特征描述",
    "type": "text|numeric|datetime",
    "priority": 1,
    "enabled": true,
    "examples": ["示例1", "示例2"],
    "extraction_rules": {
        "patterns": ["正则表达式1", "正则表达式2"],
        "keywords": ["关键词1", "关键词2"],
        "extraction_method": "regex_and_keyword|regex_only|keyword_only|custom"
    },
    "relation_mappings": {
        "to_target_type": "relation_name"
    }
}
```

### 提取规则配置

#### 正则表达式模式
```python
patterns = [
    r'Server:\s*([^\r\n]+)',           # 提取Server头
    r'X-Powered-By:\s*([^\r\n]+)',     # 提取X-Powered-By头
    r'WWW-Authenticate:\s*([^\r\n]+)'  # 提取WWW-Authenticate头
]
```

#### 关键词匹配
```python
keywords = [
    'Hikvision', 'Cisco', 'Axis', 'Dahua',
    'HTTP', 'HTTPS', 'SSL', 'TLS'
]
```

### 关系映射配置

```python
relation_mappings = {
    'to_manufacturer': 'indicates_manufacturer',    # 指示厂商
    'to_device_type': 'indicates_device_type',     # 指示设备类型
    'to_security': 'indicates_security_level',     # 指示安全级别
    'to_protocol': 'indicates_protocol'            # 指示协议
}
```

## 高级功能

### 1. 更新中层特征

```python
# 更新特征配置
updates = {
    'priority': 2,  # 提高优先级
    'examples': ['SSL', 'TLS', 'Basic Auth', 'Digest Auth'],
    'extraction_rules': {
        'patterns': [
            r'WWW-Authenticate:\s*(Basic|Digest)',
            r'SSL|TLS',
            r'Certificate',
            r'Security:\s*([^\r\n]+)'  # 添加新模式
        ],
        'keywords': ['SSL', 'TLS', 'Basic', 'Digest', 'Certificate', 'Security'],
        'extraction_method': 'regex_and_keyword'
    }
}

success = manager.update_middle_layer('security_features', updates)
```

### 2. 启用/禁用中层特征

```python
# 禁用特征层
manager.disable_middle_layer('security_features')

# 重新启用
manager.enable_middle_layer('security_features')
```

### 3. 删除中层特征

```python
# 删除特征层
success = manager.remove_middle_layer('security_features')
```

### 4. 配置导入导出

```python
# 导出配置
manager.export_config('exported_config.json')

# 导入配置
manager.import_config('imported_config.json')
```

## 知识图谱重构

### 1. 使用重构器

```python
from extensible_middle_layer import KnowledgeGraphRebuilder

# 创建重构器
rebuilder = KnowledgeGraphRebuilder(manager)

# 原始三元组
original_triples = [
    ("banner_001", "indicates_device", "camera_Hikvision"),
    ("banner_002", "indicates_device", "router_Cisco")
]

# 重构知识图谱
report = rebuilder.rebuild_knowledge_graph(original_triples)

# 显示重构结果
print(f"原始三元组数量: {report['original_triples_count']}")
print(f"重构后三元组数量: {report['rebuilt_triples_count']}")
print(f"新增实体数量: {report['new_entities_count']}")
print(f"新增关系数量: {report['new_relations_count']}")
```

### 2. 保存重构结果

```python
# 保存重构后的知识图谱
rebuilder.save_rebuilt_knowledge_graph('output/rebuild_result', report)
```

## 集成到KGE构建器

### 1. 使用可扩展KGE构建器

```python
from enhanced_kge_builder_with_extensible_layers import EnhancedKGEBuilderWithExtensibleLayers

# 初始化可扩展KGE构建器
builder = EnhancedKGEBuilderWithExtensibleLayers("kge_config.json")

# 添加自定义中层特征
protocol_config = {
    'name': '协议特征',
    'description': '网络协议相关特征',
    'type': 'text',
    'priority': 1,
    'enabled': True,
    'examples': ['HTTP/1.1', 'HTTPS', 'FTP', 'SSH'],
    'extraction_rules': {
        'patterns': [r'HTTP/\d+\.\d+', r'HTTPS', r'FTP', r'SSH'],
        'keywords': ['HTTP', 'HTTPS', 'FTP', 'SSH'],
        'extraction_method': 'regex_and_keyword'
    },
    'relation_mappings': {
        'to_device_type': 'typical_protocol_for',
        'to_security': 'indicates_protocol_security'
    }
}

builder.add_custom_middle_layer(protocol_config)

# 构建知识图谱
training_data = [
    ("HTTP/1.1 200 OK\nServer: Hikvision-Webs", "camera_Hikvision"),
    ("SSH-2.0-OpenSSH_7.4\nServer: Cisco-IOS", "router_Cisco")
]

knowledge_graph = builder.build_extensible_knowledge_graph(training_data)
```

### 2. 动态添加新特征层

```python
# 运行时添加新的端口特征层
port_config = {
    'name': '端口特征',
    'description': '网络端口相关特征',
    'type': 'numeric',
    'priority': 2,
    'enabled': True,
    'examples': ['80', '443', '22', '21'],
    'extraction_rules': {
        'patterns': [r'port\s*(\d+)', r':(\d+)/'],
        'keywords': ['80', '443', '22', '21'],
        'extraction_method': 'regex_and_keyword'
    },
    'relation_mappings': {
        'to_service': 'indicates_service',
        'to_security': 'indicates_port_security'
    }
}

builder.add_custom_middle_layer(port_config)

# 重新构建知识图谱（包含新特征层）
knowledge_graph_v2 = builder.build_extensible_knowledge_graph(training_data)
```

## 最佳实践

### 1. 特征层设计原则

- **单一职责**: 每个特征层应该专注于一个特定的特征类型
- **优先级设置**: 根据重要性设置合理的优先级
- **命名规范**: 使用清晰、一致的命名规范
- **文档化**: 为每个特征层提供详细的描述和示例

### 2. 提取规则设计

- **正则表达式**: 使用精确的正则表达式模式
- **关键词选择**: 选择具有代表性的关键词
- **测试验证**: 对提取规则进行充分测试
- **性能考虑**: 避免过于复杂的正则表达式

### 3. 关系映射设计

- **语义清晰**: 关系名称应该语义清晰
- **一致性**: 保持关系命名的一致性
- **可扩展性**: 设计可扩展的关系映射结构

### 4. 知识库管理

- **结构化**: 使用结构化的知识库条目
- **完整性**: 确保知识库条目的完整性
- **更新维护**: 定期更新和维护知识库

## 故障排除

### 常见问题

1. **特征提取失败**
   - 检查正则表达式语法
   - 验证关键词是否正确
   - 确认banner文本格式

2. **配置加载失败**
   - 检查JSON文件格式
   - 验证必需字段是否存在
   - 确认文件编码格式

3. **知识图谱重构失败**
   - 检查原始三元组格式
   - 验证中层特征配置
   - 确认输出目录权限

### 调试技巧

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 测试特征提取
features = manager.extract_middle_layer_features(banner_text)
print("提取的特征:", features)

# 检查配置
print("当前配置:", manager.middle_layers)
print("提取规则:", manager.extraction_rules)
print("关系映射:", manager.relation_mappings)
```

## 总结

可扩展中层特征系统提供了强大的动态知识图谱构建能力，通过合理配置和使用，可以显著提升IoT设备识别的准确性和灵活性。关键是要根据具体应用场景设计合适的中层特征，并建立完善的知识库和关系映射。 