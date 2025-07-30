#!/usr/bin/env python3
"""
시각화 모듈
스트릭 정보를 ASCII Art와 색상으로 시각화합니다.
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional
from collections import defaultdict


class ColorSupport:
    """터미널 색상 지원 클래스"""
    
    # ANSI 색상 코드
    COLORS = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'gray': '\033[90m',
        'bold': '\033[1m',
        'reset': '\033[0m',
    }
    
    @classmethod
    def colorize(cls, text: str, color: str) -> str:
        """텍스트에 색상을 적용합니다."""
        if color in cls.COLORS:
            return f"{cls.COLORS[color]}{text}{cls.COLORS['reset']}"
        return text
    
    @classmethod
    def bold(cls, text: str) -> str:
        """텍스트를 굵게 만듭니다."""
        return cls.colorize(text, 'bold')


class GrassVisualizer:
    """GitHub 스타일 잔디 시각화 클래스"""
    
    def __init__(self, learning_dates: Set[datetime.date]):
        self.learning_dates = learning_dates
        self.today = datetime.now().date()
        
    def _get_grass_data(self, weeks: int = 52) -> List[List[Optional[datetime.date]]]:
        """
        잔디 데이터를 생성합니다.
        
        Args:
            weeks: 표시할 주 수 (기본값: 52주 = 1년)
            
        Returns:
            2차원 배열 (주 x 요일)
        """
        grass_data = []
        end_date = self.today
        start_date = end_date - timedelta(weeks=weeks)
        
        current_date = start_date
        
        # 주의 시작을 월요일로 맞춤
        while current_date.weekday() != 0:  # 0 = 월요일
            current_date += timedelta(days=1)
        
        for week in range(weeks):
            week_data = []
            for day in range(7):  # 월~일
                date = current_date + timedelta(days=day)
                if date in self.learning_dates:
                    week_data.append(date)
                else:
                    week_data.append(None)
            grass_data.append(week_data)
            current_date += timedelta(weeks=1)
        
        return grass_data
    
    def generate_grass(self, weeks: int = 52, show_labels: bool = True) -> str:
        """
        GitHub 스타일 잔디를 생성합니다.
        
        Args:
            weeks: 표시할 주 수
            show_labels: 요일/월 라벨 표시 여부
            
        Returns:
            ASCII Art 잔디 문자열
        """
        grass_data = self._get_grass_data(weeks)
        
        output = []
        
        if show_labels:
            # 요일 라벨
            weekday_labels = ['월', '화', '수', '목', '금', '토', '일']
            label_line = "    " + " ".join(weekday_labels)
            output.append(label_line)
            output.append("")
        
        # 잔디 생성
        for week_idx, week in enumerate(grass_data):
            week_line = []
            
            if show_labels and week_idx % 4 == 0:  # 4주마다 월 라벨
                month = (self.today - timedelta(weeks=weeks-week_idx)).strftime('%m월')
                # 월 라벨과 빈 줄 추가
                output.append(f"{month:>4}")
                output.append("")  # 빈 줄 추가
                continue  # 이 주는 건너뛰고 다음 주부터 잔디 표시
            
            # 요일별 잔디 추가
            for day in week:
                if day is None:
                    week_line.append("⚪")  # 학습 없음
                else:
                    week_line.append(ColorSupport.colorize("🟢", "green"))  # 학습한 날
            
            # 잔디 줄 추가
            output.append("    " + " ".join(week_line))
        
        # 범례 추가
        legend = [
            "",
            "📅 학습 잔디 범례:",
            "🟢 학습한 날",
            "⚪ 학습 없음"
        ]
        output.extend(legend)
        
        return "\n".join(output)


class WeeklyPatternVisualizer:
    """주간 패턴 시각화 클래스"""
    
    def __init__(self, weekly_pattern: Dict[str, int]):
        self.weekly_pattern = weekly_pattern
        self.weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        self.weekday_korean = {
            'Monday': '월요일',
            'Tuesday': '화요일', 
            'Wednesday': '수요일',
            'Thursday': '목요일',
            'Friday': '금요일',
            'Saturday': '토요일',
            'Sunday': '일요일'
        }
    
    def generate_weekly_chart(self, max_bar_length: int = 20) -> str:
        """
        주간 패턴 차트를 생성합니다.
        
        Args:
            max_bar_length: 최대 바 길이
            
        Returns:
            주간 패턴 차트 문자열
        """
        if not self.weekly_pattern:
            return "📊 아직 주간 패턴 데이터가 없습니다."
        
        output = ["📊 주간 학습 패턴:"]
        
        # 최대값 찾기
        max_count = max(self.weekly_pattern.values()) if self.weekly_pattern else 1
        
        for weekday in self.weekday_order:
            count = self.weekly_pattern.get(weekday, 0)
            korean_name = self.weekday_korean.get(weekday, weekday)
            
            # 바 길이 계산
            bar_length = int((count / max_count) * max_bar_length) if max_count > 0 else 0
            bar = "█" * bar_length
            
            # 색상 적용
            if count == max_count:
                bar = ColorSupport.colorize(bar, "green")
            elif count > 0:
                bar = ColorSupport.colorize(bar, "yellow")
            
            output.append(f"  {korean_name:>4}: {bar} ({count}일)")
        
        return "\n".join(output)


class StreakVisualizer:
    """스트릭 시각화 통합 클래스"""
    
    def __init__(self, learning_dates: Set[datetime.date], analysis_result: Dict):
        self.learning_dates = learning_dates
        self.analysis_result = analysis_result
        self.grass_viz = GrassVisualizer(learning_dates)
        self.weekly_viz = WeeklyPatternVisualizer(analysis_result.get('weekly_pattern', {}))
    
    def generate_full_visualization(self, show_grass: bool = True, show_weekly: bool = True) -> str:
        """
        전체 시각화를 생성합니다.
        
        Args:
            show_grass: 잔디 표시 여부
            show_weekly: 주간 패턴 표시 여부
            
        Returns:
            전체 시각화 문자열
        """
        output = []
        
        if show_grass:
            output.append("🌱 학습 잔디:")
            output.append(self.grass_viz.generate_grass())
            output.append("")
        
        if show_weekly:
            output.append(self.weekly_viz.generate_weekly_chart())
            output.append("")
        
        return "\n".join(output)


def format_streak_with_visualization(analysis_result: Dict, show_grass: bool = True, show_weekly: bool = True) -> str:
    """
    스트릭 정보를 시각화와 함께 포맷팅합니다.
    
    Args:
        analysis_result: 분석 결과
        show_grass: 잔디 표시 여부
        show_weekly: 주간 패턴 표시 여부
        
    Returns:
        포맷팅된 문자열
    """
    if not analysis_result['learning_dates']:
        return "📚 아직 TIL 파일이 없습니다. 첫 번째 TIL을 작성해보세요!"
    
    # 기본 스트릭 정보
    output = []
    
    current_streak = analysis_result['current_streak']
    max_streak = analysis_result['max_streak']
    
    if current_streak > 0:
        output.append(ColorSupport.bold(f"🔥 현재 스트릭: {current_streak}일 연속"))
    else:
        output.append("💤 현재 스트릭: 0일 (오늘 학습하지 않았습니다)")
    
    output.append(ColorSupport.bold(f"🏆 최고 기록: {max_streak}일"))
    
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
    
    output.append("")  # 빈 줄 추가
    
    # 시각화 추가
    if show_grass or show_weekly:
        # learning_dates는 이미 datetime.date 객체들의 리스트
        learning_dates = set(analysis_result.get('learning_dates', []))
        viz = StreakVisualizer(learning_dates, analysis_result)
        output.append(viz.generate_full_visualization(show_grass, show_weekly))
    
    return "\n".join(output) 