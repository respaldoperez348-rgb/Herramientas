from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Optional

@dataclass
class Habit:
    id: str
    user_id: str
    name: str
    description: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    completion_dates: List[date] = field(default_factory=list)

class HabitoService:
    
    def __init__(self, db_repository):
        # Inject your database repository/ORM session here
        self.db = db_repository

    def create_habit(self, user_id: str, name: str, description: str = "") -> Habit:
     
        habit = Habit(
            id=self._generate_id(),
            user_id=user_id,
            name=name,
            description=description
        )
        self.db.save_habit(habit)
        return habit

    def log_completion(self, habit_id: str, completion_date: Optional[date] = None) -> bool:
       
        target_date = completion_date or date.today()
        habit = self.db.get_habit(habit_id)
        
        if not habit:
            raise ValueError(f"Habit with ID {habit_id} not found.")
            
        if target_date not in habit.completion_dates:
            habit.completion_dates.append(target_date)
            # Sort to keep chronological order
            habit.completion_dates.sort()
            self.db.update_habit(habit)
            return True
            
        return False

    def calculate_current_streak(self, habit_id: str) -> int:
        """Calculates the current consecutive day streak for a habit."""
        habit = self.db.get_habit(habit_id)
        if not habit or not habit.completion_dates:
            return 0
            
        # Simplified streak logic (assumes sorted dates)
        streak = 0
        current_date = date.today()
        
        for completion_date in reversed(habit.completion_dates):
            delta = (current_date - completion_date).days
            if delta == streak:
                streak += 1
            elif delta > streak:
                break
                
        return streak

    def _generate_id(self) -> str:
        import uuid
        return str(uuid.uuid4())
