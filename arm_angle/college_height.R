library(devtools)
library(tidyverse)
devtools::install_github(repo = "robert-frey/collegebaseball", force = TRUE)
library(collegebaseball)

d1_teams <- ncaa_teams(years = 2025, divisions = 1)
ids <- d1_teams$team_id

roster_list <- list()

for (i in seq_along(ids)) {
  team_id <- ids[i]  # Get the current team_id
  roster_list[[team_id]] <- ncaa_roster(team_id = team_id, 2025)
}

combined_rosters <- do.call(rbind, roster_list)


heights <- combined_rosters |> 
  filter(position == "P") |> 
  mutate(
    height_in_inches = as.numeric(sub("-.*", "", height)) * 12 +  # Extract feet and convert to inches
      as.numeric(sub(".*-", "", height))
  ) |> 
  select(player_name, height_in_inches) |> 
  na.omit()

write_csv(heights, "college_height.csv")

