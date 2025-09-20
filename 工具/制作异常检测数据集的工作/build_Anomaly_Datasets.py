# build_anomaly_dataset_recursive.py
import random
import shutil
from pathlib import Path
from typing import Dict, List, Set

# ============== 可按需修改的参数 ==============
BASE_DIR = Path("D:\My_job\Jack\Y1\datasets\collect_data_0826")   # 根目录：下含 2_cut(图片) 和 3_anno(标签)
IMG_DIR  = BASE_DIR / "2_cut"
LBL_DIR  = BASE_DIR / "3_anno"

# OUT_BASE    = Path("D:\My_job\Jack\Y1\datasets/collect_data_0826/anomaly_data")
OUT_BASE    = Path("anomaly_data")
TRAIN_GOOD  = OUT_BASE / "train" / "good"
TEST_GOOD   = OUT_BASE / "test" / "good"
TEST_BAD    = OUT_BASE / "test" / "bad"

IMG_EXTS = [".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp", ".JPG", ".PNG"]
RANDOM_SEED = 20240826
TEST_GOOD_RATIO = 0.20  # 20%
# ===========================================

def ensure_dirs():
    for d in [TRAIN_GOOD, TEST_GOOD, TEST_BAD]:
        d.mkdir(parents=True, exist_ok=True)

def read_label_classes(label_path: Path) -> Set[int]:
    """读取 YOLO txt，返回类别集合；忽略空行/注释/异常行。"""
    classes: Set[int] = set()
    if not label_path.exists():
        return classes
    # 对编码更宽容一些
    with label_path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if not parts:
                continue
            try:
                cls_id = int(float(parts[0]))
                classes.add(cls_id)
            except Exception:
                # 跳过格式异常行
                continue
    return classes

def unique_dest(dest_dir: Path, filename: str) -> Path:
    """在目标目录内生成不重名的文件路径（若重名则追加 _1, _2, ...）。"""
    dest = dest_dir / filename
    if not dest.exists():
        return dest
    stem = dest.stem
    suffix = dest.suffix
    i = 1
    while True:
        alt = dest_dir / f"{stem}_{i}{suffix}"
        if not alt.exists():
            return alt
        i += 1

def build_image_index() -> Dict[str, List[Path]]:
    """递归索引图片：stem(不含后缀, 原样大小写) -> [图片路径列表]"""
    index: Dict[str, List[Path]] = {}
    for ext in IMG_EXTS:
        for img in IMG_DIR.rglob(f"*{ext}"):
            index.setdefault(img.stem, []).append(img)
    return index

from typing import Optional

def find_image_for_label(lbl_path: Path, image_index: Dict[str, List[Path]]) -> Optional[Path]:
    """
    优先按相对路径匹配：
      3_anno/subdir/a.txt -> 2_cut/subdir/a.(jpg/png/...)
    若未找到，再按 stem 在索引里查找；若多候选，取第一个并给出提示。
    """
    rel = lbl_path.relative_to(LBL_DIR)          # sub/dir/a.txt
    rel_no_ext = rel.with_suffix("")             # sub/dir/a
    # 1) 相对路径匹配
    for ext in IMG_EXTS:
        candidate = (IMG_DIR / rel_no_ext).with_suffix(ext)
        if candidate.exists():
            return candidate

    # 2) 按 stem 匹配
    stem = lbl_path.stem
    cand_list = image_index.get(stem, [])
    if not cand_list:
        return None
    if len(cand_list) > 1:
        print(f"[提示] 按 stem='{stem}' 找到多个候选，使用第一个：{cand_list[0]}")
    return cand_list[0]

def main():
    random.seed(RANDOM_SEED)
    ensure_dirs()

    if not LBL_DIR.exists():
        raise FileNotFoundError(f"标签目录不存在：{LBL_DIR}")
    if not IMG_DIR.exists():
        raise FileNotFoundError(f"图片目录不存在：{IMG_DIR}")

    # 建立图片索引（递归）
    image_index = build_image_index()

    # 统计容器
    label_with_zero_relpaths: List[str] = []  # 含类别0的标签 相对路径（相对 3_anno）
    bad_images: List[Path] = []               # test/bad 的图片源路径
    good_candidates: List[Path] = []          # 文件名含 _0_Y / _0_U 的图片源路径

    # 递归遍历所有标签
    label_files = sorted(LBL_DIR.rglob("*.txt"))
    for lbl in label_files:
        classes = read_label_classes(lbl)

        # ① 含 0 的标签：收集相对路径打印
        if 0 in classes:
            label_with_zero_relpaths.append(str(lbl.relative_to(LBL_DIR)))

        # ② “包含类别但不含0”的样本 → bad（额外保存一份）
        if classes and (0 not in classes):
            img_path = find_image_for_label(lbl, image_index)
            if img_path is not None and img_path.exists():
                bad_images.append(img_path)
            else:
                print(f"[警告] 找不到与标签匹配的图片：{lbl}")

    # ③ 从图片树递归收集文件名含 _0_Y / _0_U 的候选
    for ext in IMG_EXTS:
        for img in IMG_DIR.rglob(f"*{ext}"):
            name = img.name
            if "_0_" in name or "_0_" in name:
                good_candidates.append(img)

    # 去重（以真实路径）
    bad_images = sorted(set(map(lambda p: p.resolve(), bad_images)))
    good_candidates = sorted(set(map(lambda p: p.resolve(), good_candidates)))

    # === 执行拷贝 ===
    # ② 拷贝到 test/bad（额外保存一份）
    bad_copied = 0
    for src in bad_images:
        dst = unique_dest(TEST_BAD, src.name)
        shutil.copy2(src, dst)
        bad_copied += 1

    # ③ 先把全部 good 候选拷到 train/good
    train_good_copied_paths: List[Path] = []
    for src in good_candidates:
        dst = unique_dest(TRAIN_GOOD, src.name)
        shutil.copy2(src, dst)
        train_good_copied_paths.append(dst)

    # ③ 再随机抽取 20%，**从 train/good 移动**到 test/good（不再复制，避免重合）
    n = len(train_good_copied_paths)
    k = int(round(n * TEST_GOOD_RATIO))
    test_subset = random.sample(train_good_copied_paths, k) if k > 0 else []
    moved_to_test = 0
    for src_in_train in test_subset:
        # 目标文件名仍用原名，若 test/good 已有同名则添加后缀
        dst = unique_dest(TEST_GOOD, src_in_train.name)
        shutil.move(str(src_in_train), str(dst))
        moved_to_test += 1

    # 打印结果
    print("\n===== 含类别 0 的标签（相对 3_anno/ 的路径）=====")
    for rel in sorted(label_with_zero_relpaths):
        print(rel)

    print("\n===== 处理汇总 =====")
    print(f"递归标签总数：{len(label_files)}")
    print(f"含类别 0 的标签数：{len(label_with_zero_relpaths)}")
    # for i in range(len(label_with_zero_relpaths)):
    #     print(f"包含类别“0”的数据有：{label_with_zero_relpaths[i]}")
    print(f"异常样本（test/bad）拷贝数量：{bad_copied}")
    print(f"good 候选（文件名含 _0_Y/_0_U）数量：{len(good_candidates)}")
    print(f"已拷贝至 train/good 数量：{len(train_good_copied_paths)}")
    print(f"从 train/good 随机移动到 test/good 的比例：{TEST_GOOD_RATIO*100:.0f}% -> 数量：{moved_to_test}")
    print(f"输出根目录：{OUT_BASE.resolve()}")

if __name__ == "__main__":
    main()
