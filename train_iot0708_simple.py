#!/usr/bin/env python
# coding: utf-8
"""
简化的IoT0708训练脚本
避免复杂的TensorFlow导入问题
"""
import os
import sys

def check_environment():
    """检查训练环境"""
    print("=== 检查训练环境 ===")
    
    # 检查Python版本
    python_version = sys.version_info
    print(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major != 3 or python_version.minor < 7:
        print("警告: 建议使用Python 3.7或更高版本")
    
    # 检查TensorFlow
    try:
        import tensorflow as tf
        print(f"TensorFlow版本: {tf.__version__}")
        
        # 检查GPU
        if tf.test.is_built_with_cuda():
            print("CUDA支持: 是")
            gpus = tf.config.experimental.list_physical_devices('GPU')
            if gpus:
                print(f"检测到GPU数量: {len(gpus)}")
                for i, gpu in enumerate(gpus):
                    print(f"  GPU {i}: {gpu.name}")
            else:
                print("未检测到可用的GPU")
        else:
            print("CUDA支持: 否")
            
    except ImportError:
        print("错误: 未安装TensorFlow")
        print("请运行: pip install tensorflow==1.15.0")
        return False
    
    return True

def check_data_files():
    """检查数据文件"""
    print("\n=== 检查数据文件 ===")
    
    # 检查训练数据
    train_data_files = [
        "data/iot0708_train/train.txt",
        "data/iot0708_train/entity.vocab", 
        "data/iot0708_train/relation.vocab"
    ]
    
    for file_path in train_data_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✓ {file_path} ({size:,} bytes)")
        else:
            print(f"✗ {file_path} (不存在)")
            return False
    
    # 检查样本数据
    sample_data_files = [
        "data/iot0708_sample/train.txt",
        "data/iot0708_sample/entity.vocab",
        "data/iot0708_sample/relation.vocab"
    ]
    
    print("\n样本数据:")
    for file_path in sample_data_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✓ {file_path} ({size:,} bytes)")
        else:
            print(f"✗ {file_path} (不存在)")
    
    return True

def show_training_commands():
    """显示训练命令"""
    print("\n=== 训练命令 ===")
    
    print("1. 使用样本数据进行快速测试:")
    print("   python train.py --data_file=data/iot0708_sample/train.txt \\")
    print("                   --entity_vocab=data/iot0708_sample/entity.vocab \\")
    print("                   --relation_vocab=data/iot0708_sample/relation.vocab \\")
    print("                   --batch_size=32 --max_epoch=10")
    
    print("\n2. 使用完整数据进行训练:")
    print("   python train.py --data_file=data/iot0708_train/train.txt \\")
    print("                   --entity_vocab=data/iot0708_train/entity.vocab \\")
    print("                   --relation_vocab=data/iot0708_train/relation.vocab \\")
    print("                   --batch_size=64 --max_epoch=50")
    
    print("\n3. 使用TransH模型:")
    print("   python train.py --data_file=data/iot0708_train/train.txt \\")
    print("                   --entity_vocab=data/iot0708_train/entity.vocab \\")
    print("                   --relation_vocab=data/iot0708_train/relation.vocab \\")
    print("                   --model_name=transH --batch_size=64 --max_epoch=50")

def show_data_statistics():
    """显示数据统计信息"""
    print("\n=== 数据统计信息 ===")
    
    # 统计训练数据行数
    train_file = "data/iot0708_train/train.txt"
    if os.path.exists(train_file):
        with open(train_file, 'r', encoding='utf-8') as f:
            train_lines = sum(1 for _ in f)
        print(f"训练三元组数量: {train_lines:,}")
    
    # 统计实体数量
    entity_file = "data/iot0708_train/entity.vocab"
    if os.path.exists(entity_file):
        with open(entity_file, 'r', encoding='utf-8') as f:
            entity_count = sum(1 for _ in f)
        print(f"实体数量: {entity_count:,}")
    
    # 统计关系数量
    relation_file = "data/iot0708_train/relation.vocab"
    if os.path.exists(relation_file):
        with open(relation_file, 'r', encoding='utf-8') as f:
            relation_count = sum(1 for _ in f)
        print(f"关系数量: {relation_count}")
    
    # 显示关系类型
    if os.path.exists(relation_file):
        print("\n关系类型:")
        with open(relation_file, 'r', encoding='utf-8') as f:
            for line in f:
                relation, idx = line.strip().split('\t')
                print(f"  {idx}: {relation}")

def create_training_config():
    """创建训练配置文件"""
    print("\n=== 创建训练配置 ===")
    
    config_content = '''# IoT0708 训练配置
# 复制以下内容到config.py中，或使用命令行参数

# 数据路径
data_file = 'data/iot0708_train/train.txt'
entity_vocab = 'data/iot0708_train/entity.vocab'
relation_vocab = 'data/iot0708_train/relation.vocab'

# 模型参数
model_name = 'transe'  # 可选: transe, transh, transr, distmult
entity_embedding_dim = 200
relation_embedding_dim = 50
margin = 1.0
score_func = 'l2'

# 训练参数
batch_size = 64
max_epoch = 50
learning_rate = 0.001
optimizer = 'Adam'
shuffle_buffer_size = 50000
stats_per_steps = 100

# 保存参数
save_per_epochs = 10
model_dir = 'model/iot0708'
'''
    
    config_file = "iot0708_training_config.txt"
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"配置文件已保存到: {config_file}")

def main():
    """主函数"""
    print("IoT0708 知识图谱嵌入训练准备")
    print("=" * 50)
    
    # 检查环境
    if not check_environment():
        return
    
    # 检查数据文件
    if not check_data_files():
        print("\n请先运行数据转换脚本:")
        print("python convert_iot0708_data.py")
        return
    
    # 显示数据统计
    show_data_statistics()
    
    # 创建训练配置
    create_training_config()
    
    # 显示训练命令
    show_training_commands()
    
    print("\n=== 准备完成 ===")
    print("现在可以开始训练了！")
    print("建议先使用样本数据进行快速测试，确认环境正常后再使用完整数据训练。")

if __name__ == '__main__':
    main() 