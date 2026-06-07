"""AI-powered scheduling optimization service"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, time
from dataclasses import dataclass
import random


@dataclass
class TimeSlot:
    """Represents a time slot for scheduling"""
    start: datetime
    end: datetime
    score: float = 0.0
    reason: str = ""


class ScheduleOptimizer:
    """Optimize schedule based on user preferences and constraints"""
    
    def __init__(
        self,
        user_preferences: Optional[Dict[str, Any]] = None,
        health_data: Optional[Dict[str, Any]] = None
    ):
        self.preferences = user_preferences or {}
        self.health_data = health_data or {}
    
    def calculate_time_slot_score(
        self,
        slot: TimeSlot,
        task: Dict[str, Any]
    ) -> float:
        """Calculate how suitable a time slot is for a task"""
        score = 100.0
        
        # Time of day preferences
        hour = slot.start.hour
        
        # Peak focus time bonus
        peak_focus = self.preferences.get('peak_focus_time', 'morning')
        if peak_focus == 'morning' and 8 <= hour < 12:
            score += 30
        elif peak_focus == 'afternoon' and 13 <= hour < 17:
            score += 30
        elif peak_focus == 'evening' and 17 <= hour < 21:
            score += 30
        
        # Circadian rhythm adjustments
        wake_time = self.preferences.get('wake_time')
        if wake_time:
            # Best performance 2-4 hours after waking
            # This is simplified - real circadian analysis is more complex
            hours_awake = hour - wake_time.hour if isinstance(wake_time, time) else 0
            if 2 <= hours_awake <= 4:
                score += 20
        
        # Task difficulty and optimal time matching
        task_difficulty = task.get('difficulty_score', 0.5)
        if task_difficulty > 0.7:  # Hard tasks
            # Schedule during peak hours
            if 9 <= hour < 12 or 14 <= hour < 16:
                score += 25
        
        # Health data adjustments
        if self.health_data:
            sleep_quality = self.health_data.get('sleep_quality', 75)
            if sleep_quality < 60:
                # Tired, reduce score for mentally demanding tasks
                if task_difficulty > 0.6:
                    score -= 20
        
        # Meal time avoidance
        meal_times = self.preferences.get('meal_times', {})
        if meal_times:
            for meal, meal_time in meal_times.items():
                if isinstance(meal_time, time):
                    meal_hour = meal_time.hour
                    if abs(hour - meal_hour) < 1:
                        score -= 15
        
        # Late night penalty
        if hour >= 22 or hour < 6:
            score -= 40
        
        return max(0, score)
    
    def find_optimal_time_slots(
        self,
        task: Dict[str, Any],
        available_slots: List[TimeSlot],
        count: int = 3
    ) -> List[TimeSlot]:
        """Find the best time slots for a task"""
        
        # Score each slot
        scored_slots = []
        for slot in available_slots:
            score = self.calculate_time_slot_score(slot, task)
            slot.score = score
            slot.reason = self._generate_reason(slot, task, score)
            scored_slots.append(slot)
        
        # Sort by score and return top N
        scored_slots.sort(key=lambda x: x.score, reverse=True)
        return scored_slots[:count]
    
    def _generate_reason(
        self,
        slot: TimeSlot,
        task: Dict[str, Any],
        score: float
    ) -> str:
        """Generate human-readable reason for slot recommendation"""
        hour = slot.start.hour
        reasons = []
        
        if 9 <= hour < 12:
            reasons.append("Peak morning focus hours")
        elif 14 <= hour < 16:
            reasons.append("Post-lunch clarity window")
        
        if score > 120:
            reasons.append("Aligns with your peak performance time")
        elif score > 100:
            reasons.append("Good time based on your preferences")
        elif score < 60:
            reasons.append("Not ideal timing, but available")
        
        return " • ".join(reasons) if reasons else "Available time slot"
    
    def optimize_daily_schedule(
        self,
        tasks: List[Dict[str, Any]],
        events: List[Dict[str, Any]],
        target_date: datetime
    ) -> Dict[str, Any]:
        """Optimize an entire day's schedule"""
        
        # Find available time slots
        available_slots = self._find_available_slots(events, target_date)
        
        # Sort tasks by priority and deadline
        sorted_tasks = sorted(
            tasks,
            key=lambda t: (
                self._priority_value(t.get('priority', 'medium')),
                t.get('due_date', datetime.max.isoformat())
            ),
            reverse=True
        )
        
        scheduled_tasks = []
        
        for task in sorted_tasks:
            duration = task.get('estimated_duration', 60)
            
            # Find slots that can fit this task
            suitable_slots = [
                s for s in available_slots
                if (s.end - s.start).total_seconds() / 60 >= duration
            ]
            
            if suitable_slots:
                # Get best slot
                best_slots = self.find_optimal_time_slots(
                    task,
                    suitable_slots,
                    count=1
                )
                
                if best_slots:
                    best_slot = best_slots[0]
                    
                    # Schedule the task
                    task_end = best_slot.start + timedelta(minutes=duration)
                    scheduled_tasks.append({
                        **task,
                        'scheduled_start': best_slot.start.isoformat(),
                        'scheduled_end': task_end.isoformat(),
                        'slot_score': best_slot.score,
                        'slot_reason': best_slot.reason
                    })
                    
                    # Remove used time from available slots
                    available_slots = self._remove_used_time(
                        available_slots,
                        best_slot.start,
                        task_end
                    )
        
        unscheduled_tasks = [
            t for t in sorted_tasks
            if t.get('id') not in [st.get('id') for st in scheduled_tasks]
        ]
        
        return {
            'date': target_date.date().isoformat(),
            'scheduled_tasks': scheduled_tasks,
            'unscheduled_tasks': unscheduled_tasks,
            'optimization_score': self._calculate_schedule_score(scheduled_tasks),
            'recommendations': self._generate_recommendations(scheduled_tasks, unscheduled_tasks)
        }
    
    def _find_available_slots(
        self,
        events: List[Dict[str, Any]],
        target_date: datetime
    ) -> List[TimeSlot]:
        """Find available time slots in a day"""
        
        # Define working hours (can be customized)
        day_start = target_date.replace(hour=8, minute=0, second=0, microsecond=0)
        day_end = target_date.replace(hour=22, minute=0, second=0, microsecond=0)
        
        # Sort events by start time
        sorted_events = sorted(
            events,
            key=lambda e: e.get('start_time', day_end.isoformat())
        )
        
        available_slots = []
        current_time = day_start
        
        for event in sorted_events:
            event_start = datetime.fromisoformat(event['start_time'].replace('Z', '+00:00'))
            event_end = datetime.fromisoformat(event['end_time'].replace('Z', '+00:00'))
            
            # If there's a gap before this event
            if current_time < event_start:
                available_slots.append(TimeSlot(
                    start=current_time,
                    end=event_start
                ))
            
            current_time = max(current_time, event_end)
        
        # Add remaining time in the day
        if current_time < day_end:
            available_slots.append(TimeSlot(
                start=current_time,
                end=day_end
            ))
        
        return available_slots
    
    def _remove_used_time(
        self,
        slots: List[TimeSlot],
        start: datetime,
        end: datetime
    ) -> List[TimeSlot]:
        """Remove used time from available slots"""
        new_slots = []
        
        for slot in slots:
            # No overlap
            if end <= slot.start or start >= slot.end:
                new_slots.append(slot)
            # Partial overlap - split the slot
            elif start > slot.start:
                if end < slot.end:
                    # Split into two
                    new_slots.append(TimeSlot(slot.start, start))
                    new_slots.append(TimeSlot(end, slot.end))
                else:
                    # Keep beginning
                    new_slots.append(TimeSlot(slot.start, start))
            elif end < slot.end:
                # Keep end
                new_slots.append(TimeSlot(end, slot.end))
        
        return new_slots
    
    def _priority_value(self, priority: str) -> int:
        """Convert priority string to numeric value"""
        priority_map = {
            'urgent': 4,
            'high': 3,
            'medium': 2,
            'low': 1
        }
        return priority_map.get(priority.lower(), 2)
    
    def _calculate_schedule_score(self, scheduled_tasks: List[Dict[str, Any]]) -> float:
        """Calculate overall schedule quality score"""
        if not scheduled_tasks:
            return 0.0
        
        total_score = sum(t.get('slot_score', 0) for t in scheduled_tasks)
        return round(total_score / len(scheduled_tasks), 2)
    
    def _generate_recommendations(
        self,
        scheduled_tasks: List[Dict[str, Any]],
        unscheduled_tasks: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations for the schedule"""
        recommendations = []
        
        if unscheduled_tasks:
            recommendations.append(
                f"{len(unscheduled_tasks)} task(s) couldn't be scheduled. "
                "Consider rescheduling non-essential events or splitting large tasks."
            )
        
        if len(scheduled_tasks) > 6:
            recommendations.append(
                "You have many tasks scheduled. Remember to take breaks between focused work."
            )
        
        return recommendations

