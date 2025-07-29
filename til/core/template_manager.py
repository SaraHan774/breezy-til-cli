#!/usr/bin/env python3
"""
템플릿 관리 모듈
TIL 파일 생성을 위한 다양한 템플릿을 관리합니다.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional


class TemplateManager:
    """TIL 템플릿 관리 클래스"""
    
    def __init__(self, base_dir: str):
        """
        템플릿 관리자 초기화
        
        Args:
            base_dir: TIL 기본 디렉토리
        """
        self.base_dir = base_dir
        self.templates_dir = os.path.join(base_dir, ".templates")
        self.templates_config = os.path.join(self.templates_dir, "templates.json")
        self._ensure_templates_dir()
        self._load_default_templates()
    
    def _ensure_templates_dir(self):
        """템플릿 디렉토리 생성"""
        os.makedirs(self.templates_dir, exist_ok=True)
    
    def _load_default_templates(self):
        """기본 템플릿들을 생성합니다."""
        if not os.path.exists(self.templates_config):
            self._create_default_templates()
    
    def _create_default_templates(self):
        """기본 템플릿들을 생성합니다."""
        default_templates = {
            "default": {
                "name": "기본 템플릿",
                "description": "일반적인 TIL 템플릿",
                "content": """# TIL - {date}

## 📚 오늘 학습한 내용

### 🎯 학습 목표
- 

### 📖 학습 내용
- 

### 💡 핵심 포인트
- 

### 🔗 참고 자료
- 

### 🤔 추가로 학습할 내용
- 

### 📝 메모
- 
"""
            },
            "project": {
                "name": "프로젝트 리뷰 템플릿",
                "description": "프로젝트 작업 내용을 정리하는 템플릿",
                "content": """# TIL - {date} - {category}

## 🚀 프로젝트 개요
- **프로젝트명**: 
- **작업 기간**: 
- **목표**: 

## 📋 오늘 작업 내용

### ✅ 완료한 작업
- 

### 🔄 진행 중인 작업
- 

### ❌ 문제점 및 이슈
- 

## 🛠 사용한 기술/도구
- 

## 📚 학습한 내용
- 

## 🎯 다음 단계
- 

## 💭 회고
- 
"""
            },
            "study": {
                "name": "학습 노트 템플릿",
                "description": "체계적인 학습 내용을 정리하는 템플릿",
                "content": """# TIL - {date} - {category}

## 📚 학습 주제
- **주제**: 
- **학습 시간**: 
- **학습 방식**: 

## 🎯 학습 목표
- 

## 📖 학습 내용

### 1. 기본 개념
- 

### 2. 핵심 내용
- 

### 3. 실습/예제
- 

## 💡 핵심 포인트
- 

## 🔗 참고 자료
- 

## ❓ 궁금한 점
- 

## 📝 추가 학습 계획
- 

## 💭 학습 후기
- 
"""
            },
            "bugfix": {
                "name": "버그 수정 템플릿",
                "description": "버그 수정 과정을 기록하는 템플릿",
                "content": """# TIL - {date} - {category}

## 🐛 버그 정보
- **버그 설명**: 
- **발생 환경**: 
- **재현 방법**: 

## 🔍 디버깅 과정

### 1. 문제 분석
- 

### 2. 원인 파악
- 

### 3. 해결 방법
- 

## ✅ 해결 결과
- 

## 🛠 사용한 도구/기법
- 

## 📚 학습한 내용
- 

## 💡 향후 예방책
- 

## 🔗 참고 자료
- 
"""
            },
            "minimal": {
                "name": "간단 템플릿",
                "description": "최소한의 내용만 포함하는 간단한 템플릿",
                "content": """# TIL - {date}

## 📝 오늘 학습한 내용
- 

## 💡 핵심 포인트
- 

## 🔗 참고 자료
- 
"""
            }
        }
        
        # 템플릿 파일들 생성
        for template_id, template_data in default_templates.items():
            template_file = os.path.join(self.templates_dir, f"{template_id}.md")
            with open(template_file, "w", encoding="utf-8") as f:
                f.write(template_data["content"])
        
        # 템플릿 설정 파일 생성
        with open(self.templates_config, "w", encoding="utf-8") as f:
            json.dump(default_templates, f, ensure_ascii=False, indent=2)
    
    def get_template_content(self, template_id: str, date: str, category: str) -> str:
        """
        템플릿 내용을 가져와서 변수를 치환합니다.
        
        Args:
            template_id: 템플릿 ID
            date: 날짜 문자열
            category: 카테고리
            
        Returns:
            치환된 템플릿 내용
        """
        template_file = os.path.join(self.templates_dir, f"{template_id}.md")
        
        if not os.path.exists(template_file):
            # 기본 템플릿 사용
            template_file = os.path.join(self.templates_dir, "default.md")
        
        with open(template_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 변수 치환
        content = content.replace("{date}", date)
        content = content.replace("{category}", category)
        
        return content
    
    def list_templates(self) -> Dict[str, Dict]:
        """
        사용 가능한 템플릿 목록을 반환합니다.
        
        Returns:
            템플릿 정보 딕셔너리
        """
        with open(self.templates_config, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def create_template(self, template_id: str, name: str, description: str, content: str):
        """
        새로운 템플릿을 생성합니다.
        
        Args:
            template_id: 템플릿 ID
            name: 템플릿 이름
            description: 템플릿 설명
            content: 템플릿 내용
        """
        # 템플릿 파일 생성
        template_file = os.path.join(self.templates_dir, f"{template_id}.md")
        with open(template_file, "w", encoding="utf-8") as f:
            f.write(content)
        
        # 설정 파일 업데이트
        with open(self.templates_config, "r", encoding="utf-8") as f:
            templates = json.load(f)
        
        templates[template_id] = {
            "name": name,
            "description": description,
            "content": content
        }
        
        with open(self.templates_config, "w", encoding="utf-8") as f:
            json.dump(templates, f, ensure_ascii=False, indent=2)
    
    def delete_template(self, template_id: str):
        """
        템플릿을 삭제합니다.
        
        Args:
            template_id: 삭제할 템플릿 ID
        """
        # 기본 템플릿은 삭제 불가
        if template_id in ["default", "minimal"]:
            raise ValueError("기본 템플릿은 삭제할 수 없습니다.")
        
        # 템플릿 파일 삭제
        template_file = os.path.join(self.templates_dir, f"{template_id}.md")
        if os.path.exists(template_file):
            os.remove(template_file)
        
        # 설정 파일에서 제거
        with open(self.templates_config, "r", encoding="utf-8") as f:
            templates = json.load(f)
        
        if template_id in templates:
            del templates[template_id]
            
            with open(self.templates_config, "w", encoding="utf-8") as f:
                json.dump(templates, f, ensure_ascii=False, indent=2)


def format_template_list(templates: Dict[str, Dict]) -> str:
    """
    템플릿 목록을 사용자 친화적으로 포맷팅합니다.
    
    Args:
        templates: 템플릿 정보 딕셔너리
        
    Returns:
        포맷팅된 템플릿 목록 문자열
    """
    output = ["📋 사용 가능한 템플릿:"]
    
    for template_id, template_info in templates.items():
        name = template_info["name"]
        description = template_info["description"]
        output.append(f"  {template_id:>12} - {name}")
        output.append(f"                {description}")
        output.append("")
    
    return "\n".join(output) 