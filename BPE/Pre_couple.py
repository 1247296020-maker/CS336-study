import os
from typing import BinaryIO
from BPE import BPE
def find_chunk_boundary(file: BinaryIO, desired_num_chunkssize: int,split_special_token:bytes) -> list[int]:
    # 通过特殊分割来分割文件，并行处理

    assert isinstance(split_special_token, bytes), "Must represent special token as a bytestring"
    #获取文件总长度
    file.seek(0,os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    #没个块的数目
    chunk_size = file_size // desired_num_chunkssize
    #每个块的边界 , 左闭右开
    chunk_boundaries = [i*chunk_size for i in range(desired_num_chunkssize+1)]
    chunk_boundaries[-1] =file_size

    #调整中间的边界
    min_chunk_size =4096

    for bi in range(1,len(chunk_boundaries)-1):
        initial_position = chunk_boundaries[bi]
        file.seek(initial_position)

        while True:
            mini_chunk = file.read(min_chunk_size)
            #因为剩余数据如果说超过了
            if mini_chunk == b'':
                chunk_boundaries[bi]= file_size
                break

            #通过 bytes.find() to find the special token (end)
            found_at = mini_chunk.find(split_special_token)
            if found_at != -1:
                chunk_boundaries[bi] = initial_position +found_at
                break

            initial_position += min_chunk_size
    return sorted(set(chunk_boundaries))
    # 5) 最终返回“去重+排序”的边界列表
    # 去重的原因：有可能多个估算边界最终都被推进到了同一个位置（比如文件末尾）
    # 排序是为了确保边界严格递增（满足 [start, end) 的读取模式）

diectory = './data/TinyStoriesV2-GPT4-valid.txt'
## 用法示例（示意代码，不可直接运行；你需要把 ... 换成你自己的文件路径）
with open(diectory, "rb") as f:
    # 你希望并行的进程/任务个数，例如 4 个
    num_processes = 10

    # 找到 chunk 边界（按特殊分隔符对齐）
    boundaries = find_chunk_boundary(f, num_processes, b"<|endoftext|>")

    # 下面是“串行”的读取方式：依次读取每一段 [start, end)
    # 实际项目里你可以把这些 (start, end) 分发给多个进程并行处理
    start ,end = boundaries[0],boundaries[1]
    f.seek(start)
    chunk =  f.read(end-start).decode("utf-8", errors="ignore")
    special_token = ["<|endoftext|>"]

    # 读取该段的原始字节，并解码为 utf-8 文本
    # errors="ignore" 表示如果某个位置刚好落在多字节字符中间导致解码不完整，就忽略这部分错误
    # 这可能会造成极少量字符损失，但通常不影响统计类任务
    if isinstance(chunk, str) and chunk.strip():
        function = BPE(10000)
        function.train_byte_bpe(chunk, special_token)
        print(function.token_to_id)

    # 在这里对 chunk 进行“预分词 / 统计”等处理
    # 例如：统计你的预分词器输出的 token 频次，然后把各段的统计结果合并
    # 注意：当前实现将“分隔符”包含在右侧片段开头（因为边界是分隔符起点）
    # 如果你不希望分隔符出现在任何片段里，可以在读取右侧片段时跳过 len(split_special_token) 个字节
    # 示例（仅示意）：
    #   f.seek(start + (len_token if start 是某个分隔符起点 else 0))
    #   再 read(...)
