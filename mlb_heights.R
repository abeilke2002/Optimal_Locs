player_ids <- read_csv(file.choose())
pitcher_ids <- player_ids |> 
  pull(pitcher_id) |> 
  as.numeric()

pitcher_ids_list <- as.list(pitcher_ids)
names(pitcher_ids_list) <- paste0("id_", seq_along(pitcher_ids))


batch_size <- 100
pitcher_id_batches <- split(pitcher_ids_list, ceiling(seq_along(pitcher_ids_list) / batch_size))

# Initialize an empty list to store results
all_people <- list()

# Fetch data for each batch
for (i in seq_along(pitcher_id_batches)) {
  batch <- pitcher_id_batches[[i]]
  tryCatch({
    people <- mlb_people(person_ids = batch)
    all_people[[i]] <- people
  }, error = function(e) {
    message(paste("Error with batch", i, ":", e$message))
  })
}


all_people_df <- bind_rows(all_people)

all_people_df <- all_people_df |> 
  select(id, full_name, height)

# View or save the data
write.csv(all_people_df, "player_info.csv", row.names = FALSE)
