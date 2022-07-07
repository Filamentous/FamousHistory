# FamousHistory
Using RIOT API
This a gimmick that uses RIOT api to check if a user appears in a pre-processed json.

Setup: Visit the RIOT developer portal and create a developement key.
Add this developement key to the Init in the script

HOW TO USE:
1. View example input, fill in necessary summoner information
2. Using the created input file, use the check_json function, to request only a few games from each summoner to check that they exist within the RIOT api
3. After removing or revising specified usernames, use the process_json function, this will process all games for the summoners in the input file and create a new file with the specified name
4. The check_history function will process a username and check if they have played with any of the specifed summoners in the pre-processed list.
5. The output from check history will be None or a list of tuples:("MATCH_ID", "LABEL/TAG AS summonername")
