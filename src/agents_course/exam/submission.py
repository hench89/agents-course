import gradio as gr
import pandas as pd
import requests
from dotenv import load_dotenv

from agents_course.exam.answerbank import get_answer

load_dotenv()

DEFAULT_API_URL = "https://agents-course-unit4-scoring.hf.space"
LOCAL_QUESTIONS_PATH = "./downloads/questions.csv"
LOCAL_ANSWERS_PATH = "./downloads/answers.csv"


def _download_questions() -> pd.DataFrame:
    questions_url = f"{DEFAULT_API_URL}/questions"
    response = requests.get(questions_url, timeout=15)
    response.raise_for_status()
    questions_data = response.json()

    df = pd.DataFrame(questions_data)[["task_id", "question", "file_name"]]

    def _get_attachment_url(task_id: str, file_name: str) -> str:
        if not file_name:
            return ""
        return DEFAULT_API_URL + "/files/" + task_id

    df["file_url"] = df.apply(lambda row: _get_attachment_url(row["task_id"], row["file_name"]), axis=1)
    df["file_extension"] = df["file_name"].apply(lambda x: x.split(".")[-1] if x else "")
    df.to_csv(LOCAL_QUESTIONS_PATH, index=False)

    return f"Succesfully downloaded questions and saved to {LOCAL_QUESTIONS_PATH}"


def _submit_answers(username: str, submit_url: str, answers_payload: list) -> str:
    submission_data = {
        "username": username.strip(),
        "agent_code": "https://huggingface.co/spaces//tree/main",
        "answers": answers_payload
    }
    response = requests.post(submit_url, json=submission_data, timeout=60)
    response.raise_for_status()
    result_data = response.json()
    final_status = (
        f"Submission Successful!\n"
        f"User: {result_data.get('username')}\n"
        f"Overall Score: {result_data.get('score', 'N/A')}% "
        f"({result_data.get('correct_count', '?')}/{result_data.get('total_attempted', '?')} correct)\n"
        f"Message: {result_data.get('message', 'No message received.')}"
    )
    return final_status



def run_and_submit_all(profile: gr.OAuthProfile | None) -> tuple:

    if not profile:
        print("User not logged in.")
        return "Please Login to Hugging Face with the button.", None

    username= f"{profile.username}"
    print(f"User logged in: {username}")

    results_log = []
    answers_payload = []

    df = pd.read_csv(LOCAL_QUESTIONS_PATH)
    for idx, row in df.iterrows():
        question_text = row["question"]
        task_id = row["task_id"]
        submitted_answer = get_answer(task_id)
        answers_payload.append({"task_id": task_id, "submitted_answer": submitted_answer})
        results_log.append({"Task ID": task_id, "Question": question_text, "Submitted Answer": submitted_answer})

    submit_url = f"{DEFAULT_API_URL}/submit"

    results_df = pd.DataFrame(results_log)
    final_status = _submit_answers(username, submit_url, answers_payload)
    return final_status, results_df


with gr.Blocks() as demo:

    gr.Markdown("# Agent Course Unit 4 Evaluation Submission")
    gr.LoginButton()

    gr.Markdown("## Actions")
    download_button = gr.Button("Download Evaluation Questions")
    run_button = gr.Button("Submit All Answers")

    gr.Markdown("## Outputs")
    status_output = gr.Textbox(label="Control Panel", lines=1, interactive=False)
    results_table = gr.DataFrame(label="Questions and Agent Answers", wrap=True)

    download_button.click(fn=_download_questions, outputs=[status_output])
    run_button.click(fn=run_and_submit_all, outputs=[status_output, results_table])


if __name__ == "__main__":
    demo.launch(debug=True, share=False)
