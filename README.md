> 版权归作者所有，如有转发，请注明文章出处：<https://cyrus-studio.github.io/blog/>

# 一、什么是 AAR 文件？



AAR 文件（Android Archive）是 Android Studio 用来打包 Android Library（库模块） 的一种压缩文件格式，扩展名是 .aar，类似于 Java 的 .jar 文件，但功能更丰富，用于复用 UI 组件、资源和代码。



AAR 文件结构（解压后）

```
your-lib.aar
├── AndroidManifest.xml       # 库模块的清单文件
├── classes.jar               # 编译后的 Java/Kotlin 类文件（字节码）
├── res/                      # 资源目录（layout、drawable、values 等）
├── R.txt                     # 编译生成的 R 类符号文件
├── assets/                   # assets 目录中的内容
├── libs/                     # 依赖的 .jar 库
├── jni/                      # native 库（.so 文件）
├── proguard.txt              # 混淆配置文件
├── public.txt                # 声明哪些资源是公开的
└── META-INF/                 # 元数据（如 aar metadata、许可证等）
```


使用 AAR 的场景举例：

- 引入第三方 SDK（如广告、支付库）

- 组件化开发中将公共模块打成 AAR

- 在没有上传 Maven 仓库的情况下本地集成依赖



# 二、如何解包 AAR 文件



.aar  实质上是一个 ZIP 压缩包，可以使用 Python 标准库中的 zipfile 和 os 模块实现对 .aar 文件的解包。

```
import os
import zipfile

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
```


通过 unpack_aar() 解包后，就可以进一步操作 .aar 中的内容，比如提取 classes.jar 并修改 jar 中的 java 代码。

```
(anti-app) PS D:\Python\anti-app\aar> python aarkit.py unpack "D:\Python\anti-app\app\Ksfndkd\sanfang-jiagu-0_0_1.aar"
✅ 已解包到：D:\Python\anti-app\app\Ksfndkd\sanfang-jiagu-0_0_1
```


