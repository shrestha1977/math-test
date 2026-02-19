import streamlit as st
import random
import time

TEST_DURATION = 300  
QUESTION_POOL_SIZE = 100  


# ================= QUESTION GENERATOR =================
def generate_math_questions(num=QUESTION_POOL_SIZE):
    questions = []

    for _ in range(num):

        difficulty = random.choices(
            ["easy", "moderate", "hard"],
            weights=[0.4, 0.35, 0.25]
        )[0]

        if difficulty == "easy":

            pattern = random.choice(["add", "sub", "mul", "div"])

            if pattern == "add":
                a, b = random.randint(1, 50), random.randint(1, 50)
                expr = f"{a} + {b}"

            elif pattern == "sub":
                a, b = random.randint(20, 70), random.randint(1, 20)
                expr = f"{a} - {b}"

            elif pattern == "mul":
                a, b = random.randint(2, 12), random.randint(2, 12)
                expr = f"{a} * {b}"

            else:  # div
                b = random.randint(2, 12)
                answer = random.randint(2, 12)
                a = b * answer
                expr = f"{a} / {b}"

        elif difficulty == "moderate":

            pattern = random.choice(["add_mul", "sub_mul", "div_add", "add_div"])

            if pattern == "add_mul":
                a, b, c = random.randint(1, 20), random.randint(1, 10), random.randint(1, 10)
                expr = f"{a} + {b} * {c}"

            elif pattern == "sub_mul":
                a, b, c = random.randint(20, 50), random.randint(1, 10), random.randint(1, 10)
                expr = f"{a} - {b} * {c}"

            elif pattern == "div_add":
                b = random.randint(2, 10)
                answer = random.randint(2, 10)
                a = b * answer
                c = random.randint(1, 20)
                expr = f"{a} / {b} + {c}"

            else:  # add_div
                b = random.randint(2, 10)
                answer = random.randint(2, 10)
                a = b * answer
                c = random.randint(1, 20)
                expr = f"{c} + {a} / {b}"

        else:  # hard

            pattern = random.choice(["bracket_mul", "bracket_div", "complex_mix"])

            if pattern == "bracket_mul":
                a, b, c = random.randint(1, 20), random.randint(1, 20), random.randint(1, 10)
                expr = f"({a} - {b}) * {c}"

            elif pattern == "bracket_div":
                b = random.randint(2, 10)
                answer = random.randint(2, 10)
                a = b * answer
                c = random.randint(1, 10)
                expr = f"({a} / {b}) + {c}"

            else:  # complex mix
                a, b, c, d = random.randint(1, 20), random.randint(1, 10), random.randint(2, 10), random.randint(1, 10)
                expr = f"({a} + {b}) - {c} * {d}"

        answer = int(eval(expr))
        questions.append((expr, answer, difficulty))

    return questions

# ================= SESSION STATE =================
if "test_started" not in st.session_state:
    st.session_state.test_started = False

if "start_time" not in st.session_state:
    st.session_state.start_time = None

if "questions" not in st.session_state:
    st.session_state.questions = generate_math_questions()

if "current_question_index" not in st.session_state:
    st.session_state.current_question_index = 0

if "correct_count" not in st.session_state:
    st.session_state.correct_count = 0

if "attempted" not in st.session_state:
    st.session_state.attempted = 0

if "difficulty_stats" not in st.session_state:
    st.session_state.difficulty_stats = {
        "low_attempted": 0,
        "moderate_attempted": 0,
        "high_attempted": 0,
        "low_correct": 0,
        "moderate_correct": 0,
        "high_correct": 0,
    }



# ================= TITLE =================
st.title("Numerical Ability Cognitive Task")


# ================= START SCREEN =================
if not st.session_state.test_started:

    st.write("You will have **5 minutes** to solve as many questions as possible.")
    if st.button("Start Test"):
        st.session_state.test_started = True
        st.session_state.start_time = time.time()
        st.rerun()


# ================= TEST RUNNING =================
else:

    elapsed = time.time() - st.session_state.start_time
    remaining = int(TEST_DURATION - elapsed)

    # ===== TIMER DISPLAY =====
    mins = max(0,remaining) // 60
    secs = max(0,remaining) % 60
    st.metric("⏳ Time Remaining", f"{mins:02d}:{secs:02d}")

    # ===== TIME UP =====
    if remaining <= 0:
        st.session_state.test_started = False
        st.success("Time's up!")
        st.write("Questions Attempted:", st.session_state.attempted)
        st.write("Correct Answers:", st.session_state.correct_count)

        if st.session_state.attempted > 0:
            accuracy = st.session_state.correct_count / st.session_state.attempted
            st.write("Accuracy:", f"{accuracy:.2f}")

            stats = st.session_state.difficulty_stats

            # difficulty weights
            weights = {
                "low": 1,
                "moderate": 2,
                "high": 3
            }

            weighted_correct = (
                stats["low_correct"] * weights["low"] +
                stats["moderate_correct"] * weights["moderate"] +
                stats["high_correct"] * weights["high"]
            )

            weighted_attempted = (
                stats["low_attempted"] * weights["low"] +
                stats["moderate_attempted"] * weights["moderate"] +
                stats["high_attempted"] * weights["high"]
            )

            # avoid divide by zero
            if weighted_attempted > 0:
                weighted_accuracy = weighted_correct / weighted_attempted
            else:
                weighted_accuracy = 0

            speed_efficiency = st.session_state.attempted / QUESTION_POOL_SIZE
            speed_efficiency = min(speed_efficiency, 1)

            numerical_score = (0.7 * weighted_accuracy) + (0.3 * speed_efficiency)
            
            st.write("Weighted Accuracy:", f"{weighted_accuracy:.2f}")
            st.write("Speed Efficiency:", f"{speed_efficiency:.2f}")
            st.write("Numerical Ability Score:", f"{numerical_score:.2f}")

            # store normalized score
            st.session_state["numerical_score"] = numerical_score


        if st.button("Restart"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    else:

        idx = st.session_state.current_question_index
        question, correct_answer, difficulty = st.session_state.questions[idx]

        st.subheader(f"Question: {question} = ?")

        with st.form("math_form", clear_on_submit=True):
            ans = st.text_input("Your answer", key="answer_input")
            submit = st.form_submit_button("Next")

        if submit:

            st.session_state.attempted += 1

            try:
                if int(ans) == correct_answer:
                    st.session_state.correct_count += 1
            except:
                pass

            # difficulty mapping
            if difficulty == "easy":
                level = "low"
            elif difficulty == "moderate":
                level = "moderate"
            else:
                level = "high"

            # increment attempted
            st.session_state.difficulty_stats[f"{level}_attempted"] += 1

            # increment correct if correct
            if int(ans) == correct_answer:
                st.session_state.difficulty_stats[f"{level}_correct"] += 1

            st.session_state.current_question_index += 1
            st.rerun()

        time.sleep(1)
        st.rerun()
