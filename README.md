# AI API Documentation Generator

智能 API 文档生成器，自动扫描 REST API 代码生成 OpenAPI 文档。

## 功能特性

- 🌐 支持多种框架 (Flask/FastAPI/Express)
- 📄 自动检测接口、参数、返回值
- 📋 生成标准 OpenAPI 3.0 文档
- 🎨 输出 JSON 格式文档
- 🔧 支持 Swagger UI 集成

## 安装

```bash
pip install -r requirements.txt
```

## 使用方法

```bash
# 从 Python API 生成文档
python main.py api.py

# 从 JavaScript API 生成文档
python main.py app.js
```

## 示例

```python
# app.py
from flask import Flask
app = Flask(__name__)

@app.route('/users', methods=['GET'])
def get_users():
    return {'users': []}

@app.route('/users', methods=['POST'])
def create_user():
    return {'message': 'created'}, 201
```

```bash
python main.py app.py
```

## 输出格式

生成的 OpenAPI 文档包含：
- paths - API 端点路径
- methods - HTTP 方法
- parameters - 参数定义
- responses - 响应定义
- components - 组件 schemas

## 使用 Swagger UI

生成的 JSON 文件可以直接在 Swagger Editor 中使用：
https://editor.swagger.io/

## 作者

- 邮箱: 196408245@qq.com