![word/media/image1.png](https://gitee.com/cyrus-studio/images/raw/master/894c44ad7a082a7a81f8147720142030.png)


# 三、如何重打包 AAR 文件



使用 zipfile 将解包目录重新打包成一个 .aar 文件

```
import os
import zipfile
from datetime import datetime

def pack_aar(input_dir, output_aar=None):
    # 如果输入目录不存在，打印错误信息并退出
    if not os.path.isdir(input_dir):
        print("❌ 输入目录不存在")
        return

    # 如果未指定输出 aar 文件路径，则自动生成一个带时间戳的文件名
    if output_aar is None:
        base_name = os.path.basename(os.path.normpath(input_dir))  # 获取目录名
        timestamp = datetime.now().strftime("%Y%m%d%H%M")           # 当前时间戳
        # 输出路径为：输入目录的上一级 + 自动生成的文件名
        output_aar = os.path.join(os.path.dirname(input_dir), f"{base_name}-{timestamp}.aar")

    # 创建一个压缩文件（.aar 格式），使用 ZIP_DEFLATED 压缩方式
    with zipfile.ZipFile(output_aar, "w", zipfile.ZIP_DEFLATED) as zipf:
        # 遍历输入目录及其子目录中的所有文件
        for root, _, files in os.walk(input_dir):
            for file in files:
                full_path = os.path.join(root, file)                      # 文件的完整路径
                arcname = os.path.relpath(full_path, input_dir)          # 计算相对路径（作为 zip 中的路径）
                zipf.write(full_path, arcname)                           # 写入压缩包

    print(f"✅ 已打包为：{output_aar}")
```


# 四、AAR 修改实战：注入自定义逻辑



需求：修改 jar 中指定的类 Bhubscfh 的静态代码块的 xjhbp.classescxclcy(120); 调用后插入下面的代码加载自定义的 Hook 库，实现 Hook 指定方法并修改返回值。

```
System.loadLibrary("my_hook");
```


## 将 classes.jar 转为 smali 代码



Jar → Smali 转换流程：



**1、JAR → DEX** 



使用 Google 的 D8 工具将 .jar 文件编译成 .dex 文件（Dalvik Executable 格式）：

```
d8 --output <output_dir> <jar_file>
```


d8 是 Google 提供的 Dex 编译器，用于将 Java 字节码（.class 文件）转换成 Dalvik 字节码（.dex 文件），已取代老旧的 dx 工具。它与 Android SDK 有直接关系，是 Android 构建流程中的一部分。



![word/media/image2.png](https://gitee.com/cyrus-studio/images/raw/master/df331a14160fc03502ed048ac45a8a3d.png)


**2、DEX → SMALI** 



使用 Baksmali 工具将 .dex 反编译为 smali 汇编代码：

```
java -jar baksmali.jar d classes.dex -o <output_dir>
```
相关文章：[一文搞懂 Smali 与 Baksmali：Java 层逆向必备技能](https://cyrus-studio.github.io/blog/posts/%E4%B8%80%E6%96%87%E6%90%9E%E6%87%82-smali-%E4%B8%8E-baksmalijava-%E5%B1%82%E9%80%86%E5%90%91%E5%BF%85%E5%A4%87%E6%8A%80%E8%83%BD/)



代码实现如下：

```
import os
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# 工具路径配置
TOOLS = {
    "dex2jar": Path(r"D:\Python\anti-app\dex2jar\d2j-dex2jar.bat"),
    "d8": Path(r"D:\App\android\sdk\cmdline-tools\latest\bin\d8.bat"),
    "baksmali": Path(r"./baksmali.jar"),
    "smali": Path(r"./smali.jar"),
    "java": r"java",
}

def check_tools():
    for name, path in TOOLS.items():
        if name == "java":
            continue
        if not path.exists():
            print(f"[❌] 工具 {name} 未找到: {path}")
            sys.exit(1)
    print("[✅] 所有工具检测通过")

def run_cmd(cmd, cwd=None):
    print(f"[🟢] 执行命令: {' '.join(str(x) for x in cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        print(f"[❌] 命令执行失败: {' '.join(str(x) for x in cmd)}")
        sys.exit(1)

def jar_to_smali(jar_path: Path, output_dir: Path):
    print(f"[📦] 转换 jar 到 smali: {jar_path}")
    output_smali = output_dir
    output_dex_dir = output_dir

    if output_smali.exists():
        shutil.rmtree(output_smali)
    output_smali.mkdir(parents=True, exist_ok=True)
    output_dex_dir.mkdir(parents=True, exist_ok=True)

    run_cmd([
        str(TOOLS["d8"]),
        "--output", str(output_dex_dir),
        str(jar_path)
    ])

    dex_file = output_dex_dir / "classes.dex"

    run_cmd([
        TOOLS["java"], "-jar", str(TOOLS["baksmali"]),
        "d", str(dex_file), "-o", str(output_smali)
    ])

    os.remove(dex_file)
    print(f"[✅] smali 已输出到: {output_smali}")
```


执行 jar2smali 命令得到 smali 代码

```
(anti-app) PS D:\Python\anti-app\dex2smali> python jar2smali.py jar2smali "D:\Python\anti-app\app\Ksfndkd\sanfang-jiagu-0_0_1\classes.jar"
[✅] 所有工具检测通过
[📦] 转换 jar 到 smali: D:\Python\anti-app\app\Ksfndkd\sanfang-jiagu-0_0_1\classes.jar
[🟢] 执行命令: D:\App\android\sdk\cmdline-tools\latest\bin\d8.bat --output D:\Python\anti-app\app\Ksfndkd\sanfang-jiagu-0_0_1\classes_smali D:\Python\anti-app\app\Ksfndkd\sanfang-jiagu-0_0_1\classes.jar
...
Warning in D:\Python\anti-app\app\Ksfndkd\sanfang-jiagu-0_0_1\classes.jar:marmojkfnf/huflnkmt/ncagri/jdtuadkc/Ksfndkd$a.class:
Type `com.blankj.utilcode.util.PermissionUtils$SimpleCallback` was not found, it is required for default or static interface methods desugaring of `marmojkfnf.huflnkmt.ncagri.jdtuadkc.Ksfndkd$a`
...
[🟢] 执行命令: java -jar baksmali.jar d D:\Python\anti-app\app\Ksfndkd\sanfang-jiagu-0_0_1\classes_smali\classes.dex -o D:\Python\anti-app\app\Ksfndkd\sanfang-jiagu-0_0_1\classes_smali
[✅] smali 已输出到: D:\Python\anti-app\app\Ksfndkd\sanfang-jiagu-0_0_1\classes_smali
```


## 修改 smali 文件，注入代码



找到目标类的静态代码块的 smali 代码如下：

```
# direct methods
.method public static constructor <clinit>()V
    .locals 1

    const/16 v0, 0x78

    invoke-static {v0}, Lfmfjq/twyvy/xjhbp;->classescxclcy(I)V

    return-void
.end method
```


希望在 classescxclcy 方法调用后插入自定义的代码逻辑

```
const-string v1, "my_hook"

invoke-static {v1}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V
```


如果不知道 smali 代码如何写，可以先通过 android studio 编写 java/kotlin 代码，打包 apk，再通过 ApkTool 反编译 apk 得到 smali 代码。 



参考：[一键反编译、签名、安装 APK！手把手带你玩转 ApkTool + 签名工具](https://cyrus-studio.github.io/blog/posts/%E4%B8%80%E9%94%AE%E5%8F%8D%E7%BC%96%E8%AF%91%E7%AD%BE%E5%90%8D%E5%AE%89%E8%A3%85-apk%E6%89%8B%E6%8A%8A%E6%89%8B%E5%B8%A6%E4%BD%A0%E7%8E%A9%E8%BD%AC-apktool-+-%E7%AD%BE%E5%90%8D%E5%B7%A5%E5%85%B7/)



修改后：

```
# direct methods
.method public static constructor <clinit>()V
    .locals 2

    const/16 v0, 0x78

    invoke-static {v0}, Lfmfjq/twyvy/xjhbp;->classescxclcy(I)V

    const-string v1, "my_hook"

    invoke-static {v1}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V

    return-void
.end method
```
由于修改后用到了 v0 和 v1 两个寄存器，需要把 .locals 1 改为 .locals 2，.locals 用于声明当前方法最多会用到几个寄存器。



注意：在新版 smali 的语法中，使用 registers 取代了 locals。



so 文件直接 copy 到 jni 对应架构目录下



![word/media/image3.png](https://gitee.com/cyrus-studio/images/raw/master/f9332ff5ef84fbacf26efaca693acfc7.png)


其他相关的 smali 代码直接 copy 到 smali 目录下



![word/media/image4.png](https://gitee.com/cyrus-studio/images/raw/master/4dac1684ec30c2020f70ac91ae85ef9f.png)


## 注意事项（防混淆）



编辑 proguard.txt 添加需要防止混淆的代码，否则可能出现找不到类的情况：

```
-keep class com.bytedance.** {
    *;
}
```


## 将 smali 转回 jar



Smali → Jar 转换流程：



**1、 smali → dex** 



使用 [smali 工具](https://github.com/JesusFreke/smali) 将 .smali 汇编代码打包生成 .dex 文件：

```
java -jar smali.jar a <smali_dir> -o <recompiled.dex>
```
- a 表示 assemble（汇编）。

- <smali_dir> 是包含 .smali 文件的目录。

- 输出生成 recompiled.dex。



**2、dex → jar** 



使用 [dex2jar 工具](https://github.com/pxb1988/dex2jar) 将 .dex 文件转换为 Java 字节码 .jar 文件：

```
d2j-dex2jar.sh recompiled.dex -o output.jar
```


代码实现如下：

```
def smali_to_jar(smali_dir: Path, output_jar: Path):
    print("📦 处理 smali → dex → jar")
    temp_dex = smali_dir.parent / "recompiled.dex"

    run_cmd(["java", "-jar", str(TOOLS["smali"]), "a", str(smali_dir), "-o", str(temp_dex)])
    run_cmd([str(TOOLS["dex2jar"]), str(temp_dex), "-o", str(output_jar)])
    temp_dex.unlink(missing_ok=True)
    print(f"✅ 输出 jar 文件: {output_jar}")
```


执行 smali2jar 命令把 smali 目录重写打包回 jar 文件

```
(anti-app) PS D:\Python\anti-app\dex2smali> python jar2smali.py smali2jar D:\Python\anti-app\app\Ksfndkd\sanfang-jiagu-0_0_1\classes_smali
[✅] 所有工具检测通过
📦 处理 smali → dex → jar
[🟢] 执行命令: java -jar smali.jar a D:\Python\anti-app\app\Ksfndkd\sanfang-jiagu-0_0_1\classes_smali -o D:\Python\anti-app\app\Ksfndkd\sanfang-jiagu-0_0_1\recompiled.dex
[🟢] 执行命令: D:\Python\anti-app\dex2jar\d2j-dex2jar.bat D:\Python\anti-app\app\Ksfndkd\sanfang-jiagu-0_0_1\recompiled.dex -o D:\Python\anti-app\app\Ksfndkd\sanfang-jiagu-0_0_1\classes-202507260113.jar
dex2jar D:\Python\anti-app\app\Ksfndkd\sanfang-jiagu-0_0_1\recompiled.dex -> D:\Python\anti-app\app\Ksfndkd\sanfang-jiagu-0_0_1\classes-202507260113.jar
✅ 输出 jar 文件: D:\Python\anti-app\app\Ksfndkd\sanfang-jiagu-0_0_1\classes-202507260113.jar
```


使用 jd 打开 jar 文件可以看到指定位置已经新增了自定义的代码。



![word/media/image5.png](https://gitee.com/cyrus-studio/images/raw/master/98e5b427ae9217d0a02f6301d8ab2a9f.png)


使用新打包的 jar 替换掉原来的  classes.jar，并删除 smali 目录。



## AAR 重打包



执行重打包命令把 aar 解压目录重新打包成 aar 文件。

```
(anti-app) PS D:\Python\anti-app\aar> python aarkit.py pack D:\Python\anti-app\app\Ksfndkd\sanfang-jiagu-0_0_1
✅ 已打包为：D:\Python\anti-app\app\Ksfndkd\sanfang-jiagu-0_0_1-202507260120.aar
```


# 五、Android Studio 中导入定制 AAR



1. 将 AAR 文件放入模块目录下的 libs 文件夹中：

```
app/
├── libs/
│   └── your-library.aar
```


2. 修改 build.gradle.kts：

```
dependencies {
    implementation(files("libs/sanfang-jiagu-0_0_1-202507260120.aar"))
}
```
如果你有多个 .aar 文件并希望一次性导入，可以使用：

```
dependencies {
    implementation(fileTree(mapOf("dir" to "libs", "include" to listOf("*.aar"))))
}
```


3. settings.gradle.kts 添加 flatDir：

```
dependencyResolutionManagement {
    ...
    repositories {
        ...
        flatDir {
            dirs("libs")
        }
    }
}
```


导入成功。



![word/media/image6.png](https://gitee.com/cyrus-studio/images/raw/master/c73f89472a0d0c3df049b55c2098da76.png)


# 完整源码



## 1. aar 工具源码



```
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
        timestamp = datetime.now().strftime("%Y%m%d%H%M")           # 当前时间戳
        # 输出路径为：输入目录的上一级 + 自动生成的文件名
        output_aar = os.path.join(os.path.dirname(input_dir), f"{base_name}-{timestamp}.aar")

    # 创建一个压缩文件（.aar 格式），使用 ZIP_DEFLATED 压缩方式
    with zipfile.ZipFile(output_aar, "w", zipfile.ZIP_DEFLATED) as zipf:
        # 遍历输入目录及其子目录中的所有文件
        for root, _, files in os.walk(input_dir):
            for file in files:
                full_path = os.path.join(root, file)                      # 文件的完整路径
                arcname = os.path.relpath(full_path, input_dir)          # 计算相对路径（作为 zip 中的路径）
                zipf.write(full_path, arcname)                           # 写入压缩包

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
```


## 2. jar2smali 工具源码



```
import os
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# 工具路径配置
TOOLS = {
    "dex2jar": Path(r"D:\Python\anti-app\dex2jar\d2j-dex2jar.bat"),
    "d8": Path(r"D:\App\android\sdk\cmdline-tools\latest\bin\d8.bat"),
    "baksmali": Path(r"./baksmali.jar"),
    "smali": Path(r"./smali.jar"),
    "java": r"java",
}

def check_tools():
    for name, path in TOOLS.items():
        if name == "java":
            continue
        if not path.exists():
            print(f"[❌] 工具 {name} 未找到: {path}")
            sys.exit(1)
    print("[✅] 所有工具检测通过")

def run_cmd(cmd, cwd=None):
    print(f"[🟢] 执行命令: {' '.join(str(x) for x in cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        print(f"[❌] 命令执行失败: {' '.join(str(x) for x in cmd)}")
        sys.exit(1)

def jar_to_smali(jar_path: Path, output_dir: Path):
    print(f"[📦] 转换 jar 到 smali: {jar_path}")
    output_smali = output_dir
    output_dex_dir = output_dir

    if output_smali.exists():
        shutil.rmtree(output_smali)
    output_smali.mkdir(parents=True, exist_ok=True)
    output_dex_dir.mkdir(parents=True, exist_ok=True)

    run_cmd([
        str(TOOLS["d8"]),
        "--output", str(output_dex_dir),
        str(jar_path)
    ])

    dex_file = output_dex_dir / "classes.dex"

    run_cmd([
        TOOLS["java"], "-jar", str(TOOLS["baksmali"]),
        "d", str(dex_file), "-o", str(output_smali)
    ])

    os.remove(dex_file)
    print(f"[✅] smali 已输出到: {output_smali}")

def smali_to_jar(smali_dir: Path, output_jar: Path):
    print("📦 处理 smali → dex → jar")
    temp_dex = smali_dir.parent / "recompiled.dex"

    run_cmd(["java", "-jar", str(TOOLS["smali"]), "a", str(smali_dir), "-o", str(temp_dex)])
    run_cmd([str(TOOLS["dex2jar"]), str(temp_dex), "-o", str(output_jar)])
    temp_dex.unlink(missing_ok=True)
    print(f"✅ 输出 jar 文件: {output_jar}")

def main():
    if len(sys.argv) < 3:
        print("用法：")
        print("  python jar2smali.py jar2smali mylib.jar [./output/]")
        print("  python jar2smali.py smali2jar ./mylib_smali [./output/mylib_new.jar]")
        sys.exit(1)

    check_tools()

    mode = sys.argv[1]
    if mode == "jar2smali":
        jar_path = Path(sys.argv[2])
        if not jar_path.exists():
            print(f"[❌] jar 文件不存在: {jar_path}")
            sys.exit(1)

        if len(sys.argv) >= 4:
            out_dir = Path(sys.argv[3])
        else:
            out_dir = jar_path.parent / f"{jar_path.stem}_smali"

        jar_to_smali(jar_path, out_dir)

    elif mode == "smali2jar":
        smali_dir = Path(sys.argv[2])
        if not smali_dir.exists():
            print(f"[❌] smali 目录不存在: {smali_dir}")
            sys.exit(1)

        if len(sys.argv) >= 4:
            out_jar = Path(sys.argv[3])
        else:
            timestamp = datetime.now().strftime("%Y%m%d%H%M")
            out_jar = smali_dir.parent / f"{smali_dir.name.replace('_smali', '')}-{timestamp}.jar"

        smali_to_jar(smali_dir, out_jar)

    else:
        print(f"[❌] 不支持的模式: {mode}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```


开源地址：

- [https://github.com/CYRUS-STUDIO/aarkit](https://github.com/CYRUS-STUDIO/aarkit)

- [https://github.com/CYRUS-STUDIO/dex2jar](https://github.com/CYRUS-STUDIO/dex2jar)

- [https://github.com/CYRUS-STUDIO/dex2smali](https://github.com/CYRUS-STUDIO/dex2smali)





