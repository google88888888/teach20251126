from docx import Document
import json

def split_qname(tag):
    if not tag:
        return None, None
    if tag[0] == '{':
        uri, local = tag[1:].split('}', 1)
        return uri, local
    return None, tag

def element_to_dict(el):
    uri, local = split_qname(el.tag)
    node = {
        "tag": el.tag,                 # 完整 QName 字符串，例如 "{http://...}vMerge"
        "namespace": uri,              # 命名空间 URI 或 None
        "local": local,                # 本地名，例如 "vMerge"
        "attrib": {},                  # 属性字典（QName: value）
        "text": (el.text or "").strip(),
        "children": []
    }
    for k, v in el.attrib.items():
        node["attrib"][k] = v
    for child in el:
        node["children"].append(element_to_dict(child))
    return node

if __name__ == "__main__":
    doc = Document("./3、佑荣科技2025年财审报告附注.docx")   # 改为你的文件名
    out = []
    for i, child in enumerate(doc.element.body):
        out.append({
            "index": i,
            "node": element_to_dict(child)
        })
    with open("wml_tags.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("已写入 wml_tags.json")