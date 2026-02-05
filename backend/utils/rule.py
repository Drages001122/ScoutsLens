from abc import ABC, abstractmethod


class Rule(ABC):
    def __init__(self, description: str):
        self.description = description

    @abstractmethod
    def verify(self, starting_players: list, bench_players: list) -> bool:
        pass


class SalaryRule(Rule):
    def __init__(self, max_salary: int):
        super().__init__("薪资限制")
        self.max_salary = max_salary

    def verify(self, starting_players: list, bench_players: list) -> bool:
        total_salary = sum(p.get("salary", 0) for p in starting_players + bench_players)
        return total_salary <= self.max_salary


class PlayerCountRule(Rule):
    def __init__(self, starting_player_count: int, bench_player_count: int):
        super().__init__("球员数量限制")
        self.starting_player_count = starting_player_count
        self.bench_player_count = bench_player_count

    def verify(self, starting_players: list, bench_players: list) -> bool:
        starting_players = len(starting_players)
        bench_players = len(bench_players)
        return (
            self.starting_player_count == starting_players
            and self.bench_player_count == bench_players
        )
