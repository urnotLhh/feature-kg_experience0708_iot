
# 标签数据处理报告

## 处理统计
- 总行数: 17889
- 有效行数: 17889
- 设备类型数量: 41
- 厂商数量: 1149
- 型号数量: 16295
- 设备厂商组合: 2188
- 厂商型号组合: 14978

## 生成的中层特征
1. **设备类型层** - 41 个设备类型
2. **厂商层** - 1149 个厂商
3. **型号层** - 16295 个型号
4. **设备厂商组合层** - 2188 个组合
5. **厂商型号组合层** - 14978 个组合

## 主要设备类型 (前10个)
['pda', 'pbx', 'media device', 'industrial control system', 'phone', 'bridge', 'camera', 'nvr', 'remote management', 'surveillance']

## 主要厂商 (前10个)
['pricom', 'aspect', 'belgacom', 'loxone', 'engenius', 'z-way', 'readynet', 'trend', 'vxworks', 'netopia']

## 使用说明
生成的配置文件可以直接用于可扩展中层特征系统，支持：
- 从HTTP banner中提取设备类型、厂商、型号信息
- 构建多层次知识图谱
- 进行IoT设备识别和推理
