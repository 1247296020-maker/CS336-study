#!/usr/bin/env python3
"""
Hello World 示例 / Hello World Example

这是一个简单的Hello World程序，演示Python基础语法。
This is a simple Hello World program demonstrating basic Python syntax.

学习要点 / Learning Points:
- Python程序的基本结构
- print()函数的使用
- 字符串的使用
- 注释的写法
"""

def main():
    """主函数 / Main function"""
    # 打印欢迎信息 / Print welcome message
    print("Hello, CS336 Study!")
    print("你好，CS336学习！")
    
    # 演示变量使用 / Demonstrate variable usage
    course_name = "CS336"
    student_name = "学习者"  # Student
    
    print(f"课程名称: {course_name}")
    print(f"学生姓名: {student_name}")
    
    # 演示简单计算 / Demonstrate simple calculation
    a = 10
    b = 20
    result = a + b
    print(f"计算结果: {a} + {b} = {result}")

if __name__ == "__main__":
    main()