ANSWER_FILE = "./downloads/answers.txt"


def update_key(key, value):
    data = {}
    try:
        with open(ANSWER_FILE, "r") as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    data[k] = v
    except FileNotFoundError:
        pass  # File doesn't exist yet — that's fine

    data[key] = str(value)

    with open(ANSWER_FILE, "w") as f:
        for k, v in data.items():
            f.write(f"{k}={v}\n")


def get_answer(key):
    data = {}
    try:
        with open(ANSWER_FILE, "r") as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    data[k] = v
    except FileNotFoundError:
        return ""

    return data.get(key, "default answer")
