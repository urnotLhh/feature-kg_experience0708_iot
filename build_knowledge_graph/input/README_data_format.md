# 知识图谱构建训练数据格式说明

## 文件格式要求

知识图谱构建器支持以下两种数据格式：

### 1. JSON格式 (推荐)
- 文件扩展名：`.json`
- 数据格式：JSON数组，每个元素为一个设备记录
- 示例文件：`graph_entities.json`

### 2. 文本格式 (兼容旧格式)
- 文件扩展名：`.txt`
- 数据格式：每行一个JSON对象
- 示例文件：`banner_and_lables/are-input-*.txt`

## 数据字段说明

每个设备记录应包含以下字段：

### 必需字段
- `banner`: 设备的banner信息 (字符串)
- `true_vendor`: 设备厂商 (字符串)
- `true_product`: 设备产品型号 (字符串)

### 可选字段
- `id`: 设备唯一标识符 (字符串，如不提供将自动生成)
- `port`: 端口号 (整数)
- `protocol`: 协议类型 (字符串，如 "ftp", "http", "ssh")
- `device_type`: 设备类型 (字符串，如 "printer", "camera", "router")
- `model`: 设备型号 (字符串)
- `version`: 设备版本 (字符串)

## 数据质量要求

### 1. Banner信息
- 必须包含设备的特征信息
- 建议包含厂商名称、产品型号、版本号等
- 长度建议在10-1000字符之间

### 2. 标签信息
- `true_vendor`: 必须准确，用于构建厂商实体
- `true_product`: 必须准确，用于构建产品实体
- 建议使用小写字母，避免特殊字符

### 3. 数据完整性
- 每个记录至少包含banner和标签信息
- 缺失的字段可以使用空字符串或"unknown"表示
- 建议提供尽可能完整的设备信息

## 示例数据

```json
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
```

## 数据来源建议

### 1. 网络扫描数据
- 使用nmap、masscan等工具扫描IoT设备
- 收集设备的banner信息
- 通过人工标注或自动识别获取标签

### 2. 厂商文档
- 从厂商官网获取设备型号信息
- 结合banner特征进行标注
- 确保标签的准确性

### 3. 公开数据集
- 使用公开的IoT设备数据集
- 如Shodan、Censys等平台的数据
- 注意数据质量和版权问题

## 数据预处理建议

### 1. 数据清洗
- 去除重复记录
- 过滤无效的banner信息
- 统一标签格式

### 2. 数据增强
- 添加设备类型信息
- 提取版本号信息
- 补充缺失字段

### 3. 数据验证
- 检查标签一致性
- 验证banner格式
- 确保数据完整性

## 文件组织建议

```
input/
├── graph_entities.json          # 示例数据文件
├── README_data_format.md        # 本说明文件
├── lable.txt                    # 标签映射文件
└── banner_and_lables/           # 原始数据目录
    ├── are-input-sharp.txt
    ├── are-input-axis.txt
    └── ...
```

## 注意事项

1. **数据隐私**: 确保不包含敏感信息
2. **版权问题**: 使用合法的数据来源
3. **数据质量**: 优先使用高质量、标注准确的数据
4. **数据量**: 建议至少包含1000条记录以获得良好的训练效果
5. **数据多样性**: 包含不同厂商、不同类型的设备 