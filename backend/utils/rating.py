def calculate_player_score(
    three_pointers: int,
    two_pointers: int,
    free_throws: int,
    offensive_rebounds: int,
    defensive_rebounds: int,
    assists: int,
    steals: int,
    blocks: int,
    field_goals_attempted: int,
    field_goals_made: int,
    free_throws_attempted: int,
    turnovers: int,
    personal_fouls: int,
    team_won: bool,
    minutes_played: int,
):
    score = (
        (three_pointers * 1.5)
        + two_pointers
        + (free_throws * 0.5)
        + offensive_rebounds
        + (defensive_rebounds * 0.7)
        + assists
        + (steals * 1.2)
        + (blocks * 1.2)
        - ((field_goals_attempted - field_goals_made) * 0.7)
        - ((free_throws_attempted - free_throws) * 0.4)
        - (turnovers * 1.2)
        - (personal_fouls * 0.4)
    )
    if minutes_played > 0:
        if team_won:
            score += 2
        else:
            score -= 2
    return score
