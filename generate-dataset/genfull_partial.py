import os
from datasets import Dataset, DatasetDict
import pandas as pd

def join_lines(lis):
    res = ""
    for i in range(len(lis)):
        res += lis[i]
    return res

def read_content_files(root_dir):
    data = {'content': [], 'path': [], 'len': [], "lines": []}
    cnt = 10
    queue = []
    queue.append(root_dir)
    while (len(queue) > 0 and cnt > 0):
        cur_dir = queue.pop(0)
        sub_lis = os.listdir(cur_dir)
        for file_name in sub_lis:
            file_path = os.path.join(cur_dir, file_name)
            relative_path = "topsop" + file_path[len(root_dir):]
            if os.path.isdir(file_path):
                queue.append(file_path)
            else:
                if not (file_name.endswith(".cc") or file_name.endswith(".h") or file_name.endswith(".c")):
                    continue
                cnt -= 1
                with open(file_path, 'r', encoding='utf-8') as f:
                    print(file_path)
                    l = f.readlines()
                    lines = len(l)
                    data['lines'].append(lines)  
                    content = join_lines(l)
                    data['content'].append(content)
                    data['path'].append(relative_path)
                    data['len'].append(len(content)) 
                        
    return data
        
    

root_dir = '/home/int.orion.que/dev/my_programs/topsop'
data = read_content_files(root_dir)

# 将数据转换为DataFrame
df = pd.DataFrame(data)
df.to_csv("/home/int.orion.que/dev/my_programs/generate-dataset/code-full-partial.csv", index=False)
# 将DataFrame转换为Hugging Face的数据集
dataset = Dataset.from_pandas(df)
dataset.save_to_disk('/home/int.orion.que/dev/my_programs/generate-dataset/dataset-full-partial')


# # 如果需要将数据集划分为训练集和验证集，可以使用train_test_split
# train_test_split = dataset.train_test_split(test_size=0.2)
# dataset_dict = DatasetDict(dataset)

# # 保存数据集
# dataset_dict.save_to_disk('./dataset')

# print(dataset_dict)
