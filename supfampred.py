import subprocess
import argparse
from Bio import SearchIO
default_target = 'target.fasta'
model_tab = '/mnt/data2/supfam/supfam/model.tab'

def predict_superfamily(input_fasta, hmm_library='/mnt/data2/supfam/supfam/hmmlib', output_tbl='output.tbl', e_value_threshold=0.001):
    """
    使用 SUPERFAMILY HMM 库预测 FASTA 序列的结构超家族。
    
    参数:
    - input_fasta: 输入 FASTA 文件路径。
    - hmm_library: SUPERFAMILY HMM 库路径 (默认: /mnt/data2/supfam/supfam/hmmlib)。
    - output_tbl: HMMER 输出表格文件路径 (默认: output.tbl)。
    - e_value_threshold: E-value 阈值，用于过滤显著匹配 (默认: 0.001)。
    
    返回: 打印每个查询序列的匹配超家族 ID 和细节。
    """
    # 运行 hmmscan 命令
    id_to_name = {}
    print(f"Starting prediction for file: {input_fasta}")  # 添加这行
    print(f"HMM library: {hmm_library}")
    try:
        result =subprocess.run([
        '/mnt/data2/supfam/hmmer-3.1b2/src/hmmscan',  # 添加绝对路径
        '--domtblout', output_tbl,
        '-E', str(e_value_threshold),
        hmm_library,
        input_fasta
        ], check=True, capture_output=True, text=True)
        print("hmmscan ran successfully. Stdout:", result.stdout)  # 添加
        print("Stderr (if any):", result.stderr)  # 添
    except subprocess.CalledProcessError as e:
        print(f"Error running hmmscan: {e.stderr}")
        return
    except FileNotFoundError as fnf:
        print(f"Command not found: {fnf}")  # 新增捕获
        return

    print("Parsing output file...") # 解析输出
    try:
        queries = list(SearchIO.parse(output_tbl, 'hmmscan3-domtab'))
        if not queries:
            print("No queries found in output.")  # 添加
    
        for query in SearchIO.parse(output_tbl, 'hmmscan3-domtab'):
            print(f"\nQuery sequence: {query.id}")
            if not query.hits:
                print("No significant superfamily matches found.")
                continue
            
            for hit in query.hits:
                for hsp in hit.hsps:
                    if hsp.evalue < e_value_threshold:
                        superfamily_id = hit.id  # 这是 SCOP 超家族 ID，如 '46458'
                        print(f" - Superfamily ID: {superfamily_id}")
                        print(f"   E-value: {hsp.evalue}")
                        print(f"   Bit score: {hsp.bitscore}")
                        print(f"   Domain boundaries: {hsp.query_start}-{hsp.query_end}")
    except Exception as e:
        print(f"Error parsing output: {e}")
    
    with open(model_tab, 'r') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                id_to_name[parts[0]] = parts[1]

    superfamily_name = id_to_name.get(superfamily_id, 'Unknown')
    print(f" - Superfamily Name: {superfamily_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict structural superfamilies using SUPERFAMILY HMM.")
    parser.add_argument('input_fasta', nargs='?', default='target1.fasta', help="Path to input FASTA file")  # 添加 nargs='?'
    parser.add_argument('--hmm_library', default='/mnt/data2/supfam/supfam/hmmlib', help="Path to SUPERFAMILY HMM library")
    parser.add_argument('--e_value', type=float, default=0.001, help="E-value threshold for filtering")
    
    args = parser.parse_args()
    predict_superfamily(args.input_fasta, args.hmm_library, e_value_threshold=args.e_value)