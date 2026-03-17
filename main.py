#!/usr/bin/env python3
"""
AI API Documentation Generator - 智能 API 文档生成器
自动扫描 REST API 代码生成 OpenAPI 文档
"""

import ast
import os
import sys
import json
from typing import List, Dict, Any, Optional
from colorama import init, Fore, Style

init(autoreset=True)


class APIDocGenerator:
    """API 文档生成器"""
    
    def __init__(self):
        self.endpoints = []
        self.title = "API Documentation"
        self.version = "1.0.0"
    
    def generate_openapi(self, filepath: str) -> Dict[str, Any]:
        """生成 OpenAPI 文档"""
        if not os.path.exists(filepath):
            print(f"{Fore.RED}错误: 文件不存在 - {filepath}")
            return {}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
            
            ext = os.path.splitext(filepath)[1].lower()
            
            print(f"{Fore.CYAN}正在分析: {filepath}")
            
            if ext == '.py':
                self._analyze_python_api(code)
            elif ext == '.js' or ext == '.ts':
                self._analyze_js_api(code)
            
            return self._build_openapi()
            
        except Exception as e:
            print(f"{Fore.RED}生成失败: {str(e)}")
            return {}
    
    def _analyze_python_api(self, code: str):
        """分析 Python API 代码"""
        try:
            tree = ast.parse(code)
            
            # 检测框架
            framework = self._detect_framework(code)
            print(f"{Fore.GREEN}检测到框架: {framework}")
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_name = node.name.lower()
                    
                    # 检测路由装饰器
                    endpoint = self._extract_python_endpoint(node, framework)
                    
                    if endpoint:
                        self.endpoints.append(endpoint)
                        
        except SyntaxError as e:
            print(f"{Fore.RED}语法错误: {e}")
    
    def _detect_framework(self, code: str) -> str:
        """检测框架"""
        code_lower = code.lower()
        
        if 'fastapi' in code_lower or 'from fastapi' in code_lower:
            return 'FastAPI'
        elif 'flask' in code_lower or 'from flask' in code_lower:
            return 'Flask'
        elif 'django' in code_lower or 'from django' in code_lower:
            return 'Django'
        
        return 'Flask'  # 默认 Flask
    
    def _extract_python_endpoint(self, func: ast.FunctionDef, framework: str) -> Optional[Dict]:
        """提取 Python 端点信息"""
        endpoint = {
            'path': '/',
            'method': 'GET',
            'operationId': func.name,
            'summary': func.name.replace('_', ' ').title(),
            'parameters': [],
            'responses': {}
        }
        
        # 分析装饰器
        for decorator in func.decorator_list:
            if isinstance(decorator, ast.Call):
                decorator_name = self._get_decorator_name(decorator)
                
                if decorator_name in ['app.get', 'route', 'router.get']:
                    endpoint['method'] = 'GET'
                    endpoint['path'] = self._extract_path(decorator)
                elif decorator_name in ['app.post', 'router.post']:
                    endpoint['method'] = 'POST'
                    endpoint['path'] = self._extract_path(decorator)
                elif decorator_name in ['app.put', 'router.put']:
                    endpoint['method'] = 'PUT'
                    endpoint['path'] = self._extract_path(decorator)
                elif decorator_name in ['app.delete', 'router.delete']:
                    endpoint['method'] = 'DELETE'
                    endpoint['path'] = self._extract_path(decorator)
                elif decorator_name in ['app.patch', 'router.patch']:
                    endpoint['method'] = 'PATCH'
                    endpoint['path'] = self._extract_path(decorator)
        
        # 提取参数
        args = func.args
        for arg in args.args:
            endpoint['parameters'].append({
                'name': arg.arg,
                'in': 'query',
                'required': False,
                'schema': {'type': 'string'}
            })
        
        # 添加默认响应
        endpoint['responses'] = {
            '200': {
                'description': 'Successful response',
                'content': {
                    'application/json': {
                        'schema': {'type': 'object'}
                    }
                }
            }
        }
        
        return endpoint if endpoint['path'] != '/' or endpoint['method'] != 'GET' else None
    
    def _get_decorator_name(self, decorator: ast.Call) -> str:
        """获取装饰器名称"""
        if isinstance(decorator.func, ast.Attribute):
            attr = decorator.func.attr
            if isinstance(decorator.func.value, ast.Attribute):
                value = decorator.func.value.attr
                return f"{value}.{attr}"
            elif isinstance(decorator.func.value, ast.Name):
                value = decorator.func.value.id
                return f"{value}.{attr}"
        elif isinstance(decorator.func, ast.Name):
            return decorator.func.id
        return ''
    
    def _extract_path(self, decorator: ast.Call) -> str:
        """提取路由路径"""
        if decorator.args and isinstance(decorator.args[0], ast.Constant):
            return str(decorator.args[0].value)
        return '/'
    
    def _analyze_js_api(self, code: str):
        """分析 JavaScript API 代码"""
        import re
        
        # 匹配 Express 路由
        patterns = [
            (r"app\.(get|post|put|delete|patch)\(['\"]([^'\"]+)['\"]", 'Express'),
            (r"router\.(get|post|put|delete|patch)\(['\"]([^'\"]+)['\"]", 'Express'),
            (r"@([a-z]+)\(['\"]([^'\"]+)['\"]", 'Fastify'),
        ]
        
        for pattern, framework in patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                method = match.group(1).upper()
                path = match.group(2)
                
                self.endpoints.append({
                    'path': path,
                    'method': method,
                    'operationId': f"{method.lower()}_{path.replace('/', '_')}",
                    'summary': f"{method} {path}",
                    'parameters': [],
                    'responses': {
                        '200': {'description': 'Successful response'}
                    }
                })
    
    def _build_openapi(self) -> Dict[str, Any]:
        """构建 OpenAPI 文档"""
        paths = {}
        
        for endpoint in self.endpoints:
            path = endpoint['path']
            method = endpoint['method'].lower()
            
            if path not in paths:
                paths[path] = {}
            
            paths[path][method] = {
                'summary': endpoint.get('summary', ''),
                'operationId': endpoint.get('operationId', ''),
                'parameters': endpoint.get('parameters', []),
                'responses': endpoint.get('responses', {})
            }
        
        openapi = {
            'openapi': '3.0.0',
            'info': {
                'title': self.title,
                'version': self.version,
                'description': '自动生成的 API 文档'
            },
            'paths': paths,
            'components': {
                'schemas': {}
            }
        }
        
        return openapi


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print(f"{Fore.YELLOW}使用方法: python main.py <API文件>")
        print(f"示例: python main.py api.py")
        print(f"示例: python main.py app.js")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    generator = APIDocGenerator()
    openapi = generator.generate_openapi(filepath)
    
    if openapi:
        # 输出 JSON
        json_str = json.dumps(openapi, indent=2, ensure_ascii=False)
        
        print(f"\n{Fore.GREEN}生成的 OpenAPI 文档:\n")
        print(json_str)
        
        # 保存文件
        output_file = 'openapi.json'
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(json_str)
            print(f"\n{Fore.GREEN}✓ 文档已保存: {output_file}")
        except Exception as e:
            print(f"{Fore.YELLOW}保存失败: {str(e)}")


if __name__ == '__main__':
    main()
