import pandas as pd

def print_hex(file_path):
    with open(file_path, 'rb') as file:
        binary_content = file.read()      # 读取内容为二进制
    hex_content = binary_content.hex()    # 将二进制转换成十六进制
    for i in range(0, len(hex_content), 32):    # 每32个字符（16个字节）打印一次
        print(hex_content[i:i+32])                # 打印十六进制字符串片段


file_path = r"D:\desktop\6\floruitshow.mp4"
print_hex(file_path)


