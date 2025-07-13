# 可扩展中层特征知识图谱构建系统

本系统支持从标签数据自动生成中层特征，并构建多层次知识图谱用于IoT设备识别。

## 📁 目录结构

```
build_knowledge_graph/
├── input/                          # 输入数据
│   ├── graph_entities.json         # 训练数据示例 (推荐格式)
│   ├── README_data_format.md       # 数据格式说明
│   ├── lable.txt                   # 设备标签数据 (设备类型,厂商,型号)
│   └── banner_and_lables/          # Banner和标签训练数据 (旧格式)
│       ├── are-input-axis.txt
│       ├── are-input-asus.txt
│       ├── are-input-netgear.txt
│       ├── are-input-sharp.txt
│       └── are-input-TP-LINK.txt
├── input_demo/                     # 标签处理演示
│   ├── process_labels.py           # 标签处理脚本
│   └── build_middle_feature_result/
│       ├── middle_features_config.json  # 生成的中层特征配置
│       └── processing_report.md         # 处理报告
├── extensible_kge_builder.py       # 核心知识图谱构建器
├── extensible_middle_layer.py      # 可扩展中层特征管理器
├── demo_extensible_middle_layer_usage.py  # 中层特征使用演示
├── EXTENSIBLE_MIDDLE_LAYER_GUIDE.md      # 中层特征使用指南
├── run_complete_demo.py            # 完整演示脚本
└── output/                         # 输出结果
    └── extensible_kge/             # 生成的知识图谱
        ├── extensible_triples.txt  # 三元组数据
        ├── entity.vocab            # 实体词汇表
        ├── relation.vocab          # 关系词汇表
        ├── middle_layers.json      # 中层特征信息
        └── extensible_knowledge_graph.json  # 完整知识图谱
```

## 🚀 快速开始

### 方法1: 一键运行完整演示
```bash
python run_complete_demo.py
```

这将自动执行：
1. 检查必要文件
2. 处理标签数据，生成中层特征配置
3. 构建可扩展知识图谱
4. 显示结果统计

### 方法2: 分步执行

#### 步骤1: 处理标签数据
```bash
cd input_demo
python process_labels.py
```

#### 步骤2: 构建知识图谱
```bash
python extensible_kge_builder.py
```

## 📊 中层特征层

系统自动生成以下5个中层特征层：

1. **设备类型层** - 提取camera、router、switch等设备类型
2. **厂商层** - 提取axis、hikvision、cisco等厂商信息
3. **型号层** - 提取具体设备型号
4. **设备厂商组合层** - 设备类型和厂商的组合
5. **厂商型号组合层** - 厂商和型号的组合

## 🔧 核心组件

### ExtensibleKGEBuilder
- 从middle_features_config.json加载中层特征配置
- 支持多层次实体构建
- 自动生成增强三元组
- 支持真实数据训练

### ExtensibleMiddleLayer
- 可扩展中层特征管理
- 支持动态添加、更新、删除特征层
- 配置持久化
- 知识库管理

## 📈 数据统计

基于当前标签数据：
- **设备类型**: 41种
- **厂商**: 1,149个
- **型号**: 16,295个
- **设备厂商组合**: 2,188个
- **厂商型号组合**: 14,978个

## 🎯 使用场景

1. **IoT设备识别**: 从HTTP banner识别设备类型、厂商、型号
2. **知识图谱构建**: 构建多层次设备知识图谱
3. **设备关系挖掘**: 发现设备间的关联关系
4. **安全分析**: 基于设备特征进行安全风险评估

## 📝 输入数据格式

### 1. 推荐格式 - JSON文件 (graph_entities.json)
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

### 2. 标签数据 (lable.txt)
```
设备类型,厂商,型号
camera,axis,m1054
router,cisco,isr4321
printer,hp,laserjet
```

### 3. 旧格式 - Banner训练数据
```
HTTP/1.1 401 Unauthorized\nServer: Hikvision-Webs\tcamera_hikvision_ipc
HTTP/1.1 200 OK\nServer: Cisco-IOS\trouter_cisco_isr
```

### 数据字段说明

#### 必需字段
- `banner`: 设备的banner信息 (字符串)
- `true_vendor`: 设备厂商 (字符串)
- `true_product`: 设备产品型号 (字符串)

#### 可选字段
- `id`: 设备唯一标识符 (字符串)
- `port`: 端口号 (整数)
- `protocol`: 协议类型 (字符串)
- `device_type`: 设备类型 (字符串)
- `model`: 设备型号 (字符串)
- `version`: 设备版本 (字符串)

详细格式说明请参考：`input/README_data_format.md`

## 🔄 工作流程

1. **数据预处理**: 清理和验证标签数据
2. **特征提取**: 从标签中提取设备类型、厂商、型号
3. **中层特征生成**: 创建多层次特征配置
4. **知识图谱构建**: 使用真实数据构建三元组
5. **关系映射**: 建立特征到设备的映射关系

## 📤 输出文件

### 知识图谱文件
- `extensible_triples.txt`: 标准三元组格式，可直接用于TransE训练
- `entity.vocab`: 实体词汇表
- `relation.vocab`: 关系词汇表
- `middle_layers.json`: 中层特征配置信息
- `extensible_knowledge_graph.json`: 完整知识图谱数据

### 三元组示例
```
banner_1234    indicates_device    camera_hikvision_ipc
banner_1234    contains_manufacturers    hikvision
hikvision      indicates_manufacturer    hikvision
camera_hikvision_ipc    has_manufacturer    hikvision
camera_hikvision_ipc    is_type    camera
```

## 🎯 下一步

1. **模型训练**: 使用生成的三元组训练TransE等嵌入模型
2. **设备识别**: 对新banner进行设备类型预测
3. **关系推理**: 基于知识图谱进行设备关系推理
4. **安全分析**: 结合设备特征进行安全风险评估

## ⚠️ 注意事项

- 确保输入数据编码为UTF-8
- 处理大量数据时注意内存使用
- 建议定期更新标签数据和知识库
- 可以根据需要调整特征提取规则 