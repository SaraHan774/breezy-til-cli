#!/usr/bin/env python3
"""
스트릭 분석 모듈
TIL 파일들을 분석하여 학습 스트릭과 통계를 계산합니다.
"""

import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class StreakAnalyzer:
    """TIL 파일들을 분석하여 학습 스트릭과 통계를 계산하는 클래스"""
    
    def __init__(self, base_dir: str):
        """
        스트릭 분석기 초기화
        
        Args:
            base_dir: TIL 파일들이 저장된 기본 디렉토리
        """
        self.base_dir = base_dir
        self.learning_dates = set()
        self.streak_data = {}
        
    def _extract_date_from_filename(self, filename: str) -> Optional[datetime]:
        """
        파일명에서 날짜를 추출합니다.
        
        Args:
            filename: 파일명 (예: 2025-07-29.md)
            
        Returns:
            datetime 객체 또는 None
        """
        # YYYY-MM-DD.md 형식 매칭
        date_pattern = r'(\d{4}-\d{2}-\d{2})\.md$'
        match = re.search(date_pattern, filename)
        
        if match:
            try:
                return datetime.strptime(match.group(1), '%Y-%m-%d')
            except ValueError:
                return None
        return None
    
    def _scan_til_files(self) -> None:
        """
        TIL 디렉토리를 스캔하여 학습 날짜들을 수집합니다.
        """
        self.learning_dates.clear()
        
        # 모든 하위 디렉토리를 재귀적으로 스캔
        for root, dirs, files in os.walk(self.base_dir):
            # .git, venv 등 제외
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'venv']
            
            for file in files:
                if file.endswith('.md'):
                    date = self._extract_date_from_filename(file)
                    if date:
                        self.learning_dates.add(date.date())
    
    def _calculate_streaks(self) -> None:
        """
        연속 학습일을 계산합니다.
        """
        if not self.learning_dates:
            self.streak_data = {
                'current_streak': 0,
                'max_streak': 0,
                'max_streak_start': None,
                'max_streak_end': None,
                'total_learning_days': 0,
                'first_learning_date': None,
                'last_learning_date': None,
            }
            return
            
        # 날짜들을 정렬
        sorted_dates = sorted(self.learning_dates)
        
        current_streak = 0
        max_streak = 0
        max_streak_start = None
        max_streak_end = None
        
        # 현재 스트릭 계산
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        # 최근 날짜부터 역순으로 확인
        for i in range(len(sorted_dates) - 1, -1, -1):
            date = sorted_dates[i]
            
            if date == today:
                current_streak = 1
                break
            elif date == yesterday:
                current_streak = 1
                # 어제부터 연속 확인
                for j in range(i - 1, -1, -1):
                    expected_date = date - timedelta(days=current_streak)
                    if sorted_dates[j] == expected_date:
                        current_streak += 1
                        date = expected_date
                    else:
                        break
                break
            elif date < yesterday:
                break
        
        # 최대 스트릭 계산
        temp_streak = 1
        temp_start = sorted_dates[0]
        
        for i in range(1, len(sorted_dates)):
            current_date = sorted_dates[i]
            previous_date = sorted_dates[i - 1]
            
            # 연속된 날짜인지 확인
            if (current_date - previous_date).days == 1:
                temp_streak += 1
            else:
                # 스트릭이 끊어짐
                if temp_streak > max_streak:
                    max_streak = temp_streak
                    max_streak_start = temp_start
                    max_streak_end = previous_date
                
                temp_streak = 1
                temp_start = current_date
        
        # 마지막 스트릭 확인
        if temp_streak > max_streak:
            max_streak = temp_streak
            max_streak_start = temp_start
            max_streak_end = sorted_dates[-1]
        
        self.streak_data = {
            'current_streak': current_streak,
            'max_streak': max_streak,
            'max_streak_start': max_streak_start,
            'max_streak_end': max_streak_end,
            'total_learning_days': len(self.learning_dates),
            'first_learning_date': min(self.learning_dates) if self.learning_dates else None,
            'last_learning_date': max(self.learning_dates) if self.learning_dates else None,
        }
    
    def _calculate_weekly_pattern(self) -> Dict[str, int]:
        """
        요일별 학습 패턴을 계산합니다.
        
        Returns:
            요일별 학습 횟수 딕셔너리
        """
        weekly_pattern = defaultdict(int)
        
        for date in self.learning_dates:
            weekday = date.strftime('%A')  # Monday, Tuesday, ...
            weekly_pattern[weekday] += 1
        
        return dict(weekly_pattern)
    
    def analyze(self) -> Dict:
        """
        TIL 파일들을 분석하여 스트릭과 통계를 계산합니다.
        
        Returns:
            분석 결과 딕셔너리
        """
        self._scan_til_files()
        self._calculate_streaks()
        
        # 학습 기간 계산
        if self.streak_data['first_learning_date'] and self.streak_data['last_learning_date']:
            total_days = (self.streak_data['last_learning_date'] - self.streak_data['first_learning_date']).days + 1
            learning_rate = (self.streak_data['total_learning_days'] / total_days) * 100 if total_days > 0 else 0
        else:
            total_days = 0
            learning_rate = 0
        
        return {
            **self.streak_data,
            'total_days': total_days,
            'learning_rate': round(learning_rate, 1),
            'weekly_pattern': self._calculate_weekly_pattern(),
            'learning_dates': sorted(self.learning_dates),
        }


