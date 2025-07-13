# IoT0708 知识图谱嵌入训练指南

## 数据概览

当前 `data/iot0708/` 目录包含以下文件：

- **extensible_triples.txt** (42MB, 1,132,273 行): 知识图谱三元组数据
- **entity.vocab** (283KB, 13,285 行): 实体词汇表
- **relation.vocab** (204B, 11 行): 关系词汇表
- **extensible_knowledge_graph.json** (89MB): 完整的知识图谱JSON文件
- **middle_layers.json** (401B): 中间层特征配置

## 数据格式

### 三元组格式
```
banner_9ecadd5c indicates_device        router_asus_RT-AC66U_B1
banner_9ecadd5c contains_manufacturers  asus
asus    indicates_manufacturer  asus
banner_9ecadd5c contains_models rt-ac66u_b1
rt-ac66u_b1     indicates_model RT-AC66U_B1
```

### 关系类型 (10种)
1. `contains_device_types` - 包含设备类型
2. `contains_manufacturers` - 包含制造商
3. `contains_models` - 包含型号
4. `has_manufacturer` - 有制造商
5. `has_model` - 有型号
6. `indicates_device` - 指示设备
7. `indicates_device_type` - 指示设备类型
8. `indicates_manufacturer` - 指示制造商
9. `indicates_model` - 指示型号
10. `is_type` - 是类型

## 训练步骤

### 1. 环境准备
确保已安装所需依赖：
```bash
# 检查Python版本 (需要3.7)
python --version

# 检查TensorFlow版本 (需要1.15.0)
python -c "import tensorflow as tf; print(tf.__version__)"
```

### 2. 数据格式转换
由于原始数据使用空格分隔，需要转换为制表符分隔格式：

```python
# 运行数据转换脚本
python convert_iot0708_data.py
```

### 3. 开始训练

#### 方法1: 使用原始训练脚本
```bash
# 修改config.py中的路径
# 然后运行
python train.py
```

#### 方法2: 使用专门的IoT0708训练脚本
```bash
python train_iot0708.py
```

### 4. 训练配置建议

针对大数据集 (1.1M+ 三元组) 的优化配置：

```python
# 在config.py中设置
FLAGS.batch_size = 64          # 增大batch size
FLAGS.max_epoch = 50           # 减少epoch数量
FLAGS.learning_rate = 0.001    # 调整学习率
FLAGS.shuffle_buffer_size = 50000  # 增大shuffle buffer
FLAGS.entity_embedding_dim = 200   # 实体嵌入维度
FLAGS.relation_embedding_dim = 50  # 关系嵌入维度
```

## 数据转换脚本

创建 `convert_iot0708_data.py`:

```python
#!/usr/bin/env python
# coding: utf-8
"""
转换IoT0708数据格式用于TransE训练
"""
import os
import shutil

def convert_iot0708_data():
    """转换IoT0708数据格式"""
    print("=== 转换IoT0708数据格式 ===")
    
    # 源文件路径
    source_triples = "data/iot0708/extensible_triples.txt"
    source_entity_vocab = "data/iot0708/entity.vocab"
    source_relation_vocab = "data/iot0708/relation.vocab"
    
    # 目标目录
    target_dir = "data/iot0708_train"
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    # 复制词汇文件
    shutil.copy2(source_entity_vocab, os.path.join(target_dir, "entity.vocab"))
    shutil.copy2(source_relation_vocab, os.path.join(target_dir, "relation.vocab"))
    
    # 转换triples格式
    print("转换triples格式...")
    target_triples = os.path.join(target_dir, "train.txt")
    
    with open(source_triples, 'r', encoding='utf-8') as f_in, \
         open(target_triples, 'w', encoding='utf-8') as f_out:
        for line_num, line in enumerate(f_in):
            if line_num % 100000 == 0:
                print(f"处理第 {line_num} 行...")
            
            parts = line.strip().split()
            if len(parts) >= 3:
                head, relation, tail = parts[0], parts[1], ' '.join(parts[2:])
                f_out.write(f"{head}\t{relation}\t{tail}\n")
    
    print(f"转换完成！")
    print(f"- 训练数据: {target_triples}")
    print(f"- 实体词汇: {os.path.join(target_dir, 'entity.vocab')}")
    print(f"- 关系词汇: {os.path.join(target_dir, 'relation.vocab')}")

if __name__ == '__main__':
    convert_iot0708_data()
```

## 训练监控

训练过程中会生成以下文件：

- **模型文件**: `model/iot0708/model_epoch_*.ckpt`
- **训练日志**: `summary/iot0708/` (TensorBoard可视化)
- **训练数据**: `data/iot0708_train/`

## 性能预期

基于数据规模 (1.1M+ 三元组, 13K+ 实体, 10种关系):

- **训练时间**: 预计2-4小时 (取决于硬件)
- **内存使用**: 约2-4GB RAM
- **模型大小**: 约50-100MB

## 故障排除

### 常见问题

1. **内存不足**: 减少batch_size或shuffle_buffer_size
2. **训练缓慢**: 检查GPU是否可用，或减少embedding维度
3. **数据格式错误**: 确保triples文件使用制表符分隔

### 调试建议

```python
# 检查数据格式
with open("data/iot0708_train/train.txt", 'r') as f:
    for i, line in enumerate(f):
        if i < 5:
            print(line.strip().split('\t'))
        else:
            break
```

## 下一步

训练完成后，可以：

1. 使用训练好的模型进行实体链接
2. 进行知识图谱补全任务
3. 分析嵌入向量的语义相似性
4. 构建IoT设备识别系统 