from agents_course.exam import agent
import pandas as pd
from agents_course.exam.answerbank import update_key


questions = pd.read_csv("./downloads/questions.csv")

questions_to_solve = [
    # -- skipped intentionally --
    #"a1e91b78-d3d8-4675-bb8d-62741b4b68a6", # .. In the video https://www.youtube.com/watch?v=L1vXCYZAYYM
    #"9d191bce-651d-4746-be2d-7ef8ecadb9c2", # .. "Examine the video at https://www.youtube.com/watch?v=1htKBjuUWec.
    #"7bd855d8-463d-4ed5-93ca-5fe35145f733", # .. The attached Excel file contains the sales of menu items for a local

    # -- unsure / not solved --
    #"cabe07ed-9eca-40ea-8ead-410ef5e83f91", # .. What is the surname of the equine veterinarian mentioned in
    #"840bfca7-4f7b-481a-8794-c560c340185d", # .. On June 6, 2023, an article by Carolyn Collins Petersen was published

    # -- solved --
    #"8e867cd7-cff9-4e6c-867a-ff5ddc2550be", # .. How many studio albums were published by Mercedes Sosa between
    #"2d83110e-a098-4ebb-9987-066c06fa42d0", # .. .rewsna eht sa ""tfel"" drow eht fo
    #"cca530fc-4052-43b2-b130-b30968d8aa44", # .. Review the chess position provided in the image
    #"4fc2f1ae-8625-45b5-ab34-ad4433bc21f8", # .. Who nominated the only Featured Article on English
    #"6f37996b-2ac7-44b0-8e68-6d28256631b4", # .. Given this table defining * on the set S = {a, b, c, d, e}
    #"3cef3a44-215e-4aed-8e3b-b1e3f08063b7", # .. I'm making a grocery list for my mom, but she's a
    #"99c9cc74-fdc8-46c6-8f8d-3ce2d3bfeea3", # .. Hi, I'm making a pie but I could use some help with my shopping
    #"305ac316-eef6-4446-960a-92d80d542f82", # .. Who did the actor who played Ray in the Polish-language version
    #"f918266a-b3e0-4914-865d-4faa564f1aef", # .. What is the final numeric output from the attached Python code
    #"3f57289b-8c60-48be-bd80-01f8099ca449", # .. How many at bats did the Yankee with the most walks
    #"1f975693-876d-457b-a649-393859e79bf3", # .. Hi, I was out sick from my classes on Friday, so I'm trying to figure
    #"a0c07678-e491-4bbc-8f0b-07405144218f", # .. Who are the pitchers with the number before and after Taishō Tamai
    #"5a0c1adf-205e-4841-a666-7c3ef95def9d", # .. What is the first name of the only Malko Competition recipient from
    #"bda648d7-d618-4883-88f4-3466eabd860e", # .. Where were the Vietnamese specimens described by Kuznetzov in
    #"cf106601-ab4f-4af9-b045-5295fe67b37d", # .. What country had the least number of athletes at the 1928 Summer



]


for idx, row in questions.iterrows():
    q = row["question"]
    task_id = row["task_id"]

    if task_id not in questions_to_solve:
        print(f"Skipping task {task_id}")
        continue

    header = f"Task id: {task_id}"
    print("="*30 + header + "="*30)

    print("Q: ", q)
    if pd.notnull(row["file_url"]):
        print("Q attachment: ", row["file_url"])

    print("-"*20)

    a = agent.ask_agent_a_question(q, attachment=row["file_url"])

    final_answer = a.split("FINAL ANSWER:")[-1].strip()
    update_key(task_id, final_answer)

    print("A: ", a)
    print("="*(60 - len(header)))
    input("Press any key to continue...")

