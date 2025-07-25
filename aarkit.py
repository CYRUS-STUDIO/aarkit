import os
import sys
import zipfile
from datetime import datetime


def unpack_aar(aar_path, output_dir=None):
    # 1. 校验输入文件是否是合法的 .aar 文件
    if not os.path.isfile(aar_path) or not aar_path.endswith(".aar"):
        print("❌ 输入文件不是有效的 .aar 文件")
        return

    # 2. 默认输出路径为同名目录
    if output_dir is None:
        base_name = os.path.splitext(os.path.basename(aar_path))[0]
        output_dir = os.path.join(os.path.dirname(aar_path), base_name)

    # 3. 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 4. 使用 zipfile 解压 .aar 文件
    with zipfile.ZipFile(aar_path, "r") as zip_ref:
        zip_ref.extractall(output_dir)
        print(f"✅ 已解包到：{output_dir}")


def pack_aar(input_dir, output_aar=None):
    # 如果输入目录不存在，打印错误信息并退出
    if not os.path.isdir(input_dir):
        print("❌ 输入目录不存在")
        return

    # 如果未指定输出 aar 文件路径，则自动生成一个带时间戳的文件名
    if output_aar is None:
        base_name = os.path.basename(os.path.normpath(input_dir))  # 获取目录名
        timestamp = datetime.now().strftime("%Y%m%d%H%M")  # 当前时间戳
        # 输出路径为：输入目录的上一级 + 自动生成的文件名
        output_aar = os.path.join(os.path.dirname(input_dir), f"{base_name}-{timestamp}.aar")

    # 创建一个压缩文件（.aar 格式），使用 ZIP_DEFLATED 压缩方式
    with zipfile.ZipFile(output_aar, "w", zipfile.ZIP_DEFLATED) as zipf:
        # 遍历输入目录及其子目录中的所有文件
        for root, _, files in os.walk(input_dir):
            for file in files:
                full_path = os.path.join(root, file)  # 文件的完整路径
                arcname = os.path.relpath(full_path, input_dir)  # 计算相对路径（作为 zip 中的路径）
                zipf.write(full_path, arcname)  # 写入压缩包

    print(f"✅ 已打包为：{output_aar}")


if __name__ == "__main__":
    r"""
    # 解包
    python aarkit.py unpack mylib.aar
    # → 默认输出：mylib/ （与 mylib.aar 同级）
    
    python aarkit.py unpack mylib.aar ./output_dir/
    # → 输出到指定目录
    
    # 打包
    python aarkit.py pack ./mylib/
    # → 输出为：mylib-202507231253.aar
    
    python aarkit.py pack ./mylib/ mylib.aar
    # → 输出为：mylib.aar
    """

    if len(sys.argv) < 3:
        print("用法：")
        print("  解包：python aarkit.py unpack mylib.aar [output_dir]")
        print("  打包：python aarkit.py pack ./mylib/ [output.aar]")
        sys.exit(1)

    command = sys.argv[1]
    if command == "unpack":
        aar_path = sys.argv[2]
        output_dir = sys.argv[3] if len(sys.argv) >= 4 else None
        unpack_aar(aar_path, output_dir)
    elif command == "pack":
        input_dir = sys.argv[2]
        output_aar = sys.argv[3] if len(sys.argv) >= 4 else None
        pack_aar(input_dir, output_aar)
    else:
        print(f"未知命令：{command}")
