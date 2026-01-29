def calculate_player_score(
    three_pointers,
    two_pointers,
    free_throws,
    offensive_rebounds,
    defensive_rebounds,
    assists,
    steals,
    blocks,
    field_goals_attempted,
    field_goals_made,
    free_throws_attempted,
    turnovers,
    personal_fouls,
    team_won,
    minutes_played,
):
    score = (
        (three_pointers * 1.5)
        + two_pointers
        + (free_throws * 0.5)
        + offensive_rebounds
        + (defensive_rebounds * 0.7)
        + assists
        + steals
        + blocks
        - ((field_goals_attempted - field_goals_made) * 0.7)
        - ((free_throws_attempted - free_throws) * 0.4)
        - turnovers
        - (personal_fouls * 0.4)
    )
    if minutes_played > 0:
        if team_won:
            score += 2
        else:
            score -= 2
    return score