def format_streak_output(analysis_result: Dict) -> str:
    """
    분석 결과를 사용자 친화적인 텍스트로 포맷팅합니다.
    
    Args:
        analysis_result: StreakAnalyzer.analyze()의 결과
        
    Returns:
        포맷팅된 문자열
    """
    if not analysis_result['learning_dates']:
        return "📚 아직 TIL 파일이 없습니다. 첫 번째 TIL을 작성해보세요!"
    
    output = []
    
    # 기본 스트릭 정보
    current_streak = analysis_result['current_streak']
    max_streak = analysis_result['max_streak']
    
    if current_streak > 0:
        output.append(f"🔥 현재 스트릭: {current_streak}일 연속")
    else:
        output.append("💤 현재 스트릭: 0일 (오늘 학습하지 않았습니다)")
    
    output.append(f"🏆 최고 기록: {max_streak}일")
    
    if analysis_result['max_streak_start'] and analysis_result['max_streak_end']:
        start_date = analysis_result['max_streak_start'].strftime('%Y-%m-%d')
        end_date = analysis_result['max_streak_end'].strftime('%Y-%m-%d')
        output.append(f"   📅 기간: {start_date} ~ {end_date}")
    
    # 전체 통계
    total_days = analysis_result['total_learning_days']
    learning_rate = analysis_result['learning_rate']
    
    output.append(f"📊 총 학습일: {total_days}일")
    output.append(f"📈 학습률: {learning_rate}%")
    
    # 첫 학습일과 마지막 학습일
    if analysis_result['first_learning_date']:
        first_date = analysis_result['first_learning_date'].strftime('%Y-%m-%d')
        output.append(f"🎯 첫 학습일: {first_date}")
    
    if analysis_result['last_learning_date']:
        last_date = analysis_result['last_learning_date'].strftime('%Y-%m-%d')
        output.append(f"📝 마지막 학습일: {last_date}")
    
    return "\n".join(output)


def get_streak_info(base_dir: str) -> str:
    """
    TIL 디렉토리의 스트릭 정보를 반환합니다.
    
    Args:
        base_dir: TIL 파일들이 저장된 기본 디렉토리
        
    Returns:
        포맷팅된 스트릭 정보 문자열
    """
    analyzer = StreakAnalyzer(base_dir)
    result = analyzer.analyze()
    return format_streak_output(result)


def get_streak_info_with_visualization(base_dir: str, show_grass: bool = True, show_weekly: bool = True) -> str:
    """
    TIL 디렉토리의 스트릭 정보를 시각화와 함께 반환합니다.
    
    Args:
        base_dir: TIL 파일들이 저장된 기본 디렉토리
        show_grass: 잔디 표시 여부
        show_weekly: 주간 패턴 표시 여부
        
    Returns:
        포맷팅된 스트릭 정보 문자열 (시각화 포함)
    """
    analyzer = StreakAnalyzer(base_dir)
    result = analyzer.analyze()
    
    # 시각화 모듈 import
    try:
        from til.core.visualizer import format_streak_with_visualization
        return format_streak_with_visualization(result, show_grass, show_weekly)
    except ImportError:
        # 시각화 모듈이 없으면 기본 출력
        return format_streak_output(result) 