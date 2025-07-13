#!/usr/bin/env python
# coding: utf-8
"""
IoT0708 Knowledge Graph Embedding Training Script
专门用于训练iot0708数据的脚本 - 改进版本，包含验证集和早停机制
"""
import os
import sys
import shutil
import random
import tensorflow as tf
from config import FLAGS
from kge import *
from dataset import get_iterator
from utils import print_args, load_vocab


def split_data_with_validation(source_file, train_ratio=0.8, random_seed=42):
    """将数据分割为训练集和验证集"""
    print("=== 分割数据为训练集和验证集 ===")
    
    # 读取所有三元组
    with open(source_file, 'r', encoding='utf-8') as f:
        triples = f.readlines()
    
    print(f"总三元组数量: {len(triples)}")
    
    # 设置随机种子确保可重复性
    random.seed(random_seed)
    random.shuffle(triples)
    
    # 分割数据
    split_idx = int(len(triples) * train_ratio)
    train_triples = triples[:split_idx]
    val_triples = triples[split_idx:]
    
    print(f"训练集数量: {len(train_triples)}")
    print(f"验证集数量: {len(val_triples)}")
    
    return train_triples, val_triples


def prepare_iot0708_data():
    """准备iot0708数据用于训练和验证"""
    print("=== 准备IoT0708数据 ===")
    
    # 数据文件路径
    source_triples = "data/iot0708/extensible_triples.txt"
    source_entity_vocab = "data/iot0708/entity.vocab"
    source_relation_vocab = "data/iot0708/relation.vocab"
    
    # 训练数据目录
    train_data_dir = "data/iot0708_train"
    if not os.path.exists(train_data_dir):
        os.makedirs(train_data_dir)
    
    # 复制词汇文件
    shutil.copy2(source_entity_vocab, os.path.join(train_data_dir, "entity.vocab"))
    shutil.copy2(source_relation_vocab, os.path.join(train_data_dir, "relation.vocab"))
    
    # 分割数据
    train_triples, val_triples = split_data_with_validation(source_triples)
    
    # 保存训练集
    train_file = os.path.join(train_data_dir, "train.txt")
    with open(train_file, 'w', encoding='utf-8') as f:
        for line in train_triples:
            parts = line.strip().split()
            if len(parts) >= 3:
                head, relation, tail = parts[0], parts[1], ' '.join(parts[2:])
                f.write(f"{head}\t{relation}\t{tail}\n")
    
    # 保存验证集
    val_file = os.path.join(train_data_dir, "valid.txt")
    with open(val_file, 'w', encoding='utf-8') as f:
        for line in val_triples:
            parts = line.strip().split()
            if len(parts) >= 3:
                head, relation, tail = parts[0], parts[1], ' '.join(parts[2:])
                f.write(f"{head}\t{relation}\t{tail}\n")
    
    print(f"数据准备完成！")
    print(f"- 训练数据文件: {train_file}")
    print(f"- 验证数据文件: {val_file}")
    print(f"- 实体词汇文件: {os.path.join(train_data_dir, 'entity.vocab')}")
    print(f"- 关系词汇文件: {os.path.join(train_data_dir, 'relation.vocab')}")
    
    return train_data_dir


def calculate_validation_loss(model, val_iterator, sess):
    """计算验证集损失"""
    val_loss = 0.0
    val_steps = 0
    
    sess.run(val_iterator.initializer)
    while True:
        try:
            batch_loss = model.eval(sess)
            val_loss += batch_loss
            val_steps += 1
        except tf.errors.OutOfRangeError:
            break
    
    return val_loss / val_steps if val_steps > 0 else float('inf')


def train_iot0708():
    """训练IoT0708知识图谱嵌入模型 - 改进版本"""
    print("=== 开始训练IoT0708知识图谱嵌入模型（改进版本）===")
    
    # 准备数据
    train_data_dir = prepare_iot0708_data()
    
    # 更新配置 - 针对过拟合的优化
    FLAGS.data_file = os.path.join(train_data_dir, 'train.txt')
    FLAGS.entity_vocab = os.path.join(train_data_dir, 'entity.vocab')
    FLAGS.relation_vocab = os.path.join(train_data_dir, 'relation.vocab')
    
    # 优化配置
    FLAGS.batch_size = 128  # 增大batch size减少过拟合
    FLAGS.max_epoch = 30    # 减少epoch数量
    FLAGS.learning_rate = 0.0005  # 降低学习率
    FLAGS.shuffle_buffer_size = 100000  # 增大shuffle buffer
    # FLAGS.l2_reg = 0.001  # 添加L2正则化（已在config.py定义，不能在此赋值）
    
    # 早停参数
    patience = 5  # 容忍验证损失不下降的轮数
    min_delta = 0.001  # 最小改善阈值
    
    # 打印配置
    print_args(FLAGS)
    
    # 加载词汇表
    print("加载词汇表...")
    entity_table, entity, entity_size = load_vocab(FLAGS.entity_vocab)
    relation_table, _, relation_size = load_vocab(FLAGS.relation_vocab)
    FLAGS.entity_size = entity_size
    FLAGS.relation_size = relation_size
    
    print(f"实体数量: {entity_size}")
    print(f"关系数量: {relation_size}")
    
    # 准备训练和验证数据迭代器
    print("准备数据迭代器...")
    train_iterator = get_iterator(
        FLAGS.data_file, entity, entity_table, relation_table, 
        FLAGS.batch_size, shuffle_buffer_size=FLAGS.shuffle_buffer_size
    )
    
    val_file = os.path.join(train_data_dir, 'valid.txt')
    val_iterator = get_iterator(
        val_file, entity, entity_table, relation_table, 
        FLAGS.batch_size, shuffle_buffer_size=FLAGS.shuffle_buffer_size
    )
    
    # 选择模型
    print(f"使用模型: {FLAGS.model_name}")
    if FLAGS.model_name.lower() == "transe":
        model = TransE(train_iterator, FLAGS)
    elif FLAGS.model_name.lower() == "distmult":
        model = DISTMULT(train_iterator, FLAGS)
    elif FLAGS.model_name.lower() == "transh":
        model = TransH(train_iterator, FLAGS)
    elif FLAGS.model_name.lower() == "transr":
        model = TransR(train_iterator, FLAGS)
    elif FLAGS.model_name.lower() == "transd":
        model = TransD(train_iterator, FLAGS)
    elif FLAGS.model_name.lower() == "stranse":
        model = STransE(train_iterator, FLAGS)
    else:
        print(f"不支持的模型: {FLAGS.model_name}")
        return
    
    # 构建模型图
    print("构建模型图...")
    model.build_graph()
    
    # 开始训练
    print("开始训练...")
    with tf.Session() as sess:
        init_ops = [tf.global_variables_initializer(), tf.local_variables_initializer(), tf.tables_initializer()]
        sess.run(init_ops)
        
        # 创建summary writer
        summary_dir = os.path.join("summary", "iot0708_improved")
        if not os.path.exists(summary_dir):
            os.makedirs(summary_dir)
        writer = tf.summary.FileWriter(summary_dir, sess.graph)
        
        # 早停变量
        best_val_loss = float('inf')
        patience_counter = 0
        best_epoch = 0
        
        for epoch in range(FLAGS.max_epoch):
            print(f"\n=== Epoch {epoch + 1}/{FLAGS.max_epoch} ===")
            
            # 训练阶段
            sess.run(train_iterator.initializer)
            epoch_loss = 0.0
            step = 0
            
            while True:
                try:
                    batch_loss, _, summary = model.train(sess)
                    epoch_loss += batch_loss
                    step += 1
                    
                    # 添加summary
                    if step % 100 == 0:
                        writer.add_summary(summary, global_step=epoch * 1000 + step)
                    
                    # 显示训练进度
                    if step % FLAGS.stats_per_steps == 0:
                        avg_loss = epoch_loss / step
                        print(f'Epoch {epoch + 1}, Step {step}, Avg Loss: {avg_loss:.6f}')
                        
                except tf.errors.OutOfRangeError:
                    break
            
            # 计算训练平均损失
            avg_train_loss = epoch_loss / step
            print(f'Epoch {epoch + 1} 训练完成, 平均损失: {avg_train_loss:.6f}')
            
            # 验证阶段
            print("开始验证...")
            val_loss = calculate_validation_loss(model, val_iterator, sess)
            print(f'Epoch {epoch + 1} 验证损失: {val_loss:.6f}')
            
            # 早停检查
            if val_loss < best_val_loss - min_delta:
                best_val_loss = val_loss
                patience_counter = 0
                best_epoch = epoch + 1
                
                # 保存最佳模型
                model_dir = os.path.join("model", "iot0708_improved")
                if not os.path.exists(model_dir):
                    os.makedirs(model_dir)
                save_path = os.path.join(model_dir, f"best_model_epoch_{epoch + 1}.ckpt")
                model.save(sess, save_path)
                print(f"新的最佳模型已保存到: {save_path}")
            else:
                patience_counter += 1
                print(f"验证损失未改善，patience: {patience_counter}/{patience}")
            
            # 定期保存检查点
            if (epoch + 1) % 10 == 0:
                model_dir = os.path.join("model", "iot0708_improved")
                if not os.path.exists(model_dir):
                    os.makedirs(model_dir)
                save_path = os.path.join(model_dir, f"checkpoint_epoch_{epoch + 1}.ckpt")
                model.save(sess, save_path)
                print(f"检查点已保存到: {save_path}")
            
            # 早停
            if patience_counter >= patience:
                print(f"早停触发！最佳模型在第 {best_epoch} 轮")
                break
        
        writer.close()
        print(f"训练完成！最佳验证损失: {best_val_loss:.6f} (第 {best_epoch} 轮)")


if __name__ == '__main__':
    # 设置TensorFlow日志级别
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    
    # 检查数据文件是否存在
    if not os.path.exists("data/iot0708/extensible_triples.txt"):
        print("错误: 找不到数据文件 data/iot0708/extensible_triples.txt")
        print("请先运行知识图谱构建脚本生成数据")
        sys.exit(1)
    
    # 开始训练
    train_iot0708() 